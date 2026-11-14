
from pathlib import Path

import chromadb

from app.chunking import chunk_documents
from app.embed import generate_embeddings


BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "ugcrulebook"


# Create persistent ChromaDB client
client = chromadb.PersistentClient(path=str(DB_PATH))


# Create or access collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def index_documents():

    print("Loading document chunks...")

    chunks = chunk_documents()

    if not chunks:
        print("No document chunks found.")
        return

    texts = [chunk["text"] for chunk in chunks]

    print("\nGenerating embeddings...")

    embeddings = generate_embeddings(texts)

    print("\nStoring documents in ChromaDB...")

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            chunk["metadata"] for chunk in chunks
        ]
    )

    print("\nIndexing completed!")
    print("Total chunks indexed:", collection.count())


def search_documents(question, top_k=5):

    if not question.strip():
        return []

    question_embedding = generate_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    search_results = []

    for index in range(len(results["ids"][0])):

        distance = results["distances"][0][index]

        search_results.append({
            "id": results["ids"][0][index],
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "score": 1 - distance
        })

    return search_results


if __name__ == "__main__":

    index_documents()

    print("\nTesting ChromaDB search...")

    question = "Can a college keep the original certificates of a student?"

    results = search_documents(question, top_k=5)

    print("\nQuestion:", question)

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("Score:", round(result["score"], 4))
        print("Source:", result["metadata"]["source"])
        print("Page:", result["metadata"]["page"])
        print("Text:", result["text"][:300])
        print("-" * 60)
