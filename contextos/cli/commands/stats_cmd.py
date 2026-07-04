# ===========================================================================
# ไฟล์: cli/commands/stats_cmd.py
# หน้าที่: คำสั่ง `context stats` - แสดงสถิติ workspace ของ ContextOS
# ความรับผิดชอบ: ดึงและคำนวณ metrics ต่างๆ จากฐานข้อมูล:
#   - จำนวนเอกสารและ chunk ทั้งหมด
#   - จำนวน token ดั้งเดิมรวม
#   - อัตราส่วนการบีบอัดเฉลี่ย (จาก metadata ของ chunk)
#   - latency ของ query ล่าสุด (จาก conversation history)
# ความสัมพันธ์กับระบบ: ใช้งาน modules:
#   - SQLiteMemoryRepository: สร้างตาราง DB ถ้ายังไม่มี
#   - connect (memory.db): เชื่อมต่อ SQLite โดยตรงด้วย raw SQL
#   - average (evaluation): คำนวณค่าเฉลี่ย
# เหตุผลที่ต้องมี: ให้ผู้ใช้เห็นภาพรวมของ workspace
#   เช่น import ไปกี่ไฟล์แล้ว, compression ทำงานดีแค่ไหน
# หมายเหตุ: ไฟล์นี้ใช้ raw SQL queries โดยตรงแทนการผ่าน repository
#   เพราะเป็นการ query แบบ aggregate ที่ repository ไม่มี method รองรับ
# ===========================================================================
"""Stats command for the local ContextOS workspace."""

from pathlib import Path
import json

import typer

from contextos.config import DEFAULT_DB_PATH
# average: ฟังก์ชันคำนวณค่าเฉลี่ยที่จัดการกรณีรายการว่าง (คืน 0.0)
from contextos.evaluation import average
# connect: context manager สำหรับเชื่อมต่อ SQLite database โดยตรง
from contextos.memory.db import connect
from contextos.memory.repository import SQLiteMemoryRepository


def stats_context(
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Show local workspace statistics."""

    # โหลดสถิติทั้งหมดแล้วแสดงผล
    stats = load_stats(db_path)

    typer.echo(f"Total documents: {stats['total_documents']}")
    typer.echo(f"Total chunks: {stats['total_chunks']}")
    typer.echo(f"Total original tokens: {stats['total_original_tokens']}")
    typer.echo(f"Average compression ratio: {stats['average_compression_ratio']:.4f}")
    latest_latency = stats["latest_query_latency_ms"]
    if latest_latency is None:
        typer.echo("Latest query latency: unavailable")
    else:
        typer.echo(f"Latest query latency: {latest_latency:.2f} ms")


def load_stats(db_path: str | Path) -> dict:
    """โหลดสถิติ workspace ทั้งหมดจากฐานข้อมูล
    จุดประสงค์: รวม query ข้อมูลดิบและคำนวณ metrics ไว้ในที่เดียว
    Input: db_path - path ไปยัง SQLite database
    Output: dictionary ที่มี metrics ทั้ง 5 ตัว
    เหตุผลที่แยกเป็นฟังก์ชัน: ให้ module อื่น (เช่น test) เรียกใช้ได้
    """
    # สร้างตาราง DB ถ้ายังไม่มี (กรณี workspace ใหม่)
    SQLiteMemoryRepository(db_path).init_db()

    with connect(db_path) as connection:
        # ตาราง documents: เก็บข้อมูลไฟล์ที่ import (filepath, hash, etc.)
        total_documents = connection.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]

        # ตาราง chunks: เก็บเนื้อหาที่ถูกแบ่งเป็นส่วนย่อยพร้อม metadata
        total_chunks = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

        # COALESCE: คืน 0 ถ้าไม่มี chunk เลย (ป้องกัน NULL)
        total_original_tokens = connection.execute(
            "SELECT COALESCE(SUM(token_count), 0) FROM chunks"
        ).fetchone()[0]

        # ดึง metadata_json ของ chunk ทั้งหมดเพื่อคำนวณ compression ratio
        chunk_metadata = [
            row[0]
            for row in connection.execute(
                "SELECT metadata_json FROM chunks WHERE metadata_json IS NOT NULL"
            ).fetchall()
        ]

        # ดึง metadata_json จาก conversation history เพื่อหา latency ล่าสุด
        # ORDER BY id DESC: เรียงจากใหม่ไปเก่าเพื่อหา conversation ล่าสุด
        conversation_metadata = [
            row[0]
            for row in connection.execute(
                """
                SELECT metadata_json
                FROM conversation_history
                WHERE metadata_json IS NOT NULL
                ORDER BY id DESC
                """
            ).fetchall()
        ]

    return {
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "total_original_tokens": total_original_tokens,
        "average_compression_ratio": _average_compression_ratio(chunk_metadata),
        "latest_query_latency_ms": _latest_query_latency(conversation_metadata),
    }


def _average_compression_ratio(metadata_rows: list[str]) -> float:
    """คำนวณอัตราส่วนการบีบอัดเฉลี่ยจาก metadata ของ chunk ทุกตัว
    จุดประสงค์: วัดประสิทธิภาพรวมของการ compression ทั้ง workspace
    ขั้นตอน: วนลูปผ่าน metadata ของแต่ละ chunk
      -> ดึง compression_ratio จากทุกระดับ (light, medium, aggressive)
      -> คำนวณค่าเฉลี่ย
    โครงสร้าง metadata: { "compression": { "light": { "compression_ratio": 0.85, ... } } }
    """
    ratios: list[float] = []
    for metadata_json in metadata_rows:
        metadata = _decode(metadata_json)
        compression = metadata.get("compression", {})
        # วนทุก variant (light, medium, aggressive) และเก็บ ratio
        for variant in compression.values():
            if isinstance(variant, dict) and "compression_ratio" in variant:
                ratios.append(float(variant["compression_ratio"]))
    return average(ratios)


def _latest_query_latency(metadata_rows: list[str]) -> float | None:
    """หา latency ของ query ล่าสุดจาก conversation history
    จุดประสงค์: ให้ผู้ใช้ทราบความเร็วของ retrieval ครั้งล่าสุด
    ขั้นตอน: วนลูปจาก conversation ล่าสุดไปเก่าสุด
      -> คืนค่า latency_ms ตัวแรกที่เจอ (เพราะเรียงจากใหม่ไปเก่าแล้ว)
    Output: latency ในหน่วย millisecond หรือ None ถ้ายังไม่เคย query
    """
    for metadata_json in metadata_rows:
        metadata = _decode(metadata_json)
        latency = metadata.get("latency_ms")
        if latency is not None:
            return float(latency)
    return None


def _decode(metadata_json: str) -> dict:
    """แปลง JSON string เป็น dictionary อย่างปลอดภัย
    จุดประสงค์: จัดการกรณี JSON ไม่ถูกต้องหรือไม่ใช่ dict โดยไม่ crash
    เหตุผลที่ต้องมี: metadata_json ในฐานข้อมูลอาจเสียหายหรือเป็น format อื่น
    """
    try:
        value = json.loads(metadata_json)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
