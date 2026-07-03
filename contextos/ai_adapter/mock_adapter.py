"""Mock AI adapter for tests and local dry workflows."""

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter


class MockAdapter(BaseAIAdapter):
    provider = "mock"

    def __init__(self, response: str = "Mock response generated from selected context.") -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> AIResponse:
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")
        self.prompts.append(prompt)
        return AIResponse(content=self.response, model="mock-model", provider=self.provider)
