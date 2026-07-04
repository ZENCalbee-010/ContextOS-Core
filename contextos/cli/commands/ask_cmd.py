# ===========================================================================
# ไฟล์: cli/commands/ask_cmd.py
# หน้าที่: คำสั่ง `context ask` - ถามคำถามโดยใช้ local context + AI
# ความรับผิดชอบ: เชื่อม pipeline ทั้งหมดของ Retrieval-Augmented Generation (RAG):
#   1. ดึง chunk ที่เกี่ยวข้องจากฐานข้อมูล (retrieval)
#   2. เลือก chunk ที่พอดีกับ token budget (budget selection)
#   3. สร้าง prompt จาก context ที่เลือก (context building)
#   4. ส่ง prompt ไปยัง AI adapter เพื่อสร้างคำตอบ (generation)
#   5. บันทึกบทสนทนาลงฐานข้อมูล (conversation saving)
# ความสัมพันธ์กับระบบ: ใช้งาน modules หลัก 6 ตัว:
#   - SQLiteMemoryRepository: เข้าถึงข้อมูลใน SQLite
#   - EvaluationRunner: รัน retrieval พร้อมวัด latency
#   - TokenBudgetSelector: เลือก chunk ให้อยู่ภายใน token budget
#   - ContextBuilder: สร้าง prompt สุดท้ายจาก chunk ที่เลือก
#   - AI Adapter (Claude/Mock): สร้างคำตอบจาก prompt
#   - format_source: จัดรูปแบบแหล่งอ้างอิง
# Design Pattern: Pipeline Pattern - ข้อมูลไหลผ่านขั้นตอนที่ต่อเนื่องกัน
#   แต่ละขั้นตอนแปลงข้อมูลและส่งต่อไปยังขั้นตอนถัดไป
# ===========================================================================
"""Ask command for retrieval-augmented local context prompts."""

from pathlib import Path
from typing import Literal

import typer

# AIAdapterError: exception สำหรับจัดการข้อผิดพลาดจาก AI provider
# ClaudeAdapter: ตัวเชื่อมต่อ Anthropic Claude API
# MockAdapter: ตัวเชื่อมต่อจำลองสำหรับทดสอบโดยไม่ต้องเรียก API จริง
from contextos.ai_adapter import AIAdapterError, ClaudeAdapter, MockAdapter
from contextos.cli.output import safe_echo
from contextos.config import DEFAULT_DB_PATH, DEFAULT_TOKEN_BUDGET
from contextos.context_builder import ContextBuilder
from contextos.evaluation import EvaluationRunner
from contextos.formatting import format_source
from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository
from contextos.token_budget import (
    TokenBudgetSelector,
    calculate_token_savings,
    format_token_savings_report,
)


def ask_context(
    question: str = typer.Argument(..., help="Question to answer."),
    top_k: int = typer.Option(10, "--top-k", help="Number of retrieval candidates."),
    budget: int = typer.Option(
        DEFAULT_TOKEN_BUDGET,
        "--budget",
        "-b",
        help="Maximum context token budget.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show selected context without calling an AI adapter.",
    ),
    adapter_name: Literal["claude", "mock"] = typer.Option(
        "claude",
        "--adapter",
        help="AI adapter to use.",
    ),
    db_path: Path = typer.Option(
        DEFAULT_DB_PATH,
        "--db-path",
        help="SQLite database path.",
    ),
) -> None:
    """Answer a question using selected local context."""

    # ขั้นตอนที่ 1: เตรียม repository สำหรับเข้าถึงฐานข้อมูล
    repository = SQLiteMemoryRepository(db_path)
    repository.init_db()

    # ขั้นตอนที่ 2: Retrieval - ค้นหา chunk ที่เกี่ยวข้องกับคำถาม
    # EvaluationRunner จะวัด latency ของการค้นหาด้วย
    retrieval_evaluation = EvaluationRunner(repository).run_retrieval(
        question,
        top_k=top_k,
    )
    retrieval_results = retrieval_evaluation.results

    # ขั้นตอนที่ 3: Budget Selection - เลือก chunk ให้อยู่ภายใน token budget
    # ใช้ Greedy Selection: เลือก chunk ที่ดีที่สุดก่อน จนกว่าจะเต็ม budget
    selection = TokenBudgetSelector().select(retrieval_results, max_tokens=budget)
    selected = selection.selected
    token_savings = calculate_token_savings(
        repository.get_all_chunks(),
        selected_context_tokens=selection.total_tokens,
    )

    # ขั้นตอนที่ 4: Context Building - สร้าง prompt จาก chunk ที่เลือก
    prompt = ContextBuilder(repository).build(question, selected)

    # โหมด dry_run: แสดงผล context ที่เลือกโดยไม่เรียก AI
    # เหมาะสำหรับ debug หรือตรวจสอบว่า retrieval ทำงานถูกต้อง
    if dry_run:
        safe_echo("DRY RUN")
        safe_echo(f"Selected chunks: {len(selected)}")
        safe_echo(f"Tokens used: {selection.total_tokens}")
        safe_echo("")
        safe_echo(format_token_savings_report(token_savings))
        safe_echo("")
        safe_echo(prompt)
        safe_echo("")
        _print_sources(repository, [item.chunk for item in selected])
        return

    # ขั้นตอนที่ 5: Generation - ส่ง prompt ไปยัง AI adapter เพื่อสร้างคำตอบ
    adapter = _adapter(adapter_name)
    try:
        response = adapter.generate(prompt)
    except AIAdapterError as exc:
        raise typer.ClickException(str(exc)) from exc

    # ขั้นตอนที่ 6: Conversation Saving - บันทึกทั้งคำถามและคำตอบลง DB
    # เก็บ metadata ที่จำเป็นสำหรับการวิเคราะห์ย้อนหลัง
    # เช่น chunk ไหนที่ใช้, ใช้ token เท่าไร, latency เท่าไร
    conversation_metadata = {
        "used_chunk_ids": [item.chunk.id for item in selected],
        "tokens_used": selection.total_tokens,
        "top_k": top_k,
        "budget": budget,
        "adapter": adapter.provider,
        "latency_ms": retrieval_evaluation.latency_ms,
        "token_savings": token_savings.to_metadata(),
    }
    repository.save_conversation("user", question, metadata=conversation_metadata)
    repository.save_conversation(
        "assistant",
        response.content,
        metadata=conversation_metadata,
    )

    # แสดงคำตอบจาก AI และแหล่งอ้างอิงให้ผู้ใช้
    safe_echo(response.content)
    safe_echo("")
    safe_echo(format_token_savings_report(token_savings))
    safe_echo("")
    _print_sources(repository, [item.chunk for item in selected])


def _adapter(name: str):
    """Factory function สำหรับสร้าง AI adapter ตามชื่อที่ระบุ
    จุดประสงค์: แยก logic การสร้าง adapter ออกจากฟังก์ชันหลัก
    เหตุผลที่ต้องมี: ทำให้เพิ่ม adapter ใหม่ได้ง่าย (Strategy Pattern)
    """
    if name == "mock":
        return MockAdapter()
    return ClaudeAdapter()


def _print_sources(repository: SQLiteMemoryRepository, chunks: list[Chunk]) -> None:
    """แสดงรายการแหล่งอ้างอิง (sources) ที่ใช้ตอบคำถาม
    จุดประสงค์: ให้ผู้ใช้ตรวจสอบได้ว่าคำตอบอ้างอิงจากไฟล์ไหนบ้าง
    เหตุผลที่ต้องมี: เพิ่มความโปร่งใสและน่าเชื่อถือให้กับคำตอบจาก AI
    """
    safe_echo("Sources:")
    if not chunks:
        safe_echo("- none")
        return
    for chunk in chunks:
        safe_echo(f"- {format_source(chunk, repository)}")
