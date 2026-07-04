"""Token savings reporting utilities for ask flows."""

from dataclasses import dataclass

from contextos.memory.models import Chunk


@dataclass(frozen=True)
class TokenSavingsReport:
    """Summary of how many imported tokens were avoided by context selection."""

    total_available_tokens: int
    selected_context_tokens: int
    saved_tokens: int
    savings_percent: float

    def to_metadata(self) -> dict[str, int | float]:
        """Return JSON-safe metadata for conversation_history records."""
        return {
            "total_available_tokens": self.total_available_tokens,
            "selected_context_tokens": self.selected_context_tokens,
            "saved_tokens": self.saved_tokens,
            "savings_percent": self.savings_percent,
        }


def calculate_token_savings(
    all_chunks: list[Chunk],
    *,
    selected_context_tokens: int,
) -> TokenSavingsReport:
    """Calculate token savings from all available chunks versus selected context."""
    total_available_tokens = sum(max(chunk.token_count, 0) for chunk in all_chunks)
    selected_tokens = max(selected_context_tokens, 0)

    if total_available_tokens == 0:
        return TokenSavingsReport(
            total_available_tokens=0,
            selected_context_tokens=selected_tokens,
            saved_tokens=0,
            savings_percent=0,
        )

    saved_tokens = max(total_available_tokens - selected_tokens, 0)
    savings_percent = saved_tokens / total_available_tokens * 100
    return TokenSavingsReport(
        total_available_tokens=total_available_tokens,
        selected_context_tokens=selected_tokens,
        saved_tokens=saved_tokens,
        savings_percent=savings_percent,
    )


def format_token_savings_report(report: TokenSavingsReport) -> str:
    """Format token savings for CLI output."""
    return "\n".join(
        [
            "TOKEN SAVINGS REPORT",
            f"Total available tokens: {report.total_available_tokens}",
            f"Selected context tokens: {report.selected_context_tokens}",
            f"Saved tokens: {report.saved_tokens}",
            f"Savings percent: {report.savings_percent:.2f}%",
        ]
    )
