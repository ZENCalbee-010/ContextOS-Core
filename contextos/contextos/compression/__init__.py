# =============================================================================
# compression/__init__.py — จุดเข้าถึงหลักของ package การบีบอัดข้อความ (Text Compression)
# =============================================================================
# หน้าที่: Export คลาสทั้งหมดที่เกี่ยวข้องกับการบีบอัด context ออกจาก package นี้
#          เพื่อให้ module อื่น ๆ ใน ContextOS สามารถ import ได้สะดวกในที่เดียว
#
# ความรับผิดชอบ:
#   - รวมศูนย์การ export ของ compressor ทุกระดับ (light, medium, aggressive)
#   - Export คลาสฐาน (BaseCompressor) และ data class ผลลัพธ์ (CompressionResult)
#
# ความสัมพันธ์กับระบบ ContextOS:
#   - เป็นส่วนหนึ่งของ pipeline ที่ย่อขนาด context ก่อนส่งให้ LLM
#   - ใช้ Strategy Pattern — ผู้เรียกเลือก compressor ที่เหมาะสมตามสถานการณ์
#     โดยไม่ต้องรู้รายละเอียดภายในของแต่ละ strategy
#
# Design Pattern: Strategy Pattern
#   BaseCompressor = Strategy Interface (กำหนด contract ที่ทุก compressor ต้องทำตาม)
#   LightCompressor, MediumCompressor, AggressiveCompressor = Concrete Strategies
#   โมดูลที่เรียกใช้สามารถสลับ strategy ได้ตอน runtime โดยไม่แก้โค้ดเรียก
# =============================================================================

"""Compression utilities for selected context."""

# --- Import Concrete Strategy แต่ละระดับความรุนแรงของการบีบอัด ---
from contextos.compression.aggressive import AggressiveCompressor
from contextos.compression.base import BaseCompressor, CompressionResult
from contextos.compression.light import LightCompressor
from contextos.compression.medium import MediumCompressor

# __all__ กำหนดว่า "from contextos.compression import *" จะได้คลาสอะไรบ้าง
# เรียงตามลำดับตัวอักษรเพื่อความเป็นระเบียบ
__all__ = [
    "AggressiveCompressor",
    "BaseCompressor",
    "CompressionResult",
    "LightCompressor",
    "MediumCompressor",
]
