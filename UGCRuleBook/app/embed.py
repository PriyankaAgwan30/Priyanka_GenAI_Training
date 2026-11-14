
from sentence_transformers import SentenceTransformer

# Embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts):
    """
    Convert a list of text chunks into numerical vectors.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings


if __name__ == "__main__":

    sample_texts = [
        "Students have the right to receive their original certificates.",
        "Universities must follow fee refund regulations."
    ]

    vectors = generate_embeddings(sample_texts)

    print("\nNumber of embeddings:", len(vectors))
    print("Vector dimensions:", vectors.shape)
    print("First embedding:", vectors[0][:10])
