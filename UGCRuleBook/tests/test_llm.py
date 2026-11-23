import pytest
from google.genai.errors import APIError

from backend import llm


def test_transient_provider_error_uses_bounded_retry_and_timeout(monkeypatch):
    settings = {}

    class FakeModels:
        def generate_content(self, **_kwargs):
            raise APIError(503, {"error": {"message": "busy"}})

    class FakeClient:
        def __init__(self, *, api_key, http_options):
            assert api_key == "test-key"
            settings["timeout"] = http_options.timeout
            settings["attempts"] = http_options.retry_options.attempts
            self.models = FakeModels()

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(llm.genai, "Client", FakeClient)

    with pytest.raises(llm.LLMUnavailableError):
        llm.get_llm_response("test prompt")

    assert settings == {"timeout": 30_000, "attempts": 2}


def test_invalid_provider_request_is_a_configuration_error(monkeypatch):
    class FakeModels:
        def generate_content(self, **_kwargs):
            raise APIError(400, {"error": {"message": "invalid model"}})

    class FakeClient:
        def __init__(self, **_kwargs):
            self.models = FakeModels()

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(llm.genai, "Client", FakeClient)

    with pytest.raises(llm.LLMProviderError):
        llm.get_llm_response("test prompt")
