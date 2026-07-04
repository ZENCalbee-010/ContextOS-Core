# Portfolio Token Savings Demo

## Context Selection Section 01

ContextOS measures token savings by comparing all imported chunk tokens with the selected context tokens. Local-first SQLite keeps the benchmark inspectable, repeatable, and easy to reset. BM25 retrieval ranks lexical overlap before the token budget selector chooses the highest value chunks.

## Context Selection Section 02

Context selection is more important than compression because a small relevant prompt is easier to inspect than a large noisy prompt. The benchmark report should make this visible by showing total available tokens, selected context tokens, saved tokens, and savings percent.

## Context Selection Section 03

The desktop app wraps the Python CLI and does not change retrieval behavior. Users import local files, search with BM25, ask in dry-run or mock mode, inspect token savings, and view stats from the local SQLite database.

## Context Selection Section 04

Rule-based compression remains deterministic. Light compression cleans whitespace, medium compression uses extractive sentence scoring, and aggressive compression keeps headings, bullets, signatures, and first sentences. No external model is required.

## Context Selection Section 05

Benchmark data should include enough chunks to show that ContextOS selects a subset of local context. If every chunk fits inside the token budget, savings can be zero. That is correct behavior for a very small corpus.

## Context Selection Section 06

BM25 retrieval is lexical and local. It works best when the question shares vocabulary with the documents. The benchmark query uses context selection terms so search latency and dry-run prompt construction are stable across runs.

## Context Selection Section 07

SQLite stores documents, chunks, compression metadata, and conversation history. The benchmark command can reuse an existing database safely because unchanged files are skipped by SHA-256 incremental import checks.

## Context Selection Section 08

Token savings is a selection metric, not an embedding metric. It does not require semantic search, vector indexes, hybrid ranking, or cloud infrastructure. The report is designed for local portfolio demonstrations.

## Context Selection Section 09

The ask dry-run benchmark builds the final prompt from selected chunks without calling a live AI adapter. This keeps the benchmark safe, deterministic, and suitable for automated tests or classroom demonstrations.

## Context Selection Section 10

Command logs in the desktop app show stdout, stderr, and exit code. The same CLI behavior remains available in PowerShell or any terminal through python -m contextos.cli.main.

## Context Selection Section 11

The Level 2 desktop scope is intentionally final. ContextOS does not expand into a VS Code extension, browser extension, plugin API platform, cloud sync system, multi-user service, or agent runtime.

## Context Selection Section 12

The benchmark command generates Markdown so results can be inspected, committed, shared, or added to a portfolio. The report includes configuration, summary metrics, per-step latency, token savings, compression, scope notes, and limitations.

## Context Selection Section 13

Import latency measures the existing reader, parser, indexer, compression, and memory pipeline. Search latency measures BM25 over stored chunks. Ask dry-run latency measures retrieval, token budget selection, and prompt building.

## Context Selection Section 14

Visible token savings depends on corpus size, top-k retrieval, and token budget. A larger local corpus gives ContextOS more available context than it can select, which makes saved tokens and savings percent easier to see.

## Context Selection Section 15

This portfolio benchmark file repeats the core project language across many sections so the parser creates multiple chunks. The benchmark can then show selected context as a subset of the full imported dataset.
