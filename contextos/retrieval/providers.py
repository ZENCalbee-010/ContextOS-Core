"""Factory helpers for optional retrieval providers."""

from typing import Literal

from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval.base import Retriever, RetrievalProviderUnavailable
from contextos.retrieval.bm25_retriever import BM25Retriever
from contextos.retrieval.future_embedding_retriever import FutureEmbeddingRetriever
from contextos.retrieval.future_hybrid_retriever import FutureHybridRetriever


RetrievalProviderName = Literal["bm25", "embedding", "hybrid"]


def get_retriever(
    provider: RetrievalProviderName,
    repository: SQLiteMemoryRepository,
) -> Retriever:
    """Return a retrieval provider without changing the active BM25 default."""
    if provider == "bm25":
        return BM25Retriever(repository)
    if provider == "embedding":
        return FutureEmbeddingRetriever()
    if provider == "hybrid":
        return FutureHybridRetriever()
    raise RetrievalProviderUnavailable(f"Unknown retrieval provider: {provider}")
