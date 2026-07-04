# ---------------------------------------------------------------------------
# parsers/code_parser.py — Parser สำหรับแบ่งซอร์สโค้ดเป็น chunks
# ---------------------------------------------------------------------------
# หน้าที่ : แยกซอร์สโค้ด (Python, JavaScript, TypeScript) ออกเป็น chunk
#           โดยใช้ตำแหน่งประกาศ function/class เป็นจุดตัด
# ความรับผิดชอบ :
#   1. ค้นหาจุดเริ่มต้นของ symbol (def, class, function, arrow function)
#   2. แบ่ง code ตาม symbol boundaries
#   3. ถ้าไม่พบ symbol ใดเลย → ใช้ sliding window ตาม token limit แทน
# ความสัมพันธ์กับระบบ :
#   - เป็น Concrete Strategy ของ BaseParser (Strategy Pattern)
#   - ใช้ร่วมกับ CodeReader ที่อ่านไฟล์โค้ดมาเป็นข้อความดิบ
# ---------------------------------------------------------------------------
"""Regex-based code chunking parser."""

import re

from contextos.parsers.base import BaseParser, ParsedChunk


# ---------------------------------------------------------------------------
# Regex สำหรับตรวจจับจุดเริ่มต้นของ symbol ในภาษาต่าง ๆ
# ---------------------------------------------------------------------------
# PYTHON_SYMBOL_RE — จับ def, async def, class ใน Python
#   ตัวอย่าง: "def foo(", "async def bar(", "class MyClass:"
PYTHON_SYMBOL_RE = re.compile(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_]\w*)")
# JS_TS_SYMBOL_RE — จับ function/class ใน JavaScript/TypeScript
#   รองรับ export และ async ที่นำหน้า เช่น "export async function fetchData("
JS_TS_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)"
)
# ARROW_SYMBOL_RE — จับ arrow function ที่ assign ให้ตัวแปร
#   เช่น "const handler = async (" หรือ "export let process = ("
ARROW_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("
)


# ---------------------------------------------------------------------------
# CodeParser — Concrete Strategy สำหรับแบ่งซอร์สโค้ด
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : ตัดซอร์สโค้ดออกเป็น chunks โดยเคารพขอบเขตของ function/class
# รับผิดชอบอะไร : ตรวจหา symbol → แบ่ง range → ตัดด้วย token limit
# ใช้เมื่อไร : เมื่อ pipeline ได้รับไฟล์โค้ด (.py, .js, .ts ฯลฯ)
# ทำงานร่วมกับ : BaseParser (parent), CodeReader (ส่งข้อความดิบมาให้)
class CodeParser(BaseParser):
    """Split source code around simple class and function declarations."""

    # จุดประสงค์ : แปลงข้อความโค้ดทั้งหมดเป็น list ของ ParsedChunk
    # Input : text — ซอร์สโค้ดทั้งไฟล์เป็น string
    # Output : list[ParsedChunk] — chunks ที่ตัดแบ่งแล้ว
    # ขั้นตอนการทำงาน :
    #   1. แยกข้อความเป็นบรรทัด
    #   2. ค้นหาตำแหน่ง symbol ด้วย regex
    #   3. ถ้าไม่พบ symbol → fallback ไปใช้ sliding window
    #   4. ถ้าพบ → แบ่ง ranges ตาม symbol → ตัดแต่ละ range ด้วย token limit
    #   5. renumber ลำดับ chunk ให้ต่อเนื่อง
    def parse(self, text: str) -> list[ParsedChunk]:
        lines = text.splitlines()
        symbol_starts = self._find_symbol_starts(lines)

        # ถ้าไม่พบ symbol ใดเลย (เช่น ไฟล์ config หรือ data)
        # → ใช้ line-window chunking เป็น fallback strategy
        if not symbol_starts:
            return self._chunk_line_window(lines)

        # สร้างรายการ range (start_line, end_line, section_name)
        ranges: list[tuple[int, int, str | None]] = []
        # ถ้ามีโค้ดก่อน symbol แรก (เช่น imports, module docstring)
        # → สร้าง range พิเศษชื่อ "module" ให้โค้ดส่วนนั้น
        if symbol_starts[0][0] > 1:
            ranges.append((1, symbol_starts[0][0] - 1, "module"))

        # แต่ละ symbol ครอบคลุมตั้งแต่บรรทัดที่ประกาศจนถึงก่อน symbol ถัดไป
        for index, (start_line, section) in enumerate(symbol_starts):
            next_start = (
                symbol_starts[index + 1][0]
                if index + 1 < len(symbol_starts)
                else len(lines) + 1
            )
            ranges.append((start_line, next_start - 1, section))

        # ตัดแต่ละ range ด้วย sliding window โดยรักษาขอบเขต token
        chunks: list[ParsedChunk] = []
        for start_line, end_line, section in ranges:
            block_lines = lines[start_line - 1 : end_line]
            chunks.extend(
                self._chunk_line_window(
                    block_lines,
                    start_line_offset=start_line,
                    section=section,
                    start_index=len(chunks),
                )
            )

        # จัดลำดับ chunk_index ใหม่ให้ต่อเนื่องจาก 0
        return self._renumber(chunks)

    # จุดประสงค์ : สแกนทุกบรรทัดเพื่อหาตำแหน่งที่ประกาศ function/class
    # Input : lines — รายการบรรทัดทั้งหมดของไฟล์
    # Output : list ของ (line_number, symbol_name)
    # วิธีการ : ลอง match regex ทั้ง 3 แบบ (Python, JS/TS, Arrow)
    #   ถ้า match อันใดอันหนึ่ง → บันทึกหมายเลขบรรทัดและชื่อ symbol
    def _find_symbol_starts(self, lines: list[str]) -> list[tuple[int, str]]:
        starts: list[tuple[int, str]] = []
        for line_number, line in enumerate(lines, start=1):
            match = (
                PYTHON_SYMBOL_RE.match(line)
                or JS_TS_SYMBOL_RE.match(line)
                or ARROW_SYMBOL_RE.match(line)
            )
            if match:
                starts.append((line_number, match.group(1)))
        return starts

    # จุดประสงค์ : ตัดบรรทัดเป็น chunks โดยใช้ sliding window ตาม token limit
    # Input :
    #   - lines : บรรทัดที่จะตัด
    #   - start_line_offset : หมายเลขบรรทัดเริ่มต้นจริงในไฟล์ (1-indexed)
    #   - section : ชื่อ section ที่บรรทัดเหล่านี้สังกัด
    #   - start_index : ลำดับ chunk เริ่มต้น
    # Output : list[ParsedChunk]
    # อัลกอริทึม (Sliding Window) :
    #   - สะสมบรรทัดใน current_lines ทีละบรรทัด
    #   - ก่อนเพิ่มบรรทัดใหม่ ตรวจสอบว่า token ยังไม่เกิน max_tokens
    #   - ถ้าเกิน → flush current_lines เป็น chunk แล้วเริ่มใหม่
    def _chunk_line_window(
        self,
        lines: list[str],
        *,
        start_line_offset: int = 1,
        section: str | None = None,
        start_index: int = 0,
    ) -> list[ParsedChunk]:
        chunks: list[ParsedChunk] = []
        current_lines: list[str] = []
        current_start_line = start_line_offset

        for relative_index, line in enumerate(lines, start=0):
            line_number = start_line_offset + relative_index
            candidate = [*current_lines, line]
            # ตรวจสอบว่าถ้าเพิ่มบรรทัดนี้แล้ว token จะเกิน limit หรือไม่
            if current_lines and self.count_tokens("\n".join(candidate)) > self.max_tokens:
                # เกิน limit → flush บรรทัดที่สะสมไว้เป็น chunk
                chunks.append(
                    self._make_chunk(
                        current_lines,
                        start_index + len(chunks),
                        current_start_line,
                        line_number - 1,
                        section,
                    )
                )
                # เริ่ม chunk ใหม่ด้วยบรรทัดปัจจุบัน
                current_lines = [line]
                current_start_line = line_number
            else:
                current_lines = candidate

        # flush บรรทัดที่เหลืออยู่เป็น chunk สุดท้าย
        if current_lines:
            chunks.append(
                self._make_chunk(
                    current_lines,
                    start_index + len(chunks),
                    current_start_line,
                    start_line_offset + len(lines) - 1,
                    section,
                )
            )

        return chunks

    # จุดประสงค์ : สร้าง ParsedChunk จากบรรทัดที่สะสมไว้
    # เหตุผลที่แยกเป็น method : หลีกเลี่ยงการซ้ำโค้ดสร้าง chunk ในหลายจุด
    def _make_chunk(
        self,
        lines: list[str],
        index: int,
        start_line: int,
        end_line: int,
        section: str | None,
    ) -> ParsedChunk:
        content = "\n".join(lines).strip()
        return ParsedChunk(
            content=content,
            chunk_index=index,
            start_line=start_line,
            end_line=end_line,
            section=section,
            token_count=self.count_tokens(content),
        )
