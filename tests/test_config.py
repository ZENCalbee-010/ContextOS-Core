from pathlib import Path

import pytest

from contextos.config import ConfigurationError, load_settings


def test_load_settings_uses_yaml_and_environment_overrides(tmp_path) -> None:
    settings_path = tmp_path / "settings.yaml"
    settings_path.write_text(
        """
database:
  path: custom.sqlite3
retrieval:
  algorithm: bm25
  top_k: 3
token_budget:
  max_tokens: 1000
  safety_margin: 0.1
ai_adapter:
  provider: mock
  model: test-model
""",
        encoding="utf-8",
    )

    settings = load_settings(
        settings_path,
        environ={
            "CONTEXTOS_DB_PATH": str(tmp_path / "override.sqlite3"),
            "CONTEXTOS_RETRIEVAL_TOP_K": "7",
            "CONTEXTOS_DEBUG": "true",
        },
    )

    assert settings.database.path == tmp_path / "override.sqlite3"
    assert settings.retrieval.algorithm == "bm25"
    assert settings.retrieval.top_k == 7
    assert settings.token_budget.max_tokens == 1000
    assert settings.ai_adapter.provider == "mock"
    assert settings.logging.debug is True


def test_load_settings_rejects_non_bm25_retrieval(tmp_path) -> None:
    settings_path = tmp_path / "settings.yaml"
    settings_path.write_text(
        """
retrieval:
  algorithm: vector
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="bm25"):
        load_settings(settings_path, environ={})
