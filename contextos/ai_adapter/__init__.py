"""Adapters for optional AI model integrations."""

from contextos.ai_adapter.base import (
    AIAdapterError,
    AIResponse,
    BaseAIAdapter,
    MissingAPIKeyError,
)
from contextos.ai_adapter.claude_adapter import ClaudeAdapter
from contextos.ai_adapter.mock_adapter import MockAdapter
from contextos.ai_adapter.openai_adapter import OpenAIAdapter

__all__ = [
    "AIAdapterError",
    "AIResponse",
    "BaseAIAdapter",
    "ClaudeAdapter",
    "MissingAPIKeyError",
    "MockAdapter",
    "OpenAIAdapter",
]
