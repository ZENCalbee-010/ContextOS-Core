# Project Structure

```text
ContextOS-Core/
├── contextos/
│   ├── ai_adapter/        # AI adapter strategy interfaces and placeholders
│   ├── benchmark/         # Local benchmark helpers and markdown reports
│   ├── cli/               # Typer CLI entry point, commands, and console helpers
│   ├── compression/       # Rule-based compression strategies
│   ├── context_builder/   # Prompt assembly from selected chunks
│   ├── evaluation/        # Retrieval and context quality metrics
│   ├── formatting/        # Shared source and preview formatting
│   ├── indexer/           # File hashing and incremental import pipeline
│   ├── logging/           # Rotating log configuration helpers
│   ├── memory/            # SQLite schema, models, and repository
│   ├── parsers/           # Text and code chunk parsers
│   ├── performance/       # Memory profiling utilities
│   ├── readers/           # File readers and extension detector
│   ├── retrieval/         # BM25 retriever and v2 provider interface
│   ├── token_budget/      # Greedy token budget selector
│   ├── tokenizer/         # Token counting helpers
│   ├── config.py          # Central settings loader
│   └── exceptions.py      # ContextOS exception hierarchy
├── config/
│   └── settings.yaml      # Default local configuration
├── data/                  # Local runtime data location
├── docs/                  # Usage, limitations, performance, diagrams
├── sample_data/           # Small demo documents
├── tests/                 # Pytest suite
├── ContextOS_Architecture.md
├── README.md
├── pyproject.toml
└── LICENSE
```

## Core Flow

```text
Reader -> Parser -> Indexer -> Compression -> Memory
Question -> Retriever -> Token Budget -> Context Builder -> AI Adapter
```

## Design Patterns

- Strategy Pattern: readers, compression, AI adapters, retrieval providers
- Repository Pattern: SQLite memory layer
- Pipeline Pattern: import and question flows
- Separation of Concerns: parsing, storage, retrieval, and CLI orchestration remain separate
