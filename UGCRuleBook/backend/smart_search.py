
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def smart_search(records, query):

    if not query.strip():
        return []

    documents = []

    for record in records:
        text = (
            record["rule_title"] + " " +
            record["regulation_or_circular"] + " " +
            record["student_right"] + " " +
            record["where_to_complain"]
        )
        documents.append(text)

    vectorizer = TfidfVectorizer()

    try:
        record_vectors = vectorizer.fit_transform(documents)
        query_vector = vectorizer.transform([query])

        scores = cosine_similarity(query_vector, record_vectors)[0]

        results = []

        for i in range(len(records)):
            if scores[i] > 0:
                results.append((scores[i], records[i]))

        results.sort(key=lambda item: item[0], reverse=True)

        return [record for score, record in results]

    except ValueError:
        return []
