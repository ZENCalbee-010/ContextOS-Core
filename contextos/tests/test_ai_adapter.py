import pytest

from contextos.ai_adapter import (
    AIAdapterError,
    AIResponse,
    BaseAIAdapter,
    ClaudeAdapter,
    MissingAPIKeyError,
    OpenAIAdapter,
)


class MockAIAdapter(BaseAIAdapter):
    provider = "mock"

    def __init__(self, response: str = "mock answer") -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> AIResponse:
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")
        self.prompts.append(prompt)
        return AIResponse(content=self.response, model="mock-model", provider=self.provider)


def test_mock_adapter_implements_strategy_contract():
    adapter = MockAIAdapter("Context is sufficient.")

    response = adapter.generate("SYSTEM:\nUse context.")

    assert response.content == "Context is sufficient."
    assert response.model == "mock-model"
    assert response.provider == "mock"
    assert adapter.prompts == ["SYSTEM:\nUse context."]


def test_mock_adapter_handles_empty_prompt():
    adapter = MockAIAdapter()

    with pytest.raises(AIAdapterError, match="Prompt cannot be empty"):
        adapter.generate("   ")


def test_claude_adapter_reads_api_key_from_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    adapter = ClaudeAdapter()

    assert adapter.api_key == "test-key"
    assert adapter.model == "claude-3-5-sonnet-latest"


def test_claude_adapter_errors_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    adapter = ClaudeAdapter()

    with pytest.raises(MissingAPIKeyError, match="ANTHROPIC_API_KEY"):
        adapter.generate("prompt")


def test_claude_adapter_reports_unimplemented_api_call(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    adapter = ClaudeAdapter()

    with pytest.raises(AIAdapterError, match="not implemented yet"):
        adapter.generate("prompt")


def test_openai_adapter_placeholder_errors_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    adapter = OpenAIAdapter()

    with pytest.raises(MissingAPIKeyError, match="OPENAI_API_KEY"):
        adapter.generate("prompt")


def test_openai_adapter_placeholder_reports_unimplemented_api_call(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    adapter = OpenAIAdapter()

    with pytest.raises(AIAdapterError, match="not implemented yet"):
        adapter.generate("prompt")
