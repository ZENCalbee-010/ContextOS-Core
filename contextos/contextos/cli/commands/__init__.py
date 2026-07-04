# ===========================================================================
# ไฟล์: cli/commands/__init__.py
# หน้าที่: ทำให้ไดเรกทอรี commands/ เป็น Python package
# ความรับผิดชอบ: ประกาศ namespace ให้ Python รู้จัก module คำสั่ง CLI ย่อยทั้งหมด
# ความสัมพันธ์กับระบบ: รวม command modules 5 ตัว:
#   - ask_cmd.py     : คำสั่ง `context ask`
#   - import_cmd.py  : คำสั่ง `context import`
#   - optimize_cmd.py: คำสั่ง `context optimize`
#   - search_cmd.py  : คำสั่ง `context search`
#   - stats_cmd.py   : คำสั่ง `context stats`
# Design Pattern: Separation of Concerns - แยกแต่ละ command เป็น module
#   เพื่อลดความซับซ้อนและให้ทดสอบแยกกันได้
# ===========================================================================
"""CLI command modules."""
