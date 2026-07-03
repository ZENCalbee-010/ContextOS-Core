"""OpenAI AI adapter placeholder."""

import os

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter, MissingAPIKeyError


class OpenAIAdapter(BaseAIAdapter):
    """Placeholder OpenAI adapter configured through environment variables."""

    provider = "openai"

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        model: str = "gpt-4.1-mini",
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = os.getenv(api_key_env)
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        if not self.api_key:
            raise MissingAPIKeyError(
                f"Missing OpenAI API key. Set {self.api_key_env} in the environment."
            )
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")

        raise AIAdapterError(
            "OpenAI API calls are not implemented yet. Wire an OpenAI client before using this adapter."
        )
