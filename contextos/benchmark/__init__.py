"""Benchmark utilities for ContextOS Core."""

from contextos.benchmark.benchmark_runner import (
    BenchmarkComparison,
    BenchmarkResult,
    BenchmarkRunner,
)
from contextos.benchmark.metrics import (
    TimedBlock,
    average_latency_ms,
    measure_elapsed,
    non_negative_latency_ms,
    validate_compression_ratio,
    validate_savings_percent,
)
from contextos.benchmark.report import (
    BenchmarkConfig,
    BenchmarkReport,
    StepMetric,
    generate_markdown_report,
)

__all__ = [
    "BenchmarkComparison",
    "BenchmarkConfig",
    "BenchmarkReport",
    "BenchmarkResult",
    "BenchmarkRunner",
    "StepMetric",
    "TimedBlock",
    "average_latency_ms",
    "generate_markdown_report",
    "measure_elapsed",
    "non_negative_latency_ms",
    "validate_compression_ratio",
    "validate_savings_percent",
]
