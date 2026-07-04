# ---------------------------------------------------------------------------
# readers/detector.py — ตัวเลือก reader ที่เหมาะสมตามนามสกุลไฟล์
# ---------------------------------------------------------------------------
# หน้าที่ : เป็น entry point หลักสำหรับการอ่านไฟล์ในระบบ ContextOS
#           รับ path ของไฟล์ → เลือก reader ที่เหมาะสม → อ่านและส่งผลลัพธ์กลับ
# Design Pattern : **Chain of Responsibility**
#   - READERS tuple กำหนดลำดับความสำคัญของ reader
#   - get_reader() วนหา reader ตัวแรกที่ can_read() คืน True
#   - ถ้าไม่มี reader ใดรองรับ → คืน None (ไม่ throw error)
# ความสัมพันธ์กับระบบ :
#   - เป็น "กาว" ที่เชื่อม readers กับ pipeline หลัก
#   - read_file() เป็นฟังก์ชันที่ module อื่น ๆ เรียกใช้โดยตรง
# ---------------------------------------------------------------------------
"""Reader detection by file extension."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult
from contextos.readers.code_reader import CodeReader
from contextos.readers.docx_reader import DOCXReader
from contextos.readers.pdf_reader import PDFReader
from contextos.readers.text_reader import TextReader


# ---------------------------------------------------------------------------
# READERS — ลำดับของ reader instances ที่จะถูกตรวจสอบ
# ---------------------------------------------------------------------------
# ลำดับมีความหมาย : reader ที่อยู่ก่อนจะถูกทดสอบก่อน
# ถ้ามีนามสกุลซ้ำกัน reader ตัวแรกที่ match จะถูกเลือก
# PDF และ DOCX อยู่ก่อนเพราะเป็นไฟล์เฉพาะทาง ส่วน Text/Code อยู่หลัง
READERS: tuple[BaseReader, ...] = (
    PDFReader(),
    DOCXReader(),
    TextReader(),
    CodeReader(),
)


# จุดประสงค์ : ค้นหา reader ตัวแรกที่รองรับนามสกุลของไฟล์ที่ระบุ
# Input : path — เส้นทางไฟล์ที่ต้องการอ่าน
# Output : BaseReader instance ที่เหมาะสม หรือ None ถ้าไม่มี reader รองรับ
# วิธีการ : วนลูปผ่าน READERS tuple ตามลำดับ เรียก can_read() ของแต่ละตัว
def get_reader(path: str | Path) -> BaseReader | None:
    """Return the first reader that supports the file extension."""

    file_path = Path(path)
    for reader in READERS:
        if reader.can_read(file_path):
            return reader
    return None


# จุดประสงค์ : อ่านไฟล์อย่างปลอดภัย — ไม่ throw exception ไม่ว่ากรณีใด
# Input : path — เส้นทางไฟล์ที่ต้องการอ่าน
# Output : ReaderResult เสมอ (แม้จะเกิด error ก็ตาม)
# ขั้นตอนการทำงาน :
#   1. หา reader ที่เหมาะสมด้วย get_reader()
#   2. ถ้าไม่พบ reader → คืน ReaderResult ที่มี supported=False
#   3. ถ้าพบแล้วอ่านไม่สำเร็จ (OSError) → คืน ReaderResult ที่มี error message
# เหตุผลที่ต้องมี : ทำให้ pipeline หลักไม่ต้อง try-catch เอง
#   และสามารถจัดการไฟล์ที่ไม่รองรับได้อย่างสง่างาม (graceful degradation)
def read_file(path: str | Path) -> ReaderResult:
    """Read a supported file or return an unsupported result gracefully."""

    file_path = Path(path)
    reader = get_reader(file_path)
    # กรณีไม่มี reader รองรับนามสกุลนี้
    if reader is None:
        return ReaderResult(
            text="",
            metadata={
                "filepath": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "reader": None,
            },
            supported=False,
            error=f"Unsupported file type: {file_path.suffix.lower() or '<none>'}",
        )

    # พยายามอ่านไฟล์ — จับ OSError เพื่อจัดการกรณีไฟล์เสียหายหรือ permission denied
    try:
        return reader.read(file_path)
    except OSError as exc:
        return ReaderResult(
            text="",
            metadata={
                "filepath": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "reader": reader.reader_name,
            },
            supported=True,
            error=str(exc),
        )
