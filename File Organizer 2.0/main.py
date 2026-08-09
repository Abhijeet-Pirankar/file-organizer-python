"""
main.py
-------
Entry point for File Organizer v2.0.

Run with:
    python main.py

Build EXE with:
    pyinstaller --onefile --windowed --icon=icon.ico --name="FileOrganizer" main.py
"""

import sys
import os

# ── Ensure the app's own directory is on sys.path ─────────────────────────────
# This matters when running from a PyInstaller bundle where the CWD may differ.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

# ── Windows: enable high-DPI awareness before any Tk/CTk import ───────────────
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        pass  # non-fatal — just means no DPI scaling fix on older Windows

# ── Launch the application ────────────────────────────────────────────────────
from gui import App


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()
