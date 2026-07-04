"""Benchmark command for local ContextOS workflows."""

from datetime import datetime, timezone
from pathlib import Path
import statistics

import typer

from contextos.benchmark import BenchmarkConfig, BenchmarkReport, StepMetric
from contextos.benchmark.metrics import measure_elapsed
from contextos.compression import AggressiveCompressor, LightCompressor, MediumCompressor
from contextos.config import DEFAULT_TOKEN_BUDGET
from contextos.context_builder import ContextBuilder
from contextos.indexer import FileIndexer
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Retriever
from contextos.token_budget import TokenBudgetSelector, calculate_token_savings


def benchmark_context(
    dataset: Path = typer.Option(
        Path("sample_data/benchmark"),
        "--dataset",
        help="Benchmark dataset file or folder.",
    ),
    db_path: Path = typer.Option(
        Path("data/benchmark.db"),
        "--db-path",
        help="SQLite database path. Existing data may be reused and updated safely.",
    ),
    output: Path = typer.Option(
        Path("benchmark_report.md"),
        "--output",
        help="Markdown report output path.",
    ),
    query: str = typer.Option(
        "context selection",
        "--query",
        help="BM25 search query.",
    ),
    question: str = typer.Option(
        "How does ContextOS save tokens?",
        "--question",
        help="Ask dry-run benchmark question.",
    ),
    iterations: int = typer.Option(
        3,
        "--iterations",
        help="Number of search and ask dry-run iterations.",
    ),
) -> None:
    """Run a local benchmark and generate a Markdown report."""
    if not dataset.exists():
        _fail(f"Dataset path does not exist: {dataset}")
    if iterations < 1:
        _fail("--iterations must be >= 1")

    paths = _dataset_files(dataset)
    if not paths:
        _fail(f"No supported benchmark files found: {dataset}")

    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()

    import_latency_ms = _run_import(repository, paths)
    search_latency_ms = _run_search(repository, query, iterations)
    ask_latency_ms, selected_context_tokens = _run_ask_dry_run(
        repository,
        question,
        iterations,
    )

    chunks = repository.get_all_chunks()
    total_tokens = sum(max(chunk.token_count, 0) for chunk in chunks)
    token_savings = calculate_token_savings(
        chunks,
        selected_context_tokens=selected_context_tokens,
    )
    compression_ratio = _average_compression_ratio(chunks)

    report = BenchmarkReport(
        config=BenchmarkConfig(
            dataset_path=_display_path(dataset),
            db_path=_display_path(db_path),
            query=query,
            question=question,
            iterations=iterations,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
        import_latency_ms=import_latency_ms,
        search_latency_ms=search_latency_ms,
        ask_dry_run_latency_ms=ask_latency_ms,
        total_tokens=total_tokens,
        selected_context_tokens=token_savings.selected_context_tokens,
        saved_tokens=token_savings.saved_tokens,
        savings_percent=token_savings.savings_percent,
        compression_ratio=compression_ratio,
        notes=[
            "Existing SQLite data is reused when the database already exists.",
            "Ask benchmark builds the dry-run prompt only and does not call an AI adapter.",
        ],
        step_metrics=[
            StepMetric("import", import_latency_ms, f"Indexed {len(paths)} files."),
            StepMetric("search", search_latency_ms, "BM25 search over imported chunks."),
            StepMetric("ask dry-run", ask_latency_ms, "Built selected context prompt only."),
        ],
    )
    report_path = report.write_markdown(output)

    typer.echo("Benchmark complete.")
    typer.echo(f"Report: {report_path}")
    typer.echo(f"Import latency: {report.import_latency_ms:.2f} ms")
    typer.echo(f"Search latency: {report.search_latency_ms:.2f} ms")
    typer.echo(f"Ask dry-run latency: {report.ask_dry_run_latency_ms:.2f} ms")
    typer.echo(f"Total tokens: {report.total_tokens}")
    typer.echo(f"Selected context tokens: {report.selected_context_tokens}")
    typer.echo(f"Saved tokens: {report.saved_tokens}")
    typer.echo(f"Savings percent: {report.savings_percent:.2f}%")
    typer.echo(f"Compression ratio: {report.compression_ratio:.4f}")


def _dataset_files(dataset: Path) -> list[Path]:
    if dataset.is_file():
        return [dataset]
    return sorted(
        path
        for path in dataset.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".py", ".js", ".ts", ".html", ".css", ".json", ".pdf", ".docx"}
    )


def _display_path(path: Path) -> str:
    return path.as_posix()


def _fail(message: str) -> None:
    typer.echo(message)
    raise typer.Exit(code=1)


def _run_import(repository: SQLiteMemoryRepository, paths: list[Path]) -> float:
    indexer = FileIndexer(repository)
    with measure_elapsed() as timing:
        for path in paths:
            indexer.index_file(path)
    return timing.elapsed_ms


def _run_search(repository: SQLiteMemoryRepository, query: str, iterations: int) -> float:
    retriever = BM25Retriever(repository)
    latencies: list[float] = []
    for _ in range(iterations):
        with measure_elapsed() as timing:
            retriever.search(query, top_k=10)
        latencies.append(timing.elapsed_ms)
    return statistics.fmean(latencies) if latencies else 0.0


def _run_ask_dry_run(
    repository: SQLiteMemoryRepository,
    question: str,
    iterations: int,
) -> tuple[float, int]:
    retriever = BM25Retriever(repository)
    selector = TokenBudgetSelector()
    builder = ContextBuilder(repository)
    latencies: list[float] = []
    selected_context_tokens = 0

    for _ in range(iterations):
        with measure_elapsed() as timing:
            results = retriever.search(question, top_k=10)
            selection = selector.select(results, max_tokens=DEFAULT_TOKEN_BUDGET)
            builder.build(question, selection.selected)
        latencies.append(timing.elapsed_ms)
        selected_context_tokens = selection.total_tokens

    return (statistics.fmean(latencies) if latencies else 0.0), selected_context_tokens


def _average_compression_ratio(chunks) -> float:
    ratios: list[float] = []
    for chunk in chunks:
        metadata = chunk.metadata or {}
        compression = metadata.get("compression", {})
        if not isinstance(compression, dict):
            continue
        for variant in compression.values():
            if isinstance(variant, dict) and "compression_ratio" in variant:
                ratios.append(float(variant["compression_ratio"]))
    return statistics.fmean(ratios) if ratios else 0.0
