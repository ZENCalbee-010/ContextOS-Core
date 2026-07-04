# =============================================================================
# compression/base.py — คลาสฐานและ interface หลักสำหรับการบีบอัดข้อความ
# =============================================================================
# หน้าที่: กำหนด "สัญญา" (contract) ที่ compressor ทุกตัวต้องปฏิบัติตาม
#          และจัดเตรียมเครื่องมือพื้นฐาน (regex, helper functions) ที่ใช้ร่วมกัน
#
# ความรับผิดชอบ:
#   1. BaseCompressor — Abstract Base Class ที่เป็น Strategy Interface
#   2. CompressionResult — Data class สำหรับเก็บผลลัพธ์การบีบอัด
#   3. SENTENCE_RE / WORD_RE — Regex สำหรับแยกประโยคและคำ
#   4. split_sentences() / split_paragraphs() — ฟังก์ชันช่วยตัดข้อความ
#
# Design Pattern ที่ใช้:
#   ┌─ Strategy Pattern ──────────────────────────────────────────────┐
#   │  BaseCompressor = Strategy Interface                            │
#   │  LightCompressor, MediumCompressor, AggressiveCompressor        │
#   │  = Concrete Strategies ที่ implement _compress() ต่างกัน        │
#   └─────────────────────────────────────────────────────────────────┘
#   ┌─ Template Method Pattern ───────────────────────────────────────┐
#   │  compress() เป็น template method ที่กำหนดโครงสร้างการทำงาน:     │
#   │    1. เรียก _compress() (abstract — แต่ละ subclass กำหนดเอง)    │
#   │    2. strip ผลลัพธ์                                             │
#   │    3. สร้าง CompressionResult พร้อมสถิติ                        │
#   │  Subclass ต้อง override เฉพาะ _compress() ไม่ต้องแตะ compress() │
#   └─────────────────────────────────────────────────────────────────┘
#
# ความสัมพันธ์กับระบบ ContextOS:
#   - ทุก compressor ใน package นี้สืบทอดจาก BaseCompressor
#   - module อื่น ๆ เช่น context selector จะเรียก compress() ผ่าน interface นี้
#     ทำให้สลับกลยุทธ์บีบอัดได้ง่ายตอน runtime (Separation of Concerns)
# =============================================================================

"""Base interfaces for rule-based compression."""

# abc — ใช้ ABC และ abstractmethod เพื่อบังคับให้ subclass implement _compress()
from abc import ABC, abstractmethod
# dataclass — สร้าง value object สำหรับผลลัพธ์การบีบอัดโดยไม่ต้องเขียน __init__ เอง
from dataclasses import dataclass
# re — ใช้ regular expression สำหรับแยกประโยคและคำ
import re


# ---------------------------------------------------------------------------
# CompressionResult — Data class เก็บผลลัพธ์การบีบอัดพร้อมสถิติ
# ---------------------------------------------------------------------------
# frozen=True ทำให้ instance เป็น immutable (ไม่สามารถแก้ค่าได้หลังสร้าง)
# เหตุผล: ผลลัพธ์การบีบอัดไม่ควรถูกแก้ไขหลังจากสร้างแล้ว เพื่อความปลอดภัยของข้อมูล
@dataclass(frozen=True)
class CompressionResult:
    original: str              # ข้อความต้นฉบับก่อนบีบอัด
    compressed: str            # ข้อความหลังบีบอัดแล้ว
    original_length: int       # ความยาว (จำนวน character) ของข้อความต้นฉบับ
    compressed_length: int     # ความยาวของข้อความหลังบีบอัด
    compression_ratio: float   # อัตราส่วนการบีบอัด (0.0 = ไม่ย่อเลย, 1.0 = ย่อหมด)
    strategy: str              # ชื่อกลยุทธ์ที่ใช้ เช่น "light", "medium", "aggressive"


# ---------------------------------------------------------------------------
# BaseCompressor — Abstract Base Class (Strategy Interface)
# ---------------------------------------------------------------------------
# ใช้ทำอะไร: กำหนดโครงสร้างกลางสำหรับ compressor ทุกตัว
# ใช้เมื่อไร: เมื่อต้องการสร้าง compressor ใหม่ ให้สืบทอดจากคลาสนี้
# ทำงานร่วมกับ: light.py, medium.py, aggressive.py (ทุกตัวสืบทอดจากคลาสนี้)
class BaseCompressor(ABC):
    """Strategy interface for deterministic context compression."""

    # strategy — ชื่อกลยุทธ์ที่ใช้ระบุตัวตน แต่ละ subclass จะ override ค่านี้
    strategy = "base"

    # -----------------------------------------------------------------------
    # compress() — Template Method
    # -----------------------------------------------------------------------
    # จุดประสงค์: เป็น public API หลักที่ผู้เรียกใช้งาน
    # Input: text (str) — ข้อความ context ที่ต้องการบีบอัด
    # Output: CompressionResult — ผลลัพธ์พร้อมข้อมูลสถิติ
    # ขั้นตอน:
    #   1. เรียก _compress() (abstract) เพื่อบีบอัดตามกลยุทธ์ของ subclass
    #   2. strip() ลบ whitespace หัวท้าย
    #   3. สร้าง CompressionResult รวมข้อมูลต้นฉบับ ผลลัพธ์ และอัตราส่วน
    # เหตุผลที่ต้องมี: แยก "กรอบการทำงาน" ออกจาก "วิธีการบีบอัด"
    #   ทำให้ subclass สนใจแค่ _compress() โดยไม่ต้องจัดการสถิติเอง
    def compress(self, text: str) -> CompressionResult:
        compressed = self._compress(text).strip()
        return CompressionResult(
            original=text,
            compressed=compressed,
            original_length=len(text),
            compressed_length=len(compressed),
            compression_ratio=self.compression_ratio(text, compressed),
            strategy=self.strategy,
        )

    # -----------------------------------------------------------------------
    # _compress() — Abstract Method ที่ subclass ต้อง implement
    # -----------------------------------------------------------------------
    # แต่ละ concrete strategy จะเขียนตรรกะบีบอัดของตัวเองในเมธอดนี้
    @abstractmethod
    def _compress(self, text: str) -> str:
        """Return compressed text."""

    # -----------------------------------------------------------------------
    # compression_ratio() — คำนวณอัตราส่วนการบีบอัด
    # -----------------------------------------------------------------------
    # จุดประสงค์: วัดว่าข้อความถูกย่อลงกี่เปอร์เซ็นต์
    # สูตร: 1 - (ความยาวหลังบีบอัด / ความยาวต้นฉบับ)
    # ตัวอย่าง: ต้นฉบับ 100 ตัวอักษร บีบอัดเหลือ 60 → ratio = 0.4 (ย่อลง 40%)
    # กรณีพิเศษ: ถ้าข้อความต้นฉบับว่าง คืน 0.0 เพื่อหลีกเลี่ยง ZeroDivisionError
    def compression_ratio(self, original: str, compressed: str) -> float:
        if not original:
            return 0.0
        return 1 - (len(compressed) / len(original))


# ---------------------------------------------------------------------------
# Regex Constants — ใช้ร่วมกันโดย compressor หลายตัว
# ---------------------------------------------------------------------------

# SENTENCE_RE — จับกลุ่มประโยค (ข้อความที่ลงท้ายด้วย . ! ? หรือสิ้นสุดบรรทัด)
# Pattern: จับ character ที่ไม่ใช่ .!? ตามด้วย .!? หนึ่งตัวขึ้นไป หรือจบ string
# ใช้โดย: split_sentences(), MediumCompressor, AggressiveCompressor
SENTENCE_RE = re.compile(r"[^.!?]+(?:[.!?]+|$)", re.MULTILINE)

# WORD_RE — จับกลุ่มคำที่เป็นตัวอักษรภาษาอังกฤษ (ตัวอักษรนำ + ตัวอักษร/ตัวเลข/_ อีก 2 ตัวขึ้นไป)
# ความยาวขั้นต่ำ 3 ตัวอักษรเพื่อกรอง noise เช่น "a", "in" ที่สั้นเกินไป
# ใช้โดย: MediumCompressor สำหรับนับความถี่คำ (word frequency)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


# ---------------------------------------------------------------------------
# Helper Functions — เครื่องมือตัดข้อความที่ compressor หลายตัวใช้ร่วมกัน
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    """จุดประสงค์: แยกข้อความออกเป็นรายการประโยค
    Input: text — ข้อความยาว ๆ
    Output: list ของประโยค (ตัดช่องว่างหัวท้ายแล้ว ไม่รวมประโยคว่าง)
    ใช้โดย: MediumCompressor (ให้คะแนนประโยค), AggressiveCompressor (ดึงประโยคแรก)"""
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(text) if match.group(0).strip()]


def split_paragraphs(text: str) -> list[str]:
    """จุดประสงค์: แยกข้อความออกเป็นย่อหน้า (คั่นด้วยบรรทัดว่าง)
    Input: text — ข้อความหลายย่อหน้า
    Output: list ของย่อหน้า (ตัดช่องว่างหัวท้ายแล้ว ไม่รวมย่อหน้าว่าง)
    Pattern: \\n\\s*\\n = บรรทัดใหม่ ตามด้วย whitespace หรือบรรทัดว่าง อีกบรรทัดใหม่
    ใช้โดย: AggressiveCompressor (ดึงประโยคแรกของแต่ละย่อหน้า)"""
    return [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
