import csv

from tutor.config import QUESTION_BANK
from tutor.errors import QuestionBankError

DIFFICULTIES = ["Easy", "Medium", "Hard"]


def load_questions() -> list[dict]:
    """Read every practice question from the CSV file."""
    if not QUESTION_BANK.exists():
        raise QuestionBankError("Add knowledge_base/question.bank.csv.")
    try:
        text = QUESTION_BANK.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise QuestionBankError("The question bank could not be read.") from exc
    lines = [line for line in text.splitlines() if line.strip()]
    rows = list(csv.DictReader(lines))
    if rows and "question" not in rows[0]:
        raise QuestionBankError(
            "The question bank needs question, topic, difficulty, and answer columns."
        )
    questions = []
    for row in rows:
        question = (row.get("question") or "").strip()
        answer = (row.get("answer") or "").strip()
        difficulty = (row.get("difficulty") or "").strip()
        if not question or not answer or difficulty not in DIFFICULTIES:
            continue
        questions.append(
            {
                "question": question,
                "topic": (row.get("topic") or "").strip(),
                "difficulty": difficulty,
                "answer": answer,
            }
        )
    if not questions:
        raise QuestionBankError("The question bank has no usable questions.")
    return questions


def questions_for_difficulty(difficulty: str) -> list[dict]:
    """Return the practice questions for Easy, Medium, or Hard."""
    return [
        item for item in load_questions() if item["difficulty"] == difficulty
    ]
