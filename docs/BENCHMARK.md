# ContextOS Benchmark

ContextOS Core v1.2 adds a local benchmark command for existing CLI/core flows.

The benchmark measures:

- Import latency
- BM25 search latency
- Ask dry-run latency
- Total tokens
- Selected context tokens
- Saved tokens
- Savings percent
- Rule-based compression ratio

It does not add embeddings, vector search, cloud services, or real AI API calls.

## Example

```powershell
context benchmark `
  --dataset sample_data/benchmark `
  --db-path data/benchmark.db `
  --output benchmark_report.md `
  --query "context selection" `
  --question "How does ContextOS save tokens?" `
  --iterations 3
```

Equivalent module form:

```powershell
python -m contextos.cli.main benchmark --dataset sample_data/benchmark --db-path data/benchmark.db --output benchmark_report.md
```

## Database Behavior

If `--db-path` already exists, the benchmark reuses it and relies on the existing incremental import behavior. Unchanged files may be skipped safely by SHA-256.

For a clean run, choose a new database path or remove the old benchmark database manually.

## Why Small Datasets May Show 0% Savings

Token savings compares all imported chunk tokens with the selected context tokens for one ask dry-run.

Small datasets can show `0.00%` savings when every imported chunk fits inside the ask token budget. That is expected and still correct: ContextOS did not need to discard any chunks.

To demonstrate visible savings in a portfolio run, use the default `sample_data/benchmark` dataset after the portfolio benchmark notes are included, or use a larger local folder. Once the total imported tokens exceed the selected context budget or the retriever returns fewer chunks than the full corpus, saved tokens become visible.

## Report

The generated Markdown report includes:

- Benchmark configuration
- Summary table
- Per-step metrics
- Token savings section
- Compression section
- Scope notes
- Limitations

Scope notes always include:

- BM25-only retrieval
- SQLite local-first storage
- No embeddings or vector database
- No cloud service
- No real AI adapter call during ask dry-run
