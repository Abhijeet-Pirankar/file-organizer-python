"""
categories.py
-------------
Defines the default file-extension → category mapping for File Organizer v2.0.
Custom overrides stored by config_manager are merged in at runtime so users
can add or remove extensions without touching source code.

The organizer-owned folder names are also defined here so other modules can
avoid re-scanning them.
"""

from typing import Dict, List
import config_manager


# ── Built-in category definitions ─────────────────────────────────────────────

DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Images":   [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff",
                 ".svg", ".ico", ".heic", ".raw"],
    "PDFs":     [".pdf"],
    "Videos":   [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                 ".m4v", ".3gp"],
    "Docs":     [".docx", ".doc", ".txt", ".pptx", ".ppt", ".xlsx", ".xls",
                 ".odt", ".ods", ".odp", ".rtf", ".csv", ".md"],
    "Music":    [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Programs": [".exe", ".msi", ".dmg", ".apk", ".deb", ".rpm"],
    "Code":     [".py", ".html", ".css", ".js", ".ts", ".java", ".cpp", ".c",
                 ".h", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt",
                 ".json", ".xml", ".yaml", ".yml", ".toml", ".sh", ".bat",
                 ".ps1", ".sql"],
}

# Folders the organizer itself creates — skip these during scanning
ORGANIZER_FOLDERS: List[str] = list(DEFAULT_CATEGORIES.keys()) + ["Others"]


# ── Public API ────────────────────────────────────────────────────────────────

def get_categories() -> Dict[str, List[str]]:
    """
    Returns the effective category map: defaults merged with any user-defined
    custom_categories from settings.
    Custom entries can add new categories or extend existing ones.
    """
    categories = {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}  # deep copy

    custom: Dict[str, List[str]] = config_manager.get("custom_categories", {})

    for cat_name, extensions in custom.items():
        if cat_name in categories:
            # Merge extensions (no duplicates)
            existing = set(categories[cat_name])
            for ext in extensions:
                ext = ext.lower().strip()
                if ext and not ext.startswith("."):
                    ext = "." + ext
                existing.add(ext)
            categories[cat_name] = sorted(existing)
        else:
            # Brand-new user category
            categories[cat_name] = [
                (e if e.startswith(".") else "." + e).lower().strip()
                for e in extensions if e.strip()
            ]

    return categories


def get_category_for_extension(ext: str,
                                categories: Dict[str, List[str]] | None = None
                                ) -> str:
    """
    Return the category name for a given file extension (e.g. '.jpg' → 'Images').
    Returns 'Others' if no match is found.
    """
    if categories is None:
        categories = get_categories()

    ext = ext.lower()
    for category, extensions in categories.items():
        if ext in extensions:
            return category
    return "Others"


def evaluate_rules(filename: str, ext: str) -> str | None:
    """
    Check if the file matches any custom rules.
    Rules format: {"extension": ".pdf", "contains": "college", "category": "College Documents"}
    """
    rules = config_manager.get("organization_rules", [])
    if not rules:
        return None

    fname_lower = filename.lower()
    ext_lower = ext.lower()

    for rule in rules:
        rule_ext = rule.get("extension", "").strip().lower()
        if rule_ext and not rule_ext.startswith("."):
            rule_ext = "." + rule_ext
        
        rule_contains = rule.get("contains", "").strip().lower()
        
        # Match logic
        ext_matches = (not rule_ext) or (rule_ext == ext_lower)
        contains_matches = (not rule_contains) or (rule_contains in fname_lower)
        
        if ext_matches and contains_matches:
            # If a rule has at least one condition and both passed
            if rule_ext or rule_contains:
                cat = rule.get("category", "").strip()
                if cat:
                    return cat

    return None


def get_category_for_file(filename: str, ext: str,
                           categories_map: Dict[str, List[str]] | None = None) -> str:
    """
    Evaluates rules first, then falls back to default extension mapping.
    """
    rule_category = evaluate_rules(filename, ext)
    if rule_category:
        return rule_category

    return get_category_for_extension(ext, categories_map)


def save_custom_categories(custom: Dict[str, List[str]]) -> None:
    """Persist a user-edited custom_categories dict to settings."""
    config_manager.set_value("custom_categories", custom)
