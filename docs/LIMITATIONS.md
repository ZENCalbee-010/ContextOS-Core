# ContextOS Core Limitations

ContextOS Core is intentionally small, local-first, and complete at Level 2: Desktop App.

## Final Scope Boundary

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

## BM25 Lexical Search

Retrieval uses BM25 lexical matching only. This works well when query terms overlap with document terms, but it does not understand semantic similarity. A query using different vocabulary from the source text may miss relevant chunks.

## No Embeddings Or Vector Database

ContextOS does not use embeddings, vector search, hybrid retrieval, FAISS, Chroma, Qdrant, or any other vector database. This is a deliberate scope choice to keep the project inspectable and local.

## SQLite Single-User Scope

SQLite is used as a local database for one user on one machine. ContextOS Core is not designed for concurrent multi-user writes, hosted operation, tenant isolation, or cloud synchronization.

## AI Adapter Limitations

The Claude adapter validates environment configuration but is not a live API client yet. The OpenAI adapter is a placeholder. Use `--adapter mock` or `--dry-run` for local workflows that must avoid external calls.

## Compression Limitations

Compression is rule-based only. Light, medium, and aggressive modes do not use ML, embeddings, or LLM summarization. Output quality depends on document structure and simple text rules.

## Desktop Limitations

The desktop app is a GUI wrapper around the Python CLI. It is not a separate backend, cloud service, or agent runtime. Desktop imports use the current DropZone/path workflow, with path entry available as a reliable fallback when native OS drag/drop behavior varies by runtime.

## Benchmark Limitations

Benchmark reports measure local machine behavior. Latency varies by hardware, filesystem, Python environment, and whether the SQLite database already contains unchanged files.
