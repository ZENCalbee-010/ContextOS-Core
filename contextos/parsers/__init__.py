# ---------------------------------------------------------------------------
# parsers/__init__.py — จุดเริ่มต้นของ package "parsers"
# ---------------------------------------------------------------------------
# หน้าที่ : เป็น public API ของ sub-package parsers
#           กำหนดว่า module ภายนอกจะเห็นคลาสและโมเดลอะไรบ้าง
# ความสัมพันธ์กับ ContextOS :
#   - อยู่ในขั้นตอน "แปลงข้อความดิบ → chunks" ของ pipeline
#   - readers อ่านไฟล์ → ส่งข้อความดิบมาให้ parsers ตัดแบ่ง
# Design Pattern : ใช้ re-export เพื่อให้ผู้เรียกใช้ import ได้สั้น
#   เช่น `from contextos.parsers import CodeParser` แทนที่จะระบุ path เต็ม
# ---------------------------------------------------------------------------
"""Parsers for supported document formats."""

from contextos.parsers.base import BaseParser, ParsedChunk
from contextos.parsers.code_parser import CodeParser
from contextos.parsers.text_parser import TextParser

__all__ = ["BaseParser", "CodeParser", "ParsedChunk", "TextParser"]
