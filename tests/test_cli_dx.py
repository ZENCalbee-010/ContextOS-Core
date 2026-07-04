from typer.testing import CliRunner

from contextos import __version__
from contextos.cli.main import app


runner = CliRunner()


def test_cli_help_lists_developer_experience_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "version" in result.output
    assert "config" in result.output
    assert "debug" in result.output


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"ContextOS Core {__version__}" in result.output


def test_config_command_shows_resolved_settings() -> None:
    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "ContextOS Configuration" in result.output
    assert "database.path" in result.output
    assert "retrieval.algorithm" in result.output
    assert "bm25" in result.output


def test_doctor_command_passes_for_temp_database(tmp_path) -> None:
    db_path = tmp_path / "doctor.sqlite3"

    result = runner.invoke(app, ["doctor", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "ContextOS Doctor" in result.output
    assert "Doctor check passed." in result.output


def test_debug_command_shows_local_diagnostics(tmp_path) -> None:
    db_path = tmp_path / "debug.sqlite3"

    result = runner.invoke(app, ["debug", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "ContextOS Debug" in result.output
    assert "chunk.signature" in result.output
