# ContextOS Core v1.0 Architecture

ContextOS Core is a local-first AI Context Management System. Version 1.0 is a CLI-first, single-user system focused on selecting the right context before attempting compression.

## Principle

```text
Context Selection is more important than Compression.
```

## Scope

ContextOS Core v1.0 includes:

- Typer CLI
- SQLite local database
- Local file readers
- Text and code parsers
- Incremental indexing with SHA-256 file hashes
- BM25 lexical retrieval only
- Token budget selection
- Rule-based compression only
- Prompt context building
- Claude adapter interface
- Mock adapter for tests and dry local workflows

ContextOS Core v1.0 excludes:

- FastAPI
- PostgreSQL
- Docker
- Vector databases
- Embeddings
- Hybrid retrieval
- Multi-user cloud features

## Core Flows

Indexing flow:

```text
Reader -> Parser -> Indexer -> Compression -> Memory
```

Question flow:

```text
Question -> BM25 Retriever -> Token Budget Selector -> Context Builder -> AI Adapter -> Response
```

## Components

### CLI

The CLI is implemented with Typer and exposed as the `context` command.

Primary commands:

- `context import <path>`
- `context search <query>`
- `context ask <question>`
- `context optimize <document-id-or-filepath>`
- `context stats`

### Readers

Readers use the Strategy Pattern. A detector chooses a reader by file extension.

Supported readers:

- PDF via PyMuPDF
- DOCX via python-docx
- text and Markdown
- source code files

### Parsers

Parsers split raw text into chunks with metadata:

- content
- chunk index
- token count
- optional page number
- optional start/end line
- optional section

Markdown headings and simple code functions/classes are detected without tree-sitter in v1.0.

### Indexer

The indexer computes SHA-256 hashes, skips unchanged files, parses changed files, creates chunk metadata, and stores rule-based compressed variants.

### Compression

Compression is rule-based only:

- light: whitespace cleanup and optional code comment removal
- medium: Luhn-style word-frequency extractive summarization
- aggressive: preserve headings, bullet points, signatures, and first paragraph sentences

### Memory

SQLite is accessed through a repository layer. The schema includes:

- documents
- chunks
- summaries
- conversation_history

Foreign keys are enabled, and indexes support document and chunk lookup.

### Retrieval

Retrieval is BM25-only using `rank-bm25`. No embeddings, TF-IDF, vector DB, or hybrid retrieval are used in v1.0.

### Token Budget

The token budget selector greedily selects scored chunks under an effective budget with a safety margin.

### Context Builder

The context builder renders selected chunks into a final prompt with:

- SYSTEM
- CONTEXT
- QUESTION
- INSTRUCTIONS

### AI Adapters

AI adapters use the Strategy Pattern. Claude is the primary adapter interface. OpenAI is optional and currently a placeholder. The mock adapter is used for tests and local workflows that must not call an external service.

## Testing Expectations

The MVP must include tests for:

- readers
- parsers
- indexing
- compression
- SQLite repository
- BM25 retrieval
- token budget selection
- context builder
- AI adapters
- CLI commands
- local integration workflow

The local integration workflow should exercise:

```text
import folder -> search BM25 -> ask --dry-run -> optimize document -> stats
```
