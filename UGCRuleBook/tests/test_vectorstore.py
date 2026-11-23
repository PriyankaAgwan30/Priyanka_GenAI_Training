import pytest

from backend import vectorstore


def test_search_documents_returns_empty_when_collection_has_no_index(
    monkeypatch
):
    monkeypatch.setattr(vectorstore.collection, "count", lambda: 0)
    monkeypatch.setattr(
        vectorstore,
        "generate_embeddings",
        lambda _: pytest.fail("Should not generate embeddings for an empty index")
    )

    assert vectorstore.search_documents("fee refund") == []
