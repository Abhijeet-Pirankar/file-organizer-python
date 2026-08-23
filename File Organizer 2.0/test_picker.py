import tkinter as tk
from tkinter import filedialog
import ctypes

def main():
    root = tk.Tk()
    root.attributes("-alpha", 0.0) # transparent
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    
    # Wait until the window is actually drawn before grabbing hwnd
    root.update()
    
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Error: {e}")
        
    path = filedialog.askdirectory(parent=root, title="Select Folder to Organize")
    root.destroy()
    print(path, end="")

if __name__ == "__main__":
    main()
