"""
config_manager.py
-----------------
Manages persistent user settings for File Organizer v2.0.
Settings are stored in ~/.file_organizer/settings.json so they survive
application restarts and reinstalls.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


# ── Default settings ──────────────────────────────────────────────────────────

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "dark",                  # "dark" | "light"
    "include_subfolders": False,       # recursive scan toggle
    "watch_folder": False,             # auto-monitor toggle
    "last_folder": "",                 # remember last used folder
    "custom_categories": {},           # user-added extension overrides
    "confirm_organize": True,          # confirm before organizing
    "show_notifications": True,        # show notifications
    "duplicate_action": "keep_both",   # "skip" | "keep_both" | "ask"
    "watch_folder_path": "",           # saved watch folder path
    "watch_auto_organize": True,       # auto organize new files in watch mode
    "watch_notifications": True,       # notifications in watch mode
    "organization_rules": []           # custom rules list
}

# Config directory lives in the user's home folder
CONFIG_DIR = Path.home() / ".file_organizer"
SETTINGS_FILE = CONFIG_DIR / "settings.json"


# ── Public API ────────────────────────────────────────────────────────────────

def load_settings() -> Dict[str, Any]:
    """
    Load settings from disk. Returns defaults if the file is missing or corrupt.
    Always merges with defaults so new keys are available after upgrades.
    """
    settings = dict(DEFAULT_SETTINGS)  # start with a fresh copy of defaults

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge: saved values override defaults; new default keys are added
            settings.update(saved)
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file — silently fall back to defaults
            pass

    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    """
    Persist settings to disk. Creates the config directory if needed.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except OSError as e:
        # Non-fatal — app still works; settings just won't persist
        print(f"[ConfigManager] Could not save settings: {e}")


def get(key: str, default: Any = None) -> Any:
    """Convenience: load settings and return a single key."""
    return load_settings().get(key, default)


def set_value(key: str, value: Any) -> None:
    """Convenience: load, update one key, save."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
