# ===========================================================================
# ไฟล์: cli/commands/optimize_cmd.py
# หน้าที่: คำสั่ง `context optimize` - ปรับปรุง compression metadata ของเอกสาร
# ความรับผิดชอบ: จัดการ pipeline การบีบอัดข้อมูลซ้ำ:
#   1. ค้นหาเอกสารเป้าหมายจาก ID หรือ filepath (target resolution)
#   2. ดึง chunk ทั้งหมดของเอกสารนั้น
#   3. รัน compression ระดับที่เลือกกับแต่ละ chunk (compression)
#   4. อัปเดต metadata ใน DB (metadata update)
#   5. แสดงสถิติการลด token (stats output)
# ความสัมพันธ์กับระบบ: ใช้งาน modules:
#   - SQLiteMemoryRepository: อ่านและอัปเดต chunk metadata
#   - Compressor (Light/Medium/Aggressive): บีบอัดเนื้อหาแต่ละระดับ
# เหตุผลที่ต้องมี: ลด token ที่ใช้ในการส่ง context ให้ AI
#   ยิ่งบีบอัดมาก ยิ่งใส่ context ได้มากขึ้นภายใน budget เดียวกัน
# Design Pattern: Strategy Pattern - เลือก compressor ตามระดับที่ต้องการ
#   Light: ลบ whitespace ซ้ำ, Medium: ลบ stop words, Aggressive: สรุปเนื้อหา
# ===========================================================================
"""Optimize stored chunk compression metadata."""

from pathlib import Path
from typing import Literal
import re

import typer

# นำเข้า compressor ทั้ง 3 ระดับ - แต่ละตัวใช้กลยุทธ์การบีบอัดต่างกัน
# BaseCompressor เป็น abstract base class สำหรับ polymorphism
from contextos.compression import (
    AggressiveCompressor,
    BaseCompressor,
    LightCompressor,
    MediumCompressor,
)
from contextos.config import DEFAULT_DB_PATH
from contextos.memory.models import Document
from contextos.memory.repository import SQLiteMemoryRepository


# Type alias สำหรับระดับ compression ที่รองรับ
# ใช้ Literal เพื่อให้ Typer สร้าง validation อัตโนมัติ
CompressionLevel = Literal["light", "medium", "aggressive"]


def optimize_context(
    target: str = typer.Argument(
        ...,
        help="Document id or filepath to optimize.",
    ),
    level: CompressionLevel = typer.Option(
        "light",
        "--level",
        "-l",
        help="Compression level to re-run.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Re-run a rule-based compression level for one document's chunks."""

    # เตรียม repository และค้นหาเอกสารเป้าหมาย
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    document = _resolve_document(repository, target)
    if document is None:
        raise typer.BadParameter(f"document not found: {target}")

    # ดึง chunk ทั้งหมดของเอกสารที่เลือก
    chunks = repository.get_chunks_by_document(document.id)
    compressor = _compressor(level)

    # เก็บ token ก่อนบีบอัดเพื่อคำนวณ token reduction
    before_tokens = sum(chunk.token_count for chunk in chunks)
    after_tokens = 0
    ratios: list[float] = []

    for chunk in chunks:
        # บีบอัดเนื้อหาของแต่ละ chunk ด้วย compressor ที่เลือก
        result = compressor.compress(chunk.content)
        compressed_tokens = _count_tokens(result.compressed)
        after_tokens += compressed_tokens
        ratios.append(result.compression_ratio)

        # อัปเดต metadata โดยเก็บผลลัพธ์การบีบอัดแต่ละระดับแยกกัน
        # โครงสร้าง: metadata.compression.{level} = { content, ratio, ... }
        # เก็บแยกระดับเพื่อให้เปรียบเทียบประสิทธิภาพแต่ละระดับได้
        metadata = dict(chunk.metadata or {})
        compression = dict(metadata.get("compression") or {})
        compression[level] = {
            "content": result.compressed,
            "compression_ratio": result.compression_ratio,
            "original_length": result.original_length,
            "compressed_length": result.compressed_length,
            "original_tokens": chunk.token_count,
            "compressed_tokens": compressed_tokens,
        }
        metadata["compression"] = compression
        repository.update_chunk_metadata(chunk.id, metadata)

    # คำนวณสถิติสรุป
    # average_ratio: อัตราส่วนการบีบอัดเฉลี่ย (0 = ลดได้ทั้งหมด, 1 = ไม่ลดเลย)
    # token_reduction: สัดส่วน token ที่ลดได้ (เช่น 0.30 = ลดได้ 30%)
    average_ratio = sum(ratios) / len(ratios) if ratios else 0.0
    token_reduction = 1 - (after_tokens / before_tokens) if before_tokens else 0.0

    # แสดงสรุปผลการ optimize ให้ผู้ใช้
    typer.echo(f"Document: {document.filepath}")
    typer.echo(f"Compression level: {level}")
    typer.echo(f"Chunks optimized: {len(chunks)}")
    typer.echo(f"Tokens before: {before_tokens}")
    typer.echo(f"Tokens after: {after_tokens}")
    typer.echo(f"Token reduction: {token_reduction:.4f}")
    typer.echo(f"Compression ratio: {average_ratio:.4f}")
    typer.echo(f"Average compression ratio: {average_ratio:.4f}")


def _resolve_document(
    repository: SQLiteMemoryRepository,
    target: str,
) -> Document | None:
    """ค้นหาเอกสารเป้าหมายจาก ID หรือ filepath
    จุดประสงค์: ให้ผู้ใช้ระบุเอกสารได้ทั้งด้วยตัวเลข ID หรือ path ของไฟล์
    Input: target - string ที่อาจเป็นตัวเลข (ID) หรือ path
    Output: Document object หรือ None ถ้าไม่พบ
    """
    if target.isdigit():
        return repository.get_document_by_id(int(target))
    return repository.get_document_by_path(target)


def _compressor(level: CompressionLevel) -> BaseCompressor:
    """Factory function สร้าง compressor ตามระดับที่เลือก (Strategy Pattern)
    จุดประสงค์: แยก logic การเลือก compressor ออกจากฟังก์ชันหลัก
    เหตุผลที่ต้องมี: ทำให้เพิ่มระดับ compression ใหม่ได้ง่าย
    """
    if level == "light":
        return LightCompressor()
    if level == "medium":
        return MediumCompressor()
    return AggressiveCompressor()


def _count_tokens(text: str) -> int:
    """นับจำนวน token แบบง่ายโดยนับคำที่ไม่ใช่ whitespace
    จุดประสงค์: ประมาณจำนวน token หลังบีบอัด
    เหตุผลที่ใช้ regex แทน tokenizer จริง: เร็วกว่ามากและไม่ต้องโหลด model
    \\S+ จับ sequence ของอักขระที่ไม่ใช่ whitespace เป็น 1 token
    """
    return len(re.findall(r"\S+", text))
