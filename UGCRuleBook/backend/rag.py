from backend.vectorstore import search_documents
from backend.llm import get_llm_response


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
        retrieval_query = (
            question
            + " What acts constitute ragging, including teasing, "
            "rudeness, physical abuse, sexual abuse, verbal abuse, "
            "financial extortion, forceful expenditure, humiliation, "
            "psychological harm, and forcing students to perform tasks?"
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
    You are UGCRuleBook, an assistant that answers
    student-rights questions using UGC documents.

    Follow these rules:
    1. Answer only using the provided context.
    2. Do not invent information.
    3. If the context does not contain the answer,
       reply exactly: I don't know
    4. Include source and page citations in your answer.
    5. Use simple and understandable language.
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
