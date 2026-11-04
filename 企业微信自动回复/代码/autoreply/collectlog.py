"""把日志打成一个 zip 放到桌面，文件名带时间，方便传回 Mac。

现阶段日志里只有事件和数字，没有消息原文；zip 里去姓名电话放在后面的日志收集步骤做。
"""
from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from autoreply import applog, winutil


class CollectError(Exception):
    """没有日志可收，或 zip 写不出来。"""


def collect(
    log_directory: Optional[applog.PathLike] = None,
    out_dir: Optional[applog.PathLike] = None,
    now: Optional[datetime] = None,
) -> Path:
    source = Path(log_directory) if log_directory is not None else applog.log_dir()
    files = sorted(source.glob("*.log"))
    if not files:
        raise CollectError(f"{source} 里还没有日志，请先运行一次自检")
    target_dir = Path(out_dir) if out_dir is not None else winutil.desktop_dir()
    stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    target = target_dir / f"自动回复日志_{stamp}.zip"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in files:
                archive.write(file, file.name)
    except OSError as exc:
        raise CollectError(f"zip 写不出来：{exc}") from exc
    return target


def run(
    log_directory: Optional[applog.PathLike] = None,
    out_dir: Optional[applog.PathLike] = None,
) -> int:
    try:
        target = collect(log_directory, out_dir)
    except CollectError as exc:
        print(f"没有生成：{exc}")
        return 1
    print(f"已生成：{target}")
    return 0
