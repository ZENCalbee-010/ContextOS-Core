# =============================================================================
# compression/medium.py — Concrete Strategy: การบีบอัดระดับกลาง (Medium Compression)
# =============================================================================
# หน้าที่: บีบอัดข้อความโดยเก็บเฉพาะประโยคที่สำคัญที่สุด (40% แรก)
#          ใช้อัลกอริทึม Luhn-style sentence scoring ในการจัดอันดับประโยค
#
# ความรับผิดชอบ:
#   - นับความถี่ของคำสำคัญ (กรอง stopwords ออก)
#   - ให้คะแนนแต่ละประโยคตามค่าเฉลี่ยความถี่ของคำสำคัญในประโยคนั้น
#   - เลือกเก็บ 40% ของประโยคที่มีคะแนนสูงสุด
#   - รักษาลำดับประโยคตามต้นฉบับ
#
# อัลกอริทึม Luhn-style Sentence Scoring:
#   ┌─────────────────────────────────────────────────────────────────┐
#   │ แนวคิดของ Luhn (1958):                                        │
#   │   - คำที่ปรากฏบ่อยในเอกสารมีแนวโน้มเป็นคำสำคัญ                │
#   │   - ประโยคที่มีคำสำคัญรวมตัวกันเยอะ = ประโยคที่สรุปเนื้อหาได้ดี │
#   │                                                                 │
#   │ วิธีการในโค้ดนี้:                                               │
#   │   1. นับความถี่ทุกคำ (ไม่รวม stopwords)                         │
#   │   2. คะแนนประโยค = ผลรวมความถี่คำสำคัญ / จำนวนคำสำคัญ          │
#   │      (ค่าเฉลี่ยความถี่ — ป้องกัน bias จากประโยคยาว)            │
#   │   3. เรียงคะแนนจากมากไปน้อย เลือก top 40%                      │
#   │   4. เรียงกลับตามลำดับเดิมเพื่อรักษาความต่อเนื่อง              │
#   └─────────────────────────────────────────────────────────────────┘
#
# Design Pattern: Concrete Strategy ของ Strategy Pattern
#   สืบทอดจาก BaseCompressor และ implement _compress()
#
# ความสัมพันธ์กับระบบ ContextOS:
#   - เหมาะสำหรับ context ที่ยาวปานกลาง ที่ต้องลดขนาดลงอย่างมีนัยสำคัญ
#     แต่ยังต้องรักษาประโยคที่สำคัญที่สุดไว้
#   - ทำงานร่วมกับ base.py (สืบทอด BaseCompressor, ใช้ WORD_RE, split_sentences)
# =============================================================================

"""Medium rule-based compression using Luhn-style sentence scoring."""

# Counter — โครงสร้างข้อมูลสำหรับนับความถี่คำอย่างมีประสิทธิภาพ
from collections import Counter
# math.ceil — ปัดเศษขึ้นเพื่อให้จำนวนประโยคที่เก็บไม่น้อยกว่า 40%
import math

# นำเข้า BaseCompressor (Strategy Interface) และเครื่องมือจาก base.py
# WORD_RE — regex สำหรับจับคำที่มีความยาว >= 3 ตัวอักษร
# split_sentences — ฟังก์ชันแยกข้อความเป็นรายประโยค
from contextos.compression.base import BaseCompressor, WORD_RE, split_sentences


# ---------------------------------------------------------------------------
# MediumCompressor — บีบอัดด้วยการให้คะแนนประโยคแบบ Luhn
# ---------------------------------------------------------------------------
# ใช้ทำอะไร: เลือกเก็บเฉพาะ 40% ของประโยคที่มีคะแนนสูงสุด
# รับผิดชอบอะไร: วิเคราะห์ความสำคัญของประโยคโดยดูจากความถี่คำ
# ใช้เมื่อไร: เมื่อ context ยาวเกินไปสำหรับ light compression
#   แต่ยังไม่ต้องการตัดรุนแรงถึงระดับ aggressive
# ทำงานร่วมกับ: base.py (BaseCompressor, WORD_RE, split_sentences)
class MediumCompressor(BaseCompressor):
    strategy = "medium"

    # -----------------------------------------------------------------------
    # _compress() — ตรรกะหลักของ Medium Compression
    # -----------------------------------------------------------------------
    # จุดประสงค์: เลือกประโยคสำคัญที่สุดจากข้อความ
    # Input: text (str) — ข้อความ context
    # Output: str — ข้อความที่เหลือเฉพาะประโยคสำคัญ (40%)
    # ขั้นตอน:
    #   1. แยกข้อความเป็นรายประโยค
    #   2. ถ้ามี ≤1 ประโยค คืนข้อความเดิม (ไม่มีอะไรให้ตัด)
    #   3. นับความถี่คำทั้งเอกสาร
    #   4. ให้คะแนนแต่ละประโยค
    #   5. เลือก top 40% โดยรักษาลำดับเดิม
    def _compress(self, text: str) -> str:
        sentences = split_sentences(text)
        # กรณีมีประโยคเดียวหรือไม่มีเลย ไม่จำเป็นต้องบีบอัด
        if len(sentences) <= 1:
            return text

        # นับความถี่คำทั้งเอกสาร (ไม่รวม stopwords)
        frequencies = self._word_frequencies(text)

        # ให้คะแนนทุกประโยค เก็บ (index, sentence, score) เพื่อรักษาลำดับเดิม
        scored = [
            (index, sentence, self._score_sentence(sentence, frequencies))
            for index, sentence in enumerate(sentences)
        ]

        # คำนวณจำนวนประโยคที่จะเก็บ = 40% ของทั้งหมด (ขั้นต่ำ 1 ประโยค)
        # ใช้ math.ceil เพื่อปัดขึ้นให้ไม่ตัดมากเกินไป
        keep_count = max(1, math.ceil(len(sentences) * 0.4))

        # เรียงตามคะแนนจากมากไปน้อย แล้วเก็บ index ของ top-k ประโยค
        # ใช้ set เพื่อให้ค้นหาเร็ว O(1) ตอนกรองประโยค
        selected_indexes = {
            index
            for index, _sentence, _score in sorted(
                scored,
                key=lambda item: item[2],
                reverse=True,
            )[:keep_count]
        }

        # รวมประโยคที่ถูกเลือกกลับตามลำดับเดิม (enumerate ให้ลำดับต้นฉบับ)
        # เหตุผล: รักษาความต่อเนื่องของเนื้อหา ไม่สลับลำดับประโยค
        return " ".join(
            sentence
            for index, sentence in enumerate(sentences)
            if index in selected_indexes
        )

    # -----------------------------------------------------------------------
    # _word_frequencies() — นับความถี่คำทั้งเอกสาร (ไม่รวม stopwords)
    # -----------------------------------------------------------------------
    # จุดประสงค์: สร้างตาราง frequency สำหรับใช้ให้คะแนนประโยค
    # Input: text — ข้อความทั้งหมด
    # Output: Counter — dictionary ที่ key=คำ, value=จำนวนครั้งที่ปรากฏ
    # เหตุผลที่กรอง stopwords: คำเช่น "the", "and" ปรากฏบ่อยแต่ไม่บ่งบอกความสำคัญ
    def _word_frequencies(self, text: str) -> Counter[str]:
        words = [
            word.lower()
            for word in WORD_RE.findall(text)
            if word.lower() not in STOPWORDS
        ]
        return Counter(words)

    # -----------------------------------------------------------------------
    # _score_sentence() — ให้คะแนนประโยคตามค่าเฉลี่ยความถี่คำสำคัญ
    # -----------------------------------------------------------------------
    # จุดประสงค์: วัดความสำคัญของประโยค
    # Input: sentence — ประโยคที่จะให้คะแนน, frequencies — ตารางความถี่คำ
    # Output: float — คะแนนความสำคัญ (ยิ่งสูงยิ่งสำคัญ)
    # สูตร: ผลรวมความถี่คำสำคัญ / จำนวนคำสำคัญ (ค่าเฉลี่ย)
    # เหตุผลที่ใช้ค่าเฉลี่ย: ป้องกันไม่ให้ประโยคยาว ๆ ได้เปรียบเพียงเพราะมีคำเยอะ
    # กรณีพิเศษ: ถ้าประโยคไม่มีคำสำคัญเลย คืน 0.0
    def _score_sentence(self, sentence: str, frequencies: Counter[str]) -> float:
        words = [word.lower() for word in WORD_RE.findall(sentence)]
        important_words = [word for word in words if word not in STOPWORDS]
        if not important_words:
            return 0.0
        return sum(frequencies[word] for word in important_words) / len(important_words)


# ---------------------------------------------------------------------------
# STOPWORDS — ชุดคำหยุด (stop words) ที่จะถูกตัดออกจากการวิเคราะห์ความถี่
# ---------------------------------------------------------------------------
# เหตุผลที่ต้องมี: คำเหล่านี้ปรากฏบ่อยในทุกเอกสารภาษาอังกฤษ
#   แต่ไม่ได้บ่งบอกหัวข้อหรือเนื้อหาสำคัญ ถ้าไม่กรองออก
#   ทุกประโยคจะได้คะแนนใกล้เคียงกันเพราะเจอ stopwords เท่า ๆ กัน
# หมายเหตุ: ใช้ชุดเล็ก ๆ ที่ครอบคลุมคำที่พบบ่อยที่สุดเท่านั้น
#   ไม่ต้องครบทุกคำเหมือน NLP toolkit เพราะเป็น rule-based ที่เน้นความเร็ว
STOPWORDS = {
    "and",
    "are",
    "but",
    "for",
    "from",
    "into",
    "not",
    "the",
    "this",
    "that",
    "with",
    "you",
    "your",
}
