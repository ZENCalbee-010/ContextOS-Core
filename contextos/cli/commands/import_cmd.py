# ===========================================================================
# ไฟล์: cli/commands/import_cmd.py
# หน้าที่: คำสั่ง `context import` - นำเข้าไฟล์/โฟลเดอร์เข้าสู่ ContextOS workspace
# ความรับผิดชอบ: จัดการ pipeline การนำเข้าไฟล์ทั้งหมด:
#   1. ตรวจสอบว่า path ที่ระบุมีอยู่จริง (path validation)
#   2. สแกนหาไฟล์ที่รองรับ (file scanning + reader detection)
#   3. สร้าง FileIndexer สำหรับแบ่ง chunk และจัดเก็บ (indexing pipeline)
#   4. แสดงสรุปผลการนำเข้า (summary output)
# ความสัมพันธ์กับระบบ: ใช้งาน modules:
#   - SQLiteMemoryRepository: จัดเก็บเอกสารและ chunk ลง SQLite
#   - FileIndexer: อ่านไฟล์ แบ่ง chunk และเก็บลง repository
#   - get_reader: ตรวจสอบว่าไฟล์ประเภทนี้มี reader รองรับหรือไม่
# เหตุผลที่ต้องมี: เป็นจุดเริ่มต้นของทุก workflow ใน ContextOS
#   ผู้ใช้ต้อง import ข้อมูลก่อนจึงจะ search, ask, optimize ได้
# ===========================================================================
"""Import command for local ContextOS files."""

from pathlib import Path

import typer

from contextos.cli.console import print_success, progress_iter
from contextos.config import DEFAULT_DB_PATH
# FileIndexer: ตัวจัดการการแบ่งไฟล์เป็น chunk และจัดเก็บลง DB
# IndexResult: ผลลัพธ์จากการ index แต่ละไฟล์ (status, chunk_count, token_count)
from contextos.indexer import FileIndexer, IndexResult
from contextos.memory.repository import SQLiteMemoryRepository
# get_reader: ฟังก์ชันที่ตรวจสอบนามสกุลไฟล์และคืน reader ที่เหมาะสม
# คืน None ถ้าเป็นไฟล์ที่ไม่รองรับ (เช่น .exe, .dll)
from contextos.readers import get_reader


def import_context(
    path: Path = typer.Argument(
        Path("."),
        help="File or directory to import.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
    max_tokens: int = typer.Option(
        400,
        "--max-tokens",
        help="Maximum tokens per parsed chunk.",
    ),
) -> None:
    """Import a file or folder into the local SQLite memory store."""

    # ตรวจสอบว่า path ที่ผู้ใช้ระบุมีอยู่จริงบนระบบไฟล์
    if not path.exists():
        raise typer.BadParameter(f"path does not exist: {path}")

    # สแกนหาไฟล์ที่มี reader รองรับ (กรองไฟล์ที่อ่านไม่ได้ออก)
    files = list(_iter_supported_files(path))

    # เตรียม repository และ indexer
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()
    indexer = FileIndexer(repository, max_tokens_per_chunk=max_tokens)

    # index แต่ละไฟล์: อ่าน -> แบ่ง chunk -> เก็บลง DB
    results = [
        indexer.index_file(file_path)
        for file_path in progress_iter(files, "Importing files")
    ]

    # นับสรุปผลลัพธ์
    imported = _count(results, "imported")
    skipped = _count(results, "skipped")
    total_chunks = sum(result.chunk_count for result in results)
    total_tokens = sum(result.token_count for result in results)

    # แสดงสรุปให้ผู้ใช้ทราบ
    print_success("Import complete.")
    typer.echo(f"Imported files: {imported}")
    typer.echo(f"Skipped files: {skipped}")
    typer.echo(f"Total chunks: {total_chunks}")
    typer.echo(f"Total tokens: {total_tokens}")


def _iter_supported_files(path: Path) -> list[Path]:
    """สแกนหาไฟล์ที่ ContextOS รองรับ
    จุดประสงค์: กรองเฉพาะไฟล์ที่มี reader เหมาะสม
    Input: path - ไฟล์เดียวหรือ directory
    Output: รายการ Path ของไฟล์ที่รองรับ
    ขั้นตอน: ถ้าเป็นไฟล์เดียว -> ตรวจว่ามี reader หรือไม่
             ถ้าเป็น directory -> rglob('*') สแกนทุกไฟล์แบบ recursive แล้วกรอง
    """
    if path.is_file():
        return [path] if get_reader(path) is not None else []

    # sorted() เพื่อให้ลำดับการ import คงที่ (deterministic)
    return [
        file_path
        for file_path in sorted(path.rglob("*"))
        if file_path.is_file() and get_reader(file_path) is not None
    ]


def _count(results: list[IndexResult], status: str) -> int:
    """นับจำนวนผลลัพธ์ที่มีสถานะตรงกับที่ระบุ
    จุดประสงค์: ใช้นับจำนวนไฟล์ที่ imported หรือ skipped
    """
    return sum(1 for result in results if result.status == status)
