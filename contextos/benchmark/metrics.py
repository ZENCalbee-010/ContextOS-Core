"""Reusable benchmark metric helpers."""

from collections.abc import Iterable
from contextlib import contextmanager
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class TimedBlock:
    """Measured elapsed time for a benchmark operation."""

    elapsed_ms: float


@contextmanager
def measure_elapsed() -> Iterable[TimedBlock]:
    """Measure elapsed wall-clock time in milliseconds."""
    start = time.perf_counter()
    block = TimedBlock(elapsed_ms=0.0)
    try:
        yield block
    finally:
        object.__setattr__(
            block,
            "elapsed_ms",
            non_negative_latency_ms((time.perf_counter() - start) * 1000),
        )


def non_negative_latency_ms(value: float) -> float:
    """Clamp latency values to a non-negative float."""
    return max(float(value), 0.0)


def average_latency_ms(values: Iterable[float]) -> float:
    """Return a safe average latency for zero or more measurements."""
    latencies = [non_negative_latency_ms(value) for value in values]
    if not latencies:
        return 0.0
    return sum(latencies) / len(latencies)


def validate_savings_percent(value: float) -> float:
    """Clamp token savings percentage into the display-safe range."""
    return min(max(float(value), 0.0), 100.0)


def validate_compression_ratio(value: float) -> float:
    """Clamp compression ratio into the expected 0.0 to 1.0 range."""
    return min(max(float(value), 0.0), 1.0)
