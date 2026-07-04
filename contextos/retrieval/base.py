"""Retriever interfaces for ContextOS Core v2 retrieval providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from contextos.exceptions import RetrievalError
from contextos.memory.models import Chunk


@dataclass(frozen=True)
class RetrievalResult:
    """Generic scored chunk result returned by retrieval providers."""

    chunk: Chunk
    score: float


class Retriever(Protocol):
    """Interface implemented by all retrieval providers."""

    provider_name: str

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        """Return top-k scored chunks for a query."""


class RetrievalProviderUnavailable(RetrievalError, NotImplementedError):
    """Raised when a future retrieval provider is requested before implementation."""
