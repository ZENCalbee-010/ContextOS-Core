"""Base interfaces for rule-based compression."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CompressionResult:
    original: str
    compressed: str
    original_length: int
    compressed_length: int
    compression_ratio: float
    strategy: str


class BaseCompressor(ABC):
    """Strategy interface for deterministic context compression."""

    strategy = "base"

    def compress(self, text: str) -> CompressionResult:
        compressed = self._compress(text).strip()
        return CompressionResult(
            original=text,
            compressed=compressed,
            original_length=len(text),
            compressed_length=len(compressed),
            compression_ratio=self.compression_ratio(text, compressed),
            strategy=self.strategy,
        )

    @abstractmethod
    def _compress(self, text: str) -> str:
        """Return compressed text."""

    def compression_ratio(self, original: str, compressed: str) -> float:
        if not original:
            return 0.0
        return 1 - (len(compressed) / len(original))


SENTENCE_RE = re.compile(r"[^.!?]+(?:[.!?]+|$)", re.MULTILINE)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


def split_sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(text) if match.group(0).strip()]


def split_paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
