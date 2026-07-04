# ---------------------------------------------------------------------------
# ไฟล์: token_budget/selector.py
# หน้าที่: เลือก chunks ให้อยู่ภายใน token budget โดยใช้ Greedy Algorithm
# ความรับผิดชอบ:
#   - เรียง chunks ตามอัตราส่วน score/token (คุณค่าต่อ token)
#   - เลือก chunks ที่ดีที่สุดจนกว่า budget จะเต็ม
#   - สำรอง safety margin (ค่าเริ่มต้น 12%) ไว้เผื่อ overhead
# อัลกอริทึม Greedy Selection:
#   - เป็น greedy algorithm ที่เลือกสิ่งที่ "ดีที่สุด" ในขณะนั้น
#   - คำนวณ score-per-token ratio แล้วเรียงจากมากไปน้อย
#   - เพิ่ม chunk ทีละตัวจนกว่า budget จะไม่พอ
#   - ไม่ได้ให้คำตอบที่ optimal เสมอไป แต่เร็วและใกล้เคียง optimal
# ความสัมพันธ์กับระบบ:
#   - รับ BM25Result (ที่มี score + chunk) จาก retrieval module
#   - ส่งผลลัพธ์ให้ ContextBuilder ประกอบ prompt
#   - ค่า max_tokens มาจาก config.DEFAULT_TOKEN_BUDGET
# ---------------------------------------------------------------------------
"""Greedy token budget selection for scored chunks."""

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar


# ChunkLike Protocol: กำหนดว่า object ที่มี attribute 'token_count'
# สามารถใช้ร่วมกับ selector ได้ (structural typing / duck typing)
class ChunkLike(Protocol):
    token_count: int


# ScoredChunkLike Protocol: กำหนดว่า object ต้องมี chunk และ score
# เพื่อให้ selector คำนวณ score-per-token ratio ได้
class ScoredChunkLike(Protocol):
    chunk: ChunkLike
    score: float


T = TypeVar("T", bound=ScoredChunkLike)


# TokenBudgetSelection: เก็บผลลัพธ์การเลือก chunks ภายใน budget
# ใช้ Generic[T] เพื่อให้ type ของ selected items ยืดหยุ่น
@dataclass(frozen=True)
class TokenBudgetSelection(Generic[T]):
    selected: list[T]           # chunks ที่ถูกเลือก
    total_tokens: int           # จำนวน tokens รวมที่ใช้จริง
    max_tokens: int             # budget สูงสุดที่ระบุ
    effective_budget: int       # budget หลังหัก safety margin
    safety_margin: float        # สัดส่วน margin ที่สำรองไว้ (เช่น 0.12 = 12%)


class TokenBudgetSelector:
    """Select highest score-per-token chunks under a token budget."""

    def __init__(self, *, safety_margin: float = 0.12) -> None:
        # safety_margin ต้องอยู่ระหว่าง 0 ถึง 1 (ไม่รวม 1)
        # ค่า 0.12 หมายถึงสำรอง 12% ของ budget เผื่อ prompt overhead
        # (เช่น SYSTEM_PROMPT, INSTRUCTIONS ของ ContextBuilder)
        if safety_margin < 0 or safety_margin >= 1:
            raise ValueError("safety_margin must be >= 0 and < 1")
        self.safety_margin = safety_margin

    def select(self, scored_chunks: list[T], *, max_tokens: int) -> TokenBudgetSelection[T]:
        """
        เลือก chunks ตาม Greedy Algorithm
        Input: scored_chunks (chunks พร้อม score), max_tokens (budget สูงสุด)
        Output: TokenBudgetSelection ที่มี chunks ที่เลือก + สถิติ
        ขั้นตอน:
        1. คำนวณ effective_budget = max_tokens × (1 - safety_margin)
        2. เรียง chunks ตาม score/token ratio (มากไปน้อย)
        3. เพิ่ม chunk ทีละตัว ถ้ายังไม่เกิน budget
        """
        if max_tokens < 0:
            raise ValueError("max_tokens must be >= 0")

        # คำนวณ budget จริงหลังหัก safety margin
        effective_budget = int(max_tokens * (1 - self.safety_margin))
        selected: list[T] = []
        total_tokens = 0

        # Greedy: เรียงตาม score-per-token จากมากไปน้อย แล้วเลือกทีละตัว
        for item in sorted(scored_chunks, key=self._score_per_token, reverse=True):
            token_count = max(item.chunk.token_count, 0)
            # chunk ที่มี token_count = 0 → เพิ่มได้ฟรี (ไม่กิน budget)
            if token_count == 0:
                selected.append(item)
                continue
            # ถ้าเพิ่มแล้วเกิน budget → ข้ามไป (ไม่ break เพราะอาจมี chunk เล็กกว่าที่ใส่ได้)
            if total_tokens + token_count > effective_budget:
                continue
            selected.append(item)
            total_tokens += token_count

        return TokenBudgetSelection(
            selected=selected,
            total_tokens=total_tokens,
            max_tokens=max_tokens,
            effective_budget=effective_budget,
            safety_margin=self.safety_margin,
        )

    def _score_per_token(self, item: ScoredChunkLike) -> float:
        """
        คำนวณ score-per-token ratio — ใช้เป็น key ในการเรียงลำดับ
        ยิ่งสูง → chunk นี้ให้ "ความเกี่ยวข้อง" ต่อ token ที่ใช้ไปมาก
        ใช้ max(token_count, 1) เพื่อป้องกัน division by zero
        """
        token_count = max(item.chunk.token_count, 1)
        return item.score / token_count
