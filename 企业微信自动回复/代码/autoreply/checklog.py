"""核对 Windows 上收集回来的日志 zip。

在 代码/ 目录下运行（只用标准库，不需要虚拟环境）：
    python3 -m autoreply.checklog 日志回传/<zip>

第一行输出「自检记录 X/2」，X 是打包、日志两项里最近一次结果为通过的项数。
相对路径在当前目录找不到时，再到项目根目录（代码/ 的上一级）找。
退出码：0 两项都过；1 zip 能读但没到 2/2；2 文件读不了或参数不对。
只读 zip 里的 .log，不解压到磁盘。
"""
from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Sequence

ITEM_NAMES = {"package": "打包", "log": "日志"}
MAX_LOG_BYTES = 50 * 1024 * 1024
PROJECT_ROOT = Path(__file__).resolve().parents[2]

SELFCHECK_LINE = re.compile(r"^\S+ \S+ selfcheck (package|log) (ok|fail)(?:: (.*))?$")
TOAST_LINE = re.compile(r"^\S+ \S+ toast shown$")
PASTE_LINE = re.compile(r"^\S+ \S+ paste received (\d+) chars$")


class LogZipError(Exception):
    """zip 读不了，或里面没有日志。"""


@dataclass
class Summary:
    latest: Dict[str, str] = field(default_factory=dict)
    reasons: Dict[str, str] = field(default_factory=dict)
    toast_lines: int = 0
    paste_counts: List[int] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for item in ITEM_NAMES if self.latest.get(item) == "ok")


def resolve_zip_path(argument: str, project_root: Path = PROJECT_ROOT) -> Path:
    path = Path(argument)
    if path.exists() or path.is_absolute():
        return path
    candidate = project_root / path
    return candidate if candidate.exists() else path


def read_log_text(zip_path: Path) -> str:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members = [
                info
                for info in archive.infolist()
                if info.filename.endswith(".log")
                and not PurePosixPath(info.filename).name.startswith(".")
            ]
            if not members:
                raise LogZipError(f"{zip_path} 里没有 .log 文件")
            parts = []
            for info in sorted(members, key=lambda item: item.filename):
                if info.file_size > MAX_LOG_BYTES:
                    raise LogZipError(f"{info.filename} 超过 50MB，不读")
                parts.append(archive.read(info).decode("utf-8", "replace"))
    except (OSError, zipfile.BadZipFile) as exc:
        raise LogZipError(f"读不了 {zip_path}：{exc}") from exc
    return "\n".join(parts)


def summarize(text: str) -> Summary:
    summary = Summary()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = SELFCHECK_LINE.match(line)
        if match:
            item, result, reason = match.groups()
            summary.latest[item] = result
            summary.reasons[item] = reason or ""
            continue
        if TOAST_LINE.match(line):
            summary.toast_lines += 1
            continue
        match = PASTE_LINE.match(line)
        if match:
            summary.paste_counts.append(int(match.group(1)))
    return summary


def format_summary(summary: Summary) -> List[str]:
    lines = [f"自检记录 {summary.passed}/{len(ITEM_NAMES)}"]
    for item, name in ITEM_NAMES.items():
        result = summary.latest.get(item)
        if result == "ok":
            lines.append(f"{name}：通过")
        elif result == "fail":
            lines.append(f"{name}：不通过（{summary.reasons.get(item, '')}）")
        else:
            lines.append(f"{name}：没有记录")
    lines.append(f"弹窗记录 toast shown：{summary.toast_lines} 行")
    if summary.paste_counts:
        counts = "、".join(str(count) for count in summary.paste_counts)
        lines.append(f"粘贴记录：{len(summary.paste_counts)} 次，字数依次 {counts}")
    else:
        lines.append("粘贴记录：0 次")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("用法：python3 -m autoreply.checklog 日志回传/<zip>")
        return 2
    try:
        text = read_log_text(resolve_zip_path(args[0]))
    except LogZipError as exc:
        print(str(exc))
        return 2
    summary = summarize(text)
    for line in format_summary(summary):
        print(line)
    return 0 if summary.passed == len(ITEM_NAMES) else 1


if __name__ == "__main__":
    sys.exit(main())
