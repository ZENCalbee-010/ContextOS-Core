"""Search command backed by BM25 retrieval."""

from pathlib import Path

import typer

from contextos.config import DEFAULT_DB_PATH
from contextos.formatting import format_source, preview_text
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Retriever


def search_context(
    query: str = typer.Argument(..., help="Search query."),
    top_k: int = typer.Option(
        10,
        "--top-k",
        "--limit",
        "-n",
        help="Maximum number of results.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Search imported chunks using BM25."""

    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    results = BM25Retriever(repository).search(query, top_k=top_k)

    if not results:
        typer.echo("No results found.")
        return

    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        typer.echo(f"[Result {index}]")
        typer.echo(f"Score: {result.score:.4f}")
        typer.echo(f"Source: {format_source(chunk, repository)}")
        typer.echo(f"Preview: {preview_text(chunk.content)}")
        if index < len(results):
            typer.echo("")
