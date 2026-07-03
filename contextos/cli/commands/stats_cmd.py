"""Stats command for the local ContextOS workspace."""

from pathlib import Path
import json

import typer

from contextos.config import DEFAULT_DB_PATH
from contextos.evaluation import average
from contextos.memory.db import connect
from contextos.memory.repository import SQLiteMemoryRepository


def stats_context(
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Show local workspace statistics."""

    stats = load_stats(db_path)

    typer.echo(f"Total documents: {stats['total_documents']}")
    typer.echo(f"Total chunks: {stats['total_chunks']}")
    typer.echo(f"Total original tokens: {stats['total_original_tokens']}")
    typer.echo(f"Average compression ratio: {stats['average_compression_ratio']:.4f}")
    latest_latency = stats["latest_query_latency_ms"]
    if latest_latency is None:
        typer.echo("Latest query latency: unavailable")
    else:
        typer.echo(f"Latest query latency: {latest_latency:.2f} ms")


def load_stats(db_path: str | Path) -> dict:
    SQLiteMemoryRepository(db_path).init_db()
    with connect(db_path) as connection:
        total_documents = connection.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]
        total_chunks = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        total_original_tokens = connection.execute(
            "SELECT COALESCE(SUM(token_count), 0) FROM chunks"
        ).fetchone()[0]
        chunk_metadata = [
            row[0]
            for row in connection.execute(
                "SELECT metadata_json FROM chunks WHERE metadata_json IS NOT NULL"
            ).fetchall()
        ]
        conversation_metadata = [
            row[0]
            for row in connection.execute(
                """
                SELECT metadata_json
                FROM conversation_history
                WHERE metadata_json IS NOT NULL
                ORDER BY id DESC
                """
            ).fetchall()
        ]

    return {
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "total_original_tokens": total_original_tokens,
        "average_compression_ratio": _average_compression_ratio(chunk_metadata),
        "latest_query_latency_ms": _latest_query_latency(conversation_metadata),
    }


def _average_compression_ratio(metadata_rows: list[str]) -> float:
    ratios: list[float] = []
    for metadata_json in metadata_rows:
        metadata = _decode(metadata_json)
        compression = metadata.get("compression", {})
        for variant in compression.values():
            if isinstance(variant, dict) and "compression_ratio" in variant:
                ratios.append(float(variant["compression_ratio"]))
    return average(ratios)


def _latest_query_latency(metadata_rows: list[str]) -> float | None:
    for metadata_json in metadata_rows:
        metadata = _decode(metadata_json)
        latency = metadata.get("latency_ms")
        if latency is not None:
            return float(latency)
    return None


def _decode(metadata_json: str) -> dict:
    try:
        value = json.loads(metadata_json)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
