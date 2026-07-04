# ---------------------------------------------------------------------------
# ไฟล์: indexer/indexer.py
# หน้าที่: Pipeline หลักสำหรับ index ไฟล์เข้าสู่ระบบ ContextOS
# ความรับผิดชอบ:
#   - อ่านไฟล์ → คำนวณ hash → ตรวจสอบว่าเคย index แล้วหรือไม่
#   - parse เนื้อหาเป็น chunks → extract keywords → compress variants
#   - persist ลงฐานข้อมูล SQLite ผ่าน Repository Pattern
# Design Pattern: Pipeline Pattern
#   ขั้นตอนการ index: hash check → read → parse → extract keywords
#                     → compress variants → persist
#   แต่ละขั้นตอนรับ input จากขั้นตอนก่อนหน้า และส่งต่อให้ขั้นตอนถัดไป
# ความสัมพันธ์กับระบบ:
#   - ใช้ sha256_file จาก hasher module
#   - ใช้ readers, parsers, compression modules
#   - เก็บข้อมูลผ่าน SQLiteMemoryRepository (Repository Pattern)
# ---------------------------------------------------------------------------
"""Incremental file indexing pipeline."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal

# นำเข้า Compressor ทั้ง 3 ระดับ สำหรับสร้าง compressed variants ของแต่ละ chunk
# Strategy Pattern ย่อย — เลือกระดับการบีบอัดตามความต้องการ
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


# IndexStatus: ผลลัพธ์ที่เป็นไปได้จากการ index ไฟล์
# - "imported": index สำเร็จ (ไฟล์ใหม่หรืออัปเดต)
# - "skipped": ไฟล์ไม่เปลี่ยนแปลง (hash ตรงกัน) → ข้ามไป
# - "unsupported": ประเภทไฟล์ไม่รองรับ
# - "error": เกิดข้อผิดพลาด
IndexStatus = Literal["imported", "skipped", "unsupported", "error"]


# IndexResult: เก็บผลลัพธ์การ index ไฟล์เดียว
# frozen=True → immutable เพื่อความปลอดภัยของข้อมูล
@dataclass(frozen=True)
class IndexResult:
    status: IndexStatus            # สถานะการ index
    filepath: str                  # เส้นทางไฟล์ที่ index
    sha256: str | None = None      # SHA-256 hash ของไฟล์
    document_id: int | None = None # ID ของ document ในฐานข้อมูล
    chunk_count: int = 0           # จำนวน chunks ที่สร้างจากไฟล์
    token_count: int = 0           # จำนวน tokens รวมทั้งหมด
    error: str | None = None       # ข้อความ error (ถ้ามี)


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
        # max_tokens_per_chunk: จำกัดขนาด chunk เพื่อให้พอดีกับ token budget
        self.max_tokens_per_chunk = max_tokens_per_chunk
        # keyword_limit: จำนวน keyword สูงสุดที่จะ extract จากข้อความ
        self.keyword_limit = keyword_limit

    def index_file(self, path: str | Path) -> IndexResult:
        """
        Pipeline หลักของการ index ไฟล์เดียว
        ขั้นตอน:
        1. คำนวณ SHA-256 hash
        2. ตรวจสอบว่า hash ซ้ำกับที่มีในฐานข้อมูลหรือไม่ (skip ถ้าซ้ำ)
        3. อ่านไฟล์ด้วย reader ที่เหมาะสม
        4. Parse เป็น chunks
        5. Extract keywords + compress variants
        6. Persist ลงฐานข้อมูล
        """
        file_path = Path(path)
        filepath = str(file_path)

        # ขั้นตอนที่ 1: คำนวณ SHA-256 hash ของไฟล์
        try:
            sha256 = sha256_file(file_path)
        except OSError as exc:
            return IndexResult(status="error", filepath=filepath, error=str(exc))

        # ขั้นตอนที่ 2: ตรวจสอบว่าไฟล์เคย index แล้วหรือยัง
        # ถ้า hash ตรงกัน → ไฟล์ไม่เปลี่ยน → ข้ามการ re-index (ประหยัดเวลา)
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

        # ขั้นตอนที่ 3: อ่านไฟล์ — ตรวจสอบว่ารองรับประเภทไฟล์หรือไม่
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

        # ขั้นตอนที่ 4: Parse เนื้อหาเป็น chunks ตามประเภทไฟล์
        parser = self._parser_for_reader(read_result.metadata.get("reader"))
        parsed_chunks = parser.parse(read_result.text)

        # ขั้นตอนที่ 5: Extract keywords สำหรับระดับ document
        document_keywords = self._keywords(read_result.text)
        structural_sections = [
            chunk.section for chunk in parsed_chunks if chunk.section is not None
        ]

        # ขั้นตอนที่ 6: Persist ลงฐานข้อมูล — upsert document แล้ว insert chunks
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
        """เลือก parser ที่เหมาะสมตามประเภท reader — code ใช้ CodeParser, อื่น ๆ ใช้ TextParser"""
        if reader_name == "code":
            return CodeParser(max_tokens=self.max_tokens_per_chunk)
        return TextParser(max_tokens=self.max_tokens_per_chunk)

    def _to_chunk_input(self, chunk: ParsedChunk) -> ChunkInput:
        """แปลง ParsedChunk เป็น ChunkInput พร้อม metadata เพิ่มเติม (keywords + compressed variants)"""
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
        """
        สร้าง compressed variants 3 ระดับ (Light, Medium, Aggressive)
        สำหรับแต่ละ chunk — ใช้ในการเลือกระดับการบีบอัดที่เหมาะสม
        ตาม token budget ที่มีอยู่
        """
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
        """
        Extract keywords จากข้อความ — ใช้สำหรับ metadata ของ document/chunk
        วิธีการ:
        1. ดึงคำที่มี 3 ตัวอักษรขึ้นไป (regex: ขึ้นต้นด้วยตัวอักษร)
        2. กรอง stopwords ออก (คำทั่วไปที่ไม่มีความหมายเฉพาะ)
        3. นับความถี่แล้วเรียงจากมากไปน้อย
        4. คืนค่า keyword_limit อันดับแรก
        """
        words = [
            word.lower()
            for word in re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text)
            if word.lower() not in STOPWORDS
        ]
        counts = Counter(words)
        # เรียงตามความถี่ (มากไปน้อย) แล้วตามตัวอักษร (ถ้าเท่ากัน)
        return [
            word
            for word, _count in sorted(
                counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[: self.keyword_limit]
        ]

    def _mime_type(self, reader_name: object) -> str | None:
        """แปลงชื่อ reader เป็น MIME type มาตรฐาน สำหรับเก็บใน metadata ของ document"""
        return {
            "text": "text/plain",
            "code": "text/plain",
            "pdf": "application/pdf",
            "docx": (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        }.get(reader_name)


# STOPWORDS: ชุดคำทั่วไปในภาษาอังกฤษที่จะถูกกรองออกจากการ extract keywords
# เพราะคำเหล่านี้ไม่ช่วยในการระบุเนื้อหาของเอกสาร
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
