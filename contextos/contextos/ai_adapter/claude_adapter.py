# ---------------------------------------------------------------------------
# ไฟล์: ai_adapter/claude_adapter.py
# หน้าที่: Concrete adapter สำหรับ Anthropic Claude AI model
# ความรับผิดชอบ: อ่าน API key จาก environment variable แล้วส่ง prompt
#               ไปยัง Claude API (ปัจจุบันยังไม่ implement การเรียก API จริง)
# ความสัมพันธ์กับระบบ: สืบทอดจาก BaseAIAdapter (Strategy Pattern)
#                     ใช้แทนกันได้กับ OpenAIAdapter และ MockAdapter
# ---------------------------------------------------------------------------
"""Claude AI adapter."""

# os ใช้สำหรับอ่าน environment variable (ANTHROPIC_API_KEY)
import os

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter, MissingAPIKeyError


class ClaudeAdapter(BaseAIAdapter):
    """Claude adapter configured through environment variables."""

    provider = "claude"

    def __init__(
        self,
        *,
        api_key_env: str = "ANTHROPIC_API_KEY",
        model: str = "claude-3-5-sonnet-latest",
    ) -> None:
        # เก็บชื่อ env var ไว้เพื่อใช้แสดงข้อความ error ที่ชัดเจน
        self.api_key_env = api_key_env
        # อ่าน API key จาก environment — ถ้าไม่มีจะได้ None
        self.api_key = os.getenv(api_key_env)
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        # ตรวจสอบว่ามี API key หรือไม่ก่อนเรียก API
        if not self.api_key:
            raise MissingAPIKeyError(
                f"Missing Claude API key. Set {self.api_key_env} in the environment."
            )
        # ป้องกันการส่ง prompt ว่างเปล่า
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")

        # TODO: ยังไม่ได้ implement การเรียก Anthropic API จริง
        # ต้องติดตั้ง anthropic library และเชื่อมต่อ client ก่อนใช้งาน
        raise AIAdapterError(
            "Claude API calls are not implemented yet. Install and wire an Anthropic client before using this adapter."
        )
