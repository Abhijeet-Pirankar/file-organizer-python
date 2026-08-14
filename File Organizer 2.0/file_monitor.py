"""
file_monitor.py
---------------
Optional "Watch Folder" feature for File Organizer v2.0.

Uses the `watchdog` library to monitor a directory for new files and
automatically organizes them as they arrive.

The monitor runs in a background thread and calls a user-supplied callback
when a file is successfully organized.
"""

import threading
import time
from pathlib import Path
from typing import Callable, Optional

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


import categories
import organizer as org_module
import config_manager

_global_monitor = None


# ── Event Handler ─────────────────────────────────────────────────────────────

class _OrganizerEventHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """
    Handles file-system events from watchdog.
    Only reacts to newly created files in the root of the watched folder
    (not inside organizer-owned subdirectories).
    """

    def __init__(
        self,
        watch_folder: Path,
        on_file_organized: Callable[[str, str], None],
        cooldown: float = 1.0,
    ) -> None:
        super().__init__()
        self.watch_folder = watch_folder
        self.on_file_organized = on_file_organized
        self.cooldown = cooldown  # seconds to wait before processing (file write finish)
        self._skip_dirs = set(categories.ORGANIZER_FOLDERS)
        self._processed: set[str] = set()  # avoid re-processing same file

    def on_created(self, event: "FileSystemEvent") -> None:
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only handle files directly inside the watch folder
        try:
            relative = file_path.relative_to(self.watch_folder)
        except ValueError:
            return

        # Skip files inside organizer-owned folders
        if len(relative.parts) > 1 and relative.parts[0] in self._skip_dirs:
            return

        # Skip already-processed files (watchdog sometimes fires twice)
        key = str(file_path)
        if key in self._processed:
            return
        self._processed.add(key)

        # Wait briefly for the file to finish writing
        time.sleep(self.cooldown)

        if not file_path.exists():
            self._processed.discard(key)
            return

        # Organize the single file
        self._organize_single_file(file_path)

    def _organize_single_file(self, file_path: Path) -> None:
        """Move one file into the correct category folder."""
        auto_org = config_manager.get("watch_auto_organize", True)
        
        cats = categories.get_categories()
        ext = file_path.suffix.lower()
        cat = categories.get_category_for_file(file_path.name, ext, cats)

        if not auto_org:
            self.on_file_organized(file_path.name, f"DETECTED ({cat})")
            return

        dest_dir = self.watch_folder / cat
        dest_dir.mkdir(parents=True, exist_ok=True)

        from duplicate_detector import check_duplicate, get_unique_filename
        import shutil

        dest_path = dest_dir / file_path.name
        dup = check_duplicate(file_path, dest_path)

        if dup.name_conflict:
            if dup.content_duplicate:
                # Exact duplicate — skip silently
                self.on_file_organized(file_path.name, f"SKIPPED (content duplicate → {cat})")
                return
            dest_path = get_unique_filename(dest_path)

        try:
            shutil.move(str(file_path), str(dest_path))
            self.on_file_organized(file_path.name, f"→ {cat}")
        except OSError as e:
            self.on_file_organized(file_path.name, f"ERROR: {e}")


# ── FolderMonitor ─────────────────────────────────────────────────────────────

class FolderMonitor:
    """
    High-level wrapper around watchdog's Observer.
    Runs in a background thread; safe to start/stop from the GUI thread.
    """

    def __init__(
        self,
        folder: str | Path,
        on_file_organized: Callable[[str, str], None],
    ) -> None:
        """
        Args:
            folder:             Directory to watch.
            on_file_organized:  Callback(filename, status_message) called
                                whenever a file is processed.
        """
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError(
                "The 'watchdog' library is required for folder monitoring.\n"
                "Install it with: pip install watchdog"
            )

        self.folder = Path(folder)
        self.on_file_organized = on_file_organized
        self._observer: Optional["Observer"] = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        """Start the background observer thread."""
        global _global_monitor
        if _global_monitor is not None and _global_monitor is not self:
            _global_monitor.stop()
            
        if self._running:
            return

        _global_monitor = self

        handler = _OrganizerEventHandler(
            watch_folder=self.folder,
            on_file_organized=self.on_file_organized,
        )

        self._observer = Observer()
        self._observer.schedule(handler, str(self.folder), recursive=False)
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        """Stop the observer thread gracefully."""
        global _global_monitor
        if not self._running or self._observer is None:
            return
        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        self._running = False
        if _global_monitor is self:
            _global_monitor = None
