# ---------------------------------------------------------------------------
# ไฟล์: evaluation/metrics.py
# หน้าที่: รวบรวม pure functions สำหรับคำนวณ evaluation metrics
#          ของระบบ retrieval และ compression ใน ContextOS
# ความรับผิดชอบ: คำนวณค่าตัววัดแบบ stateless (ไม่มี side effects)
#               แต่ละฟังก์ชันรับ input → คืน float โดยไม่เปลี่ยนแปลง state ใด ๆ
# ความสัมพันธ์กับระบบ: ถูกเรียกใช้โดย EvaluationRunner
#                     เพื่อวัดประสิทธิภาพของ BM25Retriever
# ---------------------------------------------------------------------------
"""Evaluation metrics for ContextOS."""

from collections.abc import Iterable


def compression_ratio(original_length: int, compressed_length: int) -> float:
    """
    คำนวณอัตราส่วนการบีบอัด (compression ratio)
    สูตร: 1 - (compressed / original)
    ผลลัพธ์ใกล้ 1.0 = บีบอัดได้มาก, ใกล้ 0.0 = แทบไม่ได้บีบอัด
    Input: original_length (ขนาดก่อนบีบอัด), compressed_length (ขนาดหลังบีบอัด)
    Output: float ระหว่าง 0.0 ถึง 1.0
    """
    if original_length <= 0:
        return 0.0
    return 1 - (compressed_length / original_length)


def retrieval_precision_at_k(
    retrieved_ids: Iterable[int],
    relevant_ids: set[int],
    *,
    k: int,
) -> float:
    """
    คำนวณ Precision@K — สัดส่วนผลลัพธ์ที่ "ตรงประเด็น" ใน top-K ผลแรก
    สูตร: จำนวน retrieved ที่อยู่ใน relevant / min(k, จำนวน retrieved)
    Input: retrieved_ids (ID ที่ค้นได้), relevant_ids (ID ที่ถูกต้อง), k (จำนวนที่พิจารณา)
    Output: float ระหว่าง 0.0 ถึง 1.0
    ยิ่งสูงยิ่งดี — หมายถึงระบบค้นหาได้ตรงประเด็นมากขึ้น
    """
    if k <= 0:
        return 0.0

    # ตัดเอาเฉพาะ top-K ผลลัพธ์แรก
    top_ids = list(retrieved_ids)[:k]
    if not top_ids:
        return 0.0

    # นับจำนวน ID ที่อยู่ในชุด relevant
    relevant_count = sum(1 for item_id in top_ids if item_id in relevant_ids)
    return relevant_count / min(k, len(top_ids))


def latency_ms(start_time: float, end_time: float) -> float:
    """
    แปลงระยะเวลาจากวินาทีเป็นมิลลิวินาที
    Input: start_time, end_time (จาก perf_counter)
    Output: float (มิลลิวินาที), ไม่ต่ำกว่า 0.0
    """
    return max(0.0, (end_time - start_time) * 1000)


def token_reduction_efficiency(original_tokens: int, reduced_tokens: int) -> float:
    """
    คำนวณประสิทธิภาพการลด token — คล้าย compression_ratio แต่ใช้กับจำนวน token
    สูตร: 1 - (reduced / original)
    Input: original_tokens (จำนวน token เดิม), reduced_tokens (จำนวน token หลังลด)
    Output: float ระหว่าง 0.0 ถึง 1.0
    """
    if original_tokens <= 0:
        return 0.0
    return 1 - (reduced_tokens / original_tokens)


def average(values: Iterable[float]) -> float:
    """
    คำนวณค่าเฉลี่ย (arithmetic mean)
    Input: iterable ของ float
    Output: ค่าเฉลี่ย หรือ 0.0 ถ้า iterable ว่าง
    """
    value_list = list(values)
    if not value_list:
        return 0.0
    return sum(value_list) / len(value_list)
