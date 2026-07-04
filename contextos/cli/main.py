# ===========================================================================
# ไฟล์: cli/main.py
# หน้าที่: จุดเริ่มต้น (entrypoint) ของ CLI ทั้งระบบ ContextOS
# ความรับผิดชอบ: สร้าง Typer application และลงทะเบียน (register) คำสั่งทั้ง 5:
#   - import  : นำเข้าไฟล์/โฟลเดอร์เข้าสู่ workspace
#   - optimize: ปรับปรุง compression metadata ของเอกสาร
#   - ask     : ถามคำถามโดยใช้ local context + AI
#   - search  : ค้นหา chunk ด้วย BM25
#   - stats   : แสดงสถิติ workspace
# ความสัมพันธ์กับระบบ: เป็นตัวกลางที่เชื่อม user กับ command modules ทั้งหมด
#   ถูกเรียกผ่าน `context` command ใน terminal
# Design Pattern: Command Pattern - แต่ละ command ถูกแยกเป็น module ย่อย
#   เพื่อให้ง่ายต่อการเพิ่ม command ใหม่โดยไม่กระทบ command เดิม
# ===========================================================================
"""Typer CLI entrypoint for ContextOS Core."""

import typer

# นำเข้าฟังก์ชันหลักของแต่ละ command จาก submodule
# แต่ละฟังก์ชันรับ arguments/options ผ่าน Typer decorators
from contextos.cli.commands.ask_cmd import ask_context
from contextos.cli.commands.benchmark_cmd import benchmark_context
from contextos.cli.commands.import_cmd import import_context
from contextos.cli.commands.optimize_cmd import optimize_context
from contextos.cli.commands.search_cmd import search_context
from contextos.cli.commands.stats_cmd import stats_context
from contextos.cli.commands.system_cmd import (
    config_context,
    debug_context,
    doctor_context,
    version_context,
)


# สร้าง Typer application หลัก
# no_args_is_help=True: ถ้าผู้ใช้พิมพ์ `context` โดยไม่มี subcommand จะแสดง help อัตโนมัติ
app = typer.Typer(
    name="context",
    help=(
        "[bold cyan]ContextOS Core[/bold cyan]: local-first AI context management "
        "with SQLite, BM25 retrieval, and rule-based compression."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)

# ลงทะเบียน command ทั้ง 5 เข้ากับ Typer app
# ใช้ pattern app.command()(function) แทน decorator @app.command()
# เพราะฟังก์ชันถูก define ไว้ใน module อื่น
app.command(name="import", help="Import local files into the ContextOS workspace.")(
    import_context
)
app.command(
    name="optimize",
    help="Optimize stored compression metadata for a document.",
)(optimize_context)
app.command(name="ask", help="Ask a question using selected local context.")(ask_context)
app.command(name="search", help="Search imported local context.")(search_context)
app.command(name="stats", help="Show local ContextOS workspace statistics.")(stats_context)
app.command(name="benchmark", help="Run a local benchmark and write a Markdown report.")(
    benchmark_context
)
app.command(name="doctor", help="Check local ContextOS environment health.")(doctor_context)
app.command(name="version", help="Show the installed ContextOS Core version.")(version_context)
app.command(name="config", help="Inspect or initialize local configuration.")(config_context)
app.command(name="debug", help="Show local debug information.")(debug_context)


# สำหรับรันโดยตรงผ่าน `python -m contextos.cli.main`
if __name__ == "__main__":
    app()
