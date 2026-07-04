# ContextOS Core Usage

These examples assume you are running commands from the repository root after installing the package in editable mode.

```powershell
cd "C:\GitHub\ContextOS-Core"
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

Dry-run prints the prompt, sources, and token savings report. It does not write conversation history.

Ask output includes a Token Savings Report:

```text
TOKEN SAVINGS REPORT
Total available tokens: 12500
Selected context tokens: 1850
Saved tokens: 10650
Savings percent: 85.20%
```

Token savings compares every imported chunk in the current SQLite database with the chunks selected for the current ask flow:

```text
saved_tokens = max(total_available_tokens - selected_context_tokens, 0)
savings_percent = saved_tokens / total_available_tokens * 100
```

When no chunks are available, saved tokens and savings percent are both `0`.

## Ask Mock

Generate a local mock response without a real AI API call:

```powershell
context ask "What is ContextOS?" --adapter mock --db-path $db
```

The mock ask flow stores conversation metadata, including used chunk ids, tokens used, latency, and token savings.

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

When available, stats also shows latest token savings from conversation history:

```text
Latest token savings: 10650 tokens (85.20%)
```

## Desktop App

The desktop MVP wraps the same CLI in a Tauri + React + TypeScript interface.

```powershell
cd apps\desktop
npm install
npm run dev
npm run tauri dev
```

Desktop database:

```text
data/desktop.db
```

Desktop workflow:

1. Import files or folders.
2. Search imported context.
3. Ask with dry-run or mock mode.
4. Check token savings.
5. View stats.

See [DESKTOP_APP.md](DESKTOP_APP.md) for setup, allowed commands, and manual QA.
