from contextos.benchmark import (
    BenchmarkConfig,
    BenchmarkReport,
    StepMetric,
    average_latency_ms,
    generate_markdown_report,
    non_negative_latency_ms,
    validate_compression_ratio,
    validate_savings_percent,
)


def make_report() -> BenchmarkReport:
    return BenchmarkReport(
        config=BenchmarkConfig(
            dataset_path="sample_data/benchmark",
            db_path="data/benchmark.sqlite3",
            query="context selection",
            question="What does ContextOS measure?",
            iterations=3,
            timestamp="2026-07-05T12:00:00",
        ),
        import_latency_ms=12.5,
        search_latency_ms=3.25,
        ask_dry_run_latency_ms=8.75,
        total_tokens=12500,
        selected_context_tokens=1850,
        saved_tokens=10650,
        savings_percent=85.2,
        compression_ratio=0.42,
        notes=["Local benchmark fixture."],
        step_metrics=[
            StepMetric("import", 12.5, "Imported sample benchmark dataset."),
            StepMetric("search", 3.25, "BM25 search over SQLite chunks."),
            StepMetric("ask dry-run", 8.75, "No real AI adapter call."),
        ],
    )


def test_markdown_report_includes_dataset_path_query_and_question() -> None:
    markdown = generate_markdown_report(make_report())

    assert "sample_data/benchmark" in markdown
    assert "context selection" in markdown
    assert "What does ContextOS measure?" in markdown


def test_markdown_report_includes_metrics_table() -> None:
    markdown = make_report().to_markdown()

    assert "| Metric | Value |" in markdown
    assert "| Import latency | 12.50 ms |" in markdown
    assert "| Search latency | 3.25 ms |" in markdown
    assert "| Ask dry-run latency | 8.75 ms |" in markdown
    assert "| Step | Latency ms | Notes |" in markdown


def test_markdown_report_displays_token_savings_values() -> None:
    markdown = make_report().to_markdown()

    assert "Total available tokens: 12500" in markdown
    assert "Selected context tokens: 1850" in markdown
    assert "Saved tokens: 10650" in markdown
    assert "Savings percent: 85.20%" in markdown


def test_markdown_report_mentions_scope_notes() -> None:
    markdown = make_report().to_markdown()

    assert "Retrieval is BM25-only." in markdown
    assert "No embeddings or vector database are used." in markdown
    assert "Storage is SQLite local-first." in markdown


def test_metric_helpers_clamp_latency_savings_and_compression_bounds() -> None:
    assert non_negative_latency_ms(-1.5) == 0.0
    assert average_latency_ms([10, -5, 20]) == 10.0
    assert validate_savings_percent(-1) == 0.0
    assert validate_savings_percent(125) == 100.0
    assert validate_compression_ratio(-0.5) == 0.0
    assert validate_compression_ratio(2.0) == 1.0


def test_report_clamps_negative_latency_and_includes_compression_ratio() -> None:
    report = BenchmarkReport(
        config=BenchmarkConfig(
            dataset_path="sample_data/benchmark",
            db_path="data/benchmark.sqlite3",
            query="context",
            question="What is measured?",
            iterations=1,
            timestamp="2026-07-05T12:00:00",
        ),
        import_latency_ms=-10,
        search_latency_ms=-1,
        ask_dry_run_latency_ms=-5,
        total_tokens=10,
        selected_context_tokens=4,
        saved_tokens=6,
        savings_percent=60,
        compression_ratio=1.5,
    )
    markdown = report.to_markdown()

    assert report.import_latency_ms == 0.0
    assert report.search_latency_ms == 0.0
    assert report.ask_dry_run_latency_ms == 0.0
    assert report.compression_ratio == 1.0
    assert "| Compression ratio | 1.0000 |" in markdown
