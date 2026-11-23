import pytest

from backend import rag
from backend.llm import LLMUnavailableError


@pytest.mark.parametrize(
    ("question", "expected_query_text"),
    [
        (
            "I got admission to another college. Can I get my fees back?",
            "delay in or denial of refund of fees",
        ),
        (
            "How can a fresher report a ragging incident?",
            "Anti-Ragging Squad",
        ),
        (
            "What is the role of the Internal Complaints Committee?",
            "Responsibilities of the Internal Complaints Committee",
        ),
    ],
)
def test_query_expansion_uses_the_relevant_regulation_terms(
    monkeypatch,
    question,
    expected_query_text,
):
    captured = {}
    result = {
        "score": 0.7,
        "text": "Relevant source text.",
        "metadata": {"source": "official.pdf", "page": 4},
    }

    def fake_search(query, _top_k):
        captured["query"] = query
        return [result]

    monkeypatch.setattr(rag, "search_documents", fake_search)
    monkeypatch.setattr(
        rag,
        "get_llm_response",
        lambda *_args: "A supported answer. [Source: official.pdf, Page: 4]",
    )

    rag.answer_question(question)

    assert expected_query_text.lower() in captured["query"].lower()


def test_missing_icc_contact_details_point_to_official_section(monkeypatch):
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [])

    response = rag.answer_question(
        "What is the email address and phone number of my college's ICC?"
    )

    assert "can't provide your college's specific ICC contact details" in (
        response["answer"]
    )
    assert "Responsibilities of the Higher Educational Institution" in (
        response["answer"]
    )
    assert response["citations"] == [
        {
            "source": "sexual_harassment_2015.pdf",
            "page": 13,
            "section": "Responsibilities of the Higher Educational Institution",
            "url": rag.SEXUAL_HARASSMENT_SOURCE_URL,
        }
    ]


def test_missing_harassment_complaint_answer_gives_verified_regulation(monkeypatch):
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [])

    response = rag.answer_question(
        "What should I do if I face sexual harassment in college?"
    )

    assert "written complaint should be submitted to the Internal Complaints" in (
        response["answer"]
    )
    assert "within three months" in response["answer"]
    assert response["citations"][0]["section"].startswith("Regulation 6:")
    assert response["citations"][0]["page"] == 16


def test_retrieved_citation_includes_regulation_section(monkeypatch):
    result = {
        "score": 0.7,
        "text": "The ICC shall inquire into a complaint.",
        "metadata": {
            "source": "sexual_harassment_2015.pdf",
            "page": 16,
            "section": (
                "Responsibilities of the Internal Complaints Committee (ICC) | "
                "Regulation 6: Process for making complaint and conducting inquiry"
            ),
        },
    }
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [result])
    monkeypatch.setattr(
        rag,
        "get_llm_response",
        lambda *_args: "The ICC handles the complaint inquiry.",
    )

    response = rag.answer_question("How does the ICC investigate harassment?")

    assert response["citations"][0]["section"] == result["metadata"]["section"]
    assert response["citations"][0]["url"] == rag.SEXUAL_HARASSMENT_SOURCE_URL


def test_harassment_outage_does_not_show_irrelevant_ragging_excerpt(monkeypatch):
    result = {
        "score": 0.8,
        "text": "An Anti-Ragging Squad shall inspect the hostel.",
        "metadata": {"source": "ragging_2009.pdf", "page": 37},
    }
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [result])

    def fail_generation(*_args):
        raise LLMUnavailableError()

    monkeypatch.setattr(rag, "get_llm_response", fail_generation)

    response = rag.answer_question(
        "What should I do if I face sexual harassment in college?"
    )

    assert "Anti-Ragging Squad" not in response["answer"]
    assert "within three months" in response["answer"]
    assert response["citations"][0]["section"].startswith("Regulation 6:")


def test_ragging_report_outage_returns_simple_steps(monkeypatch):
    result = {
        "score": 0.8,
        "text": "The Head of Institution shall file an FIR within twenty-four hours.",
        "metadata": {"source": "ragging_2009.pdf", "page": 41},
    }
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [result])

    def fail_generation(*_args):
        raise LLMUnavailableError()

    monkeypatch.setattr(rag, "get_llm_response", fail_generation)

    response = rag.answer_question("How can a fresher report a ragging incident?")

    assert "Anti-Ragging Squad/Committee" in response["answer"]
    assert "within 24 hours" in response["answer"]
    assert all(
        citation["source"] == "ragging_2009.pdf"
        for citation in response["citations"]
    )


def test_grievance_outage_explains_each_deadline(monkeypatch):
    result = {
        "score": 0.8,
        "text": "An SGRC report should be submitted within 15 working days.",
        "metadata": {"source": "grievance_2023.pdf", "page": 12},
    }
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [result])

    def fail_generation(*_args):
        raise LLMUnavailableError()

    monkeypatch.setattr(rag, "get_llm_response", fail_generation)

    response = rag.answer_question(
        "How long does a college have to resolve a student's grievance?"
    )

    assert "within 15 days" in response["answer"]
    assert "15 working days" in response["answer"]
    assert "within 30 days" in response["answer"]
    assert "not one overall deadline" in response["answer"]


def test_unsupported_question_points_to_official_ugc_rules(monkeypatch):
    monkeypatch.setattr(rag, "search_documents", lambda *_args: [])

    response = rag.answer_question(
        "Does my college provide a campus shuttle after 10 PM?"
    )

    assert "I don't know" not in response["answer"]
    assert "official UGC student-centric regulations" in response["answer"]
    assert response["citations"][0]["url"] == rag.UGC_STUDENT_REGULATIONS_URL


def test_refund_answer_excludes_irrelevant_harassment_citations(monkeypatch):
    irrelevant_result = {
        "score": 0.9,
        "text": "The ICC handles sexual harassment complaints.",
        "metadata": {"source": "sexual_harassment_2015.pdf", "page": 16},
    }
    relevant_result = {
        "score": 0.6,
        "text": "Delay in or denial of an eligible fee refund is a grievance.",
        "metadata": {"source": "grievance_2023.pdf", "page": 9},
    }
    captured = {}

    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda *_args: [irrelevant_result, relevant_result],
    )

    def fake_generation(prompt, _system_prompt):
        captured["prompt"] = prompt
        return "A fee-refund answer."

    monkeypatch.setattr(rag, "get_llm_response", fake_generation)

    response = rag.answer_question(
        "Can the college delay my fee refund?"
    )

    assert "sexual_harassment_2015.pdf" not in captured["prompt"]
    assert all(
        citation["source"].startswith("grievance_")
        for citation in response["citations"]
    )


def test_transient_llm_failure_returns_cited_source_excerpt(monkeypatch):
    result = {
        "score": 0.7,
        "text": "A student may appeal within fifteen days.",
        "metadata": {"source": "grievance_2023.pdf", "page": 12},
    }

    monkeypatch.setattr(rag, "search_documents", lambda *_args: [result])

    def fail_generation(*_args):
        raise LLMUnavailableError()

    monkeypatch.setattr(rag, "get_llm_response", fail_generation)

    response = rag.answer_question("When can I appeal?")

    assert "most relevant part of the UGC regulations" in response["answer"]
    assert "A student may appeal within fifteen days." in response["answer"]
    assert response["citations"] == [
        {
            "source": "grievance_2023.pdf",
            "page": 12,
            "url": rag.SOURCE_URLS["grievance_2023.pdf"],
        }
    ]
