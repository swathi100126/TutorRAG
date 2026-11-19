import os


class MissingApiKey(RuntimeError):
    """Raised when GROQ_API_KEY or GROQ_MODEL is not set."""


class NotesError(RuntimeError):
    """Raised when the class notes cannot be read."""


class QuestionBankError(RuntimeError):
    """Raised when the practice question file cannot be read."""


def public_error(exc: Exception) -> str:
    """Return an error message that does not include the API key."""
    message = str(exc)
    key = os.environ.get("GROQ_API_KEY", "")
    if key and key in message:
        message = message.replace(key, "[key]")
    return message
