"""Placeholder embedding retriever for the future v2 retrieval architecture."""

from contextos.retrieval.base import RetrievalProviderUnavailable, RetrievalResult


class FutureEmbeddingRetriever:
    """Reserved provider slot for future embedding retrieval."""

    provider_name = "embedding"

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        raise RetrievalProviderUnavailable(
            "Embedding retrieval is not implemented. ContextOS Core currently uses BM25 only."
        )
