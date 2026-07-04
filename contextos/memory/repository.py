# =============================================================================
# memory/repository.py — Repository Pattern สำหรับ ContextOS Memory
# =============================================================================
# หน้าที่: จัดเตรียม API สำหรับการอ่าน/เขียนข้อมูลลง SQLite database
#   โดยซ่อนรายละเอียดของ SQL queries ไว้ภายใน class
# ความรับผิดชอบ:
#   1. CRUD operations สำหรับ documents, chunks, และ conversation history
#   2. จัดการ upsert logic (insert หรือ update) สำหรับ documents
#   3. ตรวจสอบความถูกต้องของ foreign key ก่อนทำ operation
# ความสัมพันธ์กับระบบ ContextOS:
#   - เป็น data access layer ที่ถูกเรียกใช้โดย ingestion pipeline,
#     retriever, และ conversation manager
#   - ใช้ connect() จาก db.py เพื่อเปิด connection
#   - ใช้ model classes จาก models.py เป็น return type
# Design Pattern — Repository Pattern:
#   แยก data access logic ออกจาก business logic อย่างชัดเจน
#   ทำให้ SQLite access logic อยู่ในจุดเดียว และไม่รั่วไปยัง layer อื่น ๆ
#   caller ไม่ต้องรู้ว่าข้างในใช้ SQL อะไร แค่เรียก method ที่ต้องการ
# =============================================================================
"""Repository API for ContextOS local memory."""

from pathlib import Path
import sqlite3
# Iterable ใช้รับ input ที่เป็น list, generator, หรือ iterable อื่น ๆ ของ ChunkInput
from typing import Iterable

from contextos.config import DEFAULT_DB_PATH
from contextos.exceptions import MemoryError
# นำเข้า connection helpers จาก db.py — connect() ใช้เปิด connection,
# init_db (rename เป็น create_schema) ใช้สร้างตาราง
from contextos.memory.db import DatabasePath, connect, init_db as create_schema
# นำเข้า model classes ทั้งหมดที่ใช้เป็น return type และ input type
from contextos.memory.models import (
    Chunk,
    ChunkInput,
    Conversation,
    Document,
    Metadata,
    encode_metadata,
)


# =============================================================================
# SQLiteMemoryRepository
# =============================================================================
# ใช้ทำอะไร: เป็น repository class หลักที่จัดการข้อมูลทั้งหมดใน memory database
# รับผิดชอบอะไร: ซ่อน SQL queries ไว้ภายใน ให้ caller เรียกใช้ผ่าน method
# ใช้เมื่อไร: ทุกครั้งที่ต้องการอ่าน/เขียนข้อมูลลง memory database
# ทำงานร่วมกับ:
#   - db.py: ใช้ connect() เปิด connection
#   - models.py: ใช้ Document, Chunk, Conversation, etc. เป็น return type
#   - ingestion pipeline: เรียก upsert_document() และ insert_chunks()
#   - retriever: เรียก get_all_chunks(), get_chunks_by_document()
# =============================================================================
class SQLiteMemoryRepository:
    """Small sqlite3-backed repository for ContextOS memory records."""

    def __init__(self, db_path: DatabasePath = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self._all_chunks_cache: list[Chunk] | None = None
        self._all_chunks_signature: tuple[int, int | None] | None = None

    def init_db(self) -> None:
        """สร้างตารางและ indexes ใน database ถ้ายังไม่มี"""
        create_schema(self.db_path)
        self.clear_chunk_cache()

    # -------------------------------------------------------------------------
    # upsert_document — Insert หรือ Update เอกสาร
    # -------------------------------------------------------------------------
    # จุดประสงค์: บันทึกเอกสารใหม่ หรืออัปเดตเอกสารที่มีอยู่แล้ว
    # Input:
    #   - filepath: path ของไฟล์ต้นฉบับ
    #   - sha256: SHA-256 hash ของเนื้อหาไฟล์ (ใช้ตรวจ deduplication)
    #   - title, mime_type, size_bytes, metadata: ข้อมูลเพิ่มเติม (optional)
    # Output: Document object ที่บันทึกแล้ว (มี id จาก database)
    # ขั้นตอนการทำงาน:
    #   1. ค้นหา document ที่มี filepath หรือ sha256 ตรงกัน
    #   2. ถ้าทั้ง path และ hash ตรงกับ document คนละตัว → raise error
    #      (ป้องกัน data integrity violation)
    #   3. ถ้าพบ document เดิม → UPDATE
    #   4. ถ้าไม่พบ → INSERT ใหม่
    #   5. ดึง record ที่บันทึกแล้วกลับมาเป็น Document object
    # เหตุผลที่ใช้ upsert แทน insert/update แยก:
    #   ลดความซับซ้อนฝั่ง caller — ไม่ต้องตรวจสอบว่า document มีอยู่แล้วหรือไม่
    # -------------------------------------------------------------------------
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
            # ค้นหา document ที่มี filepath ตรงกัน
            path_row = connection.execute(
                "SELECT * FROM documents WHERE filepath = ?",
                (filepath_text,),
            ).fetchone()
            # ค้นหา document ที่มี sha256 hash ตรงกัน
            hash_row = connection.execute(
                "SELECT * FROM documents WHERE sha256 = ?",
                (sha256,),
            ).fetchone()

            # ถ้า filepath และ sha256 ชี้ไปที่ document คนละตัว
            # แสดงว่ามี data integrity issue — ต้อง raise error
            if path_row and hash_row and path_row["id"] != hash_row["id"]:
                raise MemoryError(
                    "filepath and sha256 belong to different documents"
                )

            existing = path_row or hash_row
            if existing:
                # อัปเดต document ที่มีอยู่แล้ว พร้อมตั้ง updated_at เป็นเวลาปัจจุบัน
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
                # ไม่พบ document เดิม → สร้างใหม่
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

            # ดึง record ที่เพิ่งบันทึกกลับมาเป็น Document object
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
            self.clear_chunk_cache()
            return Document.from_row(row)

    # -------------------------------------------------------------------------
    # insert_chunks — บันทึก chunks ของเอกสาร
    # -------------------------------------------------------------------------
    # จุดประสงค์: แทรก chunks (ท่อนข้อความ) ที่แยกออกจาก document ลง database
    # Input:
    #   - document_id: ID ของ document ที่ chunks เหล่านี้เป็นสมาชิก
    #   - chunks: iterable ของ ChunkInput objects
    #   - replace_existing: ถ้า True จะลบ chunks เดิมของ document นี้ก่อน insert
    # Output: list ของ Chunk objects ที่บันทึกแล้ว (เรียงตาม chunk_index)
    # เหตุผลที่ default replace_existing=True:
    #   เมื่อ re-import document ที่มีการแก้ไข ต้องแทนที่ chunks เดิมทั้งหมด
    #   เพื่อให้ข้อมูลตรงกับเนื้อหาล่าสุด
    # -------------------------------------------------------------------------
    def insert_chunks(
        self,
        document_id: int,
        chunks: Iterable[ChunkInput],
        *,
        replace_existing: bool = True,
    ) -> list[Chunk]:
        chunk_list = list(chunks)

        with connect(self.db_path) as connection:
            # ตรวจสอบว่า document_id มีอยู่จริงก่อน — ป้องกัน orphan chunks
            self._require_document(connection, document_id)

            # ลบ chunks เดิมทั้งหมดของ document นี้ก่อน insert ใหม่
            if replace_existing:
                connection.execute(
                    "DELETE FROM chunks WHERE document_id = ?",
                    (document_id,),
                )

            connection.executemany(
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
                [
                    (
                        document_id,
                        chunk.chunk_index,
                        chunk.content,
                        chunk.token_count,
                        chunk.start_char,
                        chunk.end_char,
                        encode_metadata(chunk.metadata),
                    )
                    for chunk in chunk_list
                ],
            )

            # ดึง chunks ทั้งหมดของ document นี้กลับมา เรียงตามลำดับ
            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document_id,),
            ).fetchall()
            chunks = [Chunk.from_row(row) for row in rows]
            self.clear_chunk_cache()
            return chunks

    # -------------------------------------------------------------------------
    # Document Query Methods — ค้นหา Document ด้วยเงื่อนไขต่าง ๆ
    # -------------------------------------------------------------------------
    # มี 3 วิธีค้นหา: ตาม filepath, ตาม SHA-256 hash, หรือตาม id
    # ทั้งหมดคืน Document | None — คืน None ถ้าไม่พบ
    # -------------------------------------------------------------------------

    def get_document_by_path(self, filepath: str | Path) -> Document | None:
        """ค้นหา document จาก filepath — ใช้ตอนตรวจสอบว่า import ไฟล์นี้แล้วหรือยัง"""
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE filepath = ?",
                (str(filepath),),
            ).fetchone()
            return Document.from_row(row) if row else None

    def get_document_by_hash(self, sha256: str) -> Document | None:
        """ค้นหา document จาก SHA-256 hash — ใช้ตรวจ deduplication ของเนื้อหา"""
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE sha256 = ?",
                (sha256,),
            ).fetchone()
            return Document.from_row(row) if row else None

    def get_document_by_id(self, document_id: int) -> Document | None:
        """ค้นหา document จาก primary key id"""
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
            return Document.from_row(row) if row else None

    # -------------------------------------------------------------------------
    # Chunk Query Methods — ดึง Chunks จาก Database
    # -------------------------------------------------------------------------

    def get_all_chunks(self) -> list[Chunk]:
        """ดึง chunks ทั้งหมดในระบบ เรียงตาม document_id และ chunk_index
        ใช้ใน full-text search หรือ BM25 ranking ที่ต้องสแกนทุก chunk
        """
        signature = self.get_chunk_cache_signature()
        if self._all_chunks_cache is not None and self._all_chunks_signature == signature:
            return list(self._all_chunks_cache)

        with connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                ORDER BY document_id ASC, chunk_index ASC
                """
            ).fetchall()
            chunks = [Chunk.from_row(row) for row in rows]
            self._all_chunks_cache = chunks
            self._all_chunks_signature = signature
            return list(chunks)

    def get_chunks_by_document(self, document_id: int) -> list[Chunk]:
        """ดึง chunks ทั้งหมดของ document เดียว เรียงตามลำดับ chunk_index
        ใช้เมื่อต้องการอ่านเนื้อหาทั้งหมดของเอกสารที่ระบุ
        """
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

    # -------------------------------------------------------------------------
    # update_chunk_metadata — อัปเดต metadata ของ chunk
    # -------------------------------------------------------------------------
    # จุดประสงค์: แก้ไขเฉพาะ metadata ของ chunk โดยไม่แก้ content
    # ใช้เมื่อ: ต้องการเพิ่ม tags หรือ metadata อื่น ๆ
    #   ให้กับ chunk ที่มีอยู่แล้ว โดยไม่ต้อง re-import ทั้ง document
    # -------------------------------------------------------------------------
    def update_chunk_metadata(self, chunk_id: int, metadata: Metadata) -> Chunk:
        with connect(self.db_path) as connection:
            # ตรวจสอบว่า chunk_id มีอยู่จริง ก่อนทำ update
            self._require_chunk(connection, chunk_id)
            connection.execute(
                """
                UPDATE chunks
                SET metadata_json = ?
                WHERE id = ?
                """,
                (encode_metadata(metadata), chunk_id),
            )
            # ดึง record ที่อัปเดตแล้วกลับมา
            row = connection.execute(
                "SELECT * FROM chunks WHERE id = ?",
                (chunk_id,),
            ).fetchone()
            self.clear_chunk_cache()
            return Chunk.from_row(row)

    # -------------------------------------------------------------------------
    # save_conversation — บันทึกข้อความสนทนา
    # -------------------------------------------------------------------------
    # จุดประสงค์: บันทึก 1 ข้อความลงตาราง conversation_history
    # Input:
    #   - role: 'user' หรือ 'assistant'
    #   - content: เนื้อหาข้อความ
    #   - metadata: ข้อมูลเพิ่มเติม เช่น model, temperature, token usage
    # Output: Conversation object ที่บันทึกแล้ว
    # เหตุผลที่เก็บ conversation: เพื่อให้ ContextOS สามารถสร้าง context
    #   จากประวัติสนทนาก่อนหน้า ส่งต่อให้ LLM ในรอบถัดไป
    # -------------------------------------------------------------------------
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

    def clear_chunk_cache(self) -> None:
        """Clear cached chunk rows after writes."""
        self._all_chunks_cache = None
        self._all_chunks_signature = None

    def get_chunk_cache_signature(self) -> tuple[int, int | None]:
        """Return a cheap signature used to invalidate chunk and BM25 caches."""
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS chunk_count, MAX(id) AS max_chunk_id FROM chunks"
            ).fetchone()
            return int(row["chunk_count"]), row["max_chunk_id"]

    # -------------------------------------------------------------------------
    # Internal Validation Methods — ตรวจสอบว่า record มีอยู่จริง
    # -------------------------------------------------------------------------
    # เหตุผลที่ต้องตรวจ: ป้องกันการ INSERT/UPDATE ที่อ้างอิง id ที่ไม่มีอยู่จริง
    # ใช้ underscore prefix (_) เพื่อระบุว่าเป็น private method
    # ไม่ควรถูกเรียกจากภายนอก class
    # -------------------------------------------------------------------------

    def _require_document(
        self,
        connection: sqlite3.Connection,
        document_id: int,
    ) -> None:
        """ตรวจสอบว่า document_id มีอยู่จริง — raise ValueError ถ้าไม่พบ"""
        row = connection.execute(
            "SELECT id FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            raise MemoryError(f"document_id does not exist: {document_id}")

    def _require_chunk(
        self,
        connection: sqlite3.Connection,
        chunk_id: int,
    ) -> None:
        """ตรวจสอบว่า chunk_id มีอยู่จริง — raise ValueError ถ้าไม่พบ"""
        row = connection.execute(
            "SELECT id FROM chunks WHERE id = ?",
            (chunk_id,),
        ).fetchone()
        if row is None:
            raise MemoryError(f"chunk_id does not exist: {chunk_id}")


# ---------------------------------------------------------------------------
# Convenience function — ฟังก์ชันช่วยสำหรับสร้าง database schema
# ---------------------------------------------------------------------------
# จุดประสงค์: ให้ caller สร้าง schema ได้ง่ายโดยไม่ต้อง instantiate repository เอง
# ใช้เมื่อ: ตอน application startup หรือใน CLI command เช่น `contextos init`
# ---------------------------------------------------------------------------
def init_db(db_path: DatabasePath = DEFAULT_DB_PATH) -> None:
    SQLiteMemoryRepository(db_path).init_db()
