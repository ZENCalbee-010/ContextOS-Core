# ContextOS Core Roadmap

ContextOS Core follows one product principle:

```text
Context Selection is more important than Compression.
```

## Current Foundation

- Local-first Typer CLI
- SQLite memory layer
- File readers and parsers
- Incremental import
- BM25 lexical retrieval
- Rule-based compression
- Token budget selection
- Context builder
- Mock AI adapter for local tests
- Claude/OpenAI adapter placeholders
- Developer commands: `doctor`, `version`, `config`, `debug`
- v2 retrieval provider foundation with BM25 active and future placeholders

## Near-Term Priorities

1. Documentation and release alignment
2. CLI output consolidation
3. Retrieval provider routing while keeping BM25 active
4. Packaging checks for wheel/sdist
5. Windows CI for CLI behavior

## v2 Retrieval Direction

See [ROADMAP_v2.md](ROADMAP_v2.md) for the detailed retrieval roadmap.

Important: v2 retrieval foundation does not implement embeddings, vector search, or hybrid ranking yet.

## Out of Scope Unless Reapproved

- FastAPI
- PostgreSQL
- Docker runtime dependency
- Vector databases
- Embeddings
- Multi-user cloud features
