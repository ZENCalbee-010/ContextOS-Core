# ContextOS Core Refactor Plan

This plan preserves the current architecture and avoids behavior changes unless explicitly called out.

## Phase 1: Documentation and Release Hygiene

Goal: make the repository describe what it actually contains.

Tasks:

- Update `ContextOS_Architecture.md` to include v1.1-v1.3 foundations and v2 retrieval placeholders.
- Update `CHANGELOG.md` for v1.1, v1.2, v1.3, and v2 retrieval foundation.
- Align `pyproject.toml` version and `contextos.__version__`.
- Clarify that embedding and hybrid providers are placeholders only.
- Add a release checklist covering tests, compileall, CLI smoke, wheel build, and tag.

Risk: low.

## Phase 2: CLI Output Consolidation

Goal: keep user-facing output consistent and Windows-safe.

Tasks:

- Create a shared CLI rendering layer for status messages, result tables, and summaries.
- Route `search`, `stats`, `optimize`, and `ask` output through shared helpers.
- Keep plain-text substrings required by existing tests.
- Keep `safe_echo` for raw prompt/dry-run content.

Risk: medium, because CLI tests assert output text.

## Phase 3: Retrieval Provider Routing

Goal: make BM25 the active provider through the new provider interface.

Tasks:

- Add `retrieval.provider` setting while keeping `retrieval.algorithm` as backward-compatible alias.
- Route search/evaluation/benchmark/ask through `get_retriever("bm25", repository)`.
- Keep future providers unavailable by default.
- Add tests that config cannot activate placeholder providers.

Risk: low if BM25 remains default.

## Phase 4: Config Loader Hardening

Goal: reduce config parsing edge cases.

Tasks:

- Either adopt `PyYAML` as a dependency or clearly document the supported YAML subset.
- Centralize default settings serialization so CLI wizard and dataclasses cannot drift.
- Add tests for invalid config lines, quoted paths, booleans, lists, and environment overrides.

Risk: low to medium depending on whether a dependency is added.

## Phase 5: Exceptions and Logging Cleanup

Goal: make diagnostics production-friendly.

Tasks:

- Rename or alias `contextos.exceptions.MemoryError` to `MemoryLayerError`.
- Replace direct generic `ValueError` in internal layers where compatibility allows.
- Add logging to index/import/search/ask/optimize boundaries.
- Ensure logs never include API key values or full prompts unless debug mode explicitly permits it.

Risk: medium due to exception compatibility.

## Phase 6: Packaging and CI

Goal: verify installability, not only testability.

Tasks:

- Add CI job to build wheel and sdist.
- Install built wheel in a clean environment and run `context --help`.
- Add Windows CI for PowerShell CLI behavior.
- Add optional coverage reporting.

Risk: low.
