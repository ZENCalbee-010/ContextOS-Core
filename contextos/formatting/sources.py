# ---------------------------------------------------------------------------
# ไฟล์: formatting/sources.py
# หน้าที่: จัดรูปแบบข้อมูลแหล่งที่มา (source) ของ chunk
#          ให้อ่านง่ายสำหรับมนุษย์ (human-readable)
# ความรับผิดชอบ:
#   - format_source: รวม filepath, section, page/line เป็นข้อความเดียว
#   - preview_text: ตัดข้อความยาวให้สั้นลงสำหรับแสดงผลใน CLI
#   - _filepath_for_chunk: หา filepath จาก metadata หรือ repository
#   - _location: จัดรูปแบบข้อมูลตำแหน่ง (page number / line range)
# ความสัมพันธ์กับระบบ:
#   - ContextBuilder เรียก format_source เพื่อแสดง source ใน prompt
#   - ใช้ Chunk model และ SQLiteMemoryRepository จาก memory module
# ---------------------------------------------------------------------------
"""Shared source formatting for chunks."""

from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


def format_source(
    chunk: Chunk,
    repository: SQLiteMemoryRepository | None = None,
) -> str:
    """Format a chunk source as filepath, section, and page/line metadata."""

    metadata = chunk.metadata or {}
    # เริ่มจาก filepath เป็นส่วนแรกเสมอ
    parts = [_filepath_for_chunk(chunk, metadata, repository)]

    # เพิ่ม section ถ้ามี (เช่น ชื่อหัวข้อในเอกสาร)
    section = metadata.get("section")
    if section:
        parts.append(str(section))

    # เพิ่มตำแหน่ง (page/line) ถ้ามี
    location = _location(metadata)
    if location:
        parts.append(location)

    # รวมทุกส่วนด้วย comma เช่น "report.pdf, Introduction, page 3"
    return ", ".join(parts)


def preview_text(text: str, *, max_length: int = 160) -> str:
    """Normalize and truncate text for CLI previews."""

    # รวม whitespace ที่ซ้ำซ้อนเป็น space เดียว เพื่อให้แสดงผลเป็นบรรทัดเดียว
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    # ตัดที่ความยาวที่กำหนด แล้วเติม "..." ต่อท้าย
    return f"{normalized[: max_length - 3].rstrip()}..."


def _filepath_for_chunk(
    chunk: Chunk,
    metadata: dict,
    repository: SQLiteMemoryRepository | None,
) -> str:
    """
    หา filepath ของ chunk — ลำดับความสำคัญ:
    1. จาก metadata ของ chunk โดยตรง (เร็วที่สุด)
    2. จาก repository โดย lookup document_id (ถ้า metadata ไม่มี)
    3. fallback เป็น "document:{id}" ถ้าไม่พบจากทั้งสองแหล่ง
    """
    filepath = metadata.get("filepath")
    if filepath:
        return str(filepath)

    # Fallback: ค้นหา filepath จาก repository ผ่าน document_id
    if repository is not None:
        document = repository.get_document_by_id(chunk.document_id)
        if document is not None:
            return document.filepath

    # Fallback สุดท้าย: ใช้ document_id แทน filepath
    return f"document:{chunk.document_id}"


def _location(metadata: dict) -> str | None:
    """
    จัดรูปแบบข้อมูลตำแหน่งใน chunk
    - ถ้ามี page_number → "page 3"
    - ถ้ามี start_line / end_line → "lines 10-20" หรือ "line 10"
    - ถ้าไม่มีข้อมูลตำแหน่ง → None
    """
    page_number = metadata.get("page_number")
    if page_number is not None:
        return f"page {page_number}"

    start_line = metadata.get("start_line")
    end_line = metadata.get("end_line")
    if start_line is not None and end_line is not None:
        if start_line == end_line:
            return f"line {start_line}"
        return f"lines {start_line}-{end_line}"
    if start_line is not None:
        return f"line {start_line}"

    return None
