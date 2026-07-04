"""Developer-experience commands for ContextOS Core."""

from __future__ import annotations

from pathlib import Path
import platform
import sys

import typer

from contextos import __version__
from contextos.cli.console import console, print_error, print_info, print_success, settings_table
from contextos.config import DEFAULT_SETTINGS_PATH, load_settings
from contextos.memory.db import connect
from contextos.memory.repository import SQLiteMemoryRepository


def version_context() -> None:
    """Show the installed ContextOS Core version."""
    print_success(f"ContextOS Core {__version__}")


def config_context(
    show: bool = typer.Option(
        True,
        "--show/--no-show",
        help="Show resolved configuration values.",
    ),
    init: bool = typer.Option(
        False,
        "--init",
        help="Create config/settings.yaml if it does not exist.",
    ),
    wizard: bool = typer.Option(
        False,
        "--wizard",
        help="Run a small interactive configuration wizard.",
    ),
) -> None:
    """Inspect or initialize local ContextOS configuration."""
    if init:
        _write_default_settings(overwrite=False)
        print_success(f"Configuration ready: {DEFAULT_SETTINGS_PATH}")

    if wizard:
        _run_config_wizard()
        print_success(f"Configuration updated: {DEFAULT_SETTINGS_PATH}")

    if show:
        settings = load_settings()
        table = settings_table("ContextOS Configuration")
        table.add_row("database.path", str(settings.database.path))
        table.add_row("compression.default_level", settings.compression.default_level)
        table.add_row("retrieval.algorithm", settings.retrieval.algorithm)
        table.add_row("retrieval.top_k", str(settings.retrieval.top_k))
        table.add_row("token_budget.max_tokens", str(settings.token_budget.max_tokens))
        table.add_row("token_budget.safety_margin", str(settings.token_budget.safety_margin))
        table.add_row("ai_adapter.provider", settings.ai_adapter.provider)
        table.add_row("ai_adapter.model", settings.ai_adapter.model)
        table.add_row("logging.level", settings.logging.level)
        console.print(table)


def doctor_context(
    db_path: Path | None = typer.Option(
        None,
        "--db-path",
        help="SQLite database path to inspect.",
    ),
) -> None:
    """Check local environment health for ContextOS Core."""
    settings = load_settings()
    database_path = db_path or settings.database.path
    checks = [
        ("Python", sys.version.split()[0], sys.version_info >= (3, 11)),
        ("Platform", platform.platform(), True),
        ("Settings file", str(DEFAULT_SETTINGS_PATH), DEFAULT_SETTINGS_PATH.exists()),
        ("SQLite database", str(database_path), _database_ok(database_path)),
        ("Retrieval", settings.retrieval.algorithm, settings.retrieval.algorithm == "bm25"),
    ]

    table = settings_table("ContextOS Doctor")
    table.add_column("Status")
    healthy = True
    for name, value, ok in checks:
        healthy = healthy and ok
        status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
        table.add_row(name, str(value), status)
    console.print(table)

    if healthy:
        print_success("Doctor check passed.")
    else:
        print_error("Doctor check found issues.")
        raise typer.Exit(1)


def debug_context(
    db_path: Path | None = typer.Option(
        None,
        "--db-path",
        help="SQLite database path to inspect.",
    ),
) -> None:
    """Show debug information for local troubleshooting."""
    settings = load_settings()
    database_path = db_path or settings.database.path
    repository = SQLiteMemoryRepository(database_path)
    repository.init_db()

    table = settings_table("ContextOS Debug")
    table.add_row("version", __version__)
    table.add_row("python", sys.version.replace("\n", " "))
    table.add_row("executable", sys.executable)
    table.add_row("database.path", str(database_path))
    table.add_row("chunk.signature", str(repository.get_chunk_cache_signature()))
    table.add_row("config.path", str(DEFAULT_SETTINGS_PATH))
    console.print(table)


def _database_ok(db_path: Path) -> bool:
    try:
        SQLiteMemoryRepository(db_path).init_db()
        with connect(db_path) as connection:
            connection.execute("SELECT COUNT(*) FROM documents").fetchone()
    except Exception:
        return False
    return True


def _write_default_settings(*, overwrite: bool) -> None:
    if DEFAULT_SETTINGS_PATH.exists() and not overwrite:
        return
    DEFAULT_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_SETTINGS_PATH.write_text(
        """database:
  path: data/contextos.sqlite3

compression:
  default_level: light
  levels:
    - light
    - medium
    - aggressive

retrieval:
  algorithm: bm25
  top_k: 5

token_budget:
  max_tokens: 8000
  safety_margin: 0.12

ai_adapter:
  provider: claude
  model: claude-3-5-sonnet-latest
  api_key_env: ANTHROPIC_API_KEY

logging:
  level: INFO
  debug: false
  file_path: data/contextos.log
  max_bytes: 1048576
  backup_count: 3
""",
        encoding="utf-8",
    )


def _run_config_wizard() -> None:
    current = load_settings()
    database_path = typer.prompt("SQLite database path", default=str(current.database.path))
    token_budget = typer.prompt("Default token budget", default=str(current.token_budget.max_tokens))
    ai_provider = typer.prompt("AI adapter provider", default=current.ai_adapter.provider)

    DEFAULT_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_SETTINGS_PATH.write_text(
        f"""database:
  path: {database_path}

compression:
  default_level: {current.compression.default_level}
  levels:
    - light
    - medium
    - aggressive

retrieval:
  algorithm: bm25
  top_k: {current.retrieval.top_k}

token_budget:
  max_tokens: {token_budget}
  safety_margin: {current.token_budget.safety_margin}

ai_adapter:
  provider: {ai_provider}
  model: {current.ai_adapter.model}
  api_key_env: {current.ai_adapter.api_key_env}

logging:
  level: {current.logging.level}
  debug: {str(current.logging.debug).lower()}
  file_path: {current.logging.file_path}
  max_bytes: {current.logging.max_bytes}
  backup_count: {current.logging.backup_count}
""",
        encoding="utf-8",
    )
