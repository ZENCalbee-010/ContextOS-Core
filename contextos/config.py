"""Centralized settings for ContextOS Core."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any, Mapping

from contextos.exceptions import ConfigurationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_SETTINGS_PATH = CONFIG_DIR / "settings.yaml"


@dataclass(frozen=True)
class DatabaseSettings:
    path: Path = DATA_DIR / "contextos.sqlite3"


@dataclass(frozen=True)
class CompressionSettings:
    default_level: str = "light"
    levels: tuple[str, ...] = ("light", "medium", "aggressive")


@dataclass(frozen=True)
class RetrievalSettings:
    top_k: int = 5
    algorithm: str = "bm25"


@dataclass(frozen=True)
class TokenBudgetSettings:
    max_tokens: int = 8_000
    safety_margin: float = 0.12


@dataclass(frozen=True)
class AIAdapterSettings:
    provider: str = "claude"
    model: str = "claude-3-5-sonnet-latest"
    api_key_env: str = "ANTHROPIC_API_KEY"


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"
    debug: bool = False
    file_path: Path = DATA_DIR / "contextos.log"
    max_bytes: int = 1_048_576
    backup_count: int = 3


@dataclass(frozen=True)
class AppSettings:
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    compression: CompressionSettings = field(default_factory=CompressionSettings)
    retrieval: RetrievalSettings = field(default_factory=RetrievalSettings)
    token_budget: TokenBudgetSettings = field(default_factory=TokenBudgetSettings)
    ai_adapter: AIAdapterSettings = field(default_factory=AIAdapterSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)


DEFAULT_SETTINGS = AppSettings()


def load_settings(
    path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> AppSettings:
    """Load settings from YAML-like config and environment overrides."""

    config_path = Path(path) if path is not None else DEFAULT_SETTINGS_PATH
    environment = os.environ if environ is None else environ
    raw = _settings_to_dict(DEFAULT_SETTINGS)

    if config_path.exists():
        raw = _deep_merge(raw, _parse_simple_yaml(config_path.read_text(encoding="utf-8")))

    raw = _apply_environment_overrides(raw, environment)
    settings = _dict_to_settings(raw)
    validate_settings(settings)
    return settings


def validate_settings(settings: AppSettings) -> None:
    """Validate settings that protect the v1.x local-first architecture."""

    if settings.retrieval.algorithm != "bm25":
        raise ConfigurationError("retrieval.algorithm must be 'bm25' until optional providers are implemented")
    if settings.compression.default_level not in settings.compression.levels:
        raise ConfigurationError("compression.default_level must be one of the configured levels")
    if settings.token_budget.max_tokens <= 0:
        raise ConfigurationError("token_budget.max_tokens must be greater than zero")
    if not 0 <= settings.token_budget.safety_margin < 1:
        raise ConfigurationError("token_budget.safety_margin must be between 0 and 1")
    if settings.logging.max_bytes <= 0:
        raise ConfigurationError("logging.max_bytes must be greater than zero")
    if settings.logging.backup_count < 0:
        raise ConfigurationError("logging.backup_count must be zero or greater")


def _settings_to_dict(settings: AppSettings) -> dict[str, Any]:
    return {
        "database": {"path": str(settings.database.path)},
        "compression": {
            "default_level": settings.compression.default_level,
            "levels": list(settings.compression.levels),
        },
        "retrieval": {
            "top_k": settings.retrieval.top_k,
            "algorithm": settings.retrieval.algorithm,
        },
        "token_budget": {
            "max_tokens": settings.token_budget.max_tokens,
            "safety_margin": settings.token_budget.safety_margin,
        },
        "ai_adapter": {
            "provider": settings.ai_adapter.provider,
            "model": settings.ai_adapter.model,
            "api_key_env": settings.ai_adapter.api_key_env,
        },
        "logging": {
            "level": settings.logging.level,
            "debug": settings.logging.debug,
            "file_path": str(settings.logging.file_path),
            "max_bytes": settings.logging.max_bytes,
            "backup_count": settings.logging.backup_count,
        },
    }


def _dict_to_settings(raw: Mapping[str, Any]) -> AppSettings:
    database = raw.get("database", {})
    compression = raw.get("compression", {})
    retrieval = raw.get("retrieval", {})
    token_budget = raw.get("token_budget", {})
    ai_adapter = raw.get("ai_adapter", {})
    logging_settings = raw.get("logging", {})

    return AppSettings(
        database=DatabaseSettings(path=_resolve_project_path(database.get("path", DEFAULT_SETTINGS.database.path))),
        compression=CompressionSettings(
            default_level=str(compression.get("default_level", "light")),
            levels=tuple(compression.get("levels", ("light", "medium", "aggressive"))),
        ),
        retrieval=RetrievalSettings(
            top_k=int(retrieval.get("top_k", 5)),
            algorithm=str(retrieval.get("algorithm", "bm25")),
        ),
        token_budget=TokenBudgetSettings(
            max_tokens=int(token_budget.get("max_tokens", 8_000)),
            safety_margin=float(token_budget.get("safety_margin", 0.12)),
        ),
        ai_adapter=AIAdapterSettings(
            provider=str(ai_adapter.get("provider", "claude")),
            model=str(ai_adapter.get("model", "claude-3-5-sonnet-latest")),
            api_key_env=str(ai_adapter.get("api_key_env", "ANTHROPIC_API_KEY")),
        ),
        logging=LoggingSettings(
            level=str(logging_settings.get("level", "INFO")),
            debug=bool(logging_settings.get("debug", False)),
            file_path=_resolve_project_path(logging_settings.get("file_path", DEFAULT_SETTINGS.logging.file_path)),
            max_bytes=int(logging_settings.get("max_bytes", 1_048_576)),
            backup_count=int(logging_settings.get("backup_count", 3)),
        ),
    )


def _apply_environment_overrides(
    raw: dict[str, Any],
    environ: Mapping[str, str],
) -> dict[str, Any]:
    overrides = {
        "CONTEXTOS_DB_PATH": ("database", "path"),
        "CONTEXTOS_COMPRESSION_LEVEL": ("compression", "default_level"),
        "CONTEXTOS_RETRIEVAL_TOP_K": ("retrieval", "top_k"),
        "CONTEXTOS_TOKEN_BUDGET": ("token_budget", "max_tokens"),
        "CONTEXTOS_TOKEN_SAFETY_MARGIN": ("token_budget", "safety_margin"),
        "CONTEXTOS_AI_PROVIDER": ("ai_adapter", "provider"),
        "CONTEXTOS_AI_MODEL": ("ai_adapter", "model"),
        "CONTEXTOS_AI_API_KEY_ENV": ("ai_adapter", "api_key_env"),
        "CONTEXTOS_LOG_LEVEL": ("logging", "level"),
        "CONTEXTOS_LOG_FILE": ("logging", "file_path"),
        "CONTEXTOS_DEBUG": ("logging", "debug"),
    }

    merged = {section: dict(values) for section, values in raw.items()}
    for env_name, (section, key) in overrides.items():
        if env_name in environ:
            merged.setdefault(section, {})[key] = _parse_scalar(environ[env_name])
    return merged


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = {key: dict(value) if isinstance(value, dict) else value for key, value in base.items()}
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the small settings.yaml shape ContextOS uses."""

    result: dict[str, Any] = {}
    current_section: str | None = None
    current_list: tuple[str, str] | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":"):
            current_section = stripped[:-1]
            current_list = None
            result.setdefault(current_section, {})
            continue

        if stripped.startswith("- ") and current_list is not None:
            section, key = current_list
            result.setdefault(section, {}).setdefault(key, []).append(_parse_scalar(stripped[2:]))
            continue

        if current_section is None or ":" not in stripped:
            raise ConfigurationError(f"Invalid settings line: {raw_line}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            result.setdefault(current_section, {})[key] = []
            current_list = (current_section, key)
        else:
            result.setdefault(current_section, {})[key] = _parse_scalar(value)
            current_list = None

    return result


def _parse_scalar(value: str) -> Any:
    stripped = value.strip().strip('"').strip("'")
    lowered = stripped.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        return stripped


SETTINGS = load_settings()
DEFAULT_DB_PATH = SETTINGS.database.path
DEFAULT_TOKEN_BUDGET = SETTINGS.token_budget.max_tokens
