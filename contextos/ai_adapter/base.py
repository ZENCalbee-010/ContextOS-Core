"""Base interfaces for AI model adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class AIAdapterError(RuntimeError):
    """Raised when an AI adapter cannot complete a request."""


class MissingAPIKeyError(AIAdapterError):
    """Raised when an adapter requires an API key that is not configured."""


@dataclass(frozen=True)
class AIResponse:
    content: str
    model: str
    provider: str


class BaseAIAdapter(ABC):
    """Strategy interface for optional AI model providers."""

    provider: str

    @abstractmethod
    def generate(self, prompt: str) -> AIResponse:
        """Generate an answer for a completed context prompt."""
