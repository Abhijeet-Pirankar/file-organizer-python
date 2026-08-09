"""
duplicate_detector.py
---------------------
Detects duplicate files for File Organizer v2.0.

Supports two detection modes:
  1. Name conflict   — a file with the same name already exists at the destination
  2. Content duplicate — same SHA-256 hash (truly identical file content)

Also provides get_unique_filename() which is the upgraded version of the
original v1 function with the same purpose.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class DuplicateInfo:
    """Result returned by check_duplicate()."""
    name_conflict: bool        # A file with the same name exists at destination
    content_duplicate: bool    # File contents are identical (SHA-256 match)
    existing_path: Optional[Path] = None  # Path to the conflicting file


# ── Core functions ────────────────────────────────────────────────────────────

def compute_sha256(path: Path, chunk_size: int = 65536) -> Optional[str]:
    """
    Compute the SHA-256 hash of a file in streaming chunks.
    Returns None if the file cannot be read (permission error, locked, etc.).
    """
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def check_duplicate(source: Path, destination: Path) -> DuplicateInfo:
    """
    Check whether moving `source` to `destination` would cause a duplicate.

    Returns a DuplicateInfo describing:
      - Whether the destination filename already exists
      - Whether the file contents are identical (only checked on name conflict)
    """
    if not destination.exists():
        return DuplicateInfo(name_conflict=False, content_duplicate=False)

    # Name conflict confirmed
    src_hash = compute_sha256(source)
    dest_hash = compute_sha256(destination)

    content_dup = (
        src_hash is not None
        and dest_hash is not None
        and src_hash == dest_hash
    )

    return DuplicateInfo(
        name_conflict=True,
        content_duplicate=content_dup,
        existing_path=destination,
    )


def get_unique_filename(destination: Path) -> Path:
    """
    Return a non-conflicting path by appending _1, _2, … to the stem.
    Upgraded version of the original v1 get_unique_filename() function.

    Example:
        photo.jpg  →  photo_1.jpg  →  photo_2.jpg  ...
    """
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
