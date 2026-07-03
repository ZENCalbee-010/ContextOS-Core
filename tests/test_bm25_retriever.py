from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Retriever
from contextos.retrieval.bm25_retriever import tokenize


def make_repository(tmp_path):
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    return repository


def test_bm25_returns_top_k_chunks_with_scores(tmp_path):
    repository = make_repository(tmp_path)
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(0, "context selection improves context quality"),
            ChunkInput(1, "database migrations and sqlite schema"),
            ChunkInput(2, "context compression reduces extra context noise"),
        ],
    )

    results = BM25Retriever(repository).search("context selection", top_k=2)

    assert len(results) == 2
    assert results[0].chunk.content == "context selection improves context quality"
    assert results[0].score >= results[1].score
    assert all(result.score > 0 for result in results)


def test_bm25_returns_empty_for_no_chunks(tmp_path):
    repository = make_repository(tmp_path)

    results = BM25Retriever(repository).search("context", top_k=5)

    assert results == []


def test_bm25_returns_empty_for_blank_query(tmp_path):
    repository = make_repository(tmp_path)
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(document.id, [ChunkInput(0, "context selection")])

    results = BM25Retriever(repository).search("   ", top_k=5)

    assert results == []


def test_bm25_respects_top_k(tmp_path):
    repository = make_repository(tmp_path)
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(0, "alpha beta context"),
            ChunkInput(1, "alpha gamma context"),
            ChunkInput(2, "alpha delta context"),
        ],
    )

    results = BM25Retriever(repository).search("alpha context", top_k=1)

    assert len(results) == 1


def test_tokenize_lowercases_and_keeps_identifiers():
    assert tokenize("Build_Context uses SQLite3!") == [
        "build_context",
        "uses",
        "sqlite3",
    ]
