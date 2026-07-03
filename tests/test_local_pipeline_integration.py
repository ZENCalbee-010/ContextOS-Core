import sqlite3

from typer.testing import CliRunner

from contextos.cli.main import app


runner = CliRunner()


def test_full_local_pipeline_uses_one_sqlite_db_and_no_ai_call(tmp_path):
    db_path = tmp_path / "contextos.sqlite3"
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    architecture_path = docs_dir / "architecture.md"
    code_path = docs_dir / "builder.py"
    architecture_path.write_text(
        "# Context Selection\n\n"
        "Context selection is more important than compression.\n\n"
        "- BM25 retrieval ranks local chunks.\n",
        encoding="utf-8",
    )
    code_path.write_text(
        "class ContextBuilder:\n"
        "    def build(self):\n"
        "        return 'prompt'\n",
        encoding="utf-8",
    )

    import_result = runner.invoke(
        app,
        ["import", str(docs_dir), "--db-path", str(db_path), "--max-tokens", "50"],
    )
    search_result = runner.invoke(
        app,
        ["search", "context selection", "--top-k", "2", "--db-path", str(db_path)],
    )
    ask_result = runner.invoke(
        app,
        [
            "ask",
            "What is more important than compression?",
            "--dry-run",
            "--adapter",
            "mock",
            "--db-path",
            str(db_path),
        ],
    )
    optimize_result = runner.invoke(
        app,
        [
            "optimize",
            str(architecture_path),
            "--level",
            "medium",
            "--db-path",
            str(db_path),
        ],
    )
    stats_result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert import_result.exit_code == 0
    assert "Imported files: 2" in import_result.output
    assert db_path.exists()

    assert search_result.exit_code == 0
    assert "[Result 1]" in search_result.output
    assert "Score:" in search_result.output
    assert str(architecture_path) in search_result.output

    assert ask_result.exit_code == 0
    assert "DRY RUN" in ask_result.output
    assert "SYSTEM:" in ask_result.output
    assert "CONTEXT:" in ask_result.output
    assert "Mock response generated" not in ask_result.output

    assert optimize_result.exit_code == 0
    assert f"Document: {architecture_path}" in optimize_result.output
    assert "Compression level: medium" in optimize_result.output
    assert "Compression ratio:" in optimize_result.output

    assert stats_result.exit_code == 0
    assert "Total documents: 2" in stats_result.output
    assert "Total chunks:" in stats_result.output

    with sqlite3.connect(db_path) as connection:
        conversation_count = connection.execute(
            "SELECT COUNT(*) FROM conversation_history"
        ).fetchone()[0]
        document_count = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    assert conversation_count == 0
    assert document_count == 2
