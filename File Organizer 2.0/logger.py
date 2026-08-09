"""
logger.py
---------
Structured logging for File Organizer v2.0.

Each log entry is written as both:
  - A human-readable line in log.txt (append mode, compatible with v1 format)
  - A JSON line in organizer_log.jsonl for machine-readable auditing

Log files are placed inside the target folder being organized.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Log entry structure ───────────────────────────────────────────────────────

class LogEntry:
    """Represents a single loggable event."""

    def __init__(
        self,
        filename: str,
        original_path: str,
        new_path: Optional[str],
        action: str,          # e.g. "MOVED", "SKIPPED", "ERROR", "UNDO"
        status: str,          # "SUCCESS" | "FAILED" | "SKIPPED"
        error_message: Optional[str] = None,
    ) -> None:
        self.timestamp = datetime.now().isoformat(timespec="seconds")
        self.filename = filename
        self.original_path = original_path
        self.new_path = new_path or ""
        self.action = action
        self.status = status
        self.error_message = error_message or ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "filename": self.filename,
            "original_path": self.original_path,
            "new_path": self.new_path,
            "action": self.action,
            "status": self.status,
            "error_message": self.error_message,
        }

    def to_human_line(self) -> str:
        """Single-line human-readable format (log.txt compatible)."""
        if self.error_message:
            return (
                f"[{self.timestamp}] {self.action} | {self.filename} | "
                f"ERROR: {self.error_message}\n"
            )
        if self.new_path:
            return (
                f"[{self.timestamp}] {self.action} | {self.filename} | "
                f"{self.original_path} → {self.new_path}\n"
            )
        return (
            f"[{self.timestamp}] {self.action} | {self.filename} | "
            f"Status: {self.status}\n"
        )


# ── Logger class ──────────────────────────────────────────────────────────────

class OrganizerLogger:
    """
    Writes structured logs to a target folder.
    Call open_session() before logging, close_session() when done.
    """

    def __init__(self, target_folder: str | Path) -> None:
        self.target_folder = Path(target_folder)
        self.log_path = self.target_folder / "log.txt"
        self.jsonl_path = self.target_folder / "organizer_log.jsonl"
        self._log_file = None
        self._jsonl_file = None

    def open_session(self) -> None:
        """Open log files and write a session header."""
        try:
            self.target_folder.mkdir(parents=True, exist_ok=True)
            self._log_file = open(self.log_path, "a", encoding="utf-8")
            self._jsonl_file = open(self.jsonl_path, "a", encoding="utf-8")

            header = (
                f"\n\n===== Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n"
            )
            self._log_file.write(header)
            self._log_file.flush()
        except OSError as e:
            print(f"[Logger] Could not open log files: {e}")

    def log(self, entry: LogEntry) -> None:
        """Write a single log entry to both log files."""
        try:
            if self._log_file and not self._log_file.closed:
                self._log_file.write(entry.to_human_line())
                self._log_file.flush()

            if self._jsonl_file and not self._jsonl_file.closed:
                self._jsonl_file.write(json.dumps(entry.to_dict()) + "\n")
                self._jsonl_file.flush()
        except OSError as e:
            print(f"[Logger] Write error: {e}")

    def log_session_summary(self, total: int, moved: int, errors: int, skipped: int) -> None:
        """Write a summary block at the end of a session."""
        summary = (
            f"--- Summary: Total={total} | Moved={moved} | "
            f"Errors={errors} | Skipped={skipped} ---\n"
            f"===== Session Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n"
        )
        try:
            if self._log_file and not self._log_file.closed:
                self._log_file.write(summary)
                self._log_file.flush()
        except OSError:
            pass

    def close_session(self) -> None:
        """Close open file handles."""
        for handle in (self._log_file, self._jsonl_file):
            if handle and not handle.closed:
                try:
                    handle.close()
                except OSError:
                    pass
        self._log_file = None
        self._jsonl_file = None

    def write_report(self, stats: dict, total_moved: int) -> Path:
        """
        Write a human-readable report.txt to the target folder.
        Returns the path to the report file.
        """
        report_path = self.target_folder / "report.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("FILE ORGANIZER REPORT\n")
                f.write("=" * 40 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total files moved: {total_moved}\n\n")
                f.write("Category Breakdown:\n")
                f.write("-" * 20 + "\n")
                for category, count in stats.items():
                    f.write(f"  {category:<15}: {count}\n")
        except OSError as e:
            print(f"[Logger] Could not write report: {e}")
        return report_path
