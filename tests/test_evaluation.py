from contextos.evaluation import (
    EvaluationRunner,
    average,
    compression_ratio,
    latency_ms,
    retrieval_precision_at_k,
    token_reduction_efficiency,
)
from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository


def test_metric_calculations():
    assert compression_ratio(100, 60) == 0.4
    assert compression_ratio(0, 60) == 0.0
    assert token_reduction_efficiency(200, 50) == 0.75
    assert retrieval_precision_at_k([1, 2, 3], {1, 3}, k=2) == 0.5
    assert latency_ms(1.0, 1.25) == 250.0
    assert average([1.0, 2.0, 3.0]) == 2.0
    assert average([]) == 0.0


def test_evaluation_runner_measures_retrieval(tmp_path):
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    chunks = repository.insert_chunks(
        document.id,
        [
            ChunkInput(0, "context selection matters", token_count=3),
            ChunkInput(1, "sqlite storage details", token_count=3),
        ],
    )

    evaluation = EvaluationRunner(repository).run_retrieval(
        "context selection",
        top_k=1,
        relevant_chunk_ids={chunks[0].id},
    )

    assert evaluation.query == "context selection"
    assert len(evaluation.results) == 1
    assert evaluation.latency_ms >= 0
    assert evaluation.precision_at_k == 1.0
