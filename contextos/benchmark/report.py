"""Benchmark report structures and Markdown generation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from contextos.benchmark.metrics import (
    non_negative_latency_ms,
    validate_compression_ratio,
    validate_savings_percent,
)


@dataclass(frozen=True)
class BenchmarkConfig:
    """Configuration used to run a local benchmark."""

    dataset_path: str
    db_path: str
    query: str
    question: str
    iterations: int
    timestamp: str


@dataclass(frozen=True)
class StepMetric:
    """Metric for one benchmark step."""

    name: str
    latency_ms: float
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "latency_ms",
            non_negative_latency_ms(self.latency_ms),
        )


@dataclass(frozen=True)
class BenchmarkReport:
    """Full benchmark result ready for Markdown rendering."""

    config: BenchmarkConfig
    import_latency_ms: float
    search_latency_ms: float
    ask_dry_run_latency_ms: float
    total_tokens: int
    selected_context_tokens: int
    saved_tokens: int
    savings_percent: float
    compression_ratio: float
    notes: list[str] = field(default_factory=list)
    step_metrics: list[StepMetric] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "import_latency_ms",
            non_negative_latency_ms(self.import_latency_ms),
        )
        object.__setattr__(
            self,
            "search_latency_ms",
            non_negative_latency_ms(self.search_latency_ms),
        )
        object.__setattr__(
            self,
            "ask_dry_run_latency_ms",
            non_negative_latency_ms(self.ask_dry_run_latency_ms),
        )
        object.__setattr__(
            self,
            "savings_percent",
            validate_savings_percent(self.savings_percent),
        )
        object.__setattr__(
            self,
            "compression_ratio",
            validate_compression_ratio(self.compression_ratio),
        )

    def to_markdown(self) -> str:
        """Render the benchmark report as Markdown."""
        return generate_markdown_report(self)

    def write_markdown(self, output_path: str | Path) -> Path:
        """Write the Markdown report to disk."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")
        return path


def generate_markdown_report(report: BenchmarkReport) -> str:
    """Generate a Markdown benchmark report."""
    lines = [
        "# ContextOS Benchmark Report",
        "",
        f"Generated: {report.config.timestamp}",
        "",
        "## Benchmark Configuration",
        "",
        f"- Dataset path: `{report.config.dataset_path}`",
        f"- Database path: `{report.config.db_path}`",
        f"- Query: `{report.config.query}`",
        f"- Question: `{report.config.question}`",
        f"- Iterations: {report.config.iterations}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Import latency | {report.import_latency_ms:.2f} ms |",
        f"| Search latency | {report.search_latency_ms:.2f} ms |",
        f"| Ask dry-run latency | {report.ask_dry_run_latency_ms:.2f} ms |",
        f"| Total tokens | {report.total_tokens} |",
        f"| Selected context tokens | {report.selected_context_tokens} |",
        f"| Saved tokens | {report.saved_tokens} |",
        f"| Savings percent | {report.savings_percent:.2f}% |",
        f"| Compression ratio | {report.compression_ratio:.4f} |",
        "",
        "## Per-Step Metrics",
        "",
        "| Step | Latency ms | Notes |",
        "| --- | ---: | --- |",
    ]

    for step in report.step_metrics:
        lines.append(
            f"| {step.name} | {step.latency_ms:.2f} | {_escape_table_text(step.notes)} |"
        )

    if not report.step_metrics:
        lines.append("| No step metrics recorded | 0.00 | unavailable |")

    lines.extend(
        [
            "",
            "## Token Savings",
            "",
            f"- Total available tokens: {report.total_tokens}",
            f"- Selected context tokens: {report.selected_context_tokens}",
            f"- Saved tokens: {report.saved_tokens}",
            f"- Savings percent: {report.savings_percent:.2f}%",
            "",
            "## Compression",
            "",
            f"- Rule-based compression ratio: {report.compression_ratio:.4f}",
            "",
            "## Scope Notes",
            "",
            "- Retrieval is BM25-only.",
            "- Storage is SQLite local-first.",
            "- No embeddings or vector database are used.",
            "- No cloud service is required.",
            "- Ask dry-run does not call a real AI adapter.",
            "",
            "## Limitations",
            "",
            "- Benchmarks are local machine measurements and vary by hardware.",
            "- The sample dataset is intentionally small and deterministic.",
            "- Results measure existing ContextOS flows without changing retrieval or compression behavior.",
        ]
    )

    if report.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in report.notes)

    return "\n".join(lines) + "\n"


def _escape_table_text(value: str) -> str:
    return value.replace("|", "\\|") if value else ""
