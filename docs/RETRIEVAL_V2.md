# ContextOS Core v2 Retrieval Foundation

ContextOS Core v2 prepares an optional retrieval-provider architecture while keeping BM25 as the only active provider.

## Active Provider

- `BM25Retriever`
- Lexical retrieval with `rank-bm25`
- Uses SQLite chunks through the existing repository layer

## Prepared Provider Slots

- `FutureEmbeddingRetriever`
- `FutureHybridRetriever`

These classes are placeholders. They intentionally raise `RetrievalProviderUnavailable` when used.

## Explicit Non-Goals

- No embeddings are generated.
- No vector database is implemented.
- No hybrid ranking is implemented.
- BM25 is not removed or replaced.

## Interface

Retrieval providers implement:

```python
search(query: str, *, top_k: int = 5) -> list[RetrievalResult]
```

Provider construction is available through:

```python
get_retriever("bm25", repository)
```

Only `"bm25"` is production-active.
