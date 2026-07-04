"""Rich console helpers for ContextOS CLI output."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, TypeVar

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table


T = TypeVar("T")

console = Console()


def print_success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def print_warning(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def print_error(message: str) -> None:
    console.print(f"[red]{message}[/red]")


def print_info(message: str) -> None:
    console.print(f"[cyan]{message}[/cyan]")


def progress_iter(items: Iterable[T], description: str) -> Iterator[T]:
    values = list(items)
    if not values:
        return iter(())

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=len(values))
        for item in values:
            yield item
            progress.advance(task)


def settings_table(title: str) -> Table:
    table = Table(title=title)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    return table


def path_text(path: str | Path) -> str:
    return str(Path(path))
