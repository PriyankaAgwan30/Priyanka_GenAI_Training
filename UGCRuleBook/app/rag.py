
from app.vectorstore import search_documents
from app.llm import get_llm_response


MIN_RELEVANCE_SCORE = 0.30


def answer_question(question, top_k=5):

    if not question.strip():
        return {
            "answer": "I don't know",
            "citations": []
        }

    # Step 1: Retrieve relevant chunks
    results = search_documents(question, top_k)

    # Step 2: Check whether relevant information was found
    if not results or results[0]["score"] < MIN_RELEVANCE_SCORE:
        return {
            "answer": "I don't know",
            "citations": []
        }

    # Step 3: Prepare context and citations
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

    # Step 4: Prepare instructions for the LLM
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

    prompt = f"""
    Student Question:
    {question}

    Retrieved Context:
    {context}

    Answer the question using only the retrieved context.
    Include citations in this format:
    [Source: filename, Page: number]
    """

    # Step 5: Generate the answer
    answer = get_llm_response(prompt, system_prompt)

    if not answer or "i don't know" in answer.lower():
        answer = "I don't know"
        citations = []

    return {
        "answer": answer,
        "citations": citations
    }
