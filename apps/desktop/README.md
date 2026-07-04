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

## Notes

- The UI is scaffolded with panels for import, search, ask, optimize, stats, token savings, and command logs.
- Buttons call a Tauri subprocess bridge when the app runs inside Tauri.
- In a plain browser, commands are logged but not executed.
- No embeddings, vector database, cloud sync, or AI API integration is included.
- The Python CLI remains the source of truth.
