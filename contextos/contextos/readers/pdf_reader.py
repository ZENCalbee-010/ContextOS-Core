# ---------------------------------------------------------------------------
# readers/pdf_reader.py — Reader สำหรับอ่านไฟล์ PDF
# ---------------------------------------------------------------------------
# หน้าที่ : อ่านเนื้อหาจากไฟล์ PDF แล้วแปลงเป็นข้อความธรรมดา (plain text)
# ความรับผิดชอบ :
#   - ดึงข้อความจากทุกหน้าของ PDF
#   - ดึง metadata จาก PDF properties (title, author, จำนวนหน้า)
# ความสัมพันธ์กับระบบ :
#   - เป็น Concrete Strategy ของ BaseReader (Strategy Pattern)
#   - ผลลัพธ์จะถูกส่งต่อให้ TextParser เพื่อตัดเป็น chunks
# หมายเหตุ : ใช้ PyMuPDF (import ในชื่อ fitz) ซึ่งเป็นไลบรารีที่เร็ว
#   และรองรับ PDF หลากหลายรูปแบบ รวมถึง PDF ที่มีภาพและตาราง
# ---------------------------------------------------------------------------
"""PDF reader powered by PyMuPDF."""

from pathlib import Path

# fitz คือ PyMuPDF — ไลบรารีสำหรับจัดการ PDF ที่มีประสิทธิภาพสูง
# ชื่อ "fitz" มาจาก MuPDF rendering engine ที่อยู่เบื้องหลัง
import fitz

from contextos.readers.base import BaseReader, ReaderResult


# ---------------------------------------------------------------------------
# PDFReader — Concrete Strategy สำหรับอ่านไฟล์ PDF
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : แปลงไฟล์ PDF เป็นข้อความธรรมดาพร้อม metadata
# รับผิดชอบอะไร : ดึงข้อความทีละหน้า + ข้อมูลเอกสาร
# ใช้เมื่อไร : เมื่อ detector เลือก reader นี้จากนามสกุล .pdf
# ทำงานร่วมกับ : BaseReader (parent), detector.py (เลือก reader)
class PDFReader(BaseReader):
    supported_extensions = frozenset({".pdf"})
    reader_name = "pdf"

    # จุดประสงค์ : อ่านไฟล์ PDF และสร้าง ReaderResult
    # Input : path — เส้นทางไฟล์ PDF ที่จะอ่าน
    # Output : ReaderResult พร้อมข้อความจากทุกหน้าและ metadata
    # ขั้นตอนการทำงาน :
    #   1. เปิดไฟล์ PDF ด้วย fitz.open() (context manager เพื่อปิดไฟล์อัตโนมัติ)
    #   2. วนดึงข้อความจากทุกหน้าเก็บไว้ใน list
    #   3. ดึง metadata พื้นฐาน + เพิ่มจำนวนหน้า, title, author
    #   4. รวมข้อความทุกหน้าด้วย newline
    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        page_text: list[str] = []

        # ใช้ context manager (with) เพื่อให้แน่ใจว่าไฟล์ถูกปิดหลังอ่านเสร็จ
        # สำคัญมากสำหรับ PDF ขนาดใหญ่ที่ใช้หน่วยความจำมาก
        with fitz.open(file_path) as document:
            # ดึงข้อความจากแต่ละหน้า — get_text() คืน plain text ของหน้านั้น
            for page in document:
                page_text.append(page.get_text())

            metadata = self._base_metadata(file_path)
            # เพิ่ม metadata เฉพาะทางของ PDF
            # ใช้ `or None` เพื่อแปลง string ว่างเป็น None
            metadata.update(
                {
                    "page_count": document.page_count,
                    "title": document.metadata.get("title") or None,
                    "author": document.metadata.get("author") or None,
                }
            )

        # รวมข้อความทุกหน้าด้วย newline แล้ว strip whitespace ที่เกินออก
        return ReaderResult(text="\n".join(page_text).strip(), metadata=metadata)
