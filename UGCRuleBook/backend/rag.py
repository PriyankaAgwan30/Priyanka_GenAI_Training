import logging

from backend.llm import LLMUnavailableError, get_llm_response
from backend.vectorstore import search_documents

MIN_RELEVANCE_SCORE = 0.30
logger = logging.getLogger(__name__)
SEXUAL_HARASSMENT_SOURCE = "sexual_harassment_2015.pdf"
SEXUAL_HARASSMENT_SOURCE_URL = (
    "https://www.ugc.gov.in/pdfnews/7203627_UGC_regulations-harassment.pdf"
)
UGC_STUDENT_REGULATIONS_URL = (
    "https://www.ugc.gov.in/regulations/UGC_Regulations_Student_Centric"
)
SOURCE_URLS = {
    "grievance_2019.pdf": (
        "https://www.ugc.gov.in/pdfnews/2813028_SG-Regulations-2019.pdf"
    ),
    "grievance_2023.pdf": (
        "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"
    ),
    "ragging_2009.pdf": (
        "https://www.ugc.gov.in/oldpdf/regulations/gazzetaug2010.pdf"
    ),
    SEXUAL_HARASSMENT_SOURCE: SEXUAL_HARASSMENT_SOURCE_URL,
}


def _is_sexual_harassment_question(question):
    question_lower = question.lower()
    return any(
        keyword in question_lower
        for keyword in (
            "harassment",
            "icc",
            "internal complaints committee",
            "sexual misconduct"
        )
    )


def _source_citation(metadata):
    citation = {
        "source": metadata["source"],
        "page": metadata["page"]
    }

    section = metadata.get("section")
    if section:
        citation["section"] = section

    url = SOURCE_URLS.get(metadata["source"])
    if url:
        citation["url"] = url

    return citation


def _official_citation(source, page=None, section=None):
    citation = {"source": source}
    if page is not None:
        citation["page"] = page
    if section:
        citation["section"] = section

    url = SOURCE_URLS.get(source)
    if url:
        citation["url"] = url
    elif source == "UGC student-centric regulations":
        citation["url"] = UGC_STUDENT_REGULATIONS_URL

    return citation


def _is_ragging_question(question):
    question_lower = question.lower()
    if "ragging" in question_lower:
        return True

    return (
        "senior" in question_lower
        and any(word in question_lower for word in ("fresher", "hostel", "junior"))
        and "sexual" not in question_lower
    )


def _is_refund_question(question):
    question_lower = question.lower()
    return any(
        keyword in question_lower
        for keyword in (
            "refund",
            "fee back",
            "fees back",
            "cancel admission",
            "withdraw admission",
            "another college",
            "previous college"
        )
    )


def _is_certificate_question(question):
    question_lower = question.lower()
    return any(
        keyword in question_lower
        for keyword in ("certificate", "marksheet", "original documents")
    )


def _offline_answer(question):
    question_lower = question.lower()

    if _is_sexual_harassment_question(question):
        return _unsupported_harassment_response(question)

    if _is_ragging_question(question):
        if any(
            keyword in question_lower
            for keyword in (
                "punishment",
                "penalty",
                "penalties",
                "punished",
                "consequence"
            )
        ):
            return {
                "answer": (
                    "The Anti-Ragging Committee can choose one or more "
                    "disciplinary actions, depending on how serious the case is. "
                    "These can include suspension, loss of a scholarship, "
                    "hostel expulsion, cancellation of admission, rustication, or "
                    "expulsion from the institution. See the UGC 2009 Ragging "
                    "Regulations, page 45."
                ),
                "citations": [
                    _official_citation("ragging_2009.pdf", 45)
                ]
            }

        if any(
            keyword in question_lower
            for keyword in (
                "report",
                "complaint",
                "complain",
                "what should i do",
                "who should i contact",
                "where can i"
            )
        ):
            return {
                "answer": (
                    "If you or another student is being ragged, tell the Head of "
                    "your institution or its Anti-Ragging Squad/Committee, or "
                    "contact the UGC Anti-Ragging Helpline. The UGC rules say the "
                    "Head must file an FIR within 24 hours when the report "
                    "indicates a possible criminal offence, and must notify the "
                    "district anti-ragging committee and the university nodal "
                    "officer. The institution should continue its own inquiry "
                    "while the police process proceeds. See the UGC 2009 "
                    "Ragging Regulations, pages 41–43."
                ),
                "citations": [
                    _official_citation("ragging_2009.pdf", 41),
                    _official_citation("ragging_2009.pdf", 42),
                    _official_citation("ragging_2009.pdf", 43),
                ]
            }

    if _is_refund_question(question):
        return {
            "answer": (
                "The UGC grievance rules treat a delayed or denied fee refund as "
                "a grievance when the student is eligible under the applicable "
                "refund policy. You can raise it through your institution's "
                "online grievance portal. The institution should send it to the "
                "Students' Grievance Redressal Committee within 15 days; the "
                "Committee should submit its report preferably within 15 working "
                "days. These are complaint-handling deadlines, not a single "
                "deadline for the refund payment itself. The refund amount and "
                "eligibility depend on the policy for your academic year."
            ),
            "citations": [
                _official_citation("grievance_2019.pdf", 10),
                _official_citation("grievance_2023.pdf", 9),
                _official_citation(
                    "grievance_2023.pdf",
                    11,
                    "Section 8: Procedure for redressal of grievances"
                ),
                _official_citation(
                    "grievance_2023.pdf",
                    12,
                    "Section 8: Procedure for redressal of grievances"
                ),
            ]
        }

    if _is_certificate_question(question):
        return {
            "answer": (
                "A college must not hold documents you deposited for admission "
                "to pressure you into paying fees for a course you do not plan "
                "to pursue. If the college is refusing to return your documents, "
                "raise the issue through its online grievance portal and ask for "
                "the Students' Grievance Redressal Committee. See the UGC "
                "grievance regulations, 2019 page 10 and 2023 page 9."
            ),
            "citations": [
                _official_citation("grievance_2019.pdf", 10),
                _official_citation("grievance_2023.pdf", 9),
            ]
        }

    if any(
        keyword in question_lower
        for keyword in (
            "grievance",
            "complaint",
            "unfair treatment",
            "faculty member",
            "college ignores",
            "college does not take",
            "ombudsperson",
            "how long",
            "how many days"
        )
    ):
        return {
            "answer": (
                "You can submit a student grievance through your institution's "
                "online portal. The institution should forward it to the "
                "Students' Grievance Redressal Committee within 15 days; the "
                "Committee should send its report preferably within 15 working "
                "days. If you are unhappy with the Committee's decision, you "
                "can appeal to the Ombudsperson within 15 days. The Ombudsperson "
                "should try to resolve the appeal within 30 days. These are "
                "separate steps, not one overall deadline. See Section 8 of the "
                "UGC 2023 Grievance Regulations, pages 11–12."
            ),
            "citations": [
                _official_citation(
                    "grievance_2023.pdf",
                    11,
                    "Section 8: Procedure for redressal of grievances"
                ),
                _official_citation(
                    "grievance_2023.pdf",
                    12,
                    "Section 8: Procedure for redressal of grievances"
                ),
            ]
        }

    return None


def _filter_results_by_topic(question, results):
    question_lower = question.lower()
    if _is_ragging_question(question):
        return [
            result for result in results
            if "ragging" in result["metadata"]["source"].lower()
        ]
    if _is_sexual_harassment_question(question):
        return [
            result for result in results
            if result["metadata"]["source"] == SEXUAL_HARASSMENT_SOURCE
        ]
    if _is_refund_question(question) or _is_certificate_question(question):
        return [
            result for result in results
            if result["metadata"]["source"].startswith("grievance_")
            or "refund" in result["metadata"]["source"].lower()
        ]
    if any(
        keyword in question_lower
        for keyword in (
            "ombudsperson",
            "grievance",
            "complaint",
            "unfair treatment",
            "faculty member"
        )
    ):
        return [
            result for result in results
            if result["metadata"]["source"].startswith("grievance_")
        ]
    return results


def _not_found_response(question, results=()):
    answer = (
        "I couldn't find a clear answer to this in the UGC documents currently "
        "indexed by UGCRuleBook. Please check the official UGC student-centric "
        "regulations and the rule for your topic. The available material may "
        "not cover every institution-specific detail or academic-year policy."
    )
    citations = [
        _source_citation(result["metadata"])
        for result in results[:3]
        if result["score"] >= MIN_RELEVANCE_SCORE
    ]
    if not citations:
        citations = [
            _official_citation("UGC student-centric regulations")
        ]
    return {"answer": answer, "citations": citations}


def _unsupported_harassment_response(question):
    question_lower = question.lower()
    if any(
        keyword in question_lower
        for keyword in ("contact", "email", "phone", "number", "address", "location")
    ):
        section = "Responsibilities of the Higher Educational Institution"
        answer = (
            "I can't provide your college's specific ICC contact details from the "
            "UGCRuleBook data. The UGC's 2015 sexual-harassment regulations direct "
            "higher educational institutions to publish ICC contact details and "
            "the complaints procedure. See the “Responsibilities of the Higher "
            "Educational Institution” section (Gazette page 13), then check your "
            "college's official website or prospectus for its local contacts."
        )
        page = 13
    elif any(
        keyword in question_lower
        for keyword in ("ignored", "ignore", "no action", "not take", "not taken")
    ):
        section = (
            "Regulation 6: Process for making complaint and conducting inquiry"
        )
        answer = (
            "The UGC's 2015 regulations require the ICC to handle complaints "
            "through a time-bound inquiry and protect complainants from "
            "retaliation. The indexed rule does not give a separate escalation "
            "deadline for a college that has not acted on a complaint. Check "
            "Regulation 6 and the ICC responsibilities section in the official "
            "UGC regulations, or contact the ICC/college administration for "
            "the status of your complaint."
        )
        page = 16
    elif any(
        keyword in question_lower
        for keyword in (
            "file",
            "submit",
            "complaint",
            "what should i do",
            "where can i",
            "how do i",
            "how long do i have",
            "within how many months"
        )
    ):
        section = (
            "Regulation 6: Process for making complaint and conducting inquiry"
        )
        answer = (
            "Under Regulation 6 of the UGC's 2015 sexual-harassment regulations, "
            "a written complaint should be submitted to the Internal Complaints "
            "Committee (ICC) within three months of the incident, or the last "
            "incident in a series. If the complainant cannot make it in writing, "
            "the ICC Presiding Officer or a member must provide reasonable "
            "assistance. The ICC may extend the deadline by up to three months "
            "for recorded reasons if circumstances prevented an earlier filing. "
            "See “Process for making complaint and conducting inquiry” "
            "(Gazette page 16 onward)."
        )
        page = 16
    else:
        section = "Responsibilities of the Internal Complaints Committee (ICC)"
        answer = (
            "If you mean sexual harassment, the Internal Complaints Committee "
            "(ICC) handles complaints and conducts inquiries under the UGC "
            "procedure. It must "
            "protect the complainant's privacy and prevent retaliation against "
            "complainants or witnesses. See the “Responsibilities of the "
            "Internal Complaints Committee” section (Gazette pages 15–16) and "
            "Regulation 6 for the complaint and inquiry process."
        )
        page = 15

    citation = {
        "source": SEXUAL_HARASSMENT_SOURCE,
        "page": page,
        "section": section,
        "url": SEXUAL_HARASSMENT_SOURCE_URL
    }
    return {"answer": answer, "citations": [citation]}


def _retrieval_fallback(results, question=None):
    results = [
        result
        for result in results
        if result["score"] >= MIN_RELEVANCE_SCORE
    ]

    if question and _is_sexual_harassment_question(question):
        results = [
            result
            for result in results
            if result["metadata"]["source"] == SEXUAL_HARASSMENT_SOURCE
        ]
        if not results:
            return _unsupported_harassment_response(question)

    if not results:
        return _not_found_response(question or "", results)

    excerpts = []
    citations = []

    for result in results[:3]:
        metadata = result["metadata"]
        citation = _source_citation(metadata)
        source = citation["source"]
        page = citation["page"]
        section_text = (
            f", Section: {citation['section']}"
            if citation.get("section")
            else ""
        )

        if citation not in citations:
            citations.append(citation)

        text = " ".join(result["text"].split())
        if text:
            excerpts.append(
                f"[Source: {source}, Page: {page}{section_text}]\n{text[:700]}"
            )

    if not excerpts:
        return _not_found_response(question or "", results)

    answer = (
        "Here is the most relevant part of the UGC regulations I found. "
        "In simple terms, it says:\n\n"
        + "\n\n".join(excerpts)
        + "\n\nCheck the cited regulation for the full context."
    )

    return {
        "answer": answer,
        "citations": citations
    }


def answer_question(question, top_k=5, conversation_history=None):

    if not question.strip():
        return {
            "answer": "Please enter a question about a student right, and I'll look it up in the UGC regulations.",
            "citations": []
        }

    # Step 1: Expand queries for better document retrieval
    question_lower = question.lower()
    retrieval_query = question

    if _is_sexual_harassment_question(question):
        retrieval_query = (
            question
            + " UGC 2015 regulations sexual harassment higher educational "
            + "institution responsibilities Internal Complaints Committee "
            + "Responsibilities of the Internal Complaints Committee "
            + "ICC contact details complaint procedure responsibilities "
            + "complaint inquiry Regulation 6"
        )

    elif "ragging" in question_lower:

        punishment_keywords = [
            "punishment",
            "punished",
            "found guilty",
            "disciplinary",
            "suspension",
            "expulsion",
            "rustication",
            "cancel admission",
            "scholarship",
            "withholding results",
            "debarred"
        ]

        action_keywords = [
            "what should i do",
            "where can i report",
            "report ragging",
            "reporting",
            "report",
            "contact",
            "complaint",
            "complain",
            "help",
            "action",
            "hostel",
            "warden",
            "police",
            "fir",
            "fresher",
            "senior",
            "victim",
            "report incident",
            "report a case",
            "how can i complain",
            "complain against",
            "complaint procedure",
            "contact authorities"
        ]

        if any(keyword in question_lower for keyword in punishment_keywords):
            retrieval_query = (
                question
                + " What punishments can the Anti-Ragging Committee award "
                + "to students found guilty of ragging? Suspension from classes, "
                + "withholding scholarship, examination restrictions, withholding results, "
                + "hostel expulsion, cancellation of admission, rustication, "
                + "institutional expulsion and disciplinary action?"
            )

        elif any(keyword in question_lower for keyword in action_keywords):
            retrieval_query = (
                question
                + " How to report a ragging incident, complaint procedure, "
                + "Anti-Ragging Squad, Anti-Ragging Committee, hostel warden, "
                + "Head of Institution, police FIR, District Anti-Ragging Committee, "
                + "University Nodal Officer, immediate action and remedial measures?"
            )

        else:
            retrieval_query = (
                question
                + " What acts constitute ragging, including teasing, "
                + "rudeness, physical abuse, sexual abuse, verbal abuse, "
                + "financial extortion, forceful expenditure, humiliation, "
                + "psychological harm, and forcing students to perform tasks?"
            )

    elif any(word in question_lower for word in [
        "certificate", "certificates", "documents", "original marksheet"
    ]):
        retrieval_query = (
            question
            + " withholding of or refusal to return any document "
            "in the form of certificates of degree diploma or any "
            "other award deposited by a student to compel payment "
            "of fees for a course or program of study which the "
            "student does not intend to pursue"
        )

    elif any(keyword in question_lower for keyword in [
        "refund",
        "withdraw admission",
        "cancel admission",
        "another college",
        "previous college",
        "fees back",
        "fee back"
    ]):
        retrieval_query = (
            question
            + " delay in or denial of refund of fees due to a student who "
            "withdraws admission within the time mentioned in the prospectus "
            "or notified by the Commission; percentage of tuition fee and "
            "other charges refundable; admission withdrawal refund timeline"
        )

    # Step 2: Retrieve relevant chunks
    results = search_documents(retrieval_query, top_k)
    results = _filter_results_by_topic(question, results)

    # Step 3: Check relevance
    if not results or results[0]["score"] < MIN_RELEVANCE_SCORE:
        return _offline_answer(question) or _not_found_response(question, results)

    # Step 4: Prepare context and citations
    context = ""
    citations = []

    for result in results:

        metadata = result["metadata"]

        source = metadata["source"]
        page = metadata["page"]
        citation = _source_citation(metadata)
        section_text = (
            f", Section: {citation['section']}"
            if citation.get("section")
            else ""
        )

        context += (
            f"\n[Source: {source}, Page: {page}{section_text}]\n"
            f"{result['text']}\n"
        )

        if citation not in citations:
            citations.append(citation)

    # Step 5: Prepare system instructions
    system_prompt = """
    You are UGCRuleBook, a helpful and knowledgeable student-rights
    assistant that explains UGC regulations to students.

    Follow these rules strictly:

    1. Answer only using the provided retrieved context.
    2. Never invent facts, regulations, penalties, procedures,
       deadlines, or student rights.
    3. Use warm, natural, simple English. Start with the direct answer,
       then add one or two useful details or next steps. Keep the answer
       concise and avoid legal jargon where possible.
    4. If the context does not answer the question, do not reply with
       "I don't know". Say that the detail was not found in the indexed
       UGC documents, point the student to the relevant official UGC
       regulation, and explain what information is missing.
    5. If the context supports only part of the question, answer that
       part and clearly state what it does not cover.
    6. Do not refuse an answer only because the student used different
       wording from the regulation.
    7. Include relevant source and page citations in your answer.
       Name the relevant regulation or section when its title appears in
       the retrieved context. Do not invent a section number or title.
    8. Rephrase information naturally instead of copying the source
       word-for-word, unless exact wording is important.
    9. Do not unnecessarily repeat the student's question in your answer.
    10. Adjust your response to the question:
       - For direct questions, answer directly.
       - For procedures, explain the steps in order.
       - For penalties, clearly list the possible consequences.
       - For definitions, explain the meaning in simple language.
       - For urgent situations, prioritize the immediate actions.
    11. Use paragraphs for simple answers and bullet points when
        listing multiple rules, steps, penalties, or options.
    12. Keep answers relevant and concise, but include all important
        information supported by the context.

    Your goal is to give a helpful, accurate answer that feels like
    a knowledgeable person explaining the rule to a student.
    """

    history_text = ""

    if conversation_history:
        for item in conversation_history[-5:]:
            history_text += (
                f"\nPrevious Question: {item['question']}\n"
                f"Previous Answer: {item['result']}\n"
            )

    prompt = f"""
    Previous Conversation:
    {history_text}

    Student Question:
    {question}

    Retrieved Context:
    {context}

    Answer the current question using only the retrieved context.
    Use previous conversation only to understand references
    such as "my previous question".

    Do not use previous answers as factual evidence.
    Include citations in this format:
    [Source: filename, Page: number]
    """

    # Step 6: Generate answer
    try:
        answer = get_llm_response(prompt, system_prompt)
    except LLMUnavailableError:
        logger.warning(
            "Using the verified local answer fallback because the language model is unavailable"
        )
        offline_answer = _offline_answer(question)
        if offline_answer:
            return offline_answer
        return _retrieval_fallback(results, question)

    if not answer or "i don't know" in answer.lower():
        return _offline_answer(question) or _not_found_response(question, results)

    return {
        "answer": answer,
        "citations": citations
    }
