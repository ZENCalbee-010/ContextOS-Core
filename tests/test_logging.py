from contextos.logging import configure_logging, get_logger


def test_configure_logging_writes_rotating_log_file(tmp_path) -> None:
    log_path = tmp_path / "contextos.log"
    logger = configure_logging(debug=True, log_file=log_path, console=False)

    logger.info("foundation logging works")

    assert log_path.exists()
    assert "foundation logging works" in log_path.read_text(encoding="utf-8")


def test_get_logger_returns_contextos_child_logger() -> None:
    logger = get_logger("tests")

    assert logger.name == "contextos.tests"
