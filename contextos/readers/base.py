"""Base interfaces for file readers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReaderResult:
    """Raw text and metadata extracted from a local file."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    supported: bool = True
    error: str | None = None


class BaseReader(ABC):
    """Strategy interface for reading a file into raw text."""

    supported_extensions: frozenset[str] = frozenset()
    reader_name = "base"

    def can_read(self, path: str | Path) -> bool:
        return Path(path).suffix.lower() in self.supported_extensions

    @abstractmethod
    def read(self, path: str | Path) -> ReaderResult:
        """Read a file and return raw text plus metadata."""

    def _base_metadata(self, path: str | Path) -> dict[str, Any]:
        file_path = Path(path)
        stat = file_path.stat()
        return {
            "filepath": str(file_path),
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "reader": self.reader_name,
            "size_bytes": stat.st_size,
        }
