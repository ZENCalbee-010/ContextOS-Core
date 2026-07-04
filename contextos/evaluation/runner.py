# ---------------------------------------------------------------------------
# ไฟล์: evaluation/runner.py
# หน้าที่: รัน evaluation ของระบบ retrieval อย่างง่าย (lightweight)
#          โดยวัด latency และ precision@k ของ BM25Retriever
# ความรับผิดชอบ:
#   - ห่อ (wrap) BM25Retriever.search() ด้วยการจับเวลา
#   - คำนวณ precision@k ถ้ามีชุดข้อมูล relevant chunk IDs
#   - เก็บผลลัพธ์ใน RetrievalEvaluation dataclass
# ความสัมพันธ์กับระบบ:
#   - ใช้ BM25Retriever จาก retrieval module
#   - ใช้ metric functions จาก evaluation.metrics
#   - ใช้ SQLiteMemoryRepository เพื่อดึง chunks
# ---------------------------------------------------------------------------
"""Evaluation runner utilities."""

from dataclasses import dataclass
# perf_counter ให้ค่าเวลาที่แม่นยำสูง เหมาะสำหรับวัด latency
from time import perf_counter

from contextos.evaluation.metrics import latency_ms, retrieval_precision_at_k
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.retrieval import BM25Result, BM25Retriever


# RetrievalEvaluation: เก็บผลลัพธ์การประเมินการค้นหาครั้งหนึ่ง
# frozen=True ทำให้เป็น immutable — ผลลัพธ์ไม่ควรถูกแก้ไขหลังสร้าง
@dataclass(frozen=True)
class RetrievalEvaluation:
    query: str                            # คำค้นหาที่ใช้ทดสอบ
    results: list[BM25Result]             # ผลลัพธ์จาก BM25 retrieval
    latency_ms: float                     # เวลาที่ใช้ในการค้นหา (มิลลิวินาที)
    precision_at_k: float | None = None   # Precision@K (ถ้ามี relevant IDs ให้เทียบ)


class EvaluationRunner:
    """Run lightweight local retrieval evaluations."""

    def __init__(self, repository: SQLiteMemoryRepository) -> None:
        self.repository = repository

    def run_retrieval(
        self,
        query: str,
        *,
        top_k: int = 5,
        relevant_chunk_ids: set[int] | None = None,
    ) -> RetrievalEvaluation:
        """
        รัน retrieval evaluation ครั้งเดียว
        Input: query (คำค้นหา), top_k (จำนวนผลลัพธ์), relevant_chunk_ids (ชุด ID ที่ถูกต้อง)
        Output: RetrievalEvaluation ที่มี latency และ precision
        ขั้นตอน: จับเวลา → เรียก BM25 search → คำนวณ precision (ถ้ามี) → สร้างผลลัพธ์
        """
        # จับเวลาเริ่มต้น
        start = perf_counter()
        results = BM25Retriever(self.repository).search(query, top_k=top_k)
        # จับเวลาสิ้นสุด
        end = perf_counter()

        # คำนวณ precision@k เฉพาะเมื่อมีชุด relevant IDs ให้เทียบ
        precision = None
        if relevant_chunk_ids is not None:
            precision = retrieval_precision_at_k(
                [result.chunk.id for result in results],
                relevant_chunk_ids,
                k=top_k,
            )

        return RetrievalEvaluation(
            query=query,
            results=results,
            latency_ms=latency_ms(start, end),
            precision_at_k=precision,
        )
