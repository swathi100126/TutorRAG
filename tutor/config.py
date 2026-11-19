import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "knowledge_base"
STORE_DIR = ROOT / "vector_store"
QUESTION_BANK = NOTES_DIR / "question.bank.csv"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "life_processes"
STORE_VERSION = "section-number-1"
TOP_K = 4

load_dotenv(ROOT / ".venv" / ".env")
load_dotenv(ROOT / ".env")


def require_groq_settings() -> None:
    """Stop before calling Groq when the key or model name is missing."""
    from tutor.errors import MissingApiKey

    if not os.environ.get("GROQ_API_KEY"):
        raise MissingApiKey("Add GROQ_API_KEY to .venv/.env.")
    if not os.environ.get("GROQ_MODEL"):
        raise MissingApiKey("Add GROQ_MODEL to .venv/.env.")
