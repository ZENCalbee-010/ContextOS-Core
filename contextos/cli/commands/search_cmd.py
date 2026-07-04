# ===========================================================================
# ไฟล์: cli/commands/search_cmd.py
# หน้าที่: คำสั่ง `context search` - ค้นหา chunk ที่ import ไว้ด้วย BM25
# ความรับผิดชอบ: จัดการ flow การค้นหาข้อมูล:
#   1. รับ query จากผู้ใช้
#   2. ค้นหา chunk ด้วย BM25Retriever
#   3. แสดงผลลัพธ์พร้อมคะแนน แหล่งที่มา และ preview
# ความสัมพันธ์กับระบบ: ใช้งาน modules:
#   - SQLiteMemoryRepository: เข้าถึง chunk ทั้งหมดใน DB
#   - BM25Retriever: ค้นหาด้วยอัลกอริทึม BM25
#   - format_source, preview_text: จัดรูปแบบผลลัพธ์
# อัลกอริทึม BM25 (Best Matching 25):
#   เป็น ranking function สำหรับ information retrieval
#   ให้คะแนนเอกสารตามความถี่ของคำค้น (term frequency) และ
#   ความหายากของคำ (inverse document frequency)
#   ยิ่งคำค้นปรากฏบ่อยในเอกสารแต่หายากในเอกสารอื่น ยิ่งได้คะแนนสูง
# ===========================================================================
"""Search command backed by BM25 retrieval."""

from pathlib import Path

import typer

from contextos.config import DEFAULT_DB_PATH
# format_source: แสดงแหล่งที่มาของ chunk (ชื่อไฟล์ + ตำแหน่ง)
# preview_text: ตัดข้อความให้สั้นสำหรับแสดง preview บน terminal
from contextos.formatting import format_source, preview_text
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Retriever


def search_context(
    query: str = typer.Argument(..., help="Search query."),
    top_k: int = typer.Option(
        10,
        "--top-k",
        "--limit",
        "-n",
        help="Maximum number of results.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Search imported chunks using BM25."""

    # เตรียม repository และรัน BM25 search
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    results = BM25Retriever(repository).search(query, top_k=top_k)

    # กรณีไม่พบผลลัพธ์
    if not results:
        typer.echo("No results found.")
        return

    # แสดงผลลัพธ์แต่ละรายการพร้อม: คะแนน BM25, แหล่งที่มา, ข้อความ preview
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        typer.echo(f"[Result {index}]")
        typer.echo(f"Score: {result.score:.4f}")
        typer.echo(f"Source: {format_source(chunk, repository)}")
        typer.echo(f"Preview: {preview_text(chunk.content)}")
        # เว้นบรรทัดว่างระหว่างผลลัพธ์ (ยกเว้นรายการสุดท้าย)
        if index < len(results):
            typer.echo("")
