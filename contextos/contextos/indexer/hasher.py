# ---------------------------------------------------------------------------
# ไฟล์: indexer/hasher.py
# หน้าที่: คำนวณ SHA-256 hash ของไฟล์แบบ incremental
#          (อ่านทีละ chunk โดยไม่ต้องโหลดไฟล์ทั้งหมดเข้า memory)
# ความรับผิดชอบ: ใช้ตรวจจับว่าไฟล์มีการเปลี่ยนแปลงหรือไม่
#               ถ้า hash เหมือนเดิม → ข้ามการ re-index (ประหยัดเวลา)
# อัลกอริทึม SHA-256:
#   - เป็น cryptographic hash function ที่ให้ผลลัพธ์ 256-bit (64 hex chars)
#   - มีคุณสมบัติ collision-resistant — โอกาสที่ไฟล์ 2 ไฟล์จะมี hash ซ้ำกันต่ำมาก
#   - การอ่านแบบ incremental (ทีละ 1MB) ทำให้รองรับไฟล์ขนาดใหญ่ได้
#     โดยไม่ใช้ memory เกินควร
# ความสัมพันธ์กับระบบ: ถูกเรียกใช้โดย FileIndexer.index_file()
#                     ในขั้นตอนแรกสุดของ Pipeline
# ---------------------------------------------------------------------------
"""File hashing utilities for incremental indexing."""

from pathlib import Path
import hashlib


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Compute the SHA-256 hash for a file without loading it all at once."""

    # สร้าง SHA-256 hash object สำหรับ incremental update
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        # อ่านไฟล์ทีละ chunk_size (ค่าเริ่มต้น 1MB = 1024*1024 bytes)
        # iter() จะหยุดเมื่อได้ b"" (หมดไฟล์)
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    # hexdigest() คืนค่า hash เป็น string hex 64 ตัวอักษร
    return digest.hexdigest()
