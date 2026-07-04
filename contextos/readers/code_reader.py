# ---------------------------------------------------------------------------
# readers/code_reader.py — Reader สำหรับอ่านไฟล์ซอร์สโค้ด
# ---------------------------------------------------------------------------
# หน้าที่ : อ่านไฟล์โค้ดหลายภาษา (.py, .js, .ts, .html, .css, .json)
#           แล้วส่งข้อความดิบพร้อม metadata กลับเป็น ReaderResult
# ความรับผิดชอบ :
#   - อ่านไฟล์เป็น UTF-8
#   - แปลงนามสกุลไฟล์เป็นชื่อภาษา (เช่น .py → "python")
# ความสัมพันธ์กับระบบ :
#   - เป็น Concrete Strategy ของ BaseReader (Strategy Pattern)
#   - ผลลัพธ์จะถูกส่งต่อให้ CodeParser เพื่อตัดเป็น chunks
# ---------------------------------------------------------------------------
"""Source code file reader."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult


# ---------------------------------------------------------------------------
# CodeReader — Concrete Strategy สำหรับอ่านไฟล์โค้ด
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : อ่านไฟล์ซอร์สโค้ดที่รองรับ แล้วเพิ่มข้อมูลภาษาใน metadata
# รับผิดชอบอะไร : อ่านเนื้อหาไฟล์ + ระบุภาษาจากนามสกุล
# ใช้เมื่อไร : เมื่อ detector เลือก reader นี้จากนามสกุลไฟล์
# ทำงานร่วมกับ : BaseReader (parent), detector.py (เลือก reader), CodeParser (ตัด chunks)
class CodeReader(BaseReader):
    # นามสกุลไฟล์ที่รองรับ — ครอบคลุมภาษาที่ใช้บ่อยในการพัฒนาเว็บและ data science
    supported_extensions = frozenset({
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
    })
    reader_name = "code"

    # จุดประสงค์ : อ่านไฟล์โค้ดและสร้าง ReaderResult
    # Input : path — เส้นทางไฟล์ที่จะอ่าน
    # Output : ReaderResult พร้อมข้อความดิบและ metadata (รวมภาษา)
    # เหตุผลที่ใช้ UTF-8 : ซอร์สโค้ดสมัยใหม่แทบทั้งหมดเป็น UTF-8
    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        metadata = self._base_metadata(file_path)
        # เพิ่มชื่อภาษาใน metadata เพื่อให้ parser เลือก strategy ที่เหมาะสม
        metadata["language"] = self._language_for_extension(file_path.suffix.lower())
        return ReaderResult(text=text, metadata=metadata)

    # จุดประสงค์ : แปลงนามสกุลไฟล์เป็นชื่อภาษาแบบอ่านง่าย
    # วิธีการ : ใช้ dict lookup — ถ้านามสกุลไม่อยู่ใน dict จะ raise KeyError
    #   ซึ่งเป็นพฤติกรรมที่ต้องการ เพราะ can_read() กรองนามสกุลที่ไม่รองรับออกก่อนแล้ว
    def _language_for_extension(self, extension: str) -> str:
        return {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
        }[extension]
