from pathlib import Path

from typer.testing import CliRunner

from contextos.cli.main import app


runner = CliRunner()


def test_benchmark_command_creates_markdown_report(tmp_path) -> None:
    output = tmp_path / "reports" / "benchmark.md"
    db_path = tmp_path / "benchmark.db"

    result = runner.invoke(
        app,
        [
            "benchmark",
            "--dataset",
            "sample_data/benchmark",
            "--db-path",
            str(db_path),
            "--output",
            str(output),
            "--query",
            "context selection",
            "--question",
            "How does ContextOS save tokens?",
            "--iterations",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert "Benchmark complete." in result.output
    assert f"Report: {output}" in result.output
    assert "Saved tokens:" in result.output
    assert output.exists()

    markdown = output.read_text(encoding="utf-8")
    assert "sample_data/benchmark" in markdown
    assert "context selection" in markdown
    assert "How does ContextOS save tokens?" in markdown
    assert "Saved tokens" in markdown
    assert "Savings percent" in markdown
    assert "Retrieval is BM25-only." in markdown
    assert "No embeddings or vector database are used." in markdown


def test_benchmark_command_rejects_invalid_dataset_path(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "benchmark",
            "--dataset",
            str(tmp_path / "missing"),
            "--db-path",
            str(tmp_path / "benchmark.db"),
        ],
    )

    assert result.exit_code != 0
    assert "Dataset path does not exist" in result.output


def test_benchmark_command_rejects_iterations_less_than_one(tmp_path) -> None:
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    (dataset / "notes.md").write_text("# Notes\n\nContext selection.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "benchmark",
            "--dataset",
            str(dataset),
            "--db-path",
            str(tmp_path / "benchmark.db"),
            "--iterations",
            "0",
        ],
    )

    assert result.exit_code != 0
    assert "--iterations must be >= 1" in result.output
