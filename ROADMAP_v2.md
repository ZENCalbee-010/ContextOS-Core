# ContextOS Core v2 Roadmap

## Product Principle

Context Selection is more important than Compression.

v2 should extend retrieval architecture without compromising the local-first, inspectable design.

## v2.0 Foundation

Status: started.

Included:

- Retrieval provider interface.
- BM25 active provider.
- Placeholder embedding provider.
- Placeholder hybrid provider.
- Provider factory.

Non-goals:

- No embeddings implementation.
- No vector database.
- No hybrid ranking.
- No cloud system.

## v2.1 Retrieval Provider Routing

Goals:

- Route `context search`, `context ask`, evaluation, and benchmark through the provider interface.
- Keep BM25 as default and only active provider.
- Make placeholder providers impossible to activate accidentally.

Deliverables:

- `retrieval.provider` setting.
- Backward-compatible config migration from `retrieval.algorithm`.
- Provider selection tests.

## v2.2 Query Understanding Without Embeddings

Goals:

- Improve lexical retrieval quality while staying BM25-only.

Possible features:

- Query normalization.
- Stopword handling.
- Field weighting for headings, filenames, and section names.
- Optional exact phrase boost.
- Better source metadata scoring.

Non-goals:

- Semantic embeddings.
- Vector search.

## v2.3 Persistent Retrieval Artifacts

Goals:

- Reduce cold-start retrieval cost for larger local corpora.

Possible features:

- Persist tokenized corpus metadata.
- Persist BM25 cache metadata.
- Detect invalidation through document/chunk signatures.

Constraints:

- SQLite only.
- No external search server.

## v2.4 Live AI Adapter Implementation

Goals:

- Implement Claude adapter as the primary live adapter.
- Keep mock adapter for tests.
- Keep OpenAI adapter optional.

Requirements:

- No hardcoded API keys.
- Redacted logs.
- Clear dry-run mode.
- Tests must not call external services.

## v2.5 Developer Experience and Packaging

Goals:

- Reliable installation and smoke tests across Windows, macOS, and Linux.
- Better debug and doctor diagnostics.
- Versioned docs aligned with tags.

Deliverables:

- Wheel/sdist CI.
- Windows CI.
- Release checklist.
- Updated docs per minor release.

## Long-Term Ideas

These are not commitments:

- Optional embedding provider.
- Optional hybrid provider.
- Optional local vector backend.
- UI layer.

Any of these should require a separate architecture decision record because they change the simplicity and inspectability of ContextOS Core.
