# ContextOS Core Technical Debt

## High Priority

1. Documentation and version drift

Current docs still emphasize v1.0 while the codebase contains v1.1 configuration/logging, v1.2 performance, v1.3 developer experience, and v2 retrieval foundation.

Impact: users and contributors may misunderstand the active scope.

2. Version metadata mismatch

`pyproject.toml` and `contextos.__version__` are at `1.1.0`, but later feature foundations exist.

Impact: releases and bug reports may reference the wrong capability set.

3. Mixed output stack

The CLI uses `typer.echo`, `safe_echo`, and Rich output.

Impact: output consistency and Windows Unicode safety can regress as commands evolve.

4. Retrieval provider architecture not fully routed

`BM25Retriever` is still instantiated directly in search, evaluation, benchmark, and ask flows.

Impact: future retrieval provider activation will require touching multiple modules.

## Medium Priority

1. Homegrown YAML parser

The settings loader implements a small custom YAML-like parser.

Impact: acceptable for the current simple settings file, but it will become fragile if config grows.

2. Default settings duplicated

Default config values exist in dataclasses, `config/settings.yaml`, and CLI wizard output.

Impact: defaults can drift.

3. Exception names overlap with built-ins

`MemoryError` can be confused with Python's built-in memory exhaustion exception.

Impact: readability and debugging friction.

4. Logging is configured but underused

Most internal workflows do not log meaningful diagnostic events.

Impact: doctor/debug commands are helpful, but failures still rely mostly on CLI output and exceptions.

5. Performance caches are process-local

Chunk and BM25 caches help in-process reuse but not separate CLI invocations.

Impact: users may not see large speedups in one-shot commands.

## Low Priority

1. Thai comments are extensive but some files still have mojibake when viewed through non-UTF-8 shell output.

Impact: source files are usable, but terminal display can be noisy.

2. Benchmark results are synthetic unless run on real project corpora.

Impact: useful as framework, less useful as product metric until standard fixtures exist.

3. CLI command registration in `main.py` is flat.

Impact: still manageable, but sub-app grouping may help if command count grows.

4. OpenAI and Claude adapters are placeholders.

Impact: acceptable for local/dry-run workflows, but live AI usage requires explicit implementation.

## Deferred By Design

- FastAPI
- PostgreSQL
- Docker
- Vector database
- Embeddings
- Multi-user cloud features

These remain out of scope unless the product direction changes.
