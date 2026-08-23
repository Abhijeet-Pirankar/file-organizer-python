import dataclasses
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import organizer as org_module
import undo_manager as undo_module
import file_monitor as fm_module

# Ensure the app's own directory is on sys.path
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

app = FastAPI(title="File Organizer API")

# Allow CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

undo_mgr = undo_module.UndoManager()
monitor = None

class AnalyzeRequest(BaseModel):
    folder: str
    recursive: bool

class OrganizeRequest(BaseModel):
    folder: str
    recursive: bool

class WatchRequest(BaseModel):
    folder: str

@app.get("/api/browse")
def browse_folder():
    """Opens a native folder dialog and returns the selected path."""
    import subprocess
    import sys
    import os

    print("\nBACKEND:", flush=True)
    print("Browse request received", flush=True)
    print("-> opening folder picker", flush=True)

    try:
        picker_script = os.path.join(os.path.dirname(__file__), "folder_picker.py")
        result = subprocess.run(
            [sys.executable, picker_script],
            capture_output=True,
            text=True,
            timeout=120,
        )
        folder_path = result.stdout.strip()
    except subprocess.TimeoutExpired:
        folder_path = ""
    except Exception:
        folder_path = ""

    if folder_path:
        print("\nBACKEND:")
        print(f"Folder selected: {folder_path}")
    else:
        print("\nBACKEND:")
        print("Folder selection was cancelled or failed.")

    return {"path": folder_path}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    if not req.folder or not os.path.isdir(req.folder):
        raise HTTPException(status_code=400, detail="Invalid folder path")
        
    try:
        res = org_module.scan_folder(req.folder, req.recursive)
        
        # Convert to the format expected by the React frontend
        
        # 1. File Info
        files = []
        for fp in res.file_previews:
            files.append({
                "filename": fp.filename,
                "size": fp.file_size,
                "category": fp.destination_category,
                "status": "Error" if fp.is_name_conflict else "Ready",
                "path": str(fp.source_path)
            })
            
        # 2. Statistics
        stats = {
            "totalFiles": res.total_files,
            "organized": 0, # Since this is just analysis
            "duplicates": res.content_duplicates,
            "errors": res.name_conflicts,
            "others": res.going_to_others,
            "totalSize": res.total_size
        }
        
        # 3. Categories
        categories = []
        total_org = res.organizable
        for cat_name, count in res.category_counts.items():
            if count > 0:
                percentage = (count / total_org * 100) if total_org > 0 else 0
                categories.append({
                    "name": cat_name,
                    "count": count,
                    "percentage": round(percentage, 2)
                })
        # Sort categories by count descending
        categories.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "files": files,
            "stats": stats,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/organize")
def organize(req: OrganizeRequest):
    if not req.folder or not os.path.isdir(req.folder):
        raise HTTPException(status_code=400, detail="Invalid folder path")
        
    try:
        # For a full implementation, we could stream progress via SSE, 
        # but the current UI simulates progress and waits for completion.
        res = org_module.organize_folder(
            folder_path=req.folder,
            recursive=req.recursive,
            on_progress=None,
            on_duplicate=None, # Uses KEEP_BOTH by default
            undo_mgr=undo_mgr
        )
        return {"success": True, "errors": res.error_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/undo")
def undo():
    if not undo_mgr.can_undo():
        return {"success": False, "message": "Nothing to undo."}
        
    try:
        res = undo_mgr.undo_last()
        return {"success": True, "details": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/watch")
def toggle_watch(req: WatchRequest):
    global monitor
    if not fm_module.WATCHDOG_AVAILABLE:
        raise HTTPException(status_code=500, detail="Watchdog library not installed.")
        
    if monitor and monitor.is_running:
        monitor.stop()
        monitor = None
        return {"status": "stopped"}
        
    if not req.folder or not os.path.isdir(req.folder):
        raise HTTPException(status_code=400, detail="Invalid folder path")
        
    try:
        def on_organized(filename, status):
            # In a full app, this would use websockets to notify the UI
            pass
            
        monitor = fm_module.FolderMonitor(req.folder, on_organized)
        monitor.start()
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
