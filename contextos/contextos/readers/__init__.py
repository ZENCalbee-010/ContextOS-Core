# ---------------------------------------------------------------------------
# readers/__init__.py — จุดเริ่มต้นของ package "readers"
# ---------------------------------------------------------------------------
# หน้าที่ : เป็น public API ของ sub-package readers
#           กำหนดว่า module ภายนอกจะเห็นคลาสและฟังก์ชันอะไรบ้าง
# ความสัมพันธ์กับ ContextOS :
#   - อยู่ในขั้นตอนแรกสุดของ pipeline : "อ่านไฟล์ → ข้อความดิบ"
#   - ผลลัพธ์ ReaderResult จะถูกส่งต่อไปให้ parsers ตัดเป็น chunks
# Design Pattern : re-export เพื่อให้ import สั้นกระชับ
#   เช่น `from contextos.readers import read_file` แทนที่จะระบุ detector module
# ---------------------------------------------------------------------------
"""Document readers for local files."""

from contextos.readers.base import BaseReader, ReaderResult
from contextos.readers.detector import get_reader, read_file

__all__ = ["BaseReader", "ReaderResult", "get_reader", "read_file"]
