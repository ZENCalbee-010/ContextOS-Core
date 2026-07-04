from dataclasses import dataclass

import pytest

from contextos.token_budget import TokenBudgetSelector


@dataclass(frozen=True)
class FakeChunk:
    token_count: int
    content: str


@dataclass(frozen=True)
class FakeScoredChunk:
    chunk: FakeChunk
    score: float


def scored(content: str, token_count: int, score: float) -> FakeScoredChunk:
    return FakeScoredChunk(FakeChunk(token_count=token_count, content=content), score)


def test_selector_sorts_by_score_token_ratio():
    selector = TokenBudgetSelector(safety_margin=0)
    items = [
        scored("high score but expensive", 100, 50),
        scored("best ratio", 10, 10),
        scored("middle ratio", 20, 15),
    ]

    result = selector.select(items, max_tokens=200)

    assert [item.chunk.content for item in result.selected] == [
        "best ratio",
        "middle ratio",
        "high score but expensive",
    ]
    assert result.total_tokens == 130


def test_selector_prevents_budget_overflow_with_safety_margin():
    selector = TokenBudgetSelector(safety_margin=0.1)
    items = [
        scored("first", 50, 100),
        scored("second", 40, 80),
        scored("would overflow effective budget", 15, 1),
    ]

    result = selector.select(items, max_tokens=100)

    assert result.effective_budget == 90
    assert result.total_tokens == 90
    assert [item.chunk.content for item in result.selected] == ["first", "second"]
    assert result.total_tokens <= result.effective_budget


def test_selector_skips_single_chunk_larger_than_effective_budget():
    selector = TokenBudgetSelector(safety_margin=0.15)
    items = [
        scored("too large", 90, 1000),
        scored("fits", 40, 10),
    ]

    result = selector.select(items, max_tokens=100)

    assert result.effective_budget == 85
    assert [item.chunk.content for item in result.selected] == ["fits"]
    assert result.total_tokens == 40


def test_selector_supports_zero_token_chunks():
    selector = TokenBudgetSelector(safety_margin=0.1)

    result = selector.select([scored("metadata", 0, 1)], max_tokens=10)

    assert [item.chunk.content for item in result.selected] == ["metadata"]
    assert result.total_tokens == 0


def test_selector_rejects_invalid_safety_margin():
    with pytest.raises(ValueError, match="safety_margin"):
        TokenBudgetSelector(safety_margin=1)


def test_selector_rejects_negative_budget():
    selector = TokenBudgetSelector()

    with pytest.raises(ValueError, match="max_tokens"):
        selector.select([], max_tokens=-1)
