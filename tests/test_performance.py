from contextos.benchmark import BenchmarkRunner
from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.performance import MemoryProfile, profile_memory
from contextos.retrieval import BM25Retriever


def test_repository_chunk_cache_reuses_until_write(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/cache.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [ChunkInput(chunk_index=0, content="cached context", token_count=2)],
    )

    first = repository.get_all_chunks()
    second = repository.get_all_chunks()

    assert first == second
    assert repository._all_chunks_cache is not None

    repository.insert_chunks(
        document.id,
        [ChunkInput(chunk_index=0, content="updated cached context", token_count=3)],
    )

    updated = repository.get_all_chunks()

    assert updated[0].content == "updated cached context"


def test_bm25_retriever_caches_index_and_invalidates_on_chunk_change(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/retrieval.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [ChunkInput(chunk_index=0, content="alpha context", token_count=2)],
    )
    retriever = BM25Retriever(repository)

    first = retriever.search("alpha", top_k=1)
    cached_signature = retriever._index_signature
    second = retriever.search("alpha", top_k=1)

    assert first[0].chunk.content == "alpha context"
    assert second[0].chunk.content == "alpha context"
    assert retriever._index_signature == cached_signature

    repository.insert_chunks(
        document.id,
        [ChunkInput(chunk_index=0, content="beta context", token_count=2)],
    )
    updated = retriever.search("beta", top_k=1)

    assert updated[0].chunk.content == "beta context"
    assert retriever._index_signature != cached_signature


def test_memory_profile_reports_peak_usage() -> None:
    result, profile = profile_memory(lambda: ["context"] * 10)

    assert result == ["context"] * 10
    assert isinstance(profile, MemoryProfile)
    assert profile.peak_bytes >= profile.current_bytes


def test_benchmark_comparison_report(tmp_path) -> None:
    runner = BenchmarkRunner(db_path=tmp_path / "benchmark.sqlite3")
    baseline = runner.run_search_benchmark("context", iterations=1)
    current = runner.run_search_benchmark("context", iterations=1)

    comparison = runner.compare_results(baseline, current)
    report = runner.generate_comparison_report([comparison])

    assert comparison.name == "search"
    assert "# ContextOS Benchmark Comparison" in report
    assert "| search |" in report
