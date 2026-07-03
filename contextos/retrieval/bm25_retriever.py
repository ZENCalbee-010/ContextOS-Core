"""BM25-only retrieval over stored SQLite chunks."""

from dataclasses import dataclass
import re

from rank_bm25 import BM25Okapi

from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class BM25Result:
    chunk: Chunk
    score: float


class BM25Retriever:
    """Retrieve top-k chunks with rank-bm25 BM25Okapi."""

    def __init__(self, repository: SQLiteMemoryRepository) -> None:
        self.repository = repository

    def search(self, query: str, *, top_k: int = 5) -> list[BM25Result]:
        if top_k <= 0:
            return []

        chunks = self.repository.get_all_chunks()
        if not chunks:
            return []

        tokenized_chunks = [tokenize(chunk.content) for chunk in chunks]
        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        bm25 = BM25Okapi(tokenized_chunks)
        scores = bm25.get_scores(tokenized_query)
        scored = [
            BM25Result(chunk=chunk, score=float(score))
            for chunk, score in zip(chunks, scores)
        ]

        return sorted(scored, key=lambda result: result.score, reverse=True)[:top_k]


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]
