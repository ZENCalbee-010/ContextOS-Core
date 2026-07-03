"""Greedy token budget selection for scored chunks."""

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar


class ChunkLike(Protocol):
    token_count: int


class ScoredChunkLike(Protocol):
    chunk: ChunkLike
    score: float


T = TypeVar("T", bound=ScoredChunkLike)


@dataclass(frozen=True)
class TokenBudgetSelection(Generic[T]):
    selected: list[T]
    total_tokens: int
    max_tokens: int
    effective_budget: int
    safety_margin: float


class TokenBudgetSelector:
    """Select highest score-per-token chunks under a token budget."""

    def __init__(self, *, safety_margin: float = 0.12) -> None:
        if safety_margin < 0 or safety_margin >= 1:
            raise ValueError("safety_margin must be >= 0 and < 1")
        self.safety_margin = safety_margin

    def select(self, scored_chunks: list[T], *, max_tokens: int) -> TokenBudgetSelection[T]:
        if max_tokens < 0:
            raise ValueError("max_tokens must be >= 0")

        effective_budget = int(max_tokens * (1 - self.safety_margin))
        selected: list[T] = []
        total_tokens = 0

        for item in sorted(scored_chunks, key=self._score_per_token, reverse=True):
            token_count = max(item.chunk.token_count, 0)
            if token_count == 0:
                selected.append(item)
                continue
            if total_tokens + token_count > effective_budget:
                continue
            selected.append(item)
            total_tokens += token_count

        return TokenBudgetSelection(
            selected=selected,
            total_tokens=total_tokens,
            max_tokens=max_tokens,
            effective_budget=effective_budget,
            safety_margin=self.safety_margin,
        )

    def _score_per_token(self, item: ScoredChunkLike) -> float:
        token_count = max(item.chunk.token_count, 1)
        return item.score / token_count
