# ---------------------------------------------------------------------------
# readers/base.py — คลาสฐานสำหรับ reader ทุกตัวในระบบ ContextOS
# ---------------------------------------------------------------------------
# หน้าที่ : กำหนด interface (ABC) ที่ reader ทุกชนิดต้อง implement
#           รวมถึงโมเดลข้อมูล ReaderResult สำหรับเก็บผลการอ่านไฟล์
# Design Pattern : **Strategy Pattern**
#   - BaseReader เป็น "Strategy Interface"
#   - Subclass อย่าง PDFReader, DOCXReader, TextReader, CodeReader
#     เป็น "Concrete Strategy" แต่ละตัวรู้วิธีอ่านไฟล์ชนิดเฉพาะ
#   - detector.py จะเลือก strategy ที่เหมาะสมตามนามสกุลไฟล์
# ความสัมพันธ์กับระบบ :
#   - อยู่ในขั้นตอนแรกของ pipeline : อ่านไฟล์ → ReaderResult
#   - ReaderResult.text จะถูกส่งต่อให้ parser เพื่อตัดเป็น chunks
# ---------------------------------------------------------------------------
"""Base interfaces for file readers."""

# abc — สร้าง Abstract Base Class เพื่อบังคับ contract
from abc import ABC, abstractmethod
# dataclass — สร้าง data container แบบ immutable สำหรับผลลัพธ์
from dataclasses import dataclass, field
# Path — จัดการ path ข้ามแพลตฟอร์ม (Windows/Linux/macOS)
from pathlib import Path
# Any — ใช้ใน type hint สำหรับ metadata ที่มี value หลายชนิด
from typing import Any


# ---------------------------------------------------------------------------
# ReaderResult — โมเดลข้อมูลสำหรับเก็บผลลัพธ์จากการอ่านไฟล์
# ---------------------------------------------------------------------------
# ใช้ frozen=True เพื่อให้ผลลัพธ์เป็น immutable
# ป้องกันไม่ให้ขั้นตอนถัดไปใน pipeline แก้ไขข้อมูลต้นฉบับโดยบังเอิญ
@dataclass(frozen=True)
class ReaderResult:
    """Raw text and metadata extracted from a local file."""

    text: str                                               # ข้อความดิบที่อ่านได้จากไฟล์
    metadata: dict[str, Any] = field(default_factory=dict)  # ข้อมูลเพิ่มเติม (ชื่อไฟล์, ขนาด, ผู้เขียน ฯลฯ)
    supported: bool = True                                  # True ถ้าไฟล์ได้รับการรองรับ, False ถ้าไม่มี reader ที่เหมาะสม
    error: str | None = None                                # ข้อความ error (ถ้าอ่านไม่สำเร็จ)


# ---------------------------------------------------------------------------
# BaseReader — Strategy Interface สำหรับการอ่านไฟล์
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : เป็นพิมพ์เขียวที่บังคับให้ reader ทุกตัวมี method read()
# รับผิดชอบอะไร : กำหนด contract และ utility method ที่ reader ทุกตัวใช้ร่วมกัน
# ทำงานร่วมกับ : detector.py (เลือก reader), parsers (รับ text ไปตัด chunk)
# เมื่อไรถึงใช้ : เมื่อต้องการสร้าง reader ชนิดใหม่ ให้ inherit จากคลาสนี้
class BaseReader(ABC):
    """Strategy interface for reading a file into raw text."""

    # นามสกุลไฟล์ที่ reader นี้รองรับ — subclass ต้อง override
    # ใช้ frozenset เพื่อป้องกันการแก้ไขหลังสร้าง instance
    supported_extensions: frozenset[str] = frozenset()
    # ชื่อ reader สำหรับใส่ใน metadata เพื่อ traceability
    reader_name = "base"

    # จุดประสงค์ : ตรวจสอบว่า reader นี้สามารถอ่านไฟล์ที่ระบุได้หรือไม่
    # วิธีการ : เทียบนามสกุลไฟล์ (lowercase) กับ supported_extensions
    # เหตุผลที่ใช้ .lower() : ให้รองรับนามสกุลทั้งพิมพ์เล็กและใหญ่ เช่น .PDF, .Pdf
    def can_read(self, path: str | Path) -> bool:
        return Path(path).suffix.lower() in self.supported_extensions

    @abstractmethod
    def read(self, path: str | Path) -> ReaderResult:
        """Read a file and return raw text plus metadata."""

    # จุดประสงค์ : ดึงข้อมูลพื้นฐานของไฟล์ (path, ชื่อ, นามสกุล, ขนาด)
    # เหตุผลที่ต้องมี : ทุก reader ต้องส่ง metadata พื้นฐานเหมือนกัน
    #   method นี้ช่วยลดโค้ดซ้ำ — subclass เรียกแล้วเพิ่ม metadata เฉพาะทาง
    # ใช้ stat() เพื่ออ่านข้อมูลจาก filesystem เช่น ขนาดไฟล์
    def _base_metadata(self, path: str | Path) -> dict[str, Any]:
        file_path = Path(path)
        stat = file_path.stat()
        return {
            "filepath": str(file_path),
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "reader": self.reader_name,
            "size_bytes": stat.st_size,
        }
