# ---------------------------------------------------------------------------
# ไฟล์: retrieval/__init__.py
# หน้าที่: เป็น public API ของ sub-package retrieval
#          ทำหน้าที่ re-export BM25Retriever และ BM25Result
# ความรับผิดชอบ: sub-package นี้จัดการการค้นหา context chunks
#               ที่เกี่ยวข้องกับคำถามของผู้ใช้ โดยใช้ BM25 algorithm
# ความสัมพันธ์กับระบบ: ผลลัพธ์จาก retrieval จะถูกส่งต่อไปยัง
#                     TokenBudgetSelector → ContextBuilder → AI Adapter
# ---------------------------------------------------------------------------
"""Retrieval components for context selection."""

from contextos.retrieval.bm25_retriever import BM25Retriever, BM25Result

__all__ = ["BM25Retriever", "BM25Result"]
