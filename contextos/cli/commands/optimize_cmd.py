"""Optimize stored chunk compression metadata."""

from pathlib import Path
from typing import Literal
import re

import typer

from contextos.compression import (
    AggressiveCompressor,
    BaseCompressor,
    LightCompressor,
    MediumCompressor,
)
from contextos.config import DEFAULT_DB_PATH
from contextos.memory.models import Document
from contextos.memory.repository import SQLiteMemoryRepository


CompressionLevel = Literal["light", "medium", "aggressive"]


def optimize_context(
    target: str = typer.Argument(
        ...,
        help="Document id or filepath to optimize.",
    ),
    level: CompressionLevel = typer.Option(
        "light",
        "--level",
        "-l",
        help="Compression level to re-run.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Re-run a rule-based compression level for one document's chunks."""

    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = _resolve_document(repository, target)
    if document is None:
        raise typer.BadParameter(f"document not found: {target}")

    chunks = repository.get_chunks_by_document(document.id)
    compressor = _compressor(level)
    before_tokens = sum(chunk.token_count for chunk in chunks)
    after_tokens = 0
    ratios: list[float] = []

    for chunk in chunks:
        result = compressor.compress(chunk.content)
        compressed_tokens = _count_tokens(result.compressed)
        after_tokens += compressed_tokens
        ratios.append(result.compression_ratio)
        metadata = dict(chunk.metadata or {})
        compression = dict(metadata.get("compression") or {})
        compression[level] = {
            "content": result.compressed,
            "compression_ratio": result.compression_ratio,
            "original_length": result.original_length,
            "compressed_length": result.compressed_length,
            "original_tokens": chunk.token_count,
            "compressed_tokens": compressed_tokens,
        }
        metadata["compression"] = compression
        repository.update_chunk_metadata(chunk.id, metadata)

    average_ratio = sum(ratios) / len(ratios) if ratios else 0.0
    token_reduction = 1 - (after_tokens / before_tokens) if before_tokens else 0.0

    typer.echo(f"Document: {document.filepath}")
    typer.echo(f"Compression level: {level}")
    typer.echo(f"Chunks optimized: {len(chunks)}")
    typer.echo(f"Tokens before: {before_tokens}")
    typer.echo(f"Tokens after: {after_tokens}")
    typer.echo(f"Token reduction: {token_reduction:.4f}")
    typer.echo(f"Compression ratio: {average_ratio:.4f}")
    typer.echo(f"Average compression ratio: {average_ratio:.4f}")


def _resolve_document(
    repository: SQLiteMemoryRepository,
    target: str,
) -> Document | None:
    if target.isdigit():
        return repository.get_document_by_id(int(target))
    return repository.get_document_by_path(target)


def _compressor(level: CompressionLevel) -> BaseCompressor:
    if level == "light":
        return LightCompressor()
    if level == "medium":
        return MediumCompressor()
    return AggressiveCompressor()


def _count_tokens(text: str) -> int:
    return len(re.findall(r"\S+", text))
