# Contributing to ContextOS Core

Thanks for considering a contribution. ContextOS Core is a local-first CLI project, so contributions should preserve the core scope and keep the system easy to inspect.

## Project Scope

ContextOS Core currently focuses on:

- Typer CLI workflows
- SQLite local storage
- BM25 lexical retrieval
- Rule-based compression
- Local single-user operation
- Testable, modular Python code

Do not add these without an accepted design discussion:

- FastAPI or web servers
- PostgreSQL or external databases
- Docker-based runtime requirements
- Embeddings or vector databases
- Multi-user cloud features

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
python -m compileall contextos
```

## Contribution Workflow

1. Open an issue or discussion for non-trivial changes.
2. Keep patches focused and small.
3. Add or update tests for behavior changes.
4. Update documentation when commands, architecture, or limitations change.
5. Run the full test suite before submitting.

## Coding Guidelines

- Keep APIs compatible unless a breaking change is explicitly approved.
- Prefer existing module patterns over new abstractions.
- Use type hints for public functions and dataclasses.
- Keep CLI output user-friendly.
- Never hardcode API keys or secrets.
- Avoid broad architecture changes in feature patches.

## Pull Request Checklist

- [ ] Tests pass with `python -m pytest`.
- [ ] Compile check passes with `python -m compileall contextos`.
- [ ] CLI help still works with `python -m contextos.cli.main --help`.
- [ ] Documentation is updated where needed.
- [ ] No new out-of-scope infrastructure was introduced.
