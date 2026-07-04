# ---------------------------------------------------------------------------
# ไฟล์: context_builder/builder.py
# หน้าที่: ประกอบ (assemble) prompt สุดท้ายจาก chunks ที่ถูกเลือกมาแล้ว
#          พร้อม system prompt, context, คำถาม, และ instructions
# ความรับผิดชอบ:
#   - รับ chunks ที่ผ่านการคัดเลือกจาก TokenBudgetSelector
#   - จัดรูปแบบแต่ละ chunk ให้มี source info (ชื่อไฟล์, หน้า, บรรทัด)
#   - รวมทุกส่วนเป็น prompt เดียวที่พร้อมส่งให้ AI adapter
# ความสัมพันธ์กับระบบ:
#   - ใช้ format_source จาก formatting module เพื่อแสดงแหล่งที่มา
#   - ใช้ Chunk model จาก memory module
#   - ใช้ SQLiteMemoryRepository เพื่อ lookup ข้อมูล document (ถ้าจำเป็น)
# ---------------------------------------------------------------------------
"""Build final prompts from selected context chunks."""

# Protocol ใช้สำหรับ structural typing (duck typing แบบมี type hint)
from typing import Protocol

from contextos.formatting import format_source
from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


# SYSTEM_PROMPT: คำสั่งระดับระบบที่บอก AI ว่าให้ตอบจาก context เท่านั้น
# ช่วยลดการ hallucinate (สร้างข้อมูลที่ไม่มีใน context)
SYSTEM_PROMPT = "You are answering using only the provided context."

# INSTRUCTIONS: รายการคำแนะนำเพิ่มเติมสำหรับ AI
# กำหนดรูปแบบการตอบ เช่น อ้างอิงแหล่งที่มา, ตอบชัดเจน
INSTRUCTIONS = [
    "Answer clearly.",
    "Cite source names when possible.",
    "If context is insufficient, say so.",
]


# ChunkSelection Protocol: กำหนดว่า object ที่มี attribute 'chunk'
# (เช่น BM25Result, TokenBudgetSelection item) สามารถใช้ร่วมกับ
# ContextBuilder ได้ โดยไม่ต้อง inherit จาก class ใด
class ChunkSelection(Protocol):
    chunk: Chunk


class ContextBuilder:
    """Render selected chunks into the final question-answer prompt."""

    def __init__(self, repository: SQLiteMemoryRepository | None = None) -> None:
        # repository: optional — ใช้สำหรับ lookup filepath ของ document
        # ในกรณีที่ chunk ไม่ได้เก็บ filepath ไว้ใน metadata
        self.repository = repository

    def build(self, question: str, chunks: list[Chunk | ChunkSelection]) -> str:
        """
        ประกอบ prompt สุดท้าย
        Input: question (คำถามของผู้ใช้), chunks (รายการ chunks ที่เลือก)
        Output: string prompt ที่มีโครงสร้าง SYSTEM → CONTEXT → QUESTION → INSTRUCTIONS
        """
        # จัดรูปแบบแต่ละ chunk พร้อมลำดับหมายเลข
        context_blocks = [
            self._format_chunk(index, self._unwrap_chunk(item))
            for index, item in enumerate(chunks, start=1)
        ]

        # ประกอบทุกส่วนเข้าด้วยกันเป็น prompt เดียว
        return "\n\n".join(
            [
                "SYSTEM:",
                SYSTEM_PROMPT,
                "CONTEXT:",
                "\n\n".join(context_blocks) if context_blocks else "(no context provided)",
                "QUESTION:",
                question,
                "INSTRUCTIONS:",
                "\n".join(f"- {instruction}" for instruction in INSTRUCTIONS),
            ]
        )

    def _unwrap_chunk(self, item: Chunk | ChunkSelection) -> Chunk:
        """แกะ Chunk ออกจาก wrapper (เช่น BM25Result) ถ้าจำเป็น"""
        if isinstance(item, Chunk):
            return item
        return item.chunk

    def _format_chunk(self, index: int, chunk: Chunk) -> str:
        """จัดรูปแบบ chunk เดียว ให้แสดงลำดับ, แหล่งที่มา, และเนื้อหา"""
        source = format_source(chunk, self.repository)
        return "\n".join(
            [
                f"[Chunk {index}]",
                f"Source: {source}",
                f"Content: {chunk.content}",
            ]
        )
