# =============================================================================
# compression/light.py — Concrete Strategy: การบีบอัดระดับเบา (Light Compression)
# =============================================================================
# หน้าที่: ลดขนาดข้อความด้วยการปรับ whitespace ให้เป็นมาตรฐาน
#          และ (ตัวเลือก) ลบ code comment ออก
#
# ความรับผิดชอบ:
#   - ยุบช่องว่าง/แท็บซ้ำ ๆ ให้เหลือช่องว่างเดียว
#   - ลบช่องว่างหัว-ท้ายบรรทัด
#   - ยุบบรรทัดว่างติดกันเกิน 2 ให้เหลือ 2
#   - ลบ comment ใน code (# และ //) ถ้าผู้ใช้เปิดตัวเลือกนี้
#
# ระดับความรุนแรง: ต่ำสุด — ไม่ลบเนื้อหาจริง เพียงทำความสะอาด formatting
# เหตุผลที่ต้องมี: context จาก source code มักมี whitespace เกินจำเป็น
#   การลดลงช่วยประหยัด token โดยไม่สูญเสียความหมาย
#
# Design Pattern: Concrete Strategy ของ Strategy Pattern
#   สืบทอดจาก BaseCompressor และ implement _compress()
#
# ความสัมพันธ์กับระบบ ContextOS:
#   - เหมาะสำหรับกรณีที่ต้องรักษาเนื้อหาให้ครบถ้วนที่สุด เช่น context ที่สั้นอยู่แล้ว
#   - ทำงานร่วมกับ base.py (สืบทอด BaseCompressor)
# =============================================================================

"""Light rule-based compression."""

# re — ใช้ regular expression สำหรับจัดการ whitespace และลบ comment
import re

# นำเข้า BaseCompressor เพื่อสืบทอดเป็น Concrete Strategy
from contextos.compression.base import BaseCompressor


# ---------------------------------------------------------------------------
# LightCompressor — บีบอัดด้วยการปรับ whitespace (ระดับเบาที่สุด)
# ---------------------------------------------------------------------------
# ใช้ทำอะไร: ลดขนาด context โดยไม่ลบเนื้อหาใด ๆ
# รับผิดชอบอะไร: ทำความสะอาด formatting ของข้อความ
# ใช้เมื่อไร: เมื่อ context ไม่ยาวมาก หรือต้องการรักษาความสมบูรณ์ของเนื้อหา
# ทำงานร่วมกับ: base.py (BaseCompressor)
class LightCompressor(BaseCompressor):
    strategy = "light"

    # -----------------------------------------------------------------------
    # __init__() — กำหนดค่าตัวเลือก
    # -----------------------------------------------------------------------
    # Input: remove_code_comments — ถ้า True จะลบ comment ในโค้ดด้วย
    # เหตุผลที่เป็น keyword-only (ใช้ *): ป้องกันการส่ง argument ผิดตำแหน่ง
    def __init__(self, *, remove_code_comments: bool = False) -> None:
        self.remove_code_comments = remove_code_comments

    # -----------------------------------------------------------------------
    # _compress() — ตรรกะหลักของ Light Compression
    # -----------------------------------------------------------------------
    # จุดประสงค์: ลด whitespace ที่ไม่จำเป็นออกจากข้อความ
    # Input: text (str) — ข้อความ context ดิบ
    # Output: str — ข้อความที่ลด whitespace แล้ว
    # ขั้นตอน:
    #   1. (ถ้าเปิด) ลบ code comment ก่อน
    #   2. ยุบ space/tab ซ้ำ ๆ ให้เหลือ space เดียว
    #   3. ลบ space หัว-ท้ายของแต่ละบรรทัด
    #   4. ยุบบรรทัดว่างติดกัน 3+ เหลือ 2 (รักษาการแบ่งย่อหน้า)
    def _compress(self, text: str) -> str:
        if self.remove_code_comments:
            text = self._remove_code_comments(text)

        # ยุบ space และ tab ที่ซ้ำกันให้เหลือ space เดียว
        text = re.sub(r"[ \t]+", " ", text)
        # ลบ space ก่อนและหลัง newline (ทำให้แต่ละบรรทัดชิดซ้าย)
        text = re.sub(r" *\n *", "\n", text)
        # ยุบบรรทัดว่างติดกัน 3 บรรทัดขึ้นไปให้เหลือ 2 (คั่นย่อหน้าพอ)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    # -----------------------------------------------------------------------
    # _remove_code_comments() — ลบ comment ออกจาก source code
    # -----------------------------------------------------------------------
    # จุดประสงค์: ลบ comment ทั้งแบบเต็มบรรทัดและแบบ inline
    # Input: text — source code ที่อาจมี comment
    # Output: str — source code โดยไม่มี comment
    # รองรับ:
    #   - Python-style (#) — ทั้งเต็มบรรทัดและ inline
    #   - C/JS-style (//) — ทั้งเต็มบรรทัดและ inline
    # ข้อจำกัด: ไม่จัดการ /* */ block comment หรือ string literal ที่มี # หรือ //
    def _remove_code_comments(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            stripped = line.lstrip()
            # ข้ามบรรทัดที่เป็น comment ทั้งบรรทัด (ขึ้นต้นด้วย # หรือ //)
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            # ลบ inline comment: whitespace ตามด้วย # หรือ // จนจบบรรทัด
            line = re.sub(r"\s+#.*$", "", line)
            line = re.sub(r"\s+//.*$", "", line)
            lines.append(line)
        return "\n".join(lines)
