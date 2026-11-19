from fastapi.testclient import TestClient

from backend import main
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_records_endpoint():
    response = client.get("/records")
    assert response.status_code == 200
    assert len(response.json()) == 20


def test_get_record_by_id():
    response = client.get("/records/1")
    assert response.status_code == 200
    assert response.json()["rule_title"] == "Student Grievance Regulations 2023"


def test_get_record_invalid_id():
    response = client.get("/records/999")
    assert response.status_code == 404


def test_search_endpoint():
    response = client.get("/search", params={"q": "ragging"})
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_ask_endpoint_with_fake_llm(monkeypatch):
    fake_result = {
        "answer": "Students can complain to the grievance committee.",
        "citations": ["grievance_2023.pdf, Page: 12"]
    }

    monkeypatch.setattr(
        main,
        "answer_question",
        lambda question: fake_result
    )

    response = client.post(
        "/ask",
        json={"question": "What can students complain about?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == fake_result["answer"]
    assert response.json()["citations"] == fake_result["citations"]