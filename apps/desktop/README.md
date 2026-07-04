# ContextOS Desktop

Level 2 desktop scaffold for ContextOS Core.

This app is a Tauri + React + TypeScript GUI wrapper around the existing Python CLI. It does not rewrite the Python core and targets:

```powershell
python -m contextos.cli.main
```

The desktop database path is:

```text
data/desktop.db
```

## Local Setup

From the repository root:

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

Run the web UI during development:

```powershell
npm run dev
```

Run the Tauri desktop shell:

```powershell
npm run tauri dev
```

Build the desktop app:

```powershell
npm run tauri build
```

## Screenshots

Screenshots are not committed yet. To capture release screenshots:

1. Run `npm run tauri dev`.
2. Import `sample_data`.
3. Search for `context selection`.
4. Ask `What is ContextOS?` with dry-run enabled.
5. Capture:
   - Full workspace with workflow guide
   - TokenSavingsPanel after ask
   - CommandLog with stdout/stderr/exit code

Suggested paths:

```text
docs/screenshots/desktop-workspace.png
docs/screenshots/desktop-token-savings.png
docs/screenshots/desktop-command-log.png
```

## Wired Commands

The desktop app calls the Python CLI through a Tauri command named `run_context_command`.
Commands are passed as argument arrays, not shell strings.

Approved desktop commands:

```text
import <path> --db-path data/desktop.db
search <query> --top-k <n> --db-path data/desktop.db
ask <question> --dry-run --adapter mock --budget <n> --db-path data/desktop.db
ask <question> --adapter mock --budget <n> --db-path data/desktop.db
optimize <document> --level light|medium|aggressive --db-path data/desktop.db
stats --db-path data/desktop.db
```

The bridge returns `stdout`, `stderr`, and `exitCode` separately for the command log.

## Manual Verification

1. Start from the repository root and install the Python package:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

2. Install the desktop dependencies:

   ```powershell
   cd apps\desktop
   npm install
   ```

3. Run the Tauri shell:

   ```powershell
   npm run tauri dev
   ```

4. In the app, run these buttons in order:

   - Import with `sample_data`
   - Search with `context selection`
   - Ask with dry run enabled
   - Load Stats
   - Optimize document `1` with `medium`

5. Confirm `CommandLog` shows stdout, stderr, and exit code, and `TokenSavingsPanel` updates after ask output contains a token savings report.

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

## Notes

- The UI is wired for import, search, dry-run ask, mock ask, optimize, stats, token savings, and command logs.
- Buttons call a safe Tauri subprocess bridge when the app runs inside Tauri.
- In a plain browser, commands are logged but not executed.
- No embeddings, vector database, cloud sync, or AI API integration is included.
- The Python CLI remains the source of truth.
