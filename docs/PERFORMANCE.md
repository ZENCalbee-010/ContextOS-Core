# ContextOS Core Performance

ContextOS Core keeps the v1.x architecture unchanged: Typer CLI, SQLite local memory, BM25 lexical retrieval, and rule-based compression.

## Improvements

### Chunk Cache

`SQLiteMemoryRepository.get_all_chunks()` caches loaded chunk rows in memory and invalidates the cache after repository writes. This reduces repeated SQLite reads during search-heavy workflows while preserving the existing repository API.

### BM25 Index Cache

`BM25Retriever` now lazy-loads the BM25 index on first search and reuses it while the chunk signature remains unchanged. The cache is invalidated when the stored chunk count or max chunk id changes.

### Lazy Loading

Retrieval no longer builds a BM25 index when the retriever is constructed. Index creation happens only when `search()` is called.

### Memory Profiling

`contextos.performance.profile_memory()` wraps local workflows with `tracemalloc` and returns current and peak memory usage. This is intended for benchmarks and diagnostics, not for changing runtime behavior.

### Import Speed

Chunk insertion uses SQLite `executemany()` to reduce per-chunk insert overhead during import and re-import.

### Benchmark Comparison

`BenchmarkRunner` can compare baseline and current benchmark results and generate markdown comparison reports.

## Usage Example

```python
from contextos.benchmark import BenchmarkRunner

runner = BenchmarkRunner(db_path="data/benchmark.sqlite3")
search_before = runner.run_search_benchmark("context", iterations=5)
search_after = runner.run_search_benchmark("context", iterations=5)
comparison = runner.compare_results(search_before, search_after)

print(runner.generate_comparison_report([comparison]))
```

## Notes

- No embeddings or vector database are introduced.
- BM25 remains the only retrieval algorithm.
- SQLite remains the only database.
- Compression remains deterministic and rule-based.
- CLI behavior and public command options remain compatible.

## Current Limitations

- Caches are in-process only and are rebuilt for new CLI process invocations.
- BM25 cache invalidation is based on chunk table signature, not a persistent index file.
- Memory profiling is opt-in and intended for benchmark runs.
- Import speed still depends on reader/parser cost for large PDFs or DOCX files.
