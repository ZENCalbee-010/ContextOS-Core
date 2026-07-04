# ---------------------------------------------------------------------------
# ไฟล์: indexer/__init__.py
# หน้าที่: เป็น public API ของ sub-package indexer
#          ทำหน้าที่ re-export FileIndexer, IndexResult, และ sha256_file
# ความรับผิดชอบ: sub-package นี้จัดการ Pipeline Pattern ของการ index ไฟล์
#               ตั้งแต่อ่านไฟล์ → hash → parse → extract keywords
#               → compress → persist ลงฐานข้อมูล
# ความสัมพันธ์กับระบบ: เป็นจุดเริ่มต้นของ data pipeline ที่นำข้อมูล
#                     จากไฟล์ local เข้าสู่ระบบ ContextOS
# ---------------------------------------------------------------------------
"""Indexing components for local context."""

from contextos.indexer.hasher import sha256_file
from contextos.indexer.indexer import FileIndexer, IndexResult

__all__ = ["FileIndexer", "IndexResult", "sha256_file"]
