"""日志：写到固定位置，一行一条，格式是「日期 时间 内容」。

Windows 上写到 %LOCALAPPDATA%\\自动回复\\日志\\autoreply.log（不要管理员权限）。
设了环境变量 AUTOREPLY_LOG_DIR 时写到它指的目录，单测和 Mac 上试跑用。
日志只记事件和数字，不记家长或测试消息的原文。
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Mapping, Optional, Union

LOG_FILE_NAME = "autoreply.log"
ENV_OVERRIDE = "AUTOREPLY_LOG_DIR"
APP_DIR_NAME = "自动回复"
LOG_DIR_NAME = "日志"

PathLike = Union[str, Path]


def app_root(
    env: Optional[Mapping[str, str]] = None, platform: Optional[str] = None
) -> Path:
    """工具在这台电脑上的根目录：日志和安装后的程序都在它下面。"""
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    if platform == "win32":
        base = env.get("LOCALAPPDATA")
        base_path = Path(base) if base else Path.home() / "AppData" / "Local"
        return base_path / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME}"


def log_dir(
    env: Optional[Mapping[str, str]] = None, platform: Optional[str] = None
) -> Path:
    env = os.environ if env is None else env
    override = env.get(ENV_OVERRIDE)
    if override:
        return Path(override)
    return app_root(env, platform) / LOG_DIR_NAME


def log_path(directory: Optional[PathLike] = None) -> Path:
    target = Path(directory) if directory is not None else log_dir()
    return target / LOG_FILE_NAME


def write(
    message: str,
    directory: Optional[PathLike] = None,
    now: Optional[datetime] = None,
) -> None:
    """追加一行日志；目录不存在就建。写不进去时抛 OSError，由调用方决定怎么提示。"""
    path = log_path(directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    one_line = " ".join(str(message).splitlines())
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{stamp} {one_line}\n")
