# ---------------------------------------------------------------------------
# ไฟล์: formatting/__init__.py
# หน้าที่: เป็น public API ของ sub-package formatting
#          ทำหน้าที่ re-export ฟังก์ชันจัดรูปแบบข้อมูลสำหรับแสดงผล
# ความรับผิดชอบ:
#   - format_source: สร้างข้อความแหล่งที่มาของ chunk (filepath, section, page/line)
#   - preview_text: ตัดข้อความให้สั้นสำหรับแสดงผลใน CLI
# ความสัมพันธ์กับระบบ: ContextBuilder ใช้ format_source
#                     เพื่อแสดงแหล่งที่มาของแต่ละ chunk ใน prompt
# ---------------------------------------------------------------------------
"""Shared formatting helpers."""

from contextos.formatting.sources import format_source, preview_text

__all__ = ["format_source", "preview_text"]
