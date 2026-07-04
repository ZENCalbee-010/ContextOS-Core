# ContextOS Core Roadmap

ContextOS Core follows one product principle:

```text
Context Selection is more important than Compression.
```

## Final Product Boundary

ContextOS Core ends at **Level 2: Desktop App**.

The project is a portfolio-ready local-first context management system, not a platform expansion project.

In scope:

- CLI Core Engine
- Desktop App
- Drag and drop files/folders
- Import, search, ask dry-run/mock, stats, benchmark
- Token Savings Report
- Local-first SQLite
- BM25 retrieval
- Rule-based compression

Out of scope:

- VS Code extension
- Browser extension
- Plugin/API layer
- Cloud sync
- Multi-user system
- Agent runtime
- Embeddings or vector database
- Semantic search

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
- Benchmark command and Markdown performance report
- Desktop MVP wrapper around the CLI

## Final Polish Priorities

1. Keep documentation aligned with the Level 2 boundary
2. Improve desktop drag/drop ergonomics
3. Add screenshots for README and desktop docs
4. Keep Python and desktop smoke tests passing
5. Preserve local-first SQLite and BM25-only behavior

## Retrieval Direction

Retrieval remains BM25-only. Placeholder retrieval providers may exist in code for architecture clarity, but embeddings, vector search, semantic search, and hybrid ranking are out of scope for this project.

## Out of Scope

- FastAPI or hosted backend
- PostgreSQL
- Docker runtime dependency
- Vector databases
- Embeddings
- Semantic search
- Multi-user cloud features
- VS Code extension
- Browser extension
- Plugin/API layer
- Agent runtime
