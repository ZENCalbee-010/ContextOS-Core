# ---------------------------------------------------------------------------
# ไฟล์: evaluation/__init__.py
# หน้าที่: เป็น public API ของ sub-package evaluation
#          ทำหน้าที่ re-export ฟังก์ชัน metrics และ EvaluationRunner
# ความรับผิดชอบ: ให้เครื่องมือสำหรับวัดคุณภาพการ retrieval
#               เช่น compression ratio, precision@k, latency, token reduction
# ความสัมพันธ์กับระบบ: ใช้ร่วมกับ BM25Retriever เพื่อประเมินผล
#                     การค้นหาข้อมูลในระบบ ContextOS
# ---------------------------------------------------------------------------
"""Evaluation tools for retrieval and context quality."""

# นำเข้า pure metric functions — ไม่มี side effects, ใช้คำนวณค่าตัววัดต่าง ๆ
from contextos.evaluation.metrics import (
    average,
    compression_ratio,
    latency_ms,
    retrieval_precision_at_k,
    token_reduction_efficiency,
)

# นำเข้า runner สำหรับรัน evaluation จริง และ dataclass เก็บผลลัพธ์
from contextos.evaluation.runner import EvaluationRunner, RetrievalEvaluation

__all__ = [
    "EvaluationRunner",
    "RetrievalEvaluation",
    "average",
    "compression_ratio",
    "latency_ms",
    "retrieval_precision_at_k",
    "token_reduction_efficiency",
]
