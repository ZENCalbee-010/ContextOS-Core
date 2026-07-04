# ---------------------------------------------------------------------------
# ไฟล์: ai_adapter/__init__.py
# หน้าที่: เป็น public API ของ sub-package ai_adapter
#          ทำหน้าที่ re-export คลาสและ exception ที่สำคัญ
#          เพื่อให้ผู้ใช้ import ได้สะดวกจาก contextos.ai_adapter โดยตรง
# ความรับผิดชอบ: รวบรวม adapters ทั้งหมด (Claude, OpenAI, Mock)
#               ไว้ในจุดเดียว ตาม Strategy Pattern
# ความสัมพันธ์กับระบบ: module ภายนอก (เช่น ContextBuilder)
#                     จะ import adapter จากที่นี่ โดยไม่ต้องรู้ว่า
#                     แต่ละ adapter อยู่ในไฟล์ไหน
# ---------------------------------------------------------------------------
"""Adapters for optional AI model integrations."""

# นำเข้า base classes, dataclass, และ exceptions จาก base module
from contextos.ai_adapter.base import (
    AIAdapterError,
    AIResponse,
    BaseAIAdapter,
    MissingAPIKeyError,
)

# นำเข้า concrete adapters แต่ละตัว
from contextos.ai_adapter.claude_adapter import ClaudeAdapter
from contextos.ai_adapter.mock_adapter import MockAdapter
from contextos.ai_adapter.openai_adapter import OpenAIAdapter

__all__ = [
    "AIAdapterError",
    "AIResponse",
    "BaseAIAdapter",
    "ClaudeAdapter",
    "MissingAPIKeyError",
    "MockAdapter",
    "OpenAIAdapter",
]
