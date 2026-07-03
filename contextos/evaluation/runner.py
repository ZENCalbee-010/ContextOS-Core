"""Evaluation runner utilities."""

from dataclasses import dataclass
from time import perf_counter

from contextos.evaluation.metrics import latency_ms, retrieval_precision_at_k
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Result, BM25Retriever


@dataclass(frozen=True)
class RetrievalEvaluation:
    query: str
    results: list[BM25Result]
    latency_ms: float
    precision_at_k: float | None = None


class EvaluationRunner:
    """Run lightweight local retrieval evaluations."""

    def __init__(self, repository: SQLiteMemoryRepository) -> None:
        self.repository = repository

    def run_retrieval(
        self,
        query: str,
        *,
        top_k: int = 5,
        relevant_chunk_ids: set[int] | None = None,
    ) -> RetrievalEvaluation:
        start = perf_counter()
        results = BM25Retriever(self.repository).search(query, top_k=top_k)
        end = perf_counter()

        precision = None
        if relevant_chunk_ids is not None:
            precision = retrieval_precision_at_k(
                [result.chunk.id for result in results],
                relevant_chunk_ids,
                k=top_k,
            )

        return RetrievalEvaluation(
            query=query,
            results=results,
            latency_ms=latency_ms(start, end),
            precision_at_k=precision,
        )
