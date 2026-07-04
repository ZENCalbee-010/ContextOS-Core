from contextos.benchmark import BenchmarkRunner


def test_benchmark_runner_generates_markdown_report(tmp_path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("# Context\n\nBM25 selects local context.", encoding="utf-8")
    runner = BenchmarkRunner(db_path=tmp_path / "benchmark.sqlite3")

    import_result = runner.run_import_benchmark([source])
    search_result = runner.run_search_benchmark("context", iterations=1)
    compression_result = runner.run_compression_benchmark(source.read_text(encoding="utf-8"), iterations=1)
    report = runner.generate_markdown_report([import_result, search_result, compression_result])
    report_path = runner.write_markdown_report([import_result], tmp_path / "report.md")

    assert import_result.name == "import"
    assert search_result.name == "search"
    assert compression_result.name == "compression"
    assert "# ContextOS Benchmark Report" in report
    assert "| import |" in report
    assert report_path.exists()
