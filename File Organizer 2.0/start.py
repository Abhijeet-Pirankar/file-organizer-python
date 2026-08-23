"""
start.py
--------
Combined startup script for File Organizer v2.0.

Starts both:
  - Python FastAPI backend on http://127.0.0.1:8000
  - Vite React frontend dev server on http://localhost:5173

Usage:
    python start.py

Then open your browser to: http://localhost:5173
"""

import subprocess
import sys
import os
import time
import threading
import signal

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.join(_BASE_DIR, 'frontend')
_VENV_PYTHON = os.path.join(_BASE_DIR, '.venv', 'Scripts', 'python.exe')

# Use venv python if available, else system python
python = _VENV_PYTHON if os.path.exists(_VENV_PYTHON) else sys.executable


def start_backend():
    print("[Backend] Starting FastAPI server on http://127.0.0.1:8000 ...")
    subprocess.run(
        [python, '-m', 'uvicorn', 'server:app', '--host', '127.0.0.1', '--port', '8000'],
        cwd=_BASE_DIR
    )


def start_frontend():
    print("[Frontend] Starting Vite dev server on http://localhost:5173 ...")
    time.sleep(1.5)  # Wait for backend to initialise
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    subprocess.run([npm_cmd, 'run', 'dev'], cwd=_FRONTEND_DIR)


if __name__ == '__main__':
    print("=" * 60)
    print("  File Organizer 2.0")
    print("  Starting backend + frontend...")
    print("=" * 60)

    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Run frontend in main thread (blocks until Ctrl+C)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n[Start] Shutting down...")
