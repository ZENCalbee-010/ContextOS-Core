"""Claude AI adapter."""

import os

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter, MissingAPIKeyError


class ClaudeAdapter(BaseAIAdapter):
    """Claude adapter configured through environment variables."""

    provider = "claude"

    def __init__(
        self,
        *,
        api_key_env: str = "ANTHROPIC_API_KEY",
        model: str = "claude-3-5-sonnet-latest",
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = os.getenv(api_key_env)
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        if not self.api_key:
            raise MissingAPIKeyError(
                f"Missing Claude API key. Set {self.api_key_env} in the environment."
            )
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")

        raise AIAdapterError(
            "Claude API calls are not implemented yet. Install and wire an Anthropic client before using this adapter."
        )
