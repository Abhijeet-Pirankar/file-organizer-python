import webview
import threading
import dataclasses
from pathlib import Path
import organizer as org_module
import undo_manager as undo_module
import file_monitor as fm_module

class Api:
    def __init__(self):
        self._window = None
        self.undo_mgr = undo_module.UndoManager()
        self.monitor = None

    def set_window(self, window):
        self._window = window

    def browse_folder(self):
        if not self._window:
            return None
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return None

    def analyze(self, folder, recursive):
        # We can just return dict directly for simple structures
        res = org_module.scan_folder(folder, recursive)
        # Avoid sending all previews to save bandwidth if not needed, but JS expects it.
        # Actually JS `analyze` only uses stats, not `file_previews`.
        d = dataclasses.asdict(res)
        d['file_previews'] = [] # Don't send huge list for just analyze
        return d

    def preview(self, folder, recursive):
        res = org_module.scan_folder(folder, recursive)
        # Convert path objects to strings for JSON serialization
        for fp in res.file_previews:
            fp.source_path = str(fp.source_path)
            fp.destination_path = str(fp.destination_path)
        return dataclasses.asdict(res)

    def organize(self, folder, recursive):
        def on_progress(filename, cat, idx, total_f):
            # Send real-time updates to JS
            if self._window:
                # evaluate_js is thread-safe in pywebview
                self._window.evaluate_js(f"window.pyUpdateProgress('{filename}', '{cat}', {idx}, {total_f})")
                
        def on_duplicate(fp, dup_info):
            # Safe default for web version without popup (for now, KEEP_BOTH)
            # In a full implementation, this could call JS to show a modal and wait.
            # Using the safe default from config or KEEP_BOTH.
            return org_module.DuplicateAction.KEEP_BOTH

        # Run in same thread since pywebview JS API calls run in a worker thread automatically.
        res = org_module.organize_folder(
            folder_path=folder,
            recursive=recursive,
            on_progress=on_progress,
            on_duplicate=on_duplicate,
            undo_mgr=self.undo_mgr
        )
        return dataclasses.asdict(res)

    def undo(self):
        if not self.undo_mgr.can_undo():
            return {"error": "Nothing to undo."}
        res = self.undo_mgr.undo_last()
        return {
            "restored": res.get("restored", 0),
            "errors": res.get("errors", []),
            "skipped": res.get("skipped", 0)
        }

    def toggle_watch(self, folder):
        if not fm_module.WATCHDOG_AVAILABLE:
            return {"error": "Watchdog library not installed."}
            
        if self.monitor and self.monitor.is_running:
            self.monitor.stop()
            self.monitor = None
            return {"status": "stopped"}
            
        def on_organized(filename, status):
            if self._window:
                self._window.evaluate_js(f"window.pyWatchEvent('{filename}', '{status}')")
                
        self.monitor = fm_module.FolderMonitor(folder, on_organized)
        self.monitor.start()
        return {"status": "started"}

    def get_activity(self):
        return self.undo_mgr.get_all_sessions_summary()
