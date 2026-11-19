import csv
import uuid
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# ---------------- CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "data" / "feedback.csv"

st.set_page_config(
    page_title="UGCRuleBook",
    page_icon="📘",
    layout="wide"
)

API_URL = st.sidebar.text_input(
    "Backend API URL",
    value="http://127.0.0.1:8000"
).rstrip("/")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback_saved" not in st.session_state:
    st.session_state.feedback_saved = set()


# ---------------- FEEDBACK ----------------

def save_feedback(question, answer, rating):

    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "question",
                "answer",
                "feedback"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            question,
            answer,
            rating
        ])


# ---------------- HEADER ----------------

st.title("📘 UGCRuleBook")
st.caption(
    "Your student-rights assistant powered by "
    "Retrieval-Augmented Generation and LangGraph."
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a feature",
    ["Student Chat", "Complaint Path"]
)

mode = st.sidebar.radio(
    "Assistant mode",
    ["RAG (/ask)", "AI Agent (/agent)"]
)

if st.sidebar.button("New conversation"):
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.feedback_saved = set()
    st.rerun()


# ---------------- STUDENT CHAT ----------------

if page == "Student Chat":

    st.subheader("Ask a student-rights question")

    st.write(
        "Ask about fee refunds, ragging, certificates, "
        "harassment, examinations, or student grievances."
    )

    # Display previous conversation
    for index, message in enumerate(st.session_state.messages):

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["role"] == "assistant":

                citations = message.get("citations", [])

                if citations:
                    with st.expander("View source citations"):
                        for citation in citations:
                            st.write(
                                f"- {citation['source']} "
                                f"(Page {citation['page']})"
                            )

                question = message.get("question", "")
                answer = message["content"]

                feedback_key = f"{index}"

                if feedback_key not in st.session_state.feedback_saved:

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "👍 Helpful",
                            key=f"up_{index}"
                        ):
                            save_feedback(
                                question, answer, "positive"
                            )
                            st.session_state.feedback_saved.add(
                                feedback_key
                            )
                            st.success("Feedback saved!")
                            st.rerun()

                    with col2:
                        if st.button(
                            "👎 Not helpful",
                            key=f"down_{index}"
                        ):
                            save_feedback(
                                question, answer, "negative"
                            )
                            st.session_state.feedback_saved.add(
                                feedback_key
                            )
                            st.success("Feedback saved!")
                            st.rerun()

                else:
                    st.caption("Feedback recorded.")

    question = st.chat_input("Enter your student-rights question...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            try:

                with st.spinner("Searching UGC regulations..."):

                    if mode == "RAG (/ask)":

                        response = requests.post(
                            f"{API_URL}/ask",
                            json={"question": question},
                            timeout=180
                        )

                        response.raise_for_status()
                        data = response.json()

                        answer = data.get(
                            "answer", "No answer returned."
                        )

                        citations = data.get("citations", [])

                    else:

                        response = requests.post(
                            f"{API_URL}/agent",
                            json={
                                "question": question,
                                "thread_id": st.session_state.thread_id
                            },
                            timeout=180
                        )

                        response.raise_for_status()
                        data = response.json()

                        result = data.get("result")

                        if isinstance(result, dict):
                            answer = result.get(
                                "answer", str(result)
                            )
                            citations = result.get("citations", [])
                        else:
                            answer = str(result or data)
                            citations = []

                st.markdown(answer)

                if citations:
                    with st.expander("View source citations"):
                        for citation in citations:
                            st.write(
                                f"- {citation['source']} "
                                f"(Page {citation['page']})"
                            )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "question": question
                })

                st.rerun()

            except requests.RequestException as error:

                st.error(
                    "Could not connect to the backend. "
                    "Check that FastAPI is running."
                )
                st.caption(str(error))


# ---------------- COMPLAINT PATH ----------------

elif page == "Complaint Path":

    st.subheader("🧭 Student Complaint Escalation Path")

    st.write(
        "Follow the escalation route for your student-rights problem."
    )

    problem = st.selectbox(
        "Select your complaint type",
        [
            "Fee Refund",
            "Ragging",
            "Harassment",
            "Marks / Examination"
        ]
    )

    complaint_details = {

        "Fee Refund": (
            "Delay or denial of fee refund after withdrawal "
            "of admission."
        ),

        "Ragging": (
            "Bullying, physical or psychological harm, "
            "or other acts covered by UGC anti-ragging regulations."
        ),

        "Harassment": (
            "Harassment or discrimination affecting a student's rights. "
            "Use the appropriate institutional committee for the nature "
            "of the complaint."
        ),

        "Marks / Examination": (
            "Examination or evaluation grievances. "
            "Revaluation and re-totalling are subject to applicable rules."
        )
    }

    st.info(complaint_details[problem])

    st.markdown("### Your escalation ladder")

    st.markdown(
        "**Step 1 — College Students' Grievance Redressal Committee (SGRC)**"
    )

    st.write(
        "Submit your complaint to the Chairperson of the college SGRC."
    )

    st.success(
        "Regulatory timeline: SGRC should preferably send its report "
        "with recommendations within 15 working days of receiving "
        "the complaint."
    )

    st.markdown("---")

    st.markdown("**Step 2 — University Ombudsperson**")

    st.write(
        "If you are dissatisfied with the SGRC decision, "
        "you may appeal to the Ombudsperson."
    )

    st.warning(
        "Appeal deadline: within 15 days of receiving the SGRC decision."
    )

    st.success(
        "Resolution effort: Ombudsperson should make efforts to resolve "
        "the grievance within 30 days of receiving the appeal."
    )

    st.markdown("---")

    st.markdown("**Step 3 — UGC e-Samadhan / UGC portal**")

    st.write(
        "If the issue remains unresolved, use the official UGC "
        "grievance channel for further assistance."
    )

    st.markdown(
        "[Visit the UGC website](https://www.ugc.gov.in/)"
    )

    st.caption(
        "The 2023 regulations cited here do not specify a separate "
        "deadline for this further contact."
    )

    st.markdown("---")

    st.markdown("### Important regulatory notes")

    st.write(
        "- An institution must forward an online complaint to the "
        "appropriate SGRC with its comments within 15 days of receiving "
        "the complaint on its portal."
    )

    st.write(
        "- Keep copies of your complaint, acknowledgement, "
        "emails, decisions, and supporting documents."
    )

    st.write(
        "- Harassment cases may also require reporting to the "
        "appropriate Internal Complaints Committee or other designated "
        "institutional body, depending on the nature of the complaint."
    )

    st.caption(
        "Source: UGC (Redressal of Grievances of Students) Regulations, "
        "2023, Sections 5 and 8, pages 11–12 of the supplied PDF."
    )


# ---------------- FOOTER ----------------

st.sidebar.markdown("---")
st.sidebar.caption("UGCRuleBook | Student Rights Assistant")
st.sidebar.caption("Developed by Priyanka Agwan")
