"""
main_web.py
-----------
Entry point for File Organizer v2.0 using the new Web/Glassmorphism Frontend.
Uses pywebview to bridge the local HTML/CSS/JS with the Python backend.
"""

import sys
import os
import webview

# Ensure the app's own directory is on sys.path
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from web_api import Api

def main() -> None:
    api = Api()
    
    # Path to the frontend index.html
    html_path = os.path.join(_BASE_DIR, 'frontend', 'index.html')
    
    # Create the webview window
    window = webview.create_window(
        'Advanced File Organizer v2.0',
        url=html_path,
        js_api=api,
        width=1100,
        height=760,
        min_size=(900, 640),
        background_color='#03050c'
    )
    
    # Give the API access to the window object so it can trigger JS callbacks
    api.set_window(window)
    
    # Start the desktop application
    webview.start(debug=False)

if __name__ == '__main__':
    main()
