from typer.testing import CliRunner
import json
import sqlite3

from contextos.cli.main import app
from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository


runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ContextOS Core" in result.output


def test_optimize_help_describes_compression_metadata() -> None:
    result = runner.invoke(app, ["optimize", "--help"])

    assert result.exit_code == 0
    assert "Optimize stored compression metadata for a document." in result.output


def test_search_command_prints_bm25_results(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/architecture.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="Context selection is more important than compression.",
                token_count=7,
                metadata={"section": "Principle", "start_line": 4, "end_line": 6},
            ),
            ChunkInput(
                chunk_index=1,
                content="SQLite stores local memory chunks.",
                token_count=5,
                metadata={"section": "Storage", "start_line": 10, "end_line": 10},
            ),
        ],
    )

    result = runner.invoke(
        app,
        ["search", "selection", "--top-k", "1", "--db-path", str(db_path)],
    )

    assert result.exit_code == 0
    assert "[Result 1]" in result.output
    assert "Score:" in result.output
    assert "Source: docs/architecture.md, Principle, lines 4-6" in result.output
    assert "Preview: Context selection is more important than compression." in result.output
    assert "[Result 2]" not in result.output


def test_search_command_prints_no_results_for_empty_db(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"

    result = runner.invoke(
        app,
        ["search", "architecture", "--db-path", str(db_path)],
    )

    assert result.exit_code == 0
    assert "No results found." in result.output


def test_import_command_imports_supported_files_recursively(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    docs_dir = tmp_path / "docs"
    nested_dir = docs_dir / "nested"
    nested_dir.mkdir(parents=True)
    notes_path = docs_dir / "notes.md"
    code_path = nested_dir / "app.py"
    unsupported_path = nested_dir / "archive.zip"
    notes_path.write_text("# Context\n\nSelection matters.", encoding="utf-8")
    code_path.write_text("def build_context():\n    return 'ok'\n", encoding="utf-8")
    unsupported_path.write_bytes(b"ignored")

    result = runner.invoke(
        app,
        [
            "import",
            str(docs_dir),
            "--db-path",
            str(db_path),
            "--max-tokens",
            "50",
        ],
    )
    repository = SQLiteMemoryRepository(db_path)
    notes_document = repository.get_document_by_path(notes_path)
    code_document = repository.get_document_by_path(code_path)
    chunks = repository.get_all_chunks()

    assert result.exit_code == 0
    assert "Imported files: 2" in result.output
    assert "Skipped files: 0" in result.output
    assert "Total chunks: 2" in result.output
    assert notes_document is not None
    assert code_document is not None
    assert len(chunks) == 2
    assert chunks[0].metadata["compression"]["light"]["content"]
    assert chunks[0].metadata["compression"]["medium"]["content"]
    assert chunks[0].metadata["compression"]["aggressive"]["content"]


def test_import_command_skips_unchanged_files(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    notes_path = tmp_path / "notes.txt"
    notes_path.write_text("stable context selection", encoding="utf-8")

    first = runner.invoke(app, ["import", str(notes_path), "--db-path", str(db_path)])
    second = runner.invoke(app, ["import", str(notes_path), "--db-path", str(db_path)])

    assert first.exit_code == 0
    assert "Imported files: 1" in first.output
    assert second.exit_code == 0
    assert "Imported files: 0" in second.output
    assert "Skipped files: 1" in second.output
    assert "Total chunks: 1" in second.output


def test_optimize_command_updates_chunk_compression_metadata(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content=(
                    "# Heading\n\n"
                    "- Keep this bullet\n\n"
                    "Context selection matters. Extra detail can go."
                ),
                token_count=10,
                metadata={"compression": {"aggressive": {"content": "old"}}},
            )
        ],
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            "docs/context.md",
            "--level",
            "aggressive",
            "--db-path",
            str(db_path),
        ],
    )
    updated_chunk = repository.get_chunks_by_document(document.id)[0]
    aggressive = updated_chunk.metadata["compression"]["aggressive"]

    assert result.exit_code == 0
    assert "Document: docs/context.md" in result.output
    assert "Compression level: aggressive" in result.output
    assert "Chunks optimized: 1" in result.output
    assert "Tokens before: 10" in result.output
    assert aggressive["content"] != "old"
    assert "# Heading" in aggressive["content"]
    assert "- Keep this bullet" in aggressive["content"]
    assert aggressive["compressed_tokens"] <= aggressive["original_tokens"]


def test_ask_command_uses_mock_adapter_and_saves_conversation(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="Context selection should happen before compression.",
                token_count=7,
                metadata={"section": "Principle", "start_line": 1, "end_line": 2},
            ),
            ChunkInput(
                chunk_index=1,
                content="Unrelated storage notes.",
                token_count=3,
                metadata={"section": "Storage"},
            ),
        ],
    )

    result = runner.invoke(
        app,
        [
            "ask",
            "What should happen before compression?",
            "--adapter",
            "mock",
            "--top-k",
            "2",
            "--budget",
            "20",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    assert "Mock response generated from selected context." in result.output
    assert "TOKEN SAVINGS REPORT" in result.output
    assert "Total available tokens: 10" in result.output
    assert "Selected context tokens: 10" in result.output
    assert "Saved tokens: 0" in result.output
    assert "Savings percent: 0.00%" in result.output
    assert "Sources:" in result.output
    assert "docs/context.md, Principle, lines 1-2" in result.output

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT role, content, metadata_json FROM conversation_history ORDER BY id"
        ).fetchall()

    assert len(rows) == 2
    assert rows[0][0] == "user"
    assert rows[0][1] == "What should happen before compression?"
    assert rows[1][0] == "assistant"
    assert rows[1][1] == "Mock response generated from selected context."
    assert '"tokens_used":' in rows[0][2]
    assert '"used_chunk_ids":' in rows[0][2]
    assert '"adapter": "mock"' in rows[0][2]
    assert '"latency_ms":' in rows[0][2]
    metadata = json.loads(rows[0][2])
    assert metadata["token_savings"] == {
        "total_available_tokens": 10,
        "selected_context_tokens": 10,
        "saved_tokens": 0,
        "savings_percent": 0.0,
    }
    assert rows[0][2] == rows[1][2]


def test_ask_command_dry_run_shows_prompt_without_saving_conversation(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="BM25 retrieval selects local chunks.",
                token_count=5,
                metadata={"section": "Retrieval"},
            )
        ],
    )

    result = runner.invoke(
        app,
        [
            "ask",
            "What selects local chunks?",
            "--dry-run",
            "--adapter",
            "mock",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    assert "DRY RUN" in result.output
    assert "TOKEN SAVINGS REPORT" in result.output
    assert "Total available tokens: 5" in result.output
    assert "Selected context tokens: 5" in result.output
    assert "Saved tokens: 0" in result.output
    assert "Savings percent: 0.00%" in result.output
    assert "SYSTEM:" in result.output
    assert "CONTEXT:" in result.output
    assert "QUESTION:" in result.output
    assert "BM25 retrieval selects local chunks." in result.output
    assert "Mock response generated" not in result.output

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM conversation_history"
        ).fetchone()[0]

    assert count == 0


def test_ask_dry_run_handles_bom_and_unicode_without_persistence(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/unicode.md", "hash-1")
    unicode_content = "\ufeffBM25 retrieval keeps cafe context and Thai text: สวัสดี"
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content=unicode_content,
                token_count=8,
                metadata={"section": "Unicode"},
            )
        ],
    )

    result = runner.invoke(
        app,
        [
            "ask",
            "What keeps cafe context?",
            "--dry-run",
            "--adapter",
            "mock",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    assert "DRY RUN" in result.output
    assert "BM25 retrieval keeps cafe context" in result.output

    stored_chunk = repository.get_chunks_by_document(document.id)[0]
    assert stored_chunk.content == unicode_content

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM conversation_history"
        ).fetchone()[0]

    assert count == 0


def test_stats_command_shows_workspace_metrics(tmp_path) -> None:
    db_path = tmp_path / "contextos.sqlite3"
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="Context selection matters.",
                token_count=3,
                metadata={
                    "compression": {
                        "light": {"compression_ratio": 0.1},
                        "medium": {"compression_ratio": 0.4},
                    }
                },
            ),
            ChunkInput(
                chunk_index=1,
                content="Compression helps fit budgets.",
                token_count=4,
                metadata={
                    "compression": {
                        "light": {"compression_ratio": 0.2},
                        "medium": {"compression_ratio": 0.5},
                    }
                },
            ),
        ],
    )
    repository.save_conversation(
        "user",
        "What matters?",
        metadata={
            "latency_ms": 12.345,
            "tokens_used": 7,
            "token_savings": {
                "total_available_tokens": 7,
                "selected_context_tokens": 3,
                "saved_tokens": 4,
                "savings_percent": 57.14285714285714,
            },
        },
    )

    result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Total documents: 1" in result.output
    assert "Total chunks: 2" in result.output
    assert "Total original tokens: 7" in result.output
    assert "Average compression ratio: 0.3000" in result.output
    assert "Latest query latency: 12.35 ms" in result.output
    assert "Latest token savings: 4 tokens (57.14%)" in result.output


def test_stats_command_handles_empty_workspace(tmp_path) -> None:
    db_path = tmp_path / "empty.sqlite3"

    result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Total documents: 0" in result.output
    assert "Total chunks: 0" in result.output
    assert "Total original tokens: 0" in result.output
    assert "Average compression ratio: 0.0000" in result.output
    assert "Latest query latency: unavailable" in result.output
    assert "Latest token savings: unavailable" in result.output
