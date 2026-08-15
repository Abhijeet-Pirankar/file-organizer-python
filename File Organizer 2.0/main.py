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
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from gui import App


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()
