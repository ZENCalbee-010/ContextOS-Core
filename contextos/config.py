"""Configuration defaults for ContextOS Core."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_DB_PATH = DATA_DIR / "contextos.sqlite3"
DEFAULT_TOKEN_BUDGET = 8_000
