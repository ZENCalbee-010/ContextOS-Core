# =============================================================================
# memory/db.py — SQLite Schema Definition และ Connection Helpers
# =============================================================================
# หน้าที่: กำหนดโครงสร้างฐานข้อมูล (schema) ของ ContextOS memory
#   และจัดเตรียมฟังก์ชันสำหรับเปิด connection ไปยัง SQLite
# ความรับผิดชอบ:
#   1. นิยาม SQL schema สำหรับ 4 ตาราง: documents, chunks, summaries,
#      conversation_history
#   2. สร้าง indexes เพื่อเพิ่มประสิทธิภาพการค้นหา
#   3. จัดการ connection พร้อม foreign key enforcement
# ความสัมพันธ์กับระบบ ContextOS:
#   - ถูกเรียกใช้โดย repository.py เพื่อเปิด connection ก่อนทำ CRUD
#   - ถูกเรียกตอน bootstrap ระบบเพื่อสร้างตารางครั้งแรก
# Design Pattern: Separation of Concerns — แยก schema/connection logic
#   ออกจาก data access logic (repository.py) อย่างชัดเจน
# =============================================================================
"""SQLite schema and connection helpers for ContextOS memory."""

# pathlib ใช้จัดการ path ของไฟล์ database แบบ cross-platform
from pathlib import Path
# sqlite3 เป็น built-in module สำหรับ embedded database — ไม่ต้องติดตั้ง server
import sqlite3
# Union ใช้สร้าง type alias ให้รองรับทั้ง str และ Path
from typing import Union

# นำเข้า path default ของ database จาก config เพื่อให้ทุก module ใช้ค่าเดียวกัน
from contextos.config import DEFAULT_DB_PATH


# Type Alias: รองรับการส่ง path เป็นได้ทั้ง string หรือ Path object
# ช่วยให้ caller เรียกใช้ได้ยืดหยุ่น เช่น connect("data.db") หรือ connect(Path("data.db"))
DatabasePath = Union[str, Path]


# =============================================================================
# SCHEMA — โครงสร้างฐานข้อมูลทั้งหมดของ ContextOS Memory
# =============================================================================
# ใช้ CREATE TABLE IF NOT EXISTS เพื่อให้รันซ้ำได้อย่างปลอดภัย (idempotent)
# PRAGMA foreign_keys = ON บังคับให้ SQLite ตรวจสอบ foreign key constraints
# ซึ่ง SQLite ปิด foreign keys ไว้เป็นค่า default ต้องเปิดเองทุกครั้ง
# =============================================================================
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filepath TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL UNIQUE,
    title TEXT,
    mime_type TEXT,
    size_bytes INTEGER,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    start_char INTEGER,
    end_char INTEGER,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    summary TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'document',
    token_count INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);
CREATE INDEX IF NOT EXISTS idx_documents_filepath ON documents(filepath);
"""
# ---------------------------------------------------------------------------
# คำอธิบายตารางแต่ละตาราง:
#
# ตาราง documents:
#   เก็บ metadata ของไฟล์ที่ถูก import เข้าระบบ
#   - filepath: path เต็มของไฟล์ต้นฉบับ (UNIQUE เพื่อป้องกัน import ซ้ำ)
#   - sha256: hash ของเนื้อหาไฟล์ใช้ตรวจจับ deduplication
#     (ถ้าเนื้อหาเหมือนกันจะมี hash เดียวกันแม้ชื่อไฟล์ต่างกัน)
#   - metadata_json: เก็บข้อมูลเพิ่มเติมเป็น JSON string
#
# ตาราง chunks:
#   เก็บท่อนข้อความ (text segments) ที่ถูกแยกออกจาก document
#   - document_id: foreign key เชื่อมกลับไปหา document ต้นทาง
#   - chunk_index: ลำดับของ chunk ในเอกสาร (UNIQUE ร่วมกับ document_id)
#   - start_char, end_char: ตำแหน่งตัวอักษรในเอกสารต้นฉบับ
#   - ON DELETE CASCADE: ลบ chunks อัตโนมัติเมื่อ document ถูกลบ
#
# ตาราง summaries:
#   เก็บบทสรุประดับ document หรือ section
#   - level: ระบุว่าเป็นสรุประดับไหน เช่น 'document', 'section'
#   - document_id: อาจเป็น NULL ได้สำหรับ summary ที่ไม่ผูกกับ document ใด
#
# ตาราง conversation_history:
#   เก็บประวัติการสนทนาระหว่าง user กับ assistant
#   - role: ระบุว่าเป็น 'user' หรือ 'assistant'
#   - ไม่มี foreign key เพราะสนทนาเป็นอิสระจาก document
#
# Indexes:
#   - idx_chunks_document_id: เร่งการค้นหา chunks ตาม document
#   - idx_documents_sha256: เร่งการตรวจ deduplication ด้วย hash
#   - idx_documents_filepath: เร่งการค้นหา document ตาม path
# ---------------------------------------------------------------------------


def connect(db_path: DatabasePath = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with foreign key checks enabled."""
    # จุดประสงค์: เปิด connection ไปยัง SQLite database พร้อมตั้งค่าที่จำเป็น
    # Input: db_path — path ของไฟล์ database (รองรับ ":memory:" สำหรับ testing)
    # Output: sqlite3.Connection object ที่พร้อมใช้งาน
    # ขั้นตอน:
    #   1. สร้าง parent directories ถ้ายังไม่มี (ยกเว้น in-memory database)
    #   2. เปิด connection
    #   3. ตั้ง row_factory = sqlite3.Row เพื่อให้ access column ด้วยชื่อได้
    #   4. เปิด foreign key enforcement (SQLite ปิดเป็น default)

    path = Path(db_path)
    # ":memory:" เป็น special path ของ SQLite สำหรับ in-memory database
    # ใช้ใน unit test เพื่อไม่ต้องสร้างไฟล์จริง
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    # Row factory ทำให้เข้าถึง column ด้วยชื่อแทน index เช่น row["id"] แทน row[0]
    connection.row_factory = sqlite3.Row
    # SQLite ไม่บังคับ foreign key โดย default — ต้องเปิดเองทุก connection
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: DatabasePath = DEFAULT_DB_PATH) -> None:
    """Create the ContextOS memory schema if it does not already exist."""
    # จุดประสงค์: สร้างตารางและ indexes ทั้งหมดถ้ายังไม่มีในฐานข้อมูล
    # เหตุผลที่ต้องมี: เรียกตอน application startup หรือ first run
    #   เพื่อเตรียมฐานข้อมูลให้พร้อมใช้งาน
    # ใช้ executescript แทน execute เพราะ SCHEMA มีหลายคำสั่ง SQL พร้อมกัน

    with connect(db_path) as connection:
        connection.executescript(SCHEMA)
