import streamlit as st

from tutor.errors import MissingApiKey, QuestionBankError, public_error
from tutor.llm import answer_question
from tutor.questions import DIFFICULTIES, questions_for_difficulty

st.set_page_config(page_title="Life Processes tutor", layout="centered")

st.title("Life Processes tutor")
st.markdown(
    "Ask a doubt from the class notes, or practise questions "
    "on nutrition, respiration, transportation, and excretion."
)

st.session_state.setdefault("profile", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("practice_index", 0)
st.session_state.setdefault("show_practice_answer", False)

with st.form("student_details"):
    nickname = st.text_input("Nickname")
    level = st.segmented_control(
        "Learning level",
        ["Beginner", "Intermediate", "Advanced"],
        default="Beginner",
        required=True,
        width="stretch",
    )
    subject = st.text_input("Subject", value="Life Processes")
    topic = st.text_input("Current topic")
    style = st.segmented_control(
        "Preferred answer style",
        ["Simple explanation", "Exam-focused"],
        default="Simple explanation",
        required=True,
        width="stretch",
    )
    submitted = st.form_submit_button("Save details", width="stretch")

if submitted:
    missing = [
        label
        for label, value in (
            ("nickname", nickname),
            ("subject", subject),
            ("current topic", topic),
        )
        if not value.strip()
    ]
    if missing:
        st.warning(
            "Enter " + ", ".join(missing) + " before saving.",
            title="Missing details",
        )
    else:
        st.session_state.profile = {
            "nickname": nickname.strip(),
            "learning_level": level,
            "subject": subject.strip(),
            "current_topic": topic.strip(),
            "answer_style": style,
        }

profile = st.session_state.profile
if not profile:
    st.info("Save your details to ask a doubt or start practice.", title="Profile")
    st.stop()

st.success("Details saved.", title="Saved")
st.markdown(
    f"**Nickname:** {profile['nickname']}  \n"
    f"**Learning level:** {profile['learning_level']}  \n"
    f"**Subject:** {profile['subject']}  \n"
    f"**Current topic:** {profile['current_topic']}  \n"
    f"**Preferred answer style:** {profile['answer_style']}"
)

section = st.segmented_control(
    "Section",
    ["Ask a doubt", "Practice"],
    default="Ask a doubt",
    required=True,
    width="stretch",
)

if section == "Practice":
    difficulty = st.segmented_control(
        "Difficulty",
        DIFFICULTIES,
        default="Easy",
        required=True,
        key="practice_difficulty",
        width="stretch",
    )
    if st.session_state.get("practice_difficulty_seen") != difficulty:
        st.session_state.practice_index = 0
        st.session_state.show_practice_answer = False
        st.session_state.practice_difficulty_seen = difficulty

    try:
        questions = questions_for_difficulty(difficulty)
    except QuestionBankError as exc:
        st.error(str(exc), title="Question bank")
        st.stop()

    if not questions:
        st.info(f"No {difficulty.lower()} questions are in the bank.", title="Practice")
        st.stop()

    index = st.session_state.practice_index % len(questions)
    item = questions[index]
    st.subheader(item["question"])
    st.caption(f"{item['difficulty']} · question {index + 1} of {len(questions)}")
    st.text_area(
        "Your attempt",
        key=f"attempt_{difficulty}_{index}",
        placeholder="Write your answer here, then reveal the bank answer.",
    )
    show_col, next_col = st.columns(2, vertical_alignment="bottom")
    with show_col:
        if st.button("Show answer", width="stretch"):
            st.session_state.show_practice_answer = True
    with next_col:
        if st.button("Next question", width="stretch"):
            st.session_state.practice_index = index + 1
            st.session_state.show_practice_answer = False
            st.rerun()
    if st.session_state.show_practice_answer:
        st.success(item["answer"], title="Answer from the question bank")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Notes used: " + ", ".join(message["sources"]))

    prompt = st.chat_input("Ask a doubt from the notes", submit_mode="disable")
    if prompt and prompt.strip():
        question = prompt.strip()
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Looking through the notes..."):
            try:
                result = answer_question(question, profile)
            except MissingApiKey as exc:
                st.session_state.messages.append(
                    {"role": "assistant", "content": str(exc)}
                )
            except Exception as exc:
                st.session_state.messages.append(
                    {"role": "assistant", "content": public_error(exc)}
                )
            else:
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    }
                )
        st.rerun()
