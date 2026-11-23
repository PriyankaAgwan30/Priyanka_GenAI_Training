from backend.llm import get_llm_response
from backend.vectorstore import search_documents

MIN_RELEVANCE_SCORE = 0.30


def answer_question(question, top_k=5, conversation_history=None):

    if not question.strip():
        return {
            "answer": "I don't know",
            "citations": []
        }

    # Step 1: Expand queries for better document retrieval
    question_lower = question.lower()
    retrieval_query = question

    if "ragging" in question_lower:

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

    # Step 2: Retrieve relevant chunks
    results = search_documents(retrieval_query, top_k)

    # Step 3: Check relevance
    if not results or results[0]["score"] < MIN_RELEVANCE_SCORE:
        return {
            "answer": "I don't know",
            "citations": []
        }

    # Step 4: Prepare context and citations
    context = ""
    citations = []

    for result in results:

        metadata = result["metadata"]

        source = metadata["source"]
        page = metadata["page"]

        context += (
            f"\n[Source: {source}, Page: {page}]\n"
            f"{result['text']}\n"
        )

        citation = {
            "source": source,
            "page": page
        }

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
    3. If the context does not contain enough information to answer,
       reply exactly: I don't know
    4. Include relevant source and page citations in your answer.
    5. Use simple, clear, natural, student-friendly English.
    6. Rephrase information naturally instead of copying the source
       word-for-word, unless exact wording is important.
    7. Vary your sentence structure, opening phrases, and explanation
       style across responses. Avoid repeatedly using the same
       introductions or answer templates.
    8. Do not unnecessarily repeat the student's question in your answer.
    9. Adjust your response to the question:
       - For direct questions, answer directly.
       - For procedures, explain the steps in order.
       - For penalties, clearly list the possible consequences.
       - For definitions, explain the meaning in simple language.
       - For urgent situations, prioritize the immediate actions.
    10. Use paragraphs for simple answers and bullet points when
        listing multiple rules, steps, penalties, or options.
    11. Keep answers relevant and concise, but include all important
        information supported by the context.
    12. Generate a fresh response for each request without sacrificing
        factual consistency or accuracy.

    Your goal is to make every answer feel natural and helpful,
    rather than repetitive, robotic, or template-generated.
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
    answer = get_llm_response(prompt, system_prompt)

    if not answer or "i don't know" in answer.lower():
        answer = "I don't know"
        citations = []

    return {
        "answer": answer,
        "citations": citations
    }
