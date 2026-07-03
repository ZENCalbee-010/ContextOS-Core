"""Dataclasses for SQLite memory records."""

from dataclasses import dataclass
import json
from sqlite3 import Row
from typing import Any


Metadata = dict[str, Any] | None


def encode_metadata(metadata: Metadata) -> str | None:
    if metadata is None:
        return None
    return json.dumps(metadata, sort_keys=True)


def decode_metadata(metadata_json: str | None) -> Metadata:
    if metadata_json is None:
        return None
    return json.loads(metadata_json)


@dataclass(frozen=True)
class Document:
    id: int
    filepath: str
    sha256: str
    title: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    metadata: Metadata = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_row(cls, row: Row) -> "Document":
        return cls(
            id=row["id"],
            filepath=row["filepath"],
            sha256=row["sha256"],
            title=row["title"],
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass(frozen=True)
class ChunkInput:
    chunk_index: int
    content: str
    token_count: int = 0
    start_char: int | None = None
    end_char: int | None = None
    metadata: Metadata = None


@dataclass(frozen=True)
class Chunk:
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: int = 0
    start_char: int | None = None
    end_char: int | None = None
    metadata: Metadata = None
    created_at: str | None = None

    @classmethod
    def from_row(cls, row: Row) -> "Chunk":
        return cls(
            id=row["id"],
            document_id=row["document_id"],
            chunk_index=row["chunk_index"],
            content=row["content"],
            token_count=row["token_count"],
            start_char=row["start_char"],
            end_char=row["end_char"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class Summary:
    id: int
    document_id: int | None
    summary: str
    level: str = "document"
    token_count: int = 0
    metadata: Metadata = None
    created_at: str | None = None

    @classmethod
    def from_row(cls, row: Row) -> "Summary":
        return cls(
            id=row["id"],
            document_id=row["document_id"],
            summary=row["summary"],
            level=row["level"],
            token_count=row["token_count"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class Conversation:
    id: int
    role: str
    content: str
    metadata: Metadata = None
    created_at: str | None = None

    @classmethod
    def from_row(cls, row: Row) -> "Conversation":
        return cls(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
        )
