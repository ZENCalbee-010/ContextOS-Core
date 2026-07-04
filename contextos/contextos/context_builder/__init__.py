# ---------------------------------------------------------------------------
# ไฟล์: context_builder/__init__.py
# หน้าที่: เป็น public API ของ sub-package context_builder
#          ทำหน้าที่ re-export ContextBuilder เพื่อให้ import ได้สะดวก
# ความรับผิดชอบ: ContextBuilder คือตัวประกอบ prompt สุดท้าย
#               ที่รวม system prompt, context chunks, คำถาม, และ instructions
#               ให้เป็นข้อความเดียวพร้อมส่งให้ AI model
# ---------------------------------------------------------------------------
"""Context pack construction utilities."""

from contextos.context_builder.builder import ContextBuilder

__all__ = ["ContextBuilder"]
