"""自检：确认打包后的程序能跑、日志能写，结果打印出来并写进日志。

屏幕输出第一行：打包 通过／日志 通过
日志记录两行：selfcheck package ok、selfcheck log ok（没过时 ok 换成 fail: 原因）。
Mac 上用 autoreply.checklog 核对这两行。
"""
from __future__ import annotations

import platform
import secrets
import sys
from pathlib import Path
from typing import Optional, Tuple

from autoreply import applog

Outcome = Tuple[bool, str]


def check_package(
    frozen: Optional[bool] = None, executable: Optional[str] = None
) -> Outcome:
    """是不是打包后的程序、窗口版程序在不在、界面组件能不能用。"""
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    if not is_frozen:
        return False, "现在跑的是源码，不是打包后的程序"
    exe = Path(sys.executable if executable is None else executable)
    window_exe = exe.with_name("autoreply_window" + exe.suffix)
    if not window_exe.exists():
        return False, f"缺少 {window_exe.name}"
    try:
        import tkinter

        tkinter.Tcl().eval("info patchlevel")
    except Exception as exc:  # 打包漏了界面组件时，错误类型不固定
        return False, f"界面组件不可用：{exc}"
    return True, ""


def check_log(directory: Optional[applog.PathLike] = None) -> Outcome:
    """写一行带随机串的记录再读回来。"""
    token = secrets.token_hex(8)
    try:
        applog.write(f"selfcheck probe {token}", directory)
        text = applog.log_path(directory).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return False, f"日志写不进去：{exc}"
    if token not in text:
        return False, "日志写了但读不回来"
    return True, ""


def _record(item: str, outcome: Outcome, directory: Optional[applog.PathLike]) -> None:
    ok, reason = outcome
    line = f"selfcheck {item} ok" if ok else f"selfcheck {item} fail: {reason}"
    try:
        applog.write(line, directory)
    except OSError:
        pass  # 日志写不进去已经由 check_log 报告


def _label(name: str, outcome: Outcome) -> str:
    ok, reason = outcome
    return f"{name} 通过" if ok else f"{name} 不通过（{reason}）"


def run(
    directory: Optional[applog.PathLike] = None,
    frozen: Optional[bool] = None,
    executable: Optional[str] = None,
) -> int:
    log_outcome = check_log(directory)
    package_outcome = check_package(frozen, executable)
    try:
        applog.write(
            f"selfcheck env python={platform.python_version()} os={platform.platform()}",
            directory,
        )
    except OSError:
        pass
    _record("package", package_outcome, directory)
    _record("log", log_outcome, directory)
    print(f"{_label('打包', package_outcome)}／{_label('日志', log_outcome)}")
    print(f"日志位置：{applog.log_path(directory)}")
    return 0 if package_outcome[0] and log_outcome[0] else 1
