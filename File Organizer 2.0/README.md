# 📂 Advanced File Organizer v2.0

> **A professional, modern desktop application for smart and safe file organization — built with Python.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)

---

## 📸 Screenshots

> _Screenshots will be added here after the first release._

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥 **Modern GUI** | Clean dark-themed desktop app built with CustomTkinter |
| 🔍 **Analyze Mode** | Scan a folder and see stats without moving anything |
| 👁 **Preview Mode** | See exactly which file goes where before committing |
| ⚡ **Smart Organize** | Move files to category folders with one click |
| ↩ **Undo** | Restore all files to their original locations after organizing |
| 🔁 **Duplicate Detection** | Detects both filename conflicts AND identical file content (SHA-256) |
| 📂 **Recursive Scanning** | Optionally include subfolders |
| ⚙ **Custom Categories** | Add your own extensions via the Settings panel |
| 👁‍🗨 **Watch Folder** | Auto-organize newly added files in real time |
| 📊 **Statistics Dashboard** | Stat cards + bar chart breakdown by category |
| 📝 **Structured Logging** | Human-readable `log.txt` + machine-readable `organizer_log.jsonl` |
| 📄 **Report** | Auto-generated `report.txt` after each organize run |

---

## 📁 Supported Categories

| Category | Extensions |
|---|---|
| 🖼 Images | `.jpg` `.jpeg` `.png` `.gif` `.webp` `.bmp` `.tiff` `.svg` `.ico` `.heic` `.raw` |
| 📄 PDFs | `.pdf` |
| 🎬 Videos | `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.flv` `.webm` `.m4v` `.3gp` |
| 📝 Docs | `.docx` `.doc` `.txt` `.pptx` `.xlsx` `.odt` `.rtf` `.csv` `.md` |
| 🎵 Music | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` `.wma` |
| 🗜 Archives | `.zip` `.rar` `.7z` `.tar` `.gz` `.bz2` `.xz` `.iso` |
| ⚙ Programs | `.exe` `.msi` `.dmg` `.apk` `.deb` `.rpm` |
| 💻 Code | `.py` `.js` `.ts` `.html` `.css` `.java` `.cpp` `.go` `.rs` `.sql` … |
| 📦 Others | Everything else |

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or newer
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Abhijeet-Pirankar/file-organizer-python.git
cd "file-organizer-python/File Organizer 2.0"

# 2. Install dependencies
pip install -r requirements.txt
```

---

## ▶ How to Run

```bash
python main.py
```

The GUI will open automatically.

---

## 🖱 How to Use

1. **Browse** — Click Browse and select the folder you want to organize.
2. **Analyze** — Click Analyze for a quick stats overview (no files moved).
3. **Preview** — Click Preview to see a file-by-file list of what will happen.
4. **Organize** — Click Organize, confirm the prompt, and let it run.
5. **Undo** — Click Undo to restore all files to their original locations.
6. **Watch** — Click Watch to auto-organize files as they are added to the folder.
7. **Settings** — Customize theme, recursive scan, and add custom extensions.

> ⚠ Files are **never deleted automatically**. Every move can be undone.

---

## 📁 Project Structure

```
File Organizer 2.0/
│
├── main.py               # Entry point — launches the GUI
├── gui.py                # CustomTkinter main window & all dialogs
├── organizer.py          # Core file-moving logic (scan + organize)
├── categories.py         # Category → extension mapping (configurable)
├── duplicate_detector.py # SHA-256 hash + name-conflict detection
├── undo_manager.py       # Session-based undo with JSON persistence
├── file_monitor.py       # watchdog-based folder watcher
├── logger.py             # Structured logging (log.txt + JSONL)
├── config_manager.py     # Settings persistence (~/.file_organizer/)
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore
```

---

## 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| CustomTkinter | Modern GUI framework |
| watchdog | File-system monitoring |
| hashlib (stdlib) | SHA-256 duplicate detection |
| pathlib (stdlib) | Cross-platform path handling |
| shutil (stdlib) | File move operations |
| threading (stdlib) | Non-blocking UI during organize |
| json (stdlib) | Config & undo persistence |
| PyInstaller | Windows EXE packaging |

---

## 📦 Building a Windows EXE

```bash
# Install PyInstaller (included in requirements.txt)
pip install pyinstaller

# Build single-file EXE (no console window)
pyinstaller --onefile --windowed --name="FileOrganizer" main.py

# The EXE will be in the dist/ folder:
#   dist/FileOrganizer.exe
```

> **Tip:** If you have an icon, add `--icon=icon.ico` to the command.

---

## 🔒 Safety Guarantees

- ✅ Files are **never deleted**
- ✅ Files are **never silently overwritten** — duplicates always ask you first
- ✅ Every organization run is **fully undoable**
- ✅ Preview before any large operation
- ✅ Organizer skips its own category folders to avoid re-organizing

---

## 🔮 Future Improvements

- [ ] Drag-and-drop folder selection
- [ ] Cloud sync integration (Google Drive / OneDrive)
- [ ] Scheduled auto-organization
- [ ] Dark/light theme toggle in the header
- [ ] Multi-folder organization in one run
- [ ] Export statistics as CSV

---

## 👨‍💻 Author

**Abhijeet Pirankar**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
