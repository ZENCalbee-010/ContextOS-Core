# Local Retrieval

ContextOS Core stores imported chunks in SQLite and retrieves relevant text with BM25 lexical search.

The v1.2 benchmark dataset is deterministic so import latency, search latency, and ask dry-run latency can be compared across releases.
