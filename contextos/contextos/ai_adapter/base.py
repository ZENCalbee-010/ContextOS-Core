# ---------------------------------------------------------------------------
# ไฟล์: ai_adapter/base.py
# หน้าที่: กำหนด interface หลัก (abstract base class) สำหรับ AI adapters
#          ทั้งหมดในระบบ ContextOS
# ความรับผิดชอบ:
#   - กำหนด "สัญญา" (contract) ที่ทุก adapter ต้องปฏิบัติตาม
#   - นิยาม data class สำหรับผลลัพธ์จาก AI (AIResponse)
#   - นิยาม exception hierarchy สำหรับข้อผิดพลาดของ adapter
# Design Pattern: Strategy Pattern — BaseAIAdapter คือ "Strategy interface"
#   ที่อนุญาตให้สลับ AI provider (OpenAI, Claude, Mock) ได้โดยไม่ต้อง
#   เปลี่ยนโค้ดของ client (เช่น ContextBuilder)
# ความสัมพันธ์กับระบบ: ClaudeAdapter, OpenAIAdapter, MockAdapter
#   ล้วนสืบทอดจาก BaseAIAdapter
# ---------------------------------------------------------------------------
"""Base interfaces for AI model adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# === Exception Hierarchy ===
# ลำดับชั้นของ exception เฉพาะสำหรับ AI adapter
# ช่วยให้ caller สามารถ catch ได้อย่างเจาะจง

class AIAdapterError(RuntimeError):
    """Raised when an AI adapter cannot complete a request."""


# MissingAPIKeyError สืบทอดจาก AIAdapterError
# แยกออกมาเพื่อให้ caller สามารถแยกแยะปัญหา "ไม่มี API key"
# ออกจากปัญหาทั่วไปของ adapter ได้
class MissingAPIKeyError(AIAdapterError):
    """Raised when an adapter requires an API key that is not configured."""


# === Data Class สำหรับผลลัพธ์ ===
# frozen=True ทำให้ instance เป็น immutable (ไม่สามารถแก้ไขค่าได้หลังสร้าง)
# เหมาะสำหรับ value object ที่ส่งผ่านระหว่าง layer
@dataclass(frozen=True)
class AIResponse:
    content: str       # เนื้อหาคำตอบจาก AI model
    model: str         # ชื่อ model ที่ใช้ เช่น "gpt-4.1-mini"
    provider: str      # ชื่อ provider เช่น "openai", "claude", "mock"


# === Strategy Interface ===
# BaseAIAdapter เป็น abstract class ที่บังคับให้ทุก concrete adapter
# implement method generate() — หัวใจของ Strategy Pattern
class BaseAIAdapter(ABC):
    """Strategy interface for optional AI model providers."""

    provider: str  # แต่ละ adapter ต้องระบุชื่อ provider ของตน

    @abstractmethod
    def generate(self, prompt: str) -> AIResponse:
        """Generate an answer for a completed context prompt."""
