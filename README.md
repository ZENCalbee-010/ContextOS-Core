# ContextOS Core v1.0

ContextOS Core is a local-first CLI-based AI Context Management System.

The main v1.0 principle is:

```text
Context Selection is more important than Compression.
```

ContextOS Core is not a web app or cloud platform. It uses a local SQLite database, BM25 lexical retrieval, rule-based compression, and a Typer CLI.

## Scope

Included in v1.0:

- CLI-first workflow using Typer
- SQLite local database
- Reader, parser, indexer, compression, memory pipeline
- BM25 retrieval only
- Token budget selection
- Prompt context building
- Claude adapter interface
- Mock adapter for tests and local dry workflows
- Rule-based compression only

Not included in v1.0:

- FastAPI
- PostgreSQL
- Docker
- Vector databases
- Embeddings
- Hybrid retrieval
- Multi-user cloud features

## Requirements

- Python 3.11+
- pip

## Setup

```powershell
cd "C:\Project\ContextOS Core\contextos"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For Claude usage, set an API key in your environment:

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
```

The current Claude adapter validates configuration but does not yet make live API calls. Use `--adapter mock` for local tests.

## CLI Commands

Show help:

```powershell
context --help
```

Import a file or folder recursively:

```powershell
context import .\docs --db-path .\data\contextos.sqlite3
```

Search imported chunks with BM25:

```powershell
context search "context selection" --top-k 5 --db-path .\data\contextos.sqlite3
```

Ask a question with selected context:

```powershell
context ask "What matters most?" --adapter mock --db-path .\data\contextos.sqlite3
```

Preview selected context without calling an adapter:

```powershell
context ask "What matters most?" --dry-run --db-path .\data\contextos.sqlite3
```

Re-run stored compression metadata for a document:

```powershell
context optimize .\docs\architecture.md --level aggressive --db-path .\data\contextos.sqlite3
```

Show workspace stats:

```powershell
context stats --db-path .\data\contextos.sqlite3
```

## Architecture

Indexing flow:

```text
Reader -> Parser -> Indexer -> Compression -> Memory
```

Question flow:

```text
Question -> BM25 Retriever -> Token Budget Selector -> Context Builder -> AI Adapter -> Response
```

## Tests

```powershell
pytest
```

## Current Limitations

- `ContextOS_Architecture.md` is not currently present in the repo.
- Claude and OpenAI adapters are not live API clients yet.
- Retrieval is intentionally BM25-only.
- Compression is intentionally rule-based only.
- SQLite schema migrations are not implemented yet.
- The system is single-user and local-first by design.
