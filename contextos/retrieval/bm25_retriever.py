# ---------------------------------------------------------------------------
# ไฟล์: retrieval/bm25_retriever.py
# หน้าที่: ค้นหา chunks ที่เกี่ยวข้องกับ query โดยใช้ BM25 algorithm
# ความรับผิดชอบ:
#   - ดึง chunks ทั้งหมดจาก SQLite repository
#   - ใช้ BM25Okapi (จาก rank_bm25 library) จัดอันดับความเกี่ยวข้อง
#   - คืน top-K ผลลัพธ์ เรียงตาม score จากมากไปน้อย
# อัลกอริทึม BM25 (Best Matching 25):
#   - เป็นอัลกอริทึม ranking ที่ใช้กันแพร่หลายใน Information Retrieval
#   - พิจารณาทั้ง Term Frequency (TF) และ Inverse Document Frequency (IDF)
#   - BM25Okapi เป็น variant ที่มีการ normalize ตามความยาวของเอกสาร
#   - ให้น้ำหนักสูงกับคำที่ปรากฏบ่อยใน chunk นั้น แต่หายากในเอกสารอื่น
# ความสัมพันธ์กับระบบ:
#   - ผลลัพธ์ (BM25Result) ถูกส่งต่อไปยัง TokenBudgetSelector
#     เพื่อเลือก chunks ที่พอดีกับ token budget
#   - ใช้ SQLiteMemoryRepository (Repository Pattern) เพื่อดึง chunks
# ---------------------------------------------------------------------------
"""BM25-only retrieval over stored SQLite chunks."""

from dataclasses import dataclass
import re

# rank_bm25: library ภายนอกที่ implement BM25Okapi algorithm
from rank_bm25 import BM25Okapi

from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


# TOKEN_RE: regex สำหรับ tokenize ข้อความ — จับคำที่ประกอบด้วย
# ตัวอักษร, ตัวเลข, หรือ underscore (รองรับชื่อตัวแปรในโค้ดด้วย)
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


# BM25Result: เก็บผลลัพธ์การค้นหาสำหรับ chunk เดียว
# frozen=True → immutable เพื่อให้ปลอดภัยในการส่งต่อ
@dataclass(frozen=True)
class BM25Result:
    chunk: Chunk    # chunk ที่ค้นพบ
    score: float    # คะแนน BM25 ยิ่งสูงยิ่งเกี่ยวข้อง


class BM25Retriever:
    """Retrieve top-k chunks with rank-bm25 BM25Okapi."""

    def __init__(self, repository: SQLiteMemoryRepository) -> None:
        self.repository = repository
        self._index_signature: tuple[int, int | None] | None = None
        self._chunks: list[Chunk] = []
        self._tokenized_chunks: list[list[str]] = []
        self._bm25: BM25Okapi | None = None

    def search(self, query: str, *, top_k: int = 5) -> list[BM25Result]:
        """
        ค้นหา chunks ที่เกี่ยวข้องกับ query
        Input: query (คำค้นหา), top_k (จำนวนผลลัพธ์สูงสุด)
        Output: list ของ BM25Result เรียงตาม score จากมากไปน้อย
        ขั้นตอน:
        1. ดึง chunks ทั้งหมดจาก repository
        2. Tokenize ทุก chunk และ query
        3. สร้าง BM25 index → คำนวณ score ของทุก chunk
        4. เรียงลำดับและตัดเอา top-K
        """
        if top_k <= 0:
            return []

        # ดึง chunks ทั้งหมดจากฐานข้อมูล
        chunks, bm25 = self._load_index()
        if not chunks or bm25 is None:
            return []

        # Tokenize เนื้อหาของแต่ละ chunk และ query
        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        # สร้าง BM25 index จาก tokenized chunks แล้วคำนวณ score
        scores = bm25.get_scores(tokenized_query)

        # จับคู่ chunk กับ score แล้วเรียงจากมากไปน้อย
        scored = [
            BM25Result(chunk=chunk, score=float(score))
            for chunk, score in zip(chunks, scores)
        ]

        return sorted(scored, key=lambda result: result.score, reverse=True)[:top_k]

    def _load_index(self) -> tuple[list[Chunk], BM25Okapi | None]:
        """Lazy-load and cache the BM25 index until stored chunks change."""
        signature = self.repository.get_chunk_cache_signature()
        if self._bm25 is not None and self._index_signature == signature:
            return self._chunks, self._bm25

        chunks = self.repository.get_all_chunks()
        tokenized_chunks = [tokenize(chunk.content) for chunk in chunks]
        bm25 = BM25Okapi(tokenized_chunks) if tokenized_chunks else None

        self._index_signature = signature
        self._chunks = chunks
        self._tokenized_chunks = tokenized_chunks
        self._bm25 = bm25
        return self._chunks, self._bm25

    def clear_cache(self) -> None:
        """Clear the cached BM25 index."""
        self._index_signature = None
        self._chunks = []
        self._tokenized_chunks = []
        self._bm25 = None


def tokenize(text: str) -> list[str]:
    """
    แปลงข้อความเป็น list ของ tokens (ตัวพิมพ์เล็กทั้งหมด)
    ใช้ regex TOKEN_RE เพื่อจับคำ — เรียบง่ายแต่เพียงพอสำหรับ BM25
    """
    return [token.lower() for token in TOKEN_RE.findall(text)]
