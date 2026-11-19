import os

from groq import Groq

from tutor.config import require_groq_settings
from tutor.retrieval import retrieve


def answer_question(question: str, profile: dict) -> dict:
    """Answer one doubt from the retrieved notes."""
    require_groq_settings()
    documents, sources = retrieve(question, profile["current_topic"])
    context = "\n\n".join(documents)
    completion = Groq().chat.completions.create(
        model=os.environ["GROQ_MODEL"],
        messages=[
            {"role": "system", "content": _instructions(profile)},
            {"role": "user", "content": f"Notes:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return {
        "answer": completion.choices[0].message.content or "",
        "sources": sources,
    }


def _instructions(profile: dict) -> str:
    level = profile["learning_level"]
    if level == "Intermediate":
        level_instruction = (
            "Give a clear explanation and include the extra details that are in the notes."
        )
    elif level == "Advanced":
        level_instruction = (
            "Give a deeper explanation and use the technical terms from the notes."
        )
    else:
        level_instruction = "Use simple language and a basic example from the notes."
    if profile["answer_style"] == "Exam-focused":
        style_instruction = (
            "Write an exam-focused answer: give the definition and the points "
            "a student would write in an exam."
        )
    else:
        style_instruction = "Use plain wording for a simple explanation."
    return (
        "You are a Life Processes tutor. "
        f"The student level is {level}. {level_instruction} {style_instruction} "
        "Answer using the retrieved notes only. "
        "Cite the note title and section number for the material you use. "
        "If the notes do not contain the answer, say so clearly and do not guess. "
        "If the question is graded homework, give hints and step-by-step guidance. "
        "Do not write the finished assignment."
    )
