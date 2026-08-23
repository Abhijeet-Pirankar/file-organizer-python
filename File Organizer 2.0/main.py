"""
main.py
-------
Entry point for File Organizer v2.0.

This app uses a React/Vite frontend (frontend/) talking to a FastAPI backend (server.py).

To start the application:
    1. Start the backend:    python main.py
    2. Start the frontend:   cd frontend && npm run dev
       Then open: http://localhost:5173

Or use the combined startup script:
    python start.py
"""

import sys
import os
import subprocess
import threading

# ── Ensure the app's own directory is on sys.path ─────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)


def main() -> None:
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
