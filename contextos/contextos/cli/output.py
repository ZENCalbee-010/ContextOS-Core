# ===========================================================================
# ไฟล์: cli/output.py
# หน้าที่: ช่วยให้การแสดงผลข้อความบน terminal ปลอดภัยจากปัญหา Unicode
# ความรับผิดชอบ: ห่อ (wrap) ฟังก์ชัน typer.echo() เพื่อจัดการกรณีที่
#   terminal ของผู้ใช้ไม่รองรับ encoding บางตัว (เช่น Windows console
#   ที่ใช้ cp1252 แต่ข้อความมีอักขระ UTF-8 พิเศษ)
# ความสัมพันธ์กับระบบ: ถูกใช้โดย command modules ทั้งหมดที่ต้องแสดง
#   ข้อความที่อาจมีอักขระนอกเหนือ ASCII เช่น ชื่อไฟล์ภาษาไทย
# เหตุผลที่ต้องมี: typer.echo() จะ crash ถ้า terminal ไม่รองรับอักขระบางตัว
#   safe_echo() จะแทนที่อักขระที่แสดงไม่ได้ด้วย '?' แทนการ crash
# ===========================================================================
"""Terminal output helpers."""

# locale ใช้ตรวจสอบ encoding ที่ terminal ของผู้ใช้ต้องการ
import locale
from typing import Any, TextIO

import typer


def safe_echo(message: Any = "", *, file: TextIO | None = None) -> None:
    """Echo text, replacing only characters unsupported by the terminal encoding."""

    try:
        # ลองแสดงผลตามปกติก่อน
        typer.echo(message, file=file)
    except UnicodeEncodeError:
        # หาก terminal ไม่รองรับอักขระบางตัว จะเข้า exception นี้
        # ลำดับการหา encoding: ของไฟล์ -> ของ locale ระบบ -> fallback เป็น utf-8
        encoding = (
            getattr(file, "encoding", None)
            or locale.getpreferredencoding(False)
            or "utf-8"
        )
        # encode แล้ว decode กลับ โดยใช้ errors='replace'
        # อักขระที่แสดงไม่ได้จะถูกแทนที่ด้วย '?' แทนที่จะ raise error
        text = str(message).encode(encoding, errors="replace").decode(encoding)
        typer.echo(text, file=file)
