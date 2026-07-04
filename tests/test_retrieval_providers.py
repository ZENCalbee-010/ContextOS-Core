import pytest

from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import (
    BM25Retriever,
    FutureEmbeddingRetriever,
    FutureHybridRetriever,
    RetrievalProviderUnavailable,
    get_retriever,
)
from contextos.retrieval.base import RetrievalResult


def make_repository(tmp_path) -> SQLiteMemoryRepository:
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/retrieval.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="BM25 remains the active retrieval provider.",
                token_count=6,
            )
        ],
    )
    return repository


def test_bm25_retriever_implements_provider_contract(tmp_path) -> None:
    repository = make_repository(tmp_path)
    retriever = BM25Retriever(repository)

    results = retriever.search("active retrieval", top_k=1)

    assert retriever.provider_name == "bm25"
    assert isinstance(results[0], RetrievalResult)
    assert "BM25 remains" in results[0].chunk.content


def test_retriever_factory_returns_active_bm25_provider(tmp_path) -> None:
    repository = make_repository(tmp_path)
    retriever = get_retriever("bm25", repository)

    assert isinstance(retriever, BM25Retriever)
    assert retriever.search("BM25", top_k=1)


def test_future_embedding_retriever_is_placeholder_only() -> None:
    retriever = FutureEmbeddingRetriever()

    with pytest.raises(RetrievalProviderUnavailable, match="not implemented"):
        retriever.search("semantic query")


def test_future_hybrid_retriever_is_placeholder_only() -> None:
    retriever = FutureHybridRetriever()

    with pytest.raises(RetrievalProviderUnavailable, match="not implemented"):
        retriever.search("hybrid query")


def test_retriever_factory_exposes_placeholders_without_activating_them(tmp_path) -> None:
    repository = make_repository(tmp_path)

    assert isinstance(get_retriever("embedding", repository), FutureEmbeddingRetriever)
    assert isinstance(get_retriever("hybrid", repository), FutureHybridRetriever)
