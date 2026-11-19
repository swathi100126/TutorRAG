import re
from pathlib import Path

from tutor.documents import note_paths, read_note
from tutor.errors import NotesError


def load_chunks() -> list[dict]:
    """Split every class note into one chunk per section."""
    chunks = []
    for path in note_paths():
        chunks.extend(chunks_from_note(path))
    if not chunks:
        raise NotesError("No Markdown notes were found in knowledge_base.")
    return chunks


def chunks_from_note(path: Path) -> list[dict]:
    """Split one note on its ## headings and keep the title and section number."""
    text = read_note(path)
    title = _field(text, "Title")
    topic = _field(text, "Topic Tag")
    section_number = _field(text, "Section Number")
    if not title:
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    title = title or path.stem
    chunks = []
    for index, part in enumerate(re.split(r"(?m)^## ", text)[1:]):
        lines = part.splitlines()
        section = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        chunks.append(
            {
                "id": f"{path.name}:{index}:{section}",
                "text": (
                    f"Title: {title}\n"
                    f"Section number: {section_number}\n"
                    f"Topic: {topic}\n"
                    f"Section: {section}\n\n"
                    f"{body}"
                ),
                "title": title,
                "topic": topic,
                "section": section,
                "section_number": section_number,
                "source": path.name,
            }
        )
    return chunks


def _field(text: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(label)}:\s*(.+)$", text)
    return match.group(1).strip() if match else ""
