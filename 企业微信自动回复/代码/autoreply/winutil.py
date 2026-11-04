"""和 Windows 打交道的两件小事：找桌面、调 PowerShell。只用标准库。"""
from __future__ import annotations

import locale
import os
import subprocess
import sys
from pathlib import Path

POWERSHELL_TIMEOUT_SECONDS = 30
CSIDL_DESKTOPDIRECTORY = 0x10


def desktop_dir() -> Path:
    """当前用户的桌面。桌面可能被 OneDrive 或公司策略挪走，所以先问系统。"""
    if sys.platform == "win32":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(
                None, CSIDL_DESKTOPDIRECTORY, None, 0, buffer
            )
            if result == 0 and buffer.value:
                return Path(buffer.value)
        except (OSError, AttributeError):
            pass
    return Path.home() / "Desktop"


def powershell_path() -> str:
    root = os.environ.get("SystemRoot", r"C:\Windows")
    return "\\".join([root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe"])


def ps_quote(text: str) -> str:
    """把文字写成 PowerShell 单引号字符串，里面的单引号要双写。"""
    return "'" + text.replace("'", "''") + "'"


def powershell_command(script: str) -> list:
    return [powershell_path(), "-NoProfile", "-NonInteractive", "-Command", script]


def run_powershell(script: str) -> subprocess.CompletedProcess:
    """跑一段 PowerShell，不弹黑窗。

    命令行走系统的宽字符接口，中文不经过代码页，所以脚本里可以直接写中文。
    窗口版程序没有标准输入输出，三个句柄都要明确给，否则子进程起不来。
    """
    return subprocess.run(
        powershell_command(script),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=POWERSHELL_TIMEOUT_SECONDS,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def decode_output(raw: bytes) -> str:
    return raw.decode(locale.getpreferredencoding(False), "replace").strip()
