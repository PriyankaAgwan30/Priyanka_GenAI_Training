
import numpy as np

from app.chunking import chunk_documents
from app.embed import generate_embeddings


def semantic_search(question, chunks, chunk_embeddings, top_k=10):

    if not question.strip():
        return []

    # Generate embedding for the user's question
    question_embedding = generate_embeddings([question])[0]

    # Calculate cosine similarity
    similarities = np.dot(chunk_embeddings, question_embedding) / (
        np.linalg.norm(chunk_embeddings, axis=1)
        * np.linalg.norm(question_embedding)
    )

    # Get indexes of top matching chunks
    top_indexes = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in top_indexes:

        results.append({
            "score": float(similarities[index]),
            "text": chunks[index]["text"],
            "metadata": chunks[index]["metadata"]
        })

    return results



if __name__ == "__main__":

    print("Loading and chunking documents...")

    chunks = chunk_documents()

    print("\nTotal chunks:", len(chunks))

    print("\nGenerating chunk embeddings...")

    texts = [chunk["text"] for chunk in chunks]

    chunk_embeddings = generate_embeddings(texts)

    questions = [
        "Can a college keep the original certificates of a student?",
        "What happens if a college refuses to refund fees?",
        "How can a student file a grievance?",
        "What is the role of the Students Grievance Redressal Committee?",
        "What is the role of an Ombudsperson?",
        "What actions can be taken against ragging?",
        "What if a college publishes false information in its prospectus?",
        "Can a college demand fees beyond its declared admission policy?",
        "What is the time limit for resolving student grievances?",
        "Which authorities can take action against an institution for grievance violations?"
    ]

    import os

    os.makedirs("eval", exist_ok=True)

    with open("eval/search_results.md", "w", encoding="utf-8") as file:

        file.write("# UGCRuleBook Semantic Search Evaluation\n\n")
        file.write("Total document chunks: " + str(len(chunks)) + "\n\n")

        for question_number, question in enumerate(questions, start=1):

            print(f"\n\nQuestion {question_number}: {question}")

            results = semantic_search(
                question,
                chunks,
                chunk_embeddings,
                top_k=5
            )

            file.write(f"## Question {question_number}\n\n")
            file.write(f"**Question:** {question}\n\n")

            for rank, result in enumerate(results, start=1):

                metadata = result["metadata"]

                print(
                    f"Rank {rank} | Score: {result['score']:.4f} | "
                    f"Source: {metadata['source']} | "
                    f"Page: {metadata['page']}"
                )

                file.write(f"### Result {rank}\n\n")
                file.write(f"- Similarity Score: {result['score']:.4f}\n")
                file.write(f"- Source: {metadata['source']}\n")
                file.write(f"- Page: {metadata['page']}\n")
                file.write(f"- Title: {metadata['title']}\n\n")
                file.write(f"**Text:** {result['text']}\n\n")
                file.write("---\n\n")

    print("\nEvaluation completed!")
    print("Results saved in eval/search_results.md")
