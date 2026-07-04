"""Memory profiling utilities for local ContextOS workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar
import tracemalloc


T = TypeVar("T")


@dataclass(frozen=True)
class MemoryProfile:
    current_bytes: int
    peak_bytes: int

    @property
    def current_kb(self) -> float:
        return self.current_bytes / 1024

    @property
    def peak_kb(self) -> float:
        return self.peak_bytes / 1024


def profile_memory(callback: Callable[[], T]) -> tuple[T, MemoryProfile]:
    """Run a callback under tracemalloc and return its result plus memory usage."""
    tracemalloc.start()
    try:
        result = callback()
        current, peak = tracemalloc.get_traced_memory()
        return result, MemoryProfile(current_bytes=current, peak_bytes=peak)
    finally:
        tracemalloc.stop()
