"""Small benchmark framework for local ContextOS workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import statistics
import tempfile
import time

from contextos.compression import AggressiveCompressor, LightCompressor, MediumCompressor
from contextos.indexer import FileIndexer
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.performance import MemoryProfile, profile_memory
from contextos.retrieval import BM25Retriever


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    iterations: int
    total_ms: float
    average_ms: float
    metadata: dict[str, float | int | str]


@dataclass(frozen=True)
class BenchmarkComparison:
    name: str
    baseline_average_ms: float
    current_average_ms: float
    delta_ms: float
    improvement_percent: float


class BenchmarkRunner:
    """Run local import, search, compression, and latency benchmarks."""

    def __init__(self, *, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else Path(tempfile.mkdtemp()) / "benchmark.sqlite3"
        self.repository = SQLiteMemoryRepository(self.db_path)
        self.repository.init_db()

    def run_import_benchmark(
        self,
        paths: list[str | Path],
        *,
        iterations: int = 1,
        max_tokens_per_chunk: int = 400,
    ) -> BenchmarkResult:
        durations: list[float] = []
        imported = 0
        skipped = 0
        total_chunks = 0

        for _ in range(iterations):
            indexer = FileIndexer(self.repository, max_tokens_per_chunk=max_tokens_per_chunk)
            start = time.perf_counter()
            results = [indexer.index_file(path) for path in paths]
            durations.append(_elapsed_ms(start))
            imported += sum(1 for result in results if result.status == "imported")
            skipped += sum(1 for result in results if result.status == "skipped")
            total_chunks += sum(result.chunk_count for result in results)

        return _result(
            "import",
            iterations,
            durations,
            {
                "files": len(paths),
                "imported": imported,
                "skipped": skipped,
                "chunks": total_chunks,
            },
        )

    def run_search_benchmark(
        self,
        query: str,
        *,
        top_k: int = 5,
        iterations: int = 5,
    ) -> BenchmarkResult:
        durations: list[float] = []
        result_count = 0
        retriever = BM25Retriever(self.repository)

        for _ in range(iterations):
            start = time.perf_counter()
            results = retriever.search(query, top_k=top_k)
            durations.append(_elapsed_ms(start))
            result_count = len(results)

        return _result(
            "search",
            iterations,
            durations,
            {"top_k": top_k, "results": result_count},
        )

    def run_compression_benchmark(
        self,
        text: str,
        *,
        iterations: int = 5,
    ) -> BenchmarkResult:
        compressors = (LightCompressor(), MediumCompressor(), AggressiveCompressor())
        durations: list[float] = []
        ratios: list[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            for compressor in compressors:
                ratios.append(compressor.compress(text).compression_ratio)
            durations.append(_elapsed_ms(start))

        return _result(
            "compression",
            iterations,
            durations,
            {
                "strategies": len(compressors),
                "average_ratio": statistics.fmean(ratios) if ratios else 0.0,
            },
        )

    def run_latency_benchmark(
        self,
        query: str,
        *,
        iterations: int = 10,
    ) -> BenchmarkResult:
        return self.run_search_benchmark(query, top_k=5, iterations=iterations)

    def profile_search_memory(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> tuple[list[object], MemoryProfile]:
        retriever = BM25Retriever(self.repository)
        return profile_memory(lambda: retriever.search(query, top_k=top_k))

    def compare_results(
        self,
        baseline: BenchmarkResult,
        current: BenchmarkResult,
    ) -> BenchmarkComparison:
        delta_ms = current.average_ms - baseline.average_ms
        improvement = (
            ((baseline.average_ms - current.average_ms) / baseline.average_ms) * 100
            if baseline.average_ms
            else 0.0
        )
        return BenchmarkComparison(
            name=current.name,
            baseline_average_ms=baseline.average_ms,
            current_average_ms=current.average_ms,
            delta_ms=delta_ms,
            improvement_percent=improvement,
        )

    def generate_markdown_report(self, results: list[BenchmarkResult]) -> str:
        lines = [
            "# ContextOS Benchmark Report",
            "",
            "| Benchmark | Iterations | Total ms | Average ms | Metadata |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
        for result in results:
            metadata = ", ".join(f"{key}={value}" for key, value in result.metadata.items())
            lines.append(
                f"| {result.name} | {result.iterations} | "
                f"{result.total_ms:.2f} | {result.average_ms:.2f} | {metadata} |"
            )
        return "\n".join(lines) + "\n"

    def generate_comparison_report(self, comparisons: list[BenchmarkComparison]) -> str:
        lines = [
            "# ContextOS Benchmark Comparison",
            "",
            "| Benchmark | Baseline avg ms | Current avg ms | Delta ms | Improvement |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for comparison in comparisons:
            lines.append(
                f"| {comparison.name} | {comparison.baseline_average_ms:.2f} | "
                f"{comparison.current_average_ms:.2f} | {comparison.delta_ms:.2f} | "
                f"{comparison.improvement_percent:.2f}% |"
            )
        return "\n".join(lines) + "\n"

    def write_markdown_report(
        self,
        results: list[BenchmarkResult],
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_markdown_report(results), encoding="utf-8")
        return path


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000


def _result(
    name: str,
    iterations: int,
    durations: list[float],
    metadata: dict[str, float | int | str],
) -> BenchmarkResult:
    total_ms = sum(durations)
    average_ms = total_ms / iterations if iterations else 0.0
    return BenchmarkResult(
        name=name,
        iterations=iterations,
        total_ms=total_ms,
        average_ms=average_ms,
        metadata=metadata,
    )
