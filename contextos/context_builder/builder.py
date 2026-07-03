"""Build final prompts from selected context chunks."""

from typing import Protocol

from contextos.formatting import format_source
from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


SYSTEM_PROMPT = "You are answering using only the provided context."
INSTRUCTIONS = [
    "Answer clearly.",
    "Cite source names when possible.",
    "If context is insufficient, say so.",
]


class ChunkSelection(Protocol):
    chunk: Chunk


class ContextBuilder:
    """Render selected chunks into the final question-answer prompt."""

    def __init__(self, repository: SQLiteMemoryRepository | None = None) -> None:
        self.repository = repository

    def build(self, question: str, chunks: list[Chunk | ChunkSelection]) -> str:
        context_blocks = [
            self._format_chunk(index, self._unwrap_chunk(item))
            for index, item in enumerate(chunks, start=1)
        ]

        return "\n\n".join(
            [
                "SYSTEM:",
                SYSTEM_PROMPT,
                "CONTEXT:",
                "\n\n".join(context_blocks) if context_blocks else "(no context provided)",
                "QUESTION:",
                question,
                "INSTRUCTIONS:",
                "\n".join(f"- {instruction}" for instruction in INSTRUCTIONS),
            ]
        )

    def _unwrap_chunk(self, item: Chunk | ChunkSelection) -> Chunk:
        if isinstance(item, Chunk):
            return item
        return item.chunk

    def _format_chunk(self, index: int, chunk: Chunk) -> str:
        source = format_source(chunk, self.repository)
        return "\n".join(
            [
                f"[Chunk {index}]",
                f"Source: {source}",
                f"Content: {chunk.content}",
            ]
        )
