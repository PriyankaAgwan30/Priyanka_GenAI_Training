MODEL_NAME = "all-MiniLM-L6-v2"

model = None


def get_model():
    global model

    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)

    return model


def generate_embeddings(texts):
    if not texts:
        return []

    embedding_model = get_model()

    return embedding_model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False
    )


if __name__ == "__main__":
    sample_texts = [
        "Students have the right to receive their original certificates.",
        "Universities must follow fee refund regulations."
    ]

    vectors = generate_embeddings(sample_texts)

    print("Number of embeddings:", len(vectors))
    print("Vector dimensions:", vectors.shape)
    print("First embedding:", vectors[0][:10])
