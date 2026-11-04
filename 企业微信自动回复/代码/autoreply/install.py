"""安装：把打包好的文件夹复制到 %LOCALAPPDATA%\\自动回复\\程序，并在桌面放快捷方式。

不要管理员权限，不写注册表。重复安装直接覆盖；日志在另一个目录，不受影响。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Optional

from autoreply import applog, winutil

PROGRAM_DIR_NAME = "程序"
SHORTCUTS = (
    ("自动回复测试窗口.lnk", "autoreply_window.exe"),
    ("自动回复自检.lnk", "自检.bat"),
    ("自动回复收集日志.lnk", "收集日志.bat"),
)


def copy_program(source: Path, target: Path) -> None:
    """source 和 target 是同一处（在安装好的目录里又点了一次）时什么也不做。"""
    if source.resolve() == target.resolve():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)


def shortcut_script(link: Path, target: Path) -> str:
    return "; ".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut({winutil.ps_quote(str(link))})",
            f"$s.TargetPath = {winutil.ps_quote(str(target))}",
            f"$s.WorkingDirectory = {winutil.ps_quote(str(target.parent))}",
            "$s.Save()",
        ]
    )


def create_shortcuts(
    program_dir: Path,
    desktop: Path,
    runner: Callable = winutil.run_powershell,
) -> List[str]:
    """返回没建成的快捷方式名字。快捷方式只为方便，建不成不算安装失败。"""
    failed = []
    for link_name, target_name in SHORTCUTS:
        script = shortcut_script(desktop / link_name, program_dir / target_name)
        try:
            ok = runner(script).returncode == 0
        except (OSError, subprocess.SubprocessError):
            ok = False
        if not ok:
            failed.append(link_name)
    return failed


def run(
    source: Optional[Path] = None,
    target: Optional[Path] = None,
    desktop: Optional[Path] = None,
    runner: Callable = winutil.run_powershell,
) -> int:
    if source is None and not getattr(sys, "frozen", False):
        print("安装只能在打包后的程序里运行。")
        return 1
    source_dir = Path(sys.executable).parent if source is None else source
    target_dir = applog.app_root() / PROGRAM_DIR_NAME if target is None else target
    try:
        copy_program(source_dir, target_dir)
    except OSError as exc:
        print(f"安装没成功：{exc}")
        print("如果测试窗口开着，先关掉它再试一次。")
        return 1
    print(f"安装完成，程序在：{target_dir}")
    desktop_dir = winutil.desktop_dir() if desktop is None else desktop
    failed = create_shortcuts(target_dir, desktop_dir, runner)
    if failed:
        print("这些桌面快捷方式没建成：" + "、".join(failed))
        print("可以直接到上面的程序文件夹里双击同名文件。")
    else:
        print(f"桌面上多了 {len(SHORTCUTS)} 个图标：测试窗口、自检、收集日志。")
    return 0
