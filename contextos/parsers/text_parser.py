# ---------------------------------------------------------------------------
# parsers/text_parser.py — Parser สำหรับแบ่งข้อความธรรมดาและ Markdown
# ---------------------------------------------------------------------------
# หน้าที่ : แบ่งข้อความ plain text หรือ Markdown ออกเป็น chunks
#           โดยใช้หัวข้อ (heading) เป็นจุดตัดหลัก และ token limit เป็นตัวควบคุมขนาด
# ความรับผิดชอบ :
#   1. ตรวจจับ Markdown heading (# ถึง ######) เพื่อแบ่ง section
#   2. ติดตาม active_section เพื่อระบุว่า chunk สังกัดหัวข้อไหน
#   3. ตัดข้อความด้วย sliding window เมื่อเกิน max_tokens
# ความสัมพันธ์กับระบบ :
#   - เป็น Concrete Strategy ของ BaseParser (Strategy Pattern)
#   - ใช้ร่วมกับ TextReader ที่อ่าน .txt/.md มาเป็นข้อความดิบ
# ---------------------------------------------------------------------------
"""Text and Markdown chunking parser."""

import re

from contextos.parsers.base import BaseParser, ParsedChunk


# HEADING_RE — regex สำหรับจับ Markdown heading ระดับ 1-6
# จับกลุ่ม 2 คือข้อความหัวข้อ เช่น "## Installation" → จับได้ "Installation"
# ใช้เป็นจุดตัดหลักในการแบ่ง section ของเอกสาร
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


# ---------------------------------------------------------------------------
# TextParser — Concrete Strategy สำหรับแบ่ง text/Markdown
# ---------------------------------------------------------------------------
# ใช้ทำอะไร : ตัดข้อความทั่วไป/Markdown เป็น chunks ขนาดเหมาะสม
# รับผิดชอบอะไร : แบ่งตาม heading + ควบคุมขนาดด้วย token limit
# ใช้เมื่อไร : เมื่อ pipeline ได้รับไฟล์ .txt หรือ .md
# ทำงานร่วมกับ : BaseParser (parent), TextReader (ส่งข้อความดิบมาให้)
class TextParser(BaseParser):
    """Split plain text or Markdown into token-bounded chunks."""

    # จุดประสงค์ : แปลงข้อความทั้งหมดเป็น list ของ ParsedChunk
    # Input : text — ข้อความ plain text หรือ Markdown ทั้งไฟล์
    # Output : list[ParsedChunk] — chunks ที่ตัดแบ่งแล้ว
    # ขั้นตอนการทำงาน :
    #   1. วนอ่านทีละบรรทัด
    #   2. ถ้าเจอ heading → flush chunk ปัจจุบัน แล้วอัปเดต active_section
    #   3. สะสมบรรทัดใน current_lines จนกว่าจะเกิน token limit
    #   4. ถ้าเกิน → flush เป็น chunk แล้วเริ่มใหม่
    #   5. ท้ายสุด flush บรรทัดที่เหลือ
    def parse(self, text: str) -> list[ParsedChunk]:
        chunks: list[ParsedChunk] = []
        current_lines: list[str] = []
        current_start_line: int | None = None
        current_section: str | None = None
        # active_section ติดตามหัวข้อล่าสุดที่พบ
        # ใช้ระบุว่า chunk ถัดไปอยู่ภายใต้หัวข้อไหน
        # ต่างจาก current_section ตรงที่ active_section อัปเดตทันทีที่เจอ heading
        # แต่ current_section จะถูก set เฉพาะตอนเริ่ม chunk ใหม่เท่านั้น
        active_section: str | None = None

        for line_number, line in enumerate(text.splitlines(), start=1):
            heading = HEADING_RE.match(line)
            if heading:
                # เจอ heading ใหม่ → flush chunk ที่สะสมไว้ (ถ้ามี)
                # เพื่อให้ heading ถัดไปเป็นจุดเริ่มต้นของ chunk ใหม่
                if current_lines:
                    chunks.append(
                        self._make_chunk(
                            current_lines,
                            len(chunks),
                            current_start_line,
                            line_number - 1,
                            current_section,
                        )
                    )
                    current_lines = []
                    current_start_line = None

                # อัปเดตชื่อหัวข้อปัจจุบัน
                active_section = heading.group(2).strip()

            # ถ้ายังไม่ได้กำหนดบรรทัดเริ่มต้น → เริ่ม chunk ใหม่ที่บรรทัดนี้
            if current_start_line is None:
                current_start_line = line_number
                current_section = active_section

            candidate = [*current_lines, line]
            # ตรวจสอบ token limit — ถ้าเพิ่มบรรทัดนี้แล้วเกิน → flush
            if current_lines and self.count_tokens("\n".join(candidate)) > self.max_tokens:
                chunks.append(
                    self._make_chunk(
                        current_lines,
                        len(chunks),
                        current_start_line,
                        line_number - 1,
                        current_section,
                    )
                )
                # เริ่ม chunk ใหม่ด้วยบรรทัดปัจจุบัน
                current_lines = [line]
                current_start_line = line_number
                current_section = active_section
            else:
                current_lines = candidate

        # flush บรรทัดที่เหลือเป็น chunk สุดท้าย
        if current_lines:
            chunks.append(
                self._make_chunk(
                    current_lines,
                    len(chunks),
                    current_start_line,
                    len(text.splitlines()) or 1,
                    current_section,
                )
            )

        return chunks

    # จุดประสงค์ : สร้าง ParsedChunk จากบรรทัดที่สะสมไว้
    # เหตุผลที่แยกเป็น method : ลดการซ้ำโค้ด เพราะถูกเรียกจากหลายจุดใน parse()
    def _make_chunk(
        self,
        lines: list[str],
        index: int,
        start_line: int | None,
        end_line: int | None,
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
