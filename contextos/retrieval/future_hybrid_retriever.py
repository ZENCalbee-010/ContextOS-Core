"""Placeholder hybrid retriever for the future v2 retrieval architecture."""

from contextos.retrieval.base import RetrievalProviderUnavailable, RetrievalResult


class FutureHybridRetriever:
    """Reserved provider slot for future hybrid lexical plus semantic retrieval."""

    provider_name = "hybrid"

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        raise RetrievalProviderUnavailable(
            "Hybrid retrieval is not implemented. ContextOS Core currently uses BM25 only."
        )
