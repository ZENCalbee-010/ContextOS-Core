"""Terminal output helpers."""

import locale
from typing import Any, TextIO

import typer


def safe_echo(message: Any = "", *, file: TextIO | None = None) -> None:
    """Echo text, replacing only characters unsupported by the terminal encoding."""

    try:
        typer.echo(message, file=file)
    except UnicodeEncodeError:
        encoding = (
            getattr(file, "encoding", None)
            or locale.getpreferredencoding(False)
            or "utf-8"
        )
        text = str(message).encode(encoding, errors="replace").decode(encoding)
        typer.echo(text, file=file)
