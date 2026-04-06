import os
import shutil

print("=== File Organizer ===")

path = input("Enter folder path: ").strip()

if not os.path.exists(path):
    print("❌ Invalid path")
    exit()

# File type categories
file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "PDFs": [".pdf"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Docs": [".docx", ".txt", ".pptx"],
    "Music": [".mp3", ".wav"]
}

# Create folders
for folder in file_types:
    os.makedirs(os.path.join(path, folder), exist_ok=True)

# Organize files
for file in os.listdir(path):
    file_path = os.path.join(path, file)

    # Skip folders
    if os.path.isdir(file_path):
        continue

    moved = False

    for folder, extensions in file_types.items():
        if any(file.lower().endswith(ext) for ext in extensions):
            shutil.move(file_path, os.path.join(path, folder, file))
            moved = True
            break

    if not moved:
        os.makedirs(os.path.join(path, "Others"), exist_ok=True)
        shutil.move(file_path, os.path.join(path, "Others", file))

print("✅ Files organized successfully!")