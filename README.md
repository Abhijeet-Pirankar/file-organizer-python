# 📁 Advanced File Organizer

A professional desktop application for **smart, safe, and organized file management**.

Built with a modern web-based UI and a Python backend, Advanced File Organizer helps users analyze and organize files on their local computer.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥️ Modern GUI | Clean dark-themed interface |
| 📂 Folder Browser | Select a local folder using the native Windows folder picker |
| 🔍 Analyze Mode | Scan a folder without moving files |
| 👁️ Preview Mode | Preview files before organizing |
| ⚡ Smart Organizer | Automatically categorize files |
| ↩️ Undo | Restore files after organizing |
| 📊 Statistics | View file counts and organization statistics |
| 🔎 Search & Filters | Search and filter analyzed files |
| 📡 Watch Mode | Monitor folders for changes |
| 🧩 Duplicate Detection | Detect duplicate files |
| 📁 Recursive Scanning | Optionally scan subfolders |
| ⚙️ Custom Rules | Configure categories and organization rules |
| 📝 Activity Log | Keep track of file operations |

---

## 📂 Supported Categories

The organizer can classify files into categories such as:

- 🖼️ Images
- 📄 PDFs
- 📝 Documents
- 🎬 Videos
- 🎵 Music
- 📦 Archives
- 💻 Programs
- 👨‍💻 Code
- 📁 Others

---

## 🏗️ Architecture

Advanced File Organizer uses a local desktop architecture:

```text
┌──────────────────────────────┐
│       Modern Web UI          │
│        React + Vite          │
└──────────────┬───────────────┘
               │
               │ Local communication
               ▼
┌──────────────────────────────┐
│       Python Backend         │
│      File Management         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Local File System       │
│  Windows folders and files   │
└──────────────────────────────┘

Author:
"Abhijeet Pirankar"
