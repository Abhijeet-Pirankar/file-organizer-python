import ctypes
import ctypes.wintypes as wintypes
import sys

def get_folder_dialog():
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    
    # Force focus by attaching to foreground window
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    if hwnd:
        # We can't easily parent a tkinter window to an arbitrary HWND without complex win32 calls,
        # but we can force our hidden root window to the foreground.
        pass

    root.attributes("-topmost", True)
    root.focus_force()
    root.lift()

    path = filedialog.askdirectory()
    root.destroy()
    print(path, end='')

get_folder_dialog()
