# ---------------------------------------------------------------------------
# ไฟล์: token_budget/__init__.py
# หน้าที่: เป็น public API ของ sub-package token_budget
#          ทำหน้าที่ re-export TokenBudgetSelector และ TokenBudgetSelection
# ความรับผิดชอบ: sub-package นี้จัดการการจัดสรร token budget
#               เพื่อเลือก chunks ที่มี "คุณค่าต่อ token" สูงสุด
#               ภายในขอบเขต token budget ที่กำหนด
# ความสัมพันธ์กับระบบ: รับ BM25Result จาก retrieval module
#                     แล้วส่ง chunks ที่เลือกให้ ContextBuilder ประกอบ prompt
# ---------------------------------------------------------------------------
"""Token budget planning utilities."""

from contextos.token_budget.selector import TokenBudgetSelection, TokenBudgetSelector

__all__ = ["TokenBudgetSelection", "TokenBudgetSelector"]
