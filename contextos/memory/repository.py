"""Repository API for ContextOS local memory."""

from pathlib import Path
import sqlite3
from typing import Iterable

from contextos.config import DEFAULT_DB_PATH
from contextos.memory.db import DatabasePath, connect, init_db as create_schema
from contextos.memory.models import (
    Chunk,
    ChunkInput,
    Conversation,
    Document,
    Metadata,
    encode_metadata,
)


class SQLiteMemoryRepository:
    """Small sqlite3-backed repository for ContextOS memory records."""

    def __init__(self, db_path: DatabasePath = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def init_db(self) -> None:
        create_schema(self.db_path)

    def upsert_document(
        self,
        filepath: str | Path,
        sha256: str,
        *,
        title: str | None = None,
        mime_type: str | None = None,
        size_bytes: int | None = None,
        metadata: Metadata = None,
    ) -> Document:
        filepath_text = str(filepath)
        metadata_json = encode_metadata(metadata)

        with connect(self.db_path) as connection:
            path_row = connection.execute(
                "SELECT * FROM documents WHERE filepath = ?",
                (filepath_text,),
            ).fetchone()
            hash_row = connection.execute(
                "SELECT * FROM documents WHERE sha256 = ?",
                (sha256,),
            ).fetchone()

            if path_row and hash_row and path_row["id"] != hash_row["id"]:
                raise ValueError(
                    "filepath and sha256 belong to different documents"
                )

            existing = path_row or hash_row
            if existing:
                connection.execute(
                    """
                    UPDATE documents
                    SET filepath = ?,
                        sha256 = ?,
                        title = ?,
                        mime_type = ?,
                        size_bytes = ?,
                        metadata_json = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        filepath_text,
                        sha256,
                        title,
                        mime_type,
                        size_bytes,
                        metadata_json,
                        existing["id"],
                    ),
                )
                document_id = existing["id"]
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO documents (
                        filepath,
                        sha256,
                        title,
                        mime_type,
                        size_bytes,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        filepath_text,
                        sha256,
                        title,
                        mime_type,
                        size_bytes,
                        metadata_json,
                    ),
                )
                document_id = cursor.lastrowid

            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
            return Document.from_row(row)

    def insert_chunks(
        self,
        document_id: int,
        chunks: Iterable[ChunkInput],
        *,
        replace_existing: bool = True,
    ) -> list[Chunk]:
        chunk_list = list(chunks)

        with connect(self.db_path) as connection:
            self._require_document(connection, document_id)

            if replace_existing:
                connection.execute(
                    "DELETE FROM chunks WHERE document_id = ?",
                    (document_id,),
                )

            for chunk in chunk_list:
                connection.execute(
                    """
                    INSERT INTO chunks (
                        document_id,
                        chunk_index,
                        content,
                        token_count,
                        start_char,
                        end_char,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        chunk.chunk_index,
                        chunk.content,
                        chunk.token_count,
                        chunk.start_char,
                        chunk.end_char,
                        encode_metadata(chunk.metadata),
                    ),
                )

            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document_id,),
            ).fetchall()
            return [Chunk.from_row(row) for row in rows]

    def get_document_by_path(self, filepath: str | Path) -> Document | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE filepath = ?",
                (str(filepath),),
            ).fetchone()
            return Document.from_row(row) if row else None

    def get_document_by_hash(self, sha256: str) -> Document | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE sha256 = ?",
                (sha256,),
            ).fetchone()
            return Document.from_row(row) if row else None

    def get_document_by_id(self, document_id: int) -> Document | None:
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
            return Document.from_row(row) if row else None

    def get_all_chunks(self) -> list[Chunk]:
        with connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                ORDER BY document_id ASC, chunk_index ASC
                """
            ).fetchall()
            return [Chunk.from_row(row) for row in rows]

    def get_chunks_by_document(self, document_id: int) -> list[Chunk]:
        with connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document_id,),
            ).fetchall()
            return [Chunk.from_row(row) for row in rows]

    def update_chunk_metadata(self, chunk_id: int, metadata: Metadata) -> Chunk:
        with connect(self.db_path) as connection:
            self._require_chunk(connection, chunk_id)
            connection.execute(
                """
                UPDATE chunks
                SET metadata_json = ?
                WHERE id = ?
                """,
                (encode_metadata(metadata), chunk_id),
            )
            row = connection.execute(
                "SELECT * FROM chunks WHERE id = ?",
                (chunk_id,),
            ).fetchone()
            return Chunk.from_row(row)

    def save_conversation(
        self,
        role: str,
        content: str,
        *,
        metadata: Metadata = None,
    ) -> Conversation:
        with connect(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO conversation_history (role, content, metadata_json)
                VALUES (?, ?, ?)
                """,
                (role, content, encode_metadata(metadata)),
            )
            row = connection.execute(
                "SELECT * FROM conversation_history WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return Conversation.from_row(row)

    def _require_document(
        self,
        connection: sqlite3.Connection,
        document_id: int,
    ) -> None:
        row = connection.execute(
            "SELECT id FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"document_id does not exist: {document_id}")

    def _require_chunk(
        self,
        connection: sqlite3.Connection,
        chunk_id: int,
    ) -> None:
        row = connection.execute(
            "SELECT id FROM chunks WHERE id = ?",
            (chunk_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"chunk_id does not exist: {chunk_id}")


def init_db(db_path: DatabasePath = DEFAULT_DB_PATH) -> None:
    SQLiteMemoryRepository(db_path).init_db()
