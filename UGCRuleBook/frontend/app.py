
import csv
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# -----------------------------
# Basic settings
# -----------------------------

st.set_page_config(
    page_title="UGCRuleBook",
    page_icon="📘",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"
FEEDBACK_FILE = Path(__file__).parent / "feedback.csv"

st.title("📘 UGCRuleBook")
st.caption("Your student rights and grievance assistant")

st.info(
    "Information from official UGC regulations for awareness only — "
    "not legal advice. Follow your institution's grievance process "
    "or consult a lawyer."
)


# -----------------------------
# Save feedback
# -----------------------------

def save_feedback(question, answer, feedback):
    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "date",
                "question",
                "answer",
                "feedback"
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            question,
            answer,
            feedback
        ])


# -----------------------------
# Display citations
# -----------------------------

def show_citations(citations):
    if not citations:
        st.caption("No document citations available.")
        return

    st.markdown("**Sources used:**")

    for citation in citations:
        if isinstance(citation, dict):
            source = citation.get("source", "Unknown source")
            page = citation.get("page", "N/A")

            st.caption(f"📄 {source} — Page {page}")

        else:
            st.caption(str(citation))


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a section",
    ["Student Chat", "Complaint Path"]
)

api_mode = st.sidebar.radio(
    "Chat mode",
    ["RAG (/ask)", "Agent (/agent)"]
)

if page == "Student Chat":

    st.header("Ask your question")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show previous messages
    for index, message in enumerate(st.session_state.messages):

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                show_citations(message.get("citations", []))

                feedback = st.feedback(
                    "thumbs",
                    key=f"feedback_{index}"
                )

                if feedback is not None and not message.get("feedback_saved"):
                    value = "up" if feedback == 1 else "down"

                    save_feedback(
                        message.get("question", ""),
                        message["content"],
                        value
                    )

                    message["feedback_saved"] = True
                    st.toast("Thank you for your feedback!")

    question = st.chat_input("Ask about student rights...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"), st.spinner("Finding the answer..."):

            try:
                if api_mode == "RAG (/ask)":
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question},
                        timeout=120
                    )

                else:
                    response = requests.post(
                        f"{API_URL}/agent",
                        json={
                            "question": question,
                            "thread_id": "ugcrulebook_student"
                        },
                        timeout=120
                    )

                response.raise_for_status()
                data = response.json()

                if api_mode == "RAG (/ask)":
                    answer = data.get("answer", "I don't know")
                    citations = data.get("citations", [])

                else:
                    result = data.get("result", {})

                    if isinstance(result, dict):
                        answer = result.get("answer", str(result))
                        citations = result.get("citations", [])
                    else:
                        answer = str(result)
                        citations = []

                st.markdown(answer)
                show_citations(citations)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "question": question,
                    "feedback_saved": False
                })

            except requests.exceptions.RequestException as error:
                answer = (
                    "I could not connect to the backend. "
                    "Please start the FastAPI server and try again."
                )

                st.error(answer)
                st.caption(str(error))


# -----------------------------
# Complaint path stepper
# -----------------------------

elif page == "Complaint Path":

    st.header("Complaint Path Stepper")

    st.write(
        "Choose your problem to understand the usual "
        "student grievance escalation process."
    )

    problem = st.selectbox(
        "Select your problem",
        [
            "Fee Refund",
            "Ragging",
            "Harassment",
            "Marks / Examination"
        ]
    )

    complaint_paths = {
        "Fee Refund": [
            (
                "1. College Grievance Committee (SGRC)",
                ("Submit a written complaint with fee receipts, "
                "admission details and withdrawal proof."),
                ("SGRC should send its report and recommendations "
                "preferably within 15 working days.")
            ),
            (
                "2. University Ombudsperson",
                ("If you are not satisfied with the SGRC decision, "
                "you can appeal to the Ombudsperson."),
                ("Appeal within 15 days of receiving the SGRC decision. "
                "The Ombudsperson should make efforts to resolve it "
                "within 30 days of receiving the appeal.")
            ),
            (
                "3. UGC e-Samadhan",
                ("If the issue remains unresolved, you can approach "
                "the UGC grievance portal with your complaint "
                "and supporting documents."),
                ("No separate resolution deadline is specified here "
                "for the UGC portal.")
            )
        ],

        "Ragging": [
            (
                "1. College Anti-Ragging Committee / Squad",
                ("Report the incident immediately to the college "
                "Anti-Ragging Committee, Anti-Ragging Squad "
                "or institutional authorities."),
                ("Report immediately. Do not wait for the ordinary "
                "grievance timeline.")
            ),
            (
                "2. University authorities / Ombudsperson",
                ("Use the applicable institutional grievance and "
                "university escalation process if the issue is "
                "not addressed."),
                ("For an SGRC decision, the appeal period is "
                "15 days. Ombudsperson efforts to resolve an appeal "
                "are within 30 days.")
            ),
            (
                "3. National Anti-Ragging Helpline",
                ("Call 1800-180-5522 or visit the official "
                "Anti-Ragging portal."),
                "Report immediately. Do not wait for a deadline."
            )
        ],

        "Harassment": [
            (
                "1. College Internal Committee / SGRC",
                ("For sexual harassment, contact the institution's "
                "Internal Committee (IC). For other student "
                "grievances, contact the SGRC."),
                ("Use the applicable committee's procedure. "
                "Do not delay reporting.")
            ),
            (
                "2. University Ombudsperson",
                ("For grievances covered by the UGC student "
                "grievance regulations, use the appeal process "
                "after the SGRC decision."),
                ("Appeal within 15 days of the SGRC decision. "
                "The Ombudsperson should make efforts to resolve "
                "the appeal within 30 days.")
            ),
            (
                "3. UGC e-Samadhan",
                ("You may approach the UGC grievance portal "
                "for an unresolved UGC-related grievance."),
                ("No separate resolution deadline is specified "
                "here for the UGC portal.")
            )
        ],

        "Marks / Examination": [
            (
                "1. College Grievance Committee (SGRC)",
                ("Submit the examination complaint with your "
                "marksheet, answer-sheet details and evidence."),
                ("SGRC should send its report and recommendations "
                "preferably within 15 working days.")
            ),
            (
                "2. University Ombudsperson",
                "You may appeal against the SGRC decision.",
                ("Appeal within 15 days of receiving the decision. "
                "The Ombudsperson should make efforts to resolve "
                "the appeal within 30 days.")
            ),
            (
                "3. UGC e-Samadhan",
                ("For an unresolved UGC-related grievance, "
                "you may approach the UGC portal."),
                ("No separate resolution deadline is specified "
                "here for the UGC portal.")
            )
        ]
    }

    # Special guidance
    if problem == "Ragging":
        st.error(
            "Important: Report ragging immediately. "
            "You can contact the National Anti-Ragging Helpline "
            "at 1800-180-5522. If anyone is in immediate danger, "
            "contact emergency services."
        )

    elif problem == "Harassment":
        st.warning(
            "Important: For sexual harassment, the institution's "
            "Internal Committee is a specific reporting route. "
            "Do not rely only on the general SGRC process."
        )

    elif problem == "Marks / Examination":
        st.info(
            "The Ombudsperson is not a general revaluation service. "
            "The UGC regulations require a specific irregularity "
            "materially affecting the result or a specific instance "
            "of discrimination."
        )

    st.divider()

    steps = complaint_paths[problem]

    for number, step in enumerate(steps):

        with st.container(border=True):

            st.subheader(step[0])
            st.write(step[1])

            st.info("⏱️ " + step[2])

            if number < len(steps) - 1:
                st.caption("⬇️ Next escalation step")

    st.divider()

    st.markdown("**Useful official links**")

    st.markdown(
        "- [UGC e-Samadhan Portal](https://samadhaan.ugc.ac.in/)"
    )

    st.markdown(
        "- [National Anti-Ragging Portal](https://antiragging.in/)"
    )

    st.markdown(
        "- [UGC Student Grievance Regulations, 2023](https://www.ugc.gov.in/e-book/UGC_Regulation/files/basic-html/page1004.html)"
    )

    st.caption(
        "Timelines are based on the UGC Student Grievance "
        "Regulations, 2023, where applicable. Special complaint "
        "procedures may have different rules. Verify the rules "
        "applicable to your institution."
    )
