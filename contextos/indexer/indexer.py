"""Incremental file indexing pipeline."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal

from contextos.compression import (
    AggressiveCompressor,
    LightCompressor,
    MediumCompressor,
)
from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.parsers import CodeParser, ParsedChunk, TextParser
from contextos.readers import read_file

from contextos.indexer.hasher import sha256_file


IndexStatus = Literal["imported", "skipped", "unsupported", "error"]


@dataclass(frozen=True)
class IndexResult:
    status: IndexStatus
    filepath: str
    sha256: str | None = None
    document_id: int | None = None
    chunk_count: int = 0
    token_count: int = 0
    error: str | None = None


class FileIndexer:
    """Read, parse, and persist local files with incremental update checks."""

    def __init__(
        self,
        repository: SQLiteMemoryRepository,
        *,
        max_tokens_per_chunk: int = 400,
        keyword_limit: int = 12,
    ) -> None:
        self.repository = repository
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.keyword_limit = keyword_limit

    def index_file(self, path: str | Path) -> IndexResult:
        file_path = Path(path)
        filepath = str(file_path)

        try:
            sha256 = sha256_file(file_path)
        except OSError as exc:
            return IndexResult(status="error", filepath=filepath, error=str(exc))

        existing = self.repository.get_document_by_path(filepath)
        if existing and existing.sha256 == sha256:
            chunks = self.repository.get_chunks_by_document(existing.id)
            return IndexResult(
                status="skipped",
                filepath=filepath,
                sha256=sha256,
                document_id=existing.id,
                chunk_count=len(chunks),
                token_count=sum(chunk.token_count for chunk in chunks),
            )

        read_result = read_file(file_path)
        if not read_result.supported:
            return IndexResult(
                status="unsupported",
                filepath=filepath,
                sha256=sha256,
                error=read_result.error,
            )
        if read_result.error:
            return IndexResult(
                status="error",
                filepath=filepath,
                sha256=sha256,
                error=read_result.error,
            )

        parser = self._parser_for_reader(read_result.metadata.get("reader"))
        parsed_chunks = parser.parse(read_result.text)
        document_keywords = self._keywords(read_result.text)
        structural_sections = [
            chunk.section for chunk in parsed_chunks if chunk.section is not None
        ]

        document = self.repository.upsert_document(
            filepath,
            sha256,
            title=file_path.name,
            mime_type=self._mime_type(read_result.metadata.get("reader")),
            size_bytes=read_result.metadata.get("size_bytes"),
            metadata={
                "reader": read_result.metadata,
                "keywords": document_keywords,
                "structure": structural_sections,
            },
        )
        stored_chunks = self.repository.insert_chunks(
            document.id,
            [self._to_chunk_input(chunk) for chunk in parsed_chunks],
            replace_existing=True,
        )

        return IndexResult(
            status="imported",
            filepath=filepath,
            sha256=sha256,
            document_id=document.id,
            chunk_count=len(stored_chunks),
            token_count=sum(chunk.token_count for chunk in stored_chunks),
        )

    def _parser_for_reader(self, reader_name: object) -> TextParser | CodeParser:
        if reader_name == "code":
            return CodeParser(max_tokens=self.max_tokens_per_chunk)
        return TextParser(max_tokens=self.max_tokens_per_chunk)

    def _to_chunk_input(self, chunk: ParsedChunk) -> ChunkInput:
        return ChunkInput(
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            token_count=chunk.token_count,
            metadata={
                "page_number": chunk.page_number,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "section": chunk.section,
                "keywords": self._keywords(chunk.content),
                "compression": self._compressed_variants(chunk.content),
            },
        )

    def _compressed_variants(self, text: str) -> dict[str, dict[str, float | str]]:
        compressors = (
            LightCompressor(),
            MediumCompressor(),
            AggressiveCompressor(),
        )
        variants = {}
        for compressor in compressors:
            result = compressor.compress(text)
            variants[result.strategy] = {
                "content": result.compressed,
                "compression_ratio": result.compression_ratio,
            }
        return variants

    def _keywords(self, text: str) -> list[str]:
        words = [
            word.lower()
            for word in re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text)
            if word.lower() not in STOPWORDS
        ]
        counts = Counter(words)
        return [
            word
            for word, _count in sorted(
                counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[: self.keyword_limit]
        ]

    def _mime_type(self, reader_name: object) -> str | None:
        return {
            "text": "text/plain",
            "code": "text/plain",
            "pdf": "application/pdf",
            "docx": (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        }.get(reader_name)


STOPWORDS = {
    "and",
    "are",
    "but",
    "for",
    "from",
    "into",
    "not",
    "the",
    "this",
    "that",
    "with",
}
