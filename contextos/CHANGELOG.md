# Changelog

## v1.0.0

Initial ContextOS Core MVP.

### Added

- Typer CLI entrypoint: `context`
- SQLite memory layer with repository pattern
- Reader strategy layer for PDF, DOCX, text, Markdown, and source code files
- Parser layer for text, Markdown headings, and simple code structure
- Incremental importer with SHA-256 unchanged-file detection
- Rule-based compression levels: light, medium, aggressive
- BM25-only retrieval using `rank-bm25`
- Token budget selector with safety margin
- Context builder for final prompt assembly
- AI adapter strategy layer with Claude, OpenAI placeholder, and mock adapter
- CLI commands: `import`, `search`, `ask`, `optimize`, `stats`
- Local pipeline integration test covering import, search, dry-run ask, optimize, and stats

### Scope Notes

- No FastAPI
- No PostgreSQL
- No Docker
- No embeddings
- No vector database
- No multi-user cloud system
