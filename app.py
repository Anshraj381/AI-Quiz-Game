import json
import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="AI Quest | DSC401-6",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
QUESTION_FILE = BASE_DIR / "questions.json"

@st.cache_data
def load_questions():
    with QUESTION_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if len(data) < 50:
        raise ValueError(f"Question bank has {len(data)} questions; at least 50 are required.")
    return data

def start_quiz(all_questions, count, difficulty, shuffle):
    pool = all_questions[:]
    if difficulty != "All":
        pool = [q for q in pool if q["difficulty"] == difficulty]
    if shuffle:
        random.shuffle(pool)
    chosen = pool[:min(count, len(pool))]
    st.session_state.quiz_questions = chosen
    st.session_state.answers = {}
    st.session_state.feedback = {}
    st.session_state.current = 0
    st.session_state.started_at = time.time()
    st.session_state.finished = False
    st.session_state.started = True

def normalize(text):
    return " ".join(str(text).strip().lower().replace("-", " ").split())

def is_correct(question, response):
    if response is None:
        return False
    if question["type"] == "fill":
        accepted = question.get("accepted", [question["answer"]])
        return normalize(response) in [normalize(x) for x in accepted]
    return response == question["answer"]

def score_quiz():
    qs = st.session_state.quiz_questions
    answers = st.session_state.answers
    return sum(1 for q in qs if is_correct(q, answers.get(q["id"]))), len(qs)

def reset_quiz():
    for key in ["quiz_questions", "answers", "feedback", "current", "started_at", "finished", "started"]:
        st.session_state.pop(key, None)

st.markdown("""
<style>
    .main-title {font-size: 2.25rem; font-weight: 800; letter-spacing: -0.04em;}
    .subtle {color: #7b8494;}
    div.stButton > button {border-radius: 10px; min-height: 2.7rem; font-weight: 600;}
    div[data-testid="stProgressBar"] > div > div {border-radius: 8px;}
    .question-box {padding: 1rem 1.1rem; border: 1px solid rgba(128,128,128,.28); border-radius: 14px; margin: .4rem 0 1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 AI Quest</div>', unsafe_allow_html=True)
st.caption("DSC401-6 · Artificial Intelligence · Units I & II")
st.write("An interactive quiz covering AI foundations, intelligent agents, environments, search algorithms, CSPs, and problem-solving.")

try:
    all_questions = load_questions()
except Exception as exc:
    st.error(f"Could not load questions.json: {exc}")
    st.info("Keep app.py and questions.json in the same folder.")
    st.stop()

with st.sidebar:
    st.header("Quiz settings")
    st.write(f"**Question bank:** {len(all_questions)} questions")
    quiz_length = st.selectbox("Questions per attempt", [10, 20, 30, 50], index=3)
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium"], index=0)
    shuffle_questions = st.checkbox("Shuffle questions", value=True)
    st.divider()
    st.caption("Scoring: each question is worth the same number of points. Your result is converted to a percentage and a mark out of 25.")
    st.caption("Tip: answer from understanding, then read the explanation after submitting.")

if not st.session_state.get("started", False):
    st.markdown("### Welcome, learner!")
    col1, col2, col3 = st.columns(3)
    col1.metric("Question bank", len(all_questions))
    col2.metric("Topics", len(set(q["topic"] for q in all_questions)))
    col3.metric("Maximum marks", "25")
    st.markdown("""
    **How to play**
    1. Choose the number of questions and difficulty in the sidebar.
    2. Answer each question and submit your response.
    3. Read the explanation and continue.
    4. Review your final result and incorrect answers.

    This game is designed for practice and classroom demonstration.
    """)
    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        start_quiz(all_questions, quiz_length, difficulty, shuffle_questions)
        st.rerun()
    st.stop()

questions = st.session_state.quiz_questions

if st.session_state.get("finished", False):
    correct, total = score_quiz()
    pct = (correct / total * 100) if total else 0
    marks = (correct / total * 25) if total else 0
    elapsed = int(time.time() - st.session_state.started_at)
    st.success("Quiz completed!")
    st.markdown("## Your results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Correct", f"{correct}/{total}")
    c2.metric("Percentage", f"{pct:.1f}%")
    c3.metric("Marks out of 25", f"{marks:.2f}/25")
    st.progress(correct / total if total else 0)
    st.caption(f"Time taken: {elapsed // 60} min {elapsed % 60} sec")
    if pct >= 80:
        st.balloons()
        st.write("Excellent work. Review the explanations to strengthen your understanding.")
    elif pct >= 60:
        st.write("Good attempt. Review missed concepts and try again.")
    else:
        st.write("Use the answer review below, then retry the quiz to improve your score.")

    st.markdown("### Answer review")
    for idx, q in enumerate(questions, start=1):
        response = st.session_state.answers.get(q["id"])
        correct_answer = is_correct(q, response)
        label = "✅" if correct_answer else "❌"
        with st.expander(f"{label} Q{idx}. {q['question']}"):
            st.write(f"**Your answer:** {response if response not in (None, '') else 'Not answered'}")
            st.write(f"**Correct answer:** {q['answer']}")
            st.write(f"**Topic:** {q['topic']} · **Difficulty:** {q['difficulty']}")
            st.write(f"**Explanation:** {q['explanation']}")
    if st.button("🔁 Start a new quiz", type="primary", use_container_width=True):
        reset_quiz()
        st.rerun()
    st.stop()

current = st.session_state.current
q = questions[current]
total = len(questions)
answered_count = len(st.session_state.answers)

st.progress((current + 1) / total, text=f"Question {current + 1} of {total}")
top1, top2 = st.columns([2, 1])
top1.caption(f"Topic: {q['topic']}")
top2.caption(f"Difficulty: {q['difficulty']} · {q['type'].replace('_', ' ').title()}")

st.markdown(f'<div class="question-box"><strong>Q{current + 1}.</strong> {q["question"]}</div>', unsafe_allow_html=True)

existing = st.session_state.answers.get(q["id"])
widget_key = f"answer_{q['id']}"

if q["type"] == "fill":
    response = st.text_input("Type your answer", value=str(existing or ""), key=widget_key, placeholder="Enter your answer...")
else:
    options = q.get("options", [])
    default_index = options.index(existing) if existing in options else None
    response = st.radio(
        "Choose your answer",
        options,
        index=default_index,
        key=widget_key,
        label_visibility="collapsed",
    )

feedback_already_shown = q["id"] in st.session_state.feedback
left, right = st.columns([1, 1])
with left:
    if st.button("Submit answer", type="primary", use_container_width=True, disabled=not str(response or "").strip()):
        st.session_state.answers[q["id"]] = response
        st.session_state.feedback[q["id"]] = is_correct(q, response)
        st.rerun()
with right:
    if st.button("Skip question", use_container_width=True):
        st.session_state.answers.setdefault(q["id"], None)
        st.session_state.feedback[q["id"]] = False
        if current < total - 1:
            st.session_state.current += 1
        else:
            st.session_state.finished = True
        st.rerun()

if feedback_already_shown:
    was_correct = st.session_state.feedback[q["id"]]
    if was_correct:
        st.success("Correct! " + q["explanation"])
    else:
        st.error(f"Not quite. Correct answer: {q['answer']}")
        st.info(q["explanation"])

    nav1, nav2, nav3 = st.columns([1, 1, 1])
    with nav1:
        if st.button("⬅ Previous", disabled=current == 0, use_container_width=True):
            st.session_state.current -= 1
            st.rerun()
    with nav2:
        if current < total - 1:
            if st.button("Next ➜", type="primary", use_container_width=True):
                st.session_state.current += 1
                st.rerun()
        else:
            if st.button("View results", type="primary", use_container_width=True):
                st.session_state.finished = True
                st.rerun()
    with nav3:
        if st.button("Finish now", use_container_width=True):
            st.session_state.finished = True
            st.rerun()
elif existing is not None:
    st.caption("Your answer is saved. Submit it to see feedback.")

st.divider()
st.caption(f"Answered: {sum(1 for qq in questions if qq['id'] in st.session_state.feedback)} / {total} · Correct answers are revealed after submission.")
