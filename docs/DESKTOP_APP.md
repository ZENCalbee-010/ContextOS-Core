# ContextOS Desktop App

The ContextOS Desktop App is a Level 2 GUI wrapper around the existing Python CLI.

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
5. View workspace stats.

## Approved Commands

The desktop bridge only allows these ContextOS commands:

```text
import <path> --db-path data/desktop.db
search <query> --top-k <n> --db-path data/desktop.db
ask <question> --dry-run --adapter mock --budget <n> --db-path data/desktop.db
ask <question> --adapter mock --budget <n> --db-path data/desktop.db
optimize <document> --level light|medium|aggressive --db-path data/desktop.db
stats --db-path data/desktop.db
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

- DropZone: imports a file or folder path.
- DocumentList: placeholder for imported document browsing.
- SearchPanel: runs BM25 search.
- AskPanel: runs dry-run or mock ask.
- OptimizePanel: re-runs stored rule-based compression metadata.
- StatsPanel: loads workspace statistics.
- TokenSavingsPanel: displays parsed token savings output.
- CommandLog: shows command, stdout, stderr, and exit code.

## Screenshot Instructions

Screenshots are not committed yet. Suggested capture flow:

1. Run `npm run tauri dev`.
2. Import `sample_data`.
3. Search `context selection`.
4. Ask `What is ContextOS?` with dry-run enabled.
5. Capture:
   - Full workspace with workflow guide.
   - TokenSavingsPanel after ask.
   - CommandLog with stdout, stderr, and exit code.

Suggested paths:

```text
docs/screenshots/desktop-workspace.png
docs/screenshots/desktop-token-savings.png
docs/screenshots/desktop-command-log.png
```

## Manual QA Checklist

- App opens without requiring a real AI API key.
- Workflow guide makes the order clear: import, search, ask, savings, stats.
- Empty CommandLog explains what to do next.
- Importing an invalid path shows an error entry.
- Searching an empty query is blocked with a clear error entry.
- Asking an empty question is blocked with a clear error entry.
- Ask dry-run does not call a real AI provider.
- Ask mock displays stdout and updates TokenSavingsPanel when savings output exists.
- Optimize supports only light, medium, and aggressive.
- Stats command writes workspace totals to CommandLog.

## Limitations

- Native drag/drop is not fully wired yet; imports currently use a path field.
- Tauri requires Rust/Cargo on the developer machine.
- The desktop app does not add cloud sync, embeddings, vector search, or real AI API calls.
