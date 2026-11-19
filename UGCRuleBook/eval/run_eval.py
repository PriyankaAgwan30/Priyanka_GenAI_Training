import json

import chromadb
from app.chunking import chunk_documents
from app.embed import generate_embeddings

MIN_RELEVANCE_SCORE = 0.30

CONFIGURATIONS = [
    {
        "name": "A - Baseline",
        "chunk_size": 800,
        "overlap": 150,
        "top_k": 5
    },
    {
        "name": "B - Alternative",
        "chunk_size": 500,
        "overlap": 100,
        "top_k": 3
    }
]


def load_eval_set():
    with open("eval/eval_set.json", "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_configuration(config, questions):

    print("\n" + "=" * 55)
    print("Evaluating:", config["name"])
    print("=" * 55)

    chunks = chunk_documents(
        chunk_size=config["chunk_size"],
        overlap=config["overlap"]
    )

    print("Total chunks:", len(chunks))

    if not chunks:
        raise ValueError("No chunks generated.")

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    # Use temporary ChromaDB storage.
    # This does not modify the production database.
    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name=f"evaluation_collection_{config['chunk_size']}_{config['top_k']}"
    )

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[chunk["metadata"] for chunk in chunks]
    )

    successful_questions = 0
    total_keywords = 0
    matched_keywords = 0
    unsupported_rejections = 0
    unsupported_total = 0

    for question_data in questions:

        question = question_data["question"]
        expected_keywords = question_data["expected_keywords"]

        query_embedding = generate_embeddings([question])[0]

        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(config["top_k"], collection.count()),
            include=["documents", "distances"]
        )

        retrieved_text = " ".join(
            results["documents"][0]
        ).lower()

        distances = results["distances"][0]

        best_score = 1 - distances[0] if distances else 0

        if question_data["answerable"]:

            matched = [
                keyword for keyword in expected_keywords
                if keyword.lower() in retrieved_text
            ]

            total_keywords += len(expected_keywords)
            matched_keywords += len(matched)

            if matched:
                successful_questions += 1

            print(
                f"Q{question_data['id']}: "
                f"{len(matched)}/{len(expected_keywords)} "
                f"keywords matched | Score: {best_score:.3f}"
            )

        else:

            unsupported_total += 1

            rejected = best_score < MIN_RELEVANCE_SCORE

            if rejected:
                unsupported_rejections += 1

            print(
                f"Q{question_data['id']}: "
                f"Unsupported question | "
                f"Score: {best_score:.3f} | "
                f"Correctly rejected: {rejected}"
            )

    answerable_total = sum(
        1 for q in questions if q["answerable"]
    )

    keyword_coverage = (
        matched_keywords / total_keywords * 100
        if total_keywords else 0
    )

    retrieval_hit_rate = (
        successful_questions / answerable_total * 100
        if answerable_total else 0
    )

    rejection_rate = (
        unsupported_rejections / unsupported_total * 100
        if unsupported_total else 0
    )

    metrics = {
        "name": config["name"],
        "chunk_size": config["chunk_size"],
        "overlap": config["overlap"],
        "top_k": config["top_k"],
        "chunks": len(chunks),
        "keyword_coverage": keyword_coverage,
        "retrieval_hit_rate": retrieval_hit_rate,
        "unsupported_rejection": rejection_rate
    }

    print("\nConfiguration results:")
    print(f"Keyword coverage: {keyword_coverage:.2f}%")
    print(f"Retrieval hit rate: {retrieval_hit_rate:.2f}%")
    print(f"Unsupported rejection: {rejection_rate:.2f}%")

    return metrics


def main():

    questions = load_eval_set()
    all_results = []

    for config in CONFIGURATIONS:
        result = evaluate_configuration(config, questions)
        all_results.append(result)

    print("\n\n" + "=" * 75)
    print("FINAL CONFIGURATION COMPARISON")
    print("=" * 75)

    print(
        f"{'Configuration':<18}"
        f"{'Chunks':<10}"
        f"{'Keyword %':<13}"
        f"{'Hit Rate %':<13}"
        f"{'Rejection %':<13}"
    )

    for result in all_results:
        print(
            f"{result['name']:<18}"
            f"{result['chunks']:<10}"
            f"{result['keyword_coverage']:<13.2f}"
            f"{result['retrieval_hit_rate']:<13.2f}"
            f"{result['unsupported_rejection']:<13.2f}"
        )

    winner = max(
        all_results,
        key=lambda result: (
            result["keyword_coverage"],
            result["retrieval_hit_rate"],
            result["unsupported_rejection"]
        )
    )

    print("\nBest configuration:", winner["name"])
    print("Chunk size:", winner["chunk_size"])
    print("Overlap:", winner["overlap"])
    print("Top-K:", winner["top_k"])


if __name__ == "__main__":
    main()
