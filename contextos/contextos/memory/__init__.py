# =============================================================================
# memory/__init__.py — Package Init สำหรับ Memory Module ของ ContextOS
# =============================================================================
# หน้าที่: เป็นจุดเริ่มต้นของ package "memory" ซึ่งรับผิดชอบการจัดเก็บและ
#   ดึงข้อมูลในระบบ local storage ของ ContextOS
# ความรับผิดชอบ: ทำให้ Python รู้จัก directory นี้เป็น package และกำหนด
#   public API ของ memory module ผ่าน docstring
# ความสัมพันธ์กับระบบ ContextOS: เป็น layer ล่างสุดที่จัดการ persistence
#   โดย module อื่น ๆ เช่น retriever, ingestion pipeline จะเรียกใช้
#   primitives ที่อยู่ใน package นี้เพื่ออ่าน/เขียนข้อมูลลง SQLite
# Sub-modules ภายใน:
#   - db.py: จัดการ connection และ schema ของ SQLite
#   - models.py: นิยาม dataclass สำหรับ record ต่าง ๆ
#   - repository.py: Repository Pattern สำหรับ CRUD operations
# =============================================================================
"""Local memory storage and retrieval primitives."""
