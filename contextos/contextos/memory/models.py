# =============================================================================
# memory/models.py — Dataclass Models สำหรับ Memory Records
# =============================================================================
# หน้าที่: นิยามโครงสร้างข้อมูล (data models) สำหรับ record ที่เก็บอยู่ใน
#   SQLite memory database ของ ContextOS
# ความรับผิดชอบ:
#   1. กำหนด dataclass สำหรับ Document, Chunk, ChunkInput, Summary, Conversation
#   2. จัดการ serialization/deserialization ของ metadata (JSON <-> dict)
#   3. แปลง sqlite3.Row กลับเป็น dataclass ผ่าน from_row() classmethod
# ความสัมพันธ์กับระบบ ContextOS:
#   - ถูกใช้โดย repository.py เป็น return type ของทุก CRUD operation
#   - ถูกใช้โดย retriever, ingestion pipeline, และ API layer
# Design Pattern:
#   - Frozen Dataclasses: ใช้ frozen=True เพื่อให้ instance เป็น immutable
#     ป้องกันการแก้ไขข้อมูลโดยไม่ตั้งใจหลังจากดึงจาก database แล้ว
#     (ถ้าต้องการเปลี่ยนค่า ต้องสร้าง instance ใหม่ด้วย dataclasses.replace())
#   - Metadata Type Alias: ใช้ type alias เพื่อให้ metadata field มี type
#     เดียวกันทุก model ลดการซ้ำซ้อนและ inconsistency
# =============================================================================
"""Dataclasses for SQLite memory records."""

from dataclasses import dataclass
# json ใช้สำหรับ encode/decode metadata dict <-> JSON string
# เพราะ SQLite ไม่รองรับ JSON type โดยตรง จึงเก็บเป็น TEXT field
import json
from sqlite3 import Row
from typing import Any


# ---------------------------------------------------------------------------
# Metadata Type Alias
# ---------------------------------------------------------------------------
# กำหนด type alias สำหรับ metadata ที่ใช้ทุก model
# เป็น dict[str, Any] หรือ None — ยืดหยุ่นพอจะเก็บ key-value อะไรก็ได้
# เช่น {"language": "th", "page": 5, "tags": ["intro", "summary"]}
# การใช้ type alias ช่วยให้แก้ไข type ได้จุดเดียวแล้วมีผลทุก model
Metadata = dict[str, Any] | None


# ---------------------------------------------------------------------------
# Helper Functions สำหรับ Metadata Serialization
# ---------------------------------------------------------------------------

def encode_metadata(metadata: Metadata) -> str | None:
    """แปลง metadata dict เป็น JSON string สำหรับเก็บลง SQLite
    จุดประสงค์: serialize dict -> JSON text เพื่อเก็บใน metadata_json column
    Input: metadata dict หรือ None
    Output: JSON string หรือ None
    หมายเหตุ: sort_keys=True ทำให้ JSON output เรียงตาม key เสมอ
      เพื่อให้ผลลัพธ์ deterministic (เปรียบเทียบง่าย, test ง่าย)
    """
    if metadata is None:
        return None
    return json.dumps(metadata, sort_keys=True)


def decode_metadata(metadata_json: str | None) -> Metadata:
    """แปลง JSON string กลับเป็น metadata dict
    จุดประสงค์: deserialize JSON text จาก database กลับเป็น Python dict
    Input: JSON string จาก metadata_json column หรือ None
    Output: dict หรือ None
    """
    if metadata_json is None:
        return None
    return json.loads(metadata_json)


# =============================================================================
# Document — แทนไฟล์เอกสารที่ถูก import เข้าระบบ
# =============================================================================
# ใช้ทำอะไร: เก็บข้อมูล metadata ของไฟล์ต้นฉบับ เช่น path, hash, ขนาด
# รับผิดชอบอะไร: เป็นตัวแทนของ 1 record ในตาราง documents
# ใช้เมื่อไร: เมื่อ import ไฟล์ใหม่ หรือ query ข้อมูลไฟล์ที่เคย import แล้ว
# ทำงานร่วมกับ: repository.py (upsert_document, get_document_by_*)
# sha256: ใช้ SHA-256 hash เพื่อตรวจจับ deduplication — ถ้าเนื้อหาเหมือนกัน
#   จะได้ hash เดียวกันแม้ชื่อไฟล์จะต่างกัน
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
        """สร้าง Document จาก sqlite3.Row — แปลง metadata_json กลับเป็น dict"""
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


# =============================================================================
# ChunkInput — ข้อมูล input สำหรับสร้าง Chunk ใหม่
# =============================================================================
# ใช้ทำอะไร: เป็น DTO (Data Transfer Object) ที่ส่งเข้า insert_chunks()
# รับผิดชอบอะไร: เก็บข้อมูลที่จำเป็นในการสร้าง chunk โดยยังไม่มี id
#   (เพราะ id จะถูกกำหนดโดย database หลัง INSERT)
# เหตุผลที่แยกจาก Chunk: Chunk มี id และ document_id ที่ได้จาก database
#   แต่ ChunkInput ยังไม่มีค่าเหล่านั้นในตอนที่สร้าง
# start_char, end_char: ตำแหน่งตัวอักษรในเอกสารต้นฉบับ ใช้สำหรับ
#   highlight หรือ trace กลับไปยังตำแหน่งเดิมในไฟล์
@dataclass(frozen=True)
class ChunkInput:
    chunk_index: int
    content: str
    token_count: int = 0
    start_char: int | None = None
    end_char: int | None = None
    metadata: Metadata = None


# =============================================================================
# Chunk — ท่อนข้อความที่ถูกแยกออกจาก Document
# =============================================================================
# ใช้ทำอะไร: แทน 1 record ในตาราง chunks ที่เก็บอยู่ใน database แล้ว
# รับผิดชอบอะไร: เก็บเนื้อหาข้อความ, ลำดับ, จำนวน token, และ metadata
# ใช้เมื่อไร: เมื่อดึง chunks จาก database เพื่อใช้ใน retrieval หรือ search
# ทำงานร่วมกับ: repository.py (insert_chunks, get_all_chunks, get_chunks_by_document)
# document_id: foreign key เชื่อมกลับไปหา Document ต้นทาง
# token_count: จำนวน token ของข้อความ — ใช้ควบคุมขนาด context window ของ LLM
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
        """สร้าง Chunk จาก sqlite3.Row — แปลง metadata_json กลับเป็น dict"""
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


# =============================================================================
# Summary — บทสรุประดับ Document หรือ Section
# =============================================================================
# ใช้ทำอะไร: เก็บบทสรุปที่สร้างจาก LLM หรือ extractive summarization
# รับผิดชอบอะไร: แทน 1 record ในตาราง summaries
# ใช้เมื่อไร: เมื่อต้องการดูภาพรวมของเอกสารโดยไม่ต้องอ่านทั้งหมด
# level: ระบุระดับของ summary เช่น 'document' (สรุปทั้งเอกสาร)
#   หรือ 'section' (สรุปเฉพาะส่วน)
# document_id: อาจเป็น None ได้สำหรับ summary ที่ไม่ผูกกับเอกสารใดเอกสารหนึ่ง
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
        """สร้าง Summary จาก sqlite3.Row"""
        return cls(
            id=row["id"],
            document_id=row["document_id"],
            summary=row["summary"],
            level=row["level"],
            token_count=row["token_count"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
        )


# =============================================================================
# Conversation — ประวัติการสนทนาระหว่าง User กับ Assistant
# =============================================================================
# ใช้ทำอะไร: เก็บ 1 ข้อความในประวัติสนทนา (ทั้ง user และ assistant)
# รับผิดชอบอะไร: แทน 1 record ในตาราง conversation_history
# ใช้เมื่อไร: เมื่อบันทึกหรือดึงประวัติสนทนาเพื่อสร้าง context ให้ LLM
# role: 'user' หรือ 'assistant' — ระบุว่าข้อความนี้ส่งมาจากใคร
# metadata: เก็บข้อมูลเพิ่มเติม เช่น model ที่ใช้, temperature, token usage
@dataclass(frozen=True)
class Conversation:
    id: int
    role: str
    content: str
    metadata: Metadata = None
    created_at: str | None = None

    @classmethod
    def from_row(cls, row: Row) -> "Conversation":
        """สร้าง Conversation จาก sqlite3.Row"""
        return cls(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            metadata=decode_metadata(row["metadata_json"]),
            created_at=row["created_at"],
        )
