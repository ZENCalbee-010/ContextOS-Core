"""Typer CLI entrypoint for ContextOS Core."""

import typer

from contextos.cli.commands.ask_cmd import ask_context
from contextos.cli.commands.import_cmd import import_context
from contextos.cli.commands.optimize_cmd import optimize_context
from contextos.cli.commands.search_cmd import search_context
from contextos.cli.commands.stats_cmd import stats_context


app = typer.Typer(
    name="context",
    help="ContextOS Core: local-first AI context management.",
    no_args_is_help=True,
)

app.command(name="import", help="Import local files into the ContextOS workspace.")(
    import_context
)
app.command(
    name="optimize",
    help="Optimize stored compression metadata for a document.",
)(optimize_context)
app.command(name="ask", help="Ask a question using selected local context.")(ask_context)
app.command(name="search", help="Search imported local context.")(search_context)
app.command(name="stats", help="Show local ContextOS workspace statistics.")(stats_context)


if __name__ == "__main__":
    app()
