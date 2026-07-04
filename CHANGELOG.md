# Changelog

## Unreleased

### Added

- `context benchmark` command for local benchmark reports.
- Benchmark documentation in `docs/BENCHMARK.md`.
- Final Level 2 Desktop App scope documentation.
- Expanded benchmark sample notes for portfolio token savings demos.

### Changed

- README, roadmap, desktop docs, and limitations now mark VS Code extensions, browser extensions, plugin/API layers, cloud sync, multi-user systems, agent runtime, embeddings/vector DB, and semantic search as out of scope.

## v1.1.0

Release theme: Token Savings Report + Desktop App MVP.

### Added

- Token Savings Report for `context ask`.
- Token savings metadata stored in `conversation_history.metadata_json`.
- `context stats` now shows the latest token savings when available.
- Desktop app MVP under `apps/desktop` using React, TypeScript, and Tauri.
- Safe desktop subprocess bridge for approved ContextOS CLI commands only.
- Desktop panels for import, search, ask, optimize, stats, token savings, and command logs.
- Desktop UX workflow guide, empty states, loading states, command status display, and manual QA checklist.
- Desktop documentation in `docs/DESKTOP_APP.md`.

### Changed

- README and usage docs now cover token savings and desktop setup.
- Desktop command log now separates stdout, stderr, and exit code.
- Token savings output is parsed into the desktop `TokenSavingsPanel`.

### Scope Notes

- Python core remains CLI-first.
- Desktop app wraps the existing CLI; it does not replace or rewrite the core.
- BM25 remains the only active retrieval algorithm.
- No embeddings, vector database, cloud sync, or real AI API calls were added.

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
