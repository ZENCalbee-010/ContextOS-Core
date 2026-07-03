"""Base parser interfaces and chunk models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ParsedChunk:
    content: str
    chunk_index: int
    token_count: int
    page_number: int | None = None
    start_line: int | None = None
    end_line: int | None = None
    section: str | None = None


class BaseParser(ABC):
    """Strategy interface for turning raw text into chunks."""

    def __init__(self, max_tokens: int = 400) -> None:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero")
        self.max_tokens = max_tokens

    @abstractmethod
    def parse(self, text: str) -> list[ParsedChunk]:
        """Split raw text into parser chunks."""

    def count_tokens(self, text: str) -> int:
        return len(re.findall(r"\S+", text))

    def _renumber(self, chunks: list[ParsedChunk]) -> list[ParsedChunk]:
        return [
            ParsedChunk(
                content=chunk.content,
                chunk_index=index,
                token_count=chunk.token_count,
                page_number=chunk.page_number,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                section=chunk.section,
            )
            for index, chunk in enumerate(chunks)
        ]
