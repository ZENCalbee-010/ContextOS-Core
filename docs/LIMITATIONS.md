# ContextOS Core v1.0 Limitations

ContextOS Core v1.0 is intentionally small and local-first.

## BM25 Lexical Search

Retrieval uses BM25 lexical matching only. This works well when query terms overlap with document terms, but it does not understand semantic similarity. A query using different vocabulary from the source text may miss relevant chunks.

## No Embeddings Or Vector Database

Version 1.0 does not use embeddings, vector search, hybrid retrieval, FAISS, Chroma, Qdrant, or any other vector database. This is a deliberate scope choice to keep the MVP inspectable and local.

## SQLite Single-User Scope

SQLite is used as a local database for one user on one machine. ContextOS Core v1.0 is not designed for concurrent multi-user writes, hosted operation, tenant isolation, or cloud synchronization.

## AI Adapter Limitations

The Claude adapter validates environment configuration but is not a live API client yet. The OpenAI adapter is a placeholder. Use `--adapter mock` or `--dry-run` for local workflows that must avoid external calls.

## Compression Limitations

Compression is rule-based only. Light, medium, and aggressive modes do not use ML, embeddings, or LLM summarization. Output quality depends on document structure and simple text rules.
