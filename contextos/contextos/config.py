# ---------------------------------------------------------------------------
# ไฟล์: config.py
# หน้าที่: กำหนดค่าคงที่ (configuration defaults) สำหรับ ContextOS Core
#          ได้แก่ เส้นทางโปรเจกต์, ไดเรกทอรีข้อมูล, ฐานข้อมูลเริ่มต้น
#          และค่า token budget เริ่มต้น
# ความรับผิดชอบ: รวมศูนย์ค่าตั้งต้นไว้ที่เดียว เพื่อให้ทุก module
#               อ้างอิงจากจุดเดียวกัน (Single Source of Truth)
# ความสัมพันธ์กับระบบ: module อื่น ๆ เช่น indexer, retrieval, memory
#                     จะ import ค่าเหล่านี้เพื่อหา path ของ DB หรือ config
# ---------------------------------------------------------------------------
"""Configuration defaults for ContextOS Core."""

# pathlib ใช้สำหรับจัดการเส้นทางไฟล์แบบ cross-platform
from pathlib import Path


# PROJECT_ROOT: คำนวณจากตำแหน่งไฟล์นี้ ย้อนขึ้นไป 1 ระดับ (parents[1])
# เพื่อชี้ไปที่ root ของโปรเจกต์ contextos
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# DATA_DIR: โฟลเดอร์สำหรับเก็บข้อมูล เช่น ฐานข้อมูล SQLite
DATA_DIR = PROJECT_ROOT / "data"

# CONFIG_DIR: โฟลเดอร์สำหรับเก็บไฟล์ตั้งค่าของโปรเจกต์
CONFIG_DIR = PROJECT_ROOT / "config"

# DEFAULT_DB_PATH: เส้นทางเริ่มต้นของฐานข้อมูล SQLite
# ใช้โดย SQLiteMemoryRepository (Repository Pattern)
DEFAULT_DB_PATH = DATA_DIR / "contextos.sqlite3"

# DEFAULT_TOKEN_BUDGET: จำนวน token สูงสุดเริ่มต้น (8,000 tokens)
# ที่ TokenBudgetSelector จะใช้ในการจัดสรร context ให้ AI model
DEFAULT_TOKEN_BUDGET = 8_000
