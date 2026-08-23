import sys
import subprocess
import tempfile
import os

def main():
    # VBScript is the most bulletproof way to guarantee a native Windows
    # folder picker appears in the foreground without any tkinter thread/focus bugs.
    vbs_code = """
Dim objShell, objFolder
Set objShell = CreateObject("Shell.Application")
' &H200 = BIF_NEWDIALOGSTYLE (shows modern folder picker)
' &H40 = BIF_USENEWUI
Set objFolder = objShell.BrowseForFolder(0, "Select Folder to Organize", &H200 + &H40, 0)
If Not objFolder Is Nothing Then
    Wscript.Echo objFolder.Self.Path
End If
"""
    fd, path = tempfile.mkstemp(suffix=".vbs")
    os.close(fd)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(vbs_code)
        
    try:
        # Run cscript natively. It will pop a standard Windows dialog.
        result = subprocess.run(["cscript.exe", "//Nologo", path], capture_output=True, text=True)
        folder = result.stdout.strip()
        print(folder, end="")
    finally:
        os.remove(path)

if __name__ == "__main__":
    main()
