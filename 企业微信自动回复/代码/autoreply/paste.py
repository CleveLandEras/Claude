"""手动粘贴的逻辑：计字、写日志。界面在 window.py，这里不碰 tkinter。

字数口径：空格、换行、制表符不算，其余每个字符（汉字、字母、数字、标点）算 1 个。
这样 Windows 的换行符差异不影响字数。日志只记字数，不记粘贴的原文。
"""
from __future__ import annotations

from typing import Optional

from autoreply import applog


def count_chars(text: str) -> int:
    return sum(1 for char in text if not char.isspace())


def receive(text: str, directory: Optional[applog.PathLike] = None) -> str:
    """记下这次粘贴，返回窗口上要显示的那句话。"""
    count = count_chars(text)
    try:
        applog.write(f"paste received {count} chars", directory)
    except OSError as exc:
        return f"已收到 {count} 字（日志没写上：{exc}）"
    return f"已收到 {count} 字"
