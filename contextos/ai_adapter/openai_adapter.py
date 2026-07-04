# ---------------------------------------------------------------------------
# ไฟล์: ai_adapter/openai_adapter.py
# หน้าที่: Concrete adapter สำหรับ OpenAI API (GPT models)
# ความรับผิดชอบ: อ่าน API key จาก environment variable แล้วส่ง prompt
#               ไปยัง OpenAI API (ปัจจุบันยังไม่ implement การเรียก API จริง)
# ความสัมพันธ์กับระบบ: สืบทอดจาก BaseAIAdapter (Strategy Pattern)
#                     ใช้แทนกันได้กับ ClaudeAdapter และ MockAdapter
# ---------------------------------------------------------------------------
"""OpenAI AI adapter placeholder."""

# os ใช้สำหรับอ่าน environment variable (OPENAI_API_KEY)
import os

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter, MissingAPIKeyError


class OpenAIAdapter(BaseAIAdapter):
    """Placeholder OpenAI adapter configured through environment variables."""

    provider = "openai"

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        model: str = "gpt-4.1-mini",
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
                f"Missing OpenAI API key. Set {self.api_key_env} in the environment."
            )
        # ป้องกันการส่ง prompt ว่างเปล่า
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")

        # TODO: ยังไม่ได้ implement การเรียก OpenAI API จริง
        # ต้องติดตั้ง openai library และเชื่อมต่อ client ก่อนใช้งาน
        raise AIAdapterError(
            "OpenAI API calls are not implemented yet. Wire an OpenAI client before using this adapter."
        )
