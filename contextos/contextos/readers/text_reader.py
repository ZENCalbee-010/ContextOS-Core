# ---------------------------------------------------------------------------
# readers/text_reader.py — Reader สำหรับอ่านไฟล์ข้อความธรรมดาและ Markdown
# ---------------------------------------------------------------------------
# หน้าที่ : อ่านไฟล์ .txt, .md, .markdown แล้วส่งข้อความดิบพร้อม metadata
# ความรับผิดชอบ :
#   - อ่านไฟล์เป็น UTF-8
#   - ระบุรูปแบบ (format) ว่าเป็น "text" หรือ "markdown" ใน metadata
# ความสัมพันธ์กับระบบ :
#   - เป็น Concrete Strategy ของ BaseReader (Strategy Pattern)
#   - ผลลัพธ์จะถูกส่งต่อให้ TextParser เพื่อตัดเป็น chunks
#   - TextParser จะใช้ข้อมูล format ในการตัดสินใจแบ่ง heading (สำหรับ markdown)
# ---------------------------------------------------------------------------
"""Plain text and Markdown reader."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult


# ---------------------------------------------------------------------------
# TextReader — Concrete Strategy สำหรับอ่านไฟล์ข้อความ
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : อ่านไฟล์ข้อความธรรมดาหรือ Markdown
# รับผิดชอบอะไร : อ่านเนื้อหาไฟล์ + ระบุรูปแบบเอกสาร
# ใช้เมื่อไร : เมื่อ detector เลือก reader นี้จากนามสกุล .txt/.md/.markdown
# ทำงานร่วมกับ : BaseReader (parent), detector.py (เลือก reader), TextParser (ตัด chunks)
class TextReader(BaseReader):
    # รองรับ .md และ .markdown ทั้งคู่ เพราะ convention ของ Markdown ใช้ได้ทั้งสองนามสกุล
    supported_extensions = frozenset({".txt", ".md", ".markdown"})
    reader_name = "text"

    # จุดประสงค์ : อ่านไฟล์ข้อความและสร้าง ReaderResult
    # Input : path — เส้นทางไฟล์ที่จะอ่าน
    # Output : ReaderResult พร้อมข้อความดิบและ metadata (รวม format)
    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        metadata = self._base_metadata(file_path)
        # ระบุ format เป็น "markdown" ถ้านามสกุลเป็น .md หรือ .markdown
        # เพื่อให้ parser ตัดสินใจว่าจะใช้ heading-based chunking หรือไม่
        metadata["format"] = "markdown" if file_path.suffix.lower() in {".md", ".markdown"} else "text"
        return ReaderResult(text=text, metadata=metadata)
