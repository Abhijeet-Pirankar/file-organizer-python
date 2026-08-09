import os
import shutil
from datetime import datetime


def get_unique_filename(destination):
    if not os.path.exists(destination):
        return destination

    base, extension = os.path.splitext(destination)
    counter = 1

    while os.path.exists(destination):
        destination = f"{base}_{counter}{extension}"
        counter += 1

    return destination


print("=== Advanced File Organizer ===")

path = input("Enter folder path: ").strip()

if not os.path.exists(path):
    print("❌ Invalid path")
    exit()

# File type categories
file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "PDFs": [".pdf"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Docs": [".docx", ".txt", ".pptx", ".xlsx"],
    "Music": [".mp3", ".wav"],
    "Archives": [".zip", ".rar", ".7z"],
    "Programs": [".exe", ".msi"],
    "Code": [".py", ".html", ".css", ".js", ".java", ".cpp"]
}

# Create folders
for folder in file_types:
    os.makedirs(os.path.join(path, folder), exist_ok=True)

# Statistics
stats = {
    "Images": 0,
    "PDFs": 0,
    "Videos": 0,
    "Docs": 0,
    "Music": 0,
    "Archives": 0,
    "Programs": 0,
    "Code": 0,
    "Others": 0
}

total_moved = 0

# Log file
log_file = open("log.txt", "a", encoding="utf-8")
log_file.write(
    f"\n\n===== Run Started: {datetime.now()} =====\n"
)

# Organize files
for file in os.listdir(path):
    file_path = os.path.join(path, file)

    if os.path.isdir(file_path):
        continue

    moved = False

    for folder, extensions in file_types.items():

        if any(file.lower().endswith(ext) for ext in extensions):

            try:
                destination = os.path.join(path, folder, file)
                destination = get_unique_filename(destination)

                print(f"Moving {file} → {folder}")

                shutil.move(file_path, destination)

                log_file.write(
                    f"Moved {file} -> {folder}\n"
                )

                stats[folder] += 1
                total_moved += 1

                moved = True
                break

            except Exception as e:
                print(f"Error moving {file}: {e}")
                log_file.write(
                    f"ERROR: {file} -> {e}\n"
                )

    if not moved:
        try:
            os.makedirs(
                os.path.join(path, "Others"),
                exist_ok=True
            )

            destination = os.path.join(
                path,
                "Others",
                file
            )

            destination = get_unique_filename(destination)

            print(f"Moving {file} → Others")

            shutil.move(file_path, destination)

            log_file.write(
                f"Moved {file} -> Others\n"
            )

            stats["Others"] += 1
            total_moved += 1

        except Exception as e:
            print(f"Error moving {file}: {e}")
            log_file.write(
                f"ERROR: {file} -> {e}\n"
            )

# Create report
report_path = os.path.join(path, "report.txt")

with open(report_path, "w", encoding="utf-8") as report:
    report.write("FILE ORGANIZER REPORT\n")
    report.write("=" * 30 + "\n\n")

    report.write(f"Total files moved: {total_moved}\n\n")

    for category, count in stats.items():
        report.write(f"{category}: {count}\n")

log_file.write(
    f"Total files moved: {total_moved}\n"
)
log_file.write(
    f"===== Run Finished =====\n"
)

log_file.close()

# Final Summary
print("\n✅ Files organized successfully!")
print(f"Total files moved: {total_moved}")

for category, count in stats.items():
    print(f"{category}: {count}")

print("\n📄 Report saved as report.txt")
print("📝 Activity saved in log.txt")

input("\nPress Enter to exit...")