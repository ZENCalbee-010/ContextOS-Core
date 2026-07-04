from contextos.memory.models import Chunk
from contextos.token_budget import calculate_token_savings, format_token_savings_report


def chunk(token_count: int) -> Chunk:
    return Chunk(
        id=1,
        document_id=1,
        chunk_index=0,
        content="content",
        token_count=token_count,
    )


def test_calculate_token_savings_compares_all_chunks_to_selected_tokens() -> None:
    report = calculate_token_savings(
        [chunk(10_000), chunk(2_500)],
        selected_context_tokens=1_850,
    )

    assert report.total_available_tokens == 12_500
    assert report.selected_context_tokens == 1_850
    assert report.saved_tokens == 10_650
    assert report.savings_percent == 85.2
    assert report.to_metadata() == {
        "total_available_tokens": 12_500,
        "selected_context_tokens": 1_850,
        "saved_tokens": 10_650,
        "savings_percent": 85.2,
    }


def test_calculate_token_savings_handles_empty_workspace() -> None:
    report = calculate_token_savings([], selected_context_tokens=100)

    assert report.total_available_tokens == 0
    assert report.selected_context_tokens == 100
    assert report.saved_tokens == 0
    assert report.savings_percent == 0


def test_format_token_savings_report() -> None:
    report = calculate_token_savings(
        [chunk(12_500)],
        selected_context_tokens=1_850,
    )

    assert format_token_savings_report(report) == (
        "TOKEN SAVINGS REPORT\n"
        "Total available tokens: 12500\n"
        "Selected context tokens: 1850\n"
        "Saved tokens: 10650\n"
        "Savings percent: 85.20%"
    )
