"""
undo_manager.py
---------------
Tracks every file move performed by the organizer and allows the user to
restore files to their original locations (undo the last session).

Undo history is persisted to ~/.file_organizer/undo_history.json so it
survives application restarts.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional


# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".file_organizer"
UNDO_FILE = CONFIG_DIR / "undo_history.json"


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class UndoRecord:
    """Represents a single file move that can be reversed."""
    original_path: str    # where the file came from
    new_path: str         # where the file was moved to
    timestamp: str        # ISO-8601 timestamp of the move


@dataclass
class UndoSession:
    """A group of UndoRecords created by one Organize operation."""
    session_id: str           # ISO timestamp used as unique key
    folder: str               # the folder that was organized
    records: List[UndoRecord]
    errors: int = 0
    duplicates: int = 0
    skipped: int = 0


# ── UndoManager ──────────────────────────────────────────────────────────────

class UndoManager:
    """
    Manages undo sessions. Each Organize run creates one session.
    Only the last session is kept for undo (older history is retained in the
    JSON for auditing but cannot be selectively undone via the UI).
    """

    def __init__(self) -> None:
        self._current_session: Optional[UndoSession] = None
        self._all_sessions: List[dict] = self._load_raw()

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def start_session(self, folder: str) -> None:
        """Begin recording moves for a new organize operation."""
        session_id = datetime.now().isoformat(timespec="seconds")
        self._current_session = UndoSession(
            session_id=session_id,
            folder=folder,
            records=[],
        )

    def record_move(self, original: Path, new: Path) -> None:
        """Record one file move. Must be called after start_session()."""
        if self._current_session is None:
            return
        self._current_session.records.append(
            UndoRecord(
                original_path=str(original),
                new_path=str(new),
                timestamp=datetime.now().isoformat(timespec="seconds"),
            )
        )

    def commit_session(self, errors: int = 0, duplicates: int = 0, skipped: int = 0) -> None:
        """
        Finalize the current session and persist it to disk.
        Keeps the 10 most recent sessions in history.
        """
        if self._current_session is None:
            return

        self._current_session.errors = errors
        self._current_session.duplicates = duplicates
        self._current_session.skipped = skipped

        session_dict = {
            "session_id": self._current_session.session_id,
            "folder": self._current_session.folder,
            "records": [asdict(r) for r in self._current_session.records],
            "errors": errors,
            "duplicates": duplicates,
            "skipped": skipped
        }

        self._all_sessions.append(session_dict)
        # Keep only the 10 most recent sessions
        self._all_sessions = self._all_sessions[-10:]

        self._save_raw(self._all_sessions)
        self._current_session = None

    def discard_session(self) -> None:
        """Discard the current session without saving (e.g. on error)."""
        self._current_session = None

    # ── Undo ─────────────────────────────────────────────────────────────────

    def can_undo(self) -> bool:
        """Returns True if there is at least one saved session to undo."""
        return len(self._all_sessions) > 0

    def get_last_session_summary(self) -> Optional[dict]:
        """Return the most recent session's metadata (no full record list)."""
        if not self._all_sessions:
            return None
        s = self._all_sessions[-1]
        return {
            "session_id": s["session_id"],
            "folder": s["folder"],
            "file_count": len(s.get("records", [])),
            "errors": s.get("errors", 0),
            "duplicates": s.get("duplicates", 0),
            "skipped": s.get("skipped", 0)
        }

    def get_all_sessions_summary(self) -> List[dict]:
        """Return metadata for all sessions in history."""
        summaries = []
        for s in reversed(self._all_sessions):
            summaries.append({
                "session_id": s["session_id"],
                "folder": s["folder"],
                "file_count": len(s.get("records", [])),
                "errors": s.get("errors", 0),
                "duplicates": s.get("duplicates", 0),
                "skipped": s.get("skipped", 0)
            })
        return summaries

    def undo_last(
        self,
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> dict:
        """
        Restore all files from the most recent session to their original paths.

        Args:
            on_progress: Optional callback(filename, status) for UI updates.

        Returns:
            {
                "restored": int,
                "skipped": int,
                "errors": List[str],
                "total": int,
            }
        """
        if not self._all_sessions:
            return {"restored": 0, "skipped": 0, "errors": [], "total": 0}

        last_session = self._all_sessions[-1]
        records = last_session.get("records", [])

        restored = 0
        skipped = 0
        errors: List[str] = []

        for rec in reversed(records):  # reverse order for safety
            src = Path(rec["new_path"])
            dest = Path(rec["original_path"])

            filename = src.name

            if not src.exists():
                msg = f"File no longer exists: {src.name}"
                errors.append(msg)
                if on_progress:
                    on_progress(filename, f"MISSING: {src.name}")
                continue

            if dest.exists():
                msg = f"Original location occupied: {dest.name}"
                errors.append(msg)
                if on_progress:
                    on_progress(filename, f"CONFLICT: {dest.name}")
                skipped += 1
                continue

            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dest)
                restored += 1
                if on_progress:
                    on_progress(filename, "RESTORED")
            except OSError as e:
                msg = f"Error restoring {src.name}: {e}"
                errors.append(msg)
                if on_progress:
                    on_progress(filename, f"ERROR: {e}")

        # Remove the undone session from history
        if not errors and skipped == 0:
            self._all_sessions.pop()
            self._save_raw(self._all_sessions)

        return {
            "restored": restored,
            "skipped": skipped,
            "errors": errors,
            "total": len(records),
        }

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load_raw(self) -> List[dict]:
        if not UNDO_FILE.exists():
            return []
        try:
            with open(UNDO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_raw(self, sessions: List[dict]) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(UNDO_FILE, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"[UndoManager] Could not save undo history: {e}")
