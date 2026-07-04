# ContextOS Benchmark Report

Generated: 2026-07-04T18:32:16.926939+00:00

## Benchmark Configuration

- Dataset path: `sample_data/benchmark`
- Database path: `data/benchmark_final.db`
- Query: `context selection`
- Question: `How does ContextOS save tokens?`
- Iterations: 3

## Summary

| Metric | Value |
| --- | ---: |
| Import latency | 106.77 ms |
| Search latency | 3.85 ms |
| Ask dry-run latency | 22.06 ms |
| Total tokens | 689 |
| Selected context tokens | 389 |
| Saved tokens | 300 |
| Savings percent | 43.54% |
| Compression ratio | 0.2877 |

## Per-Step Metrics

| Step | Latency ms | Notes |
| --- | ---: | --- |
| import | 106.77 | Indexed 4 files. |
| search | 3.85 | BM25 search over imported chunks. |
| ask dry-run | 22.06 | Built selected context prompt only. |

## Token Savings

- Total available tokens: 689
- Selected context tokens: 389
- Saved tokens: 300
- Savings percent: 43.54%

## Compression

- Rule-based compression ratio: 0.2877

## Scope Notes

- Retrieval is BM25-only.
- Storage is SQLite local-first.
- No embeddings or vector database are used.
- No cloud service is required.
- Ask dry-run does not call a real AI adapter.

## Limitations

- Benchmarks are local machine measurements and vary by hardware.
- The sample dataset is intentionally small and deterministic.
- Results measure existing ContextOS flows without changing retrieval or compression behavior.

## Notes

- Existing SQLite data is reused when the database already exists.
- Ask benchmark builds the dry-run prompt only and does not call an AI adapter.
