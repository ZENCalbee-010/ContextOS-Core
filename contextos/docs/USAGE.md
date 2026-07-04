# ContextOS Core Usage

These examples assume you are running commands from the repository root after installing the package in editable mode.

```powershell
cd "C:\Project\ContextOS Core\contextos"
python -m pip install -e ".[dev]"
```

Use one local SQLite database for a workflow:

```powershell
$db = ".\data\contextos.sqlite3"
```

## Import

Import a folder recursively:

```powershell
context import .\sample_data --db-path $db
```

Import a single file:

```powershell
context import .\sample_data\context_principles.md --db-path $db
```

## Search

Search imported chunks with BM25:

```powershell
context search "context selection" --top-k 5 --db-path $db
```

The result output includes score, source, section or line information when available, and preview text.

## Ask Dry Run

Preview selected context without calling an AI adapter:

```powershell
context ask "Why is context selection important?" --dry-run --adapter mock --db-path $db
```

Dry-run prints the prompt and sources, and does not write conversation history.

## Optimize

Re-run one stored compression level for a document:

```powershell
context optimize .\sample_data\context_principles.md --level medium --db-path $db
```

Supported levels:

- `light`
- `medium`
- `aggressive`

## Stats

Show local workspace statistics:

```powershell
context stats --db-path $db
```

Stats include total documents, total chunks, original tokens, average compression ratio, and latest query latency when available.
