# ContextOS Desktop App

The ContextOS Desktop App is the final project level: Level 2.

It is a GUI wrapper around the existing Python CLI.

It does not rewrite the Python core. The desktop backend target is:

```powershell
python -m contextos.cli.main
```

## Stack

- Tauri
- React
- TypeScript
- Python subprocess bridge

## Location

```text
apps/desktop
```

## Database

The desktop MVP uses:

```text
data/desktop.db
```

## Workflow

1. Import files first.
2. Search imported context.
3. Ask with dry-run or mock mode.
4. Check token savings.
5. Run stats and benchmark.

## Final Scope

In scope:

- Desktop import/search/ask/stats/benchmark workflows
- Drag and drop files/folders
- Dry-run and mock ask modes
- Token Savings Report
- Local-first SQLite storage
- BM25 retrieval
- Rule-based compression

Out of scope:

- VS Code extension
- Browser extension
- Plugin/API layer
- Cloud sync
- Multi-user system
- Agent runtime
- Embeddings or vector database
- Semantic search

## Approved Commands

The desktop bridge only allows these ContextOS commands:

```text
import <path> --db-path data/desktop.db
search <query> --top-k <n> --db-path data/desktop.db
ask <question> --top-k <n> --budget <n> --dry-run --db-path data/desktop.db
ask <question> --top-k <n> --budget <n> --adapter mock --db-path data/desktop.db
optimize <document> --level light|medium|aggressive --db-path data/desktop.db
stats --db-path data/desktop.db
benchmark --dataset sample_data/benchmark --db-path data/benchmark_desktop.db --output benchmark_report_desktop.md --query <query> --question <question> --iterations <n>
```

Arguments are passed as arrays through Tauri. The app does not execute arbitrary shell strings.

## Setup

Install the Python package from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install desktop dependencies:

```powershell
cd apps\desktop
npm install
```

Run the browser development view:

```powershell
npm run dev
```

Run the Tauri shell:

```powershell
npm run tauri dev
```

Build the frontend:

```powershell
npm run build
```

## UI Panels

- DropZone: imports selected files or folders through the local CLI.
- DocumentList: placeholder for imported document browsing.
- SearchPanel: runs BM25 search and displays parsed result cards with raw output fallback.
- AskPanel: runs dry-run or mock ask and displays prompt preview, mock output, and sources when parseable.
- OptimizePanel: re-runs stored rule-based compression metadata.
- StatsPanel: loads workspace statistics and parsed metric cards.
- BenchmarkPanel: runs local benchmark and displays latency, compression, and token savings metrics.
- TokenSavingsPanel: displays parsed token savings output with an efficiency meter.
- CommandLog: shows command, args, stdout, stderr, exit code, duration, collapsed output, and copy output action.

## Screenshot Instructions

Screenshots are not committed yet. Suggested capture flow:

1. Run `npm run tauri dev`.
2. Import `sample_data`.
3. Search `context selection`.
4. Ask `What is ContextOS?` with dry-run enabled.
5. Capture:
   - Full workspace with workflow guide.
   - TokenSavingsPanel after ask.
   - CommandLog with args, collapsed stdout/stderr, exit code, duration, and copy output action.

Suggested paths:

```text
docs/screenshots/desktop-workspace.png
docs/screenshots/desktop-token-savings.png
docs/screenshots/desktop-command-log.png
```

## Manual QA Checklist

- App opens without requiring a real AI API key.
- Workflow guide makes the order clear: import, search, ask, savings, stats/benchmark.
- Empty CommandLog explains what to do next.
- Importing an invalid path shows an error entry.
- Unsupported dropped files are marked and skipped.
- Searching an empty query is blocked with a clear error entry.
- Asking an empty question is blocked with a clear error entry.
- Ask dry-run does not call a real AI provider.
- Ask mock displays stdout and updates TokenSavingsPanel when savings output exists.
- TokenSavingsPanel explains what token savings means and displays an efficiency meter.
- CommandLog collapses long output and can copy stdout/stderr.
- Settings shows the backend command, current DB path, and Desktop scope note.
- Benchmark supports query, question, iterations, parsed metrics, and raw output fallback.
- Optimize supports only light, medium, and aggressive.
- Stats command writes workspace totals to CommandLog.

## Limitations

- Desktop imports use the Level 2 DropZone/path workflow, with path entry available as a reliable fallback when native OS drag/drop behavior varies by runtime.
- Tauri requires Rust/Cargo on the developer machine.
- The desktop app does not add cloud sync, embeddings, vector search, or real AI API calls.
