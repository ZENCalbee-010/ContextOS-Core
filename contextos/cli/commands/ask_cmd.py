"""Ask command for retrieval-augmented local context prompts."""

from pathlib import Path
from typing import Literal

import typer

from contextos.ai_adapter import AIAdapterError, ClaudeAdapter, MockAdapter
from contextos.cli.output import safe_echo
from contextos.config import DEFAULT_DB_PATH, DEFAULT_TOKEN_BUDGET
from contextos.context_builder import ContextBuilder
from contextos.evaluation import EvaluationRunner
from contextos.formatting import format_source
from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.token_budget import TokenBudgetSelector


def ask_context(
    question: str = typer.Argument(..., help="Question to answer."),
    top_k: int = typer.Option(10, "--top-k", help="Number of retrieval candidates."),
    budget: int = typer.Option(
        DEFAULT_TOKEN_BUDGET,
        "--budget",
        "-b",
        help="Maximum context token budget.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show selected context without calling an AI adapter.",
    ),
    adapter_name: Literal["claude", "mock"] = typer.Option(
        "claude",
        "--adapter",
        help="AI adapter to use.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Answer a question using selected local context."""

    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()

    retrieval_evaluation = EvaluationRunner(repository).run_retrieval(
        question,
        top_k=top_k,
    )
    retrieval_results = retrieval_evaluation.results
    selection = TokenBudgetSelector().select(retrieval_results, max_tokens=budget)
    selected = selection.selected
    prompt = ContextBuilder(repository).build(question, selected)

    if dry_run:
        safe_echo("DRY RUN")
        safe_echo(f"Selected chunks: {len(selected)}")
        safe_echo(f"Tokens used: {selection.total_tokens}")
        safe_echo("")
        safe_echo(prompt)
        safe_echo("")
        _print_sources(repository, [item.chunk for item in selected])
        return

    adapter = _adapter(adapter_name)
    try:
        response = adapter.generate(prompt)
    except AIAdapterError as exc:
        raise typer.ClickException(str(exc)) from exc

    conversation_metadata = {
        "used_chunk_ids": [item.chunk.id for item in selected],
        "tokens_used": selection.total_tokens,
        "top_k": top_k,
        "budget": budget,
        "adapter": adapter.provider,
        "latency_ms": retrieval_evaluation.latency_ms,
    }
    repository.save_conversation("user", question, metadata=conversation_metadata)
    repository.save_conversation(
        "assistant",
        response.content,
        metadata=conversation_metadata,
    )

    typer.echo(response.content)
    typer.echo("")
    _print_sources(repository, [item.chunk for item in selected])


def _adapter(name: str):
    if name == "mock":
        return MockAdapter()
    return ClaudeAdapter()


def _print_sources(repository: SQLiteMemoryRepository, chunks: list[Chunk]) -> None:
    safe_echo("Sources:")
    if not chunks:
        safe_echo("- none")
        return
    for chunk in chunks:
        safe_echo(f"- {format_source(chunk, repository)}")
