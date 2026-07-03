"""Evaluation metrics for ContextOS."""

from collections.abc import Iterable


def compression_ratio(original_length: int, compressed_length: int) -> float:
    if original_length <= 0:
        return 0.0
    return 1 - (compressed_length / original_length)


def retrieval_precision_at_k(
    retrieved_ids: Iterable[int],
    relevant_ids: set[int],
    *,
    k: int,
) -> float:
    if k <= 0:
        return 0.0

    top_ids = list(retrieved_ids)[:k]
    if not top_ids:
        return 0.0

    relevant_count = sum(1 for item_id in top_ids if item_id in relevant_ids)
    return relevant_count / min(k, len(top_ids))


def latency_ms(start_time: float, end_time: float) -> float:
    return max(0.0, (end_time - start_time) * 1000)


def token_reduction_efficiency(original_tokens: int, reduced_tokens: int) -> float:
    if original_tokens <= 0:
        return 0.0
    return 1 - (reduced_tokens / original_tokens)


def average(values: Iterable[float]) -> float:
    value_list = list(values)
    if not value_list:
        return 0.0
    return sum(value_list) / len(value_list)
