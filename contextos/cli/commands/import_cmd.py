"""Import command for local ContextOS files."""

from pathlib import Path

import typer

from contextos.config import DEFAULT_DB_PATH
from contextos.indexer import FileIndexer, IndexResult
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.readers import get_reader


def import_context(
    path: Path = typer.Argument(
        Path("."),
        help="File or directory to import.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
    max_tokens: int = typer.Option(
        400,
        "--max-tokens",
        help="Maximum tokens per parsed chunk.",
    ),
) -> None:
    """Import a file or folder into the local SQLite memory store."""

    if not path.exists():
        raise typer.BadParameter(f"path does not exist: {path}")

    files = list(_iter_supported_files(path))
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    indexer = FileIndexer(repository, max_tokens_per_chunk=max_tokens)

    results = [indexer.index_file(file_path) for file_path in files]
    imported = _count(results, "imported")
    skipped = _count(results, "skipped")
    total_chunks = sum(result.chunk_count for result in results)
    total_tokens = sum(result.token_count for result in results)

    typer.echo(f"Imported files: {imported}")
    typer.echo(f"Skipped files: {skipped}")
    typer.echo(f"Total chunks: {total_chunks}")
    typer.echo(f"Total tokens: {total_tokens}")


def _iter_supported_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if get_reader(path) is not None else []

    return [
        file_path
        for file_path in sorted(path.rglob("*"))
        if file_path.is_file() and get_reader(file_path) is not None
    ]


def _count(results: list[IndexResult], status: str) -> int:
    return sum(1 for result in results if result.status == status)
