# ---------------------------------------------------------------------------
# parsers/base.py — คลาสฐานสำหรับ parser ทุกตัวในระบบ ContextOS
# ---------------------------------------------------------------------------
# หน้าที่ : กำหนด interface (ABC) ที่ parser ทุก strategy ต้อง implement
#           รวมถึงโมเดลข้อมูล ParsedChunk ที่เป็นผลลัพธ์ของการตัดข้อความ
# Design Pattern : **Strategy Pattern**
#   - BaseParser เป็น "Strategy Interface"
#   - Subclass อย่าง CodeParser, TextParser เป็น "Concrete Strategy"
#   - ช่วยให้เปลี่ยนวิธีตัดข้อความได้โดยไม่ต้องแก้ pipeline หลัก
# ความสัมพันธ์กับระบบ :
#   - ข้อมูลที่ readers อ่านมาจะถูกส่งเข้า parse() ของ parser ที่เหมาะสม
#   - ผลลัพธ์ ParsedChunk จะถูกนำไปสร้าง keyword/structural index ต่อ
# ---------------------------------------------------------------------------
"""Base parser interfaces and chunk models."""

# abc — ใช้สร้าง Abstract Base Class เพื่อบังคับ contract ของ subclass
from abc import ABC, abstractmethod
# dataclass — สร้าง data container แบบ immutable (frozen) สำหรับ chunk
from dataclasses import dataclass
# re — ใช้ regex นับจำนวน token ด้วยวิธี whitespace-split
import re

from contextos.exceptions import ParserError


# ---------------------------------------------------------------------------
# ParsedChunk — โมเดลข้อมูลสำหรับ "ชิ้นส่วนข้อความ" ที่ตัดแบ่งแล้ว
# ---------------------------------------------------------------------------
# ใช้ frozen=True เพื่อให้ chunk เป็น immutable — ป้องกันการแก้ไขโดยบังเอิญ
# หลังจากสร้างแล้ว ซึ่งสำคัญเมื่อ chunk ถูกส่งต่อไปหลายขั้นตอนใน pipeline
@dataclass(frozen=True)
class ParsedChunk:
    content: str                        # เนื้อหาข้อความที่อยู่ใน chunk นี้
    chunk_index: int                    # ลำดับของ chunk (เริ่มจาก 0)
    token_count: int                    # จำนวน token โดยประมาณ (นับจาก whitespace)
    page_number: int | None = None      # หมายเลขหน้า (ถ้ามาจาก PDF)
    start_line: int | None = None       # บรรทัดเริ่มต้นในไฟล์ต้นฉบับ
    end_line: int | None = None         # บรรทัดสุดท้ายในไฟล์ต้นฉบับ
    section: str | None = None          # ชื่อ section/heading ที่ chunk นี้สังกัด


# ---------------------------------------------------------------------------
# BaseParser — Strategy Interface สำหรับการแบ่งข้อความเป็น chunks
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : เป็นพิมพ์เขียวที่บังคับให้ parser ทุกตัวมี method parse()
# ทำงานร่วมกับ : CodeParser, TextParser (concrete strategies)
# เมื่อไรถึงใช้ : เมื่อต้องการสร้าง parser ชนิดใหม่ ให้ inherit จากคลาสนี้
class BaseParser(ABC):
    """Strategy interface for turning raw text into chunks."""

    # จุดประสงค์ : กำหนดขนาด token สูงสุดต่อ chunk
    # Input : max_tokens — จำนวน token สูงสุดที่ chunk หนึ่งจะมีได้
    # เหตุผลที่ validate : ค่า 0 หรือลบจะทำให้ลูปตัด chunk ไม่มีวันหยุด
    def __init__(self, max_tokens: int = 400) -> None:
        if max_tokens <= 0:
            raise ParserError("max_tokens must be greater than zero")
        self.max_tokens = max_tokens

    @abstractmethod
    def parse(self, text: str) -> list[ParsedChunk]:
        """Split raw text into parser chunks."""

    # จุดประสงค์ : นับจำนวน token แบบประมาณโดยใช้ whitespace เป็นตัวแบ่ง
    # วิธีการ : regex \S+ จับ "คำ" ทุกคำที่ไม่ใช่ whitespace
    # เหตุผลที่ใช้ regex แทน split() : ให้ผลสม่ำเสมอกว่ากับ whitespace หลายแบบ
    # หมายเหตุ : เป็นการประมาณค่า ไม่ใช่ tokenizer ที่แท้จริงของ LLM
    def count_tokens(self, text: str) -> int:
        return len(re.findall(r"\S+", text))

    # จุดประสงค์ : รีเซ็ตลำดับ chunk_index ให้เรียงจาก 0 ใหม่ต่อเนื่อง
    # เหตุผลที่ต้องมี : เมื่อ parser ตัดข้อความเป็นกลุ่มย่อยหลายรอบแล้วรวมกัน
    #   ลำดับ chunk_index อาจไม่ต่อเนื่อง method นี้จึงจัดลำดับใหม่ให้ถูกต้อง
    # ใช้ frozen dataclass จึงต้องสร้าง ParsedChunk ใหม่ทุกตัว (ไม่ mutate)
    def _renumber(self, chunks: list[ParsedChunk]) -> list[ParsedChunk]:
        return [
            ParsedChunk(
                content=chunk.content,
                chunk_index=index,
                token_count=chunk.token_count,
                page_number=chunk.page_number,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                section=chunk.section,
            )
            for index, chunk in enumerate(chunks)
        ]
