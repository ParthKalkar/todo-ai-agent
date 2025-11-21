import os
import pytest


@pytest.fixture(autouse=True)
def no_openai_env(monkeypatch):
    """Ensure tests don't accidentally call the real OpenAI/LangChain by clearing the API key.

    Tests can opt-in to LLM behavior by setting OPENAI_API_KEY in the test itself.
    """
    # Ensure OPENAI_API_KEY is not set during tests by default
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    yield
