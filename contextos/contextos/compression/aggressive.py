# =============================================================================
# compression/aggressive.py — Concrete Strategy: การบีบอัดระดับรุนแรง (Aggressive)
# =============================================================================
# หน้าที่: บีบอัดข้อความให้เหลือเฉพาะโครงสร้างสำคัญ (หัวข้อ, bullet, function
#          signature) และประโยคแรกของแต่ละย่อหน้า
#
# ความรับผิดชอบ:
#   - ดึงหัวข้อ Markdown (# heading)
#   - ดึง bullet/numbered list items
#   - ดึง function/class signature จาก source code
#   - ดึงประโยคแรกของแต่ละย่อหน้า (เป็นตัวแทนเนื้อหาย่อหน้านั้น)
#   - ตัดข้อมูลซ้ำออก (deduplication)
#
# อัลกอริทึม: Greedy Structural Extraction (ดึงโครงสร้างแบบโลภ)
#   ┌─────────────────────────────────────────────────────────────────┐
#   │ แนวคิด: ข้อมูลที่สำคัญที่สุดในเอกสารมักอยู่ที่:              │
#   │   1. หัวข้อ — บอกโครงสร้างของเอกสาร                            │
#   │   2. รายการ (bullets) — บอกประเด็นสำคัญ                        │
#   │   3. Signature — บอกโครงสร้างโค้ด (API surface)                │
#   │   4. ประโยคแรกของย่อหน้า — มักเป็น topic sentence              │
#   │                                                                 │
#   │ วิธีการ (2 รอบ):                                                │
#   │   รอบ 1: สแกนทีละบรรทัด จับ heading, bullet, signature         │
#   │   รอบ 2: สแกนทีละย่อหน้า ดึงประโยคแรก                         │
#   │   ทั้ง 2 รอบใช้ seen set กรองข้อมูลซ้ำ                        │
#   └─────────────────────────────────────────────────────────────────┘
#
# Design Pattern: Concrete Strategy ของ Strategy Pattern
#   สืบทอดจาก BaseCompressor และ implement _compress()
#
# ความสัมพันธ์กับระบบ ContextOS:
#   - ใช้เมื่อ context ยาวมาก ต้องลดขนาดอย่างรุนแรง
#   - ยอมสูญเสียรายละเอียดเพื่อแลกกับขนาดที่เล็กลงมาก
#   - ทำงานร่วมกับ base.py (BaseCompressor, split_paragraphs, split_sentences)
# =============================================================================

"""Aggressive rule-based compression."""

# re — ใช้ regular expression สำหรับจับ pattern โครงสร้างเอกสาร
import re

# นำเข้า BaseCompressor (Strategy Interface) และ helper functions จาก base.py
from contextos.compression.base import BaseCompressor, split_paragraphs, split_sentences


# ---------------------------------------------------------------------------
# Regex Constants — Pattern สำหรับจับโครงสร้างสำคัญ
# ---------------------------------------------------------------------------

# HEADING_RE — จับหัวข้อ Markdown (# ถึง ######)
# Pattern: เว้นวรรคนำไม่เกิน 3 ตัว + # 1-6 ตัว + เว้นวรรค + ตัวอักษร
# ตัวอย่างที่จับได้: "## Installation", "### API Reference"
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S+")

# BULLET_RE — จับรายการ bullet หรือ numbered list
# Pattern: whitespace นำ (ถ้ามี) + เครื่องหมาย (-*+) หรือตัวเลข. หรือตัวเลข) + เว้นวรรค
# ตัวอย่างที่จับได้: "- item", "* item", "1. item", "2) item"
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")

# SIGNATURE_RE — จับ function/class signature จากหลายภาษา
# รองรับ:
#   - Python: def func_name, async def func_name, class ClassName
#   - JavaScript/TypeScript: function func_name, export function, export async function
#   - JS arrow functions: const/let/var name = (...) หรือ async (...)
# เหตุผลที่ครอบคลุมหลายภาษา: ContextOS อาจรับ context จาก source code ภาษาต่าง ๆ
SIGNATURE_RE = re.compile(
    r"^\s*(?:export\s+)?(?:(?:async\s+)?(?:def|function)\s+\w+|class\s+\w+|"
    r"(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\()"
)


# ---------------------------------------------------------------------------
# AggressiveCompressor — บีบอัดด้วยการดึงโครงสร้างสำคัญ (ระดับรุนแรง)
# ---------------------------------------------------------------------------
# ใช้ทำอะไร: ลดข้อความให้เหลือเฉพาะ "โครง" ของเอกสาร
# รับผิดชอบอะไร: ดึงหัวข้อ, bullet, signature, และประโยคแรกของแต่ละย่อหน้า
# ใช้เมื่อไร: เมื่อ context ยาวมากจนต้องลดรุนแรง หรือเมื่อต้องการแค่ภาพรวม
# ทำงานร่วมกับ: base.py (BaseCompressor, split_paragraphs, split_sentences)
class AggressiveCompressor(BaseCompressor):
    strategy = "aggressive"

    # -----------------------------------------------------------------------
    # _compress() — ตรรกะหลักของ Aggressive Compression
    # -----------------------------------------------------------------------
    # จุดประสงค์: ดึงเฉพาะส่วนโครงสร้างสำคัญจากข้อความ
    # Input: text (str) — ข้อความ context ยาว ๆ
    # Output: str — ข้อความที่เหลือเฉพาะโครงสร้าง
    # ขั้นตอน (Greedy 2-pass):
    #   รอบ 1 — สแกนทีละบรรทัดเพื่อจับ structural elements
    #   รอบ 2 — สแกนทีละย่อหน้าเพื่อดึง topic sentence (ประโยคแรก)
    #   ทั้ง 2 รอบใช้ seen set ร่วมกันเพื่อกรองข้อมูลซ้ำ
    def _compress(self, text: str) -> str:
        kept: list[str] = []    # รายการบรรทัดที่จะเก็บไว้ในผลลัพธ์
        seen: set[str] = set()  # ชุดข้อความที่เคยเก็บแล้ว (สำหรับ deduplication)

        # --- รอบ 1: สแกนทีละบรรทัด จับ heading, bullet, signature ---
        for line in text.splitlines():
            stripped = line.strip()
            # ข้ามบรรทัดว่าง
            if not stripped:
                continue
            # ตรวจว่าบรรทัดนี้เป็นโครงสร้างสำคัญหรือไม่ (ตรวจทั้ง 3 pattern)
            if (
                HEADING_RE.match(stripped)
                or BULLET_RE.match(stripped)
                or SIGNATURE_RE.match(stripped)
            ):
                self._append_unique(kept, seen, stripped)

        # --- รอบ 2: ดึงประโยคแรกของแต่ละย่อหน้า (topic sentence) ---
        # ประโยคแรกของย่อหน้ามักสรุปเนื้อหาทั้งย่อหน้า
        for paragraph in split_paragraphs(text):
            sentences = split_sentences(paragraph)
            if sentences:
                self._append_unique(kept, seen, sentences[0])

        return "\n".join(kept)

    # -----------------------------------------------------------------------
    # _append_unique() — เพิ่มข้อความโดยไม่ให้ซ้ำ (Deduplication)
    # -----------------------------------------------------------------------
    # จุดประสงค์: ป้องกันข้อมูลซ้ำในผลลัพธ์
    # Input: kept — รายการผลลัพธ์, seen — ชุดข้อความที่เพิ่มแล้ว, value — ข้อความใหม่
    # เหตุผลที่ต้องมี: รอบ 1 และรอบ 2 อาจจับข้อความเดียวกัน เช่น
    #   ประโยคแรกของย่อหน้าที่เป็น bullet → ถูกจับทั้ง 2 รอบ
    #   ใช้ seen set (O(1) lookup) เพื่อตรวจสอบอย่างมีประสิทธิภาพ
    def _append_unique(self, kept: list[str], seen: set[str], value: str) -> None:
        if value not in seen:
            kept.append(value)
            seen.add(value)
