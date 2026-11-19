import hashlib
from pathlib import Path

from tutor.config import NOTES_DIR, STORE_VERSION
from tutor.errors import NotesError


def note_paths() -> list[Path]:
    """Return the Markdown class notes in filename order."""
    return sorted(NOTES_DIR.glob("note*.md"))


def read_note(path: Path) -> str:
    """Read one note as text."""
    return path.read_text(encoding="utf-8")


def notes_fingerprint() -> str:
    """Change when a note file changes, so the vector store can be rebuilt."""
    hasher = hashlib.sha256()
    hasher.update(STORE_VERSION.encode())
    paths = note_paths()
    if not paths:
        raise NotesError("No Markdown notes were found in knowledge_base.")
    for path in paths:
        hasher.update(path.name.encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()
