# ---------------------------------------------------------------------------
# ไฟล์: ai_adapter/mock_adapter.py
# หน้าที่: Adapter จำลอง (mock) สำหรับใช้ในการทดสอบ (testing)
#          และ workflow แบบ dry-run ที่ไม่ต้องการเรียก API จริง
# ความรับผิดชอบ:
#   - เก็บบันทึก prompt ทุกครั้งที่ถูกเรียก (เพื่อ assertion ใน test)
#   - คืนค่า response สำเร็จรูป (canned response) ที่กำหนดไว้ล่วงหน้า
# ความสัมพันธ์กับระบบ: สืบทอดจาก BaseAIAdapter (Strategy Pattern)
#   ใช้แทน ClaudeAdapter/OpenAIAdapter ในสภาพแวดล้อมทดสอบ
#   เพื่อให้ test รันได้โดยไม่ต้องมี API key หรือเชื่อมต่ออินเทอร์เน็ต
# ---------------------------------------------------------------------------
"""Mock AI adapter for tests and local dry workflows."""

from contextos.ai_adapter.base import AIAdapterError, AIResponse, BaseAIAdapter


class MockAdapter(BaseAIAdapter):
    provider = "mock"

    def __init__(self, response: str = "Mock response generated from selected context.") -> None:
        # response: คำตอบสำเร็จรูปที่จะคืนทุกครั้งที่ถูกเรียก generate()
        self.response = response
        # prompts: เก็บ prompt ที่ได้รับทั้งหมด เพื่อให้ test ตรวจสอบได้ว่า
        # มีการเรียก generate() กี่ครั้ง และด้วย prompt อะไรบ้าง
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> AIResponse:
        # ป้องกันการส่ง prompt ว่างเปล่า เพื่อให้ behavior สอดคล้องกับ adapter จริง
        if not prompt.strip():
            raise AIAdapterError("Prompt cannot be empty.")
        # บันทึก prompt ลงใน list สำหรับ test assertions
        self.prompts.append(prompt)
        return AIResponse(content=self.response, model="mock-model", provider=self.provider)
