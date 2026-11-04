"""弹窗提醒：Windows 上弹系统通知，并写一行日志 toast shown。

后端可替换：show() 只认一个带 show(title, body) 方法的对象，出错时抛 ToastError。
Windows 用系统自带的 PowerShell 调通知区图标，不需要装任何东西；
其他系统没有弹窗，默认后端直接报错，日志记 toast failed，不会假装弹过。
"""
from __future__ import annotations

import subprocess
import sys
from typing import Callable, Optional

from autoreply import applog, winutil

TEST_TITLE = "测试提醒"
TEST_BODY = "看到这条，说明这台电脑能弹提醒。"
BALLOON_MILLISECONDS = 10000
KEEP_ALIVE_SECONDS = 6


class ToastError(Exception):
    """弹窗没有弹出来。"""


def balloon_script(title: str, body: str) -> str:
    """组一段单行 PowerShell：通知区放个图标，弹提醒，停几秒再收掉。"""
    if not title or not body:
        raise ToastError("提醒的标题和内容都不能为空")
    return "; ".join(
        [
            "$ErrorActionPreference = 'Stop'",
            "Add-Type -AssemblyName System.Windows.Forms",
            "Add-Type -AssemblyName System.Drawing",
            "$n = New-Object System.Windows.Forms.NotifyIcon",
            "$n.Icon = [System.Drawing.SystemIcons]::Information",
            "$n.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info",
            f"$n.BalloonTipTitle = {winutil.ps_quote(title)}",
            f"$n.BalloonTipText = {winutil.ps_quote(body)}",
            "$n.Visible = $true",
            f"$n.ShowBalloonTip({BALLOON_MILLISECONDS})",
            f"Start-Sleep -Seconds {KEEP_ALIVE_SECONDS}",
            "$n.Dispose()",
        ]
    )


class PowerShellBalloon:
    """Windows 后端。runner 可替换，单测里不真的跑 PowerShell。"""

    def __init__(
        self, runner: Callable[[str], subprocess.CompletedProcess] = winutil.run_powershell
    ) -> None:
        self.runner = runner

    def show(self, title: str, body: str) -> None:
        result = self.runner(balloon_script(title, body))
        if result.returncode != 0:
            detail = winutil.decode_output(result.stderr or b"")
            raise ToastError(f"PowerShell 退出码 {result.returncode}：{detail}")


class NoPopup:
    """非 Windows 后端：没有系统弹窗可用。"""

    def show(self, title: str, body: str) -> None:
        raise ToastError("这台电脑不是 Windows，不弹窗")


def default_backend(platform: Optional[str] = None):
    current = sys.platform if platform is None else platform
    return PowerShellBalloon() if current == "win32" else NoPopup()


def show(
    title: str = TEST_TITLE,
    body: str = TEST_BODY,
    backend=None,
    directory: Optional[applog.PathLike] = None,
) -> bool:
    """弹提醒并写日志，返回是否弹出。"""
    chosen = default_backend() if backend is None else backend
    try:
        chosen.show(title, body)
    except (ToastError, OSError, subprocess.SubprocessError) as exc:
        one_line = " ".join(str(exc).split())
        applog.write(f"toast failed: {one_line}", directory)
        return False
    applog.write("toast shown", directory)
    return True
