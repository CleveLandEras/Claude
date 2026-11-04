"""记录和「今日自动回复」核对页（思考页 7.1 ⑤）。

每条家长消息一行，存到 记录/<日期>.jsonl；核对页是同一目录下的本地 HTML，只列当天自动发出的。
写盘前去标识化：原话、回复、出处都过 redact；日志只写事件和数字，也过一遍 redact。

暂按（可推翻）：
- 家长列存代号，不存备注名。思考页 7.1 ⑤ 这一列写的是备注名，但派活要求写盘前去标识化，
  备注名本身就是姓名或姓名加称呼。代价：二讲看核对页认不出是哪位家长，要撤回时得按时间和回复内容去找。
- 核对结果用 mark_check 写回。核对页是静态文件，点不了「对／错」；入口要等工具窗口定下来再接。
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

from . import applog
from .classify import Decision
from .guards import QUEUE, REMIND, SEND, recall_notice
from .redact import redact

ENV_OVERRIDE = "AUTOREPLY_RECORDS_DIR"
RECORDS_DIR_NAME = "记录"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

CHECK_RIGHT = "对"
CHECK_WRONG = "错"
_UNCHECKED_TEXT = "未核对"

_ACTIONS = (SEND, REMIND, QUEUE)
AUTO_ROW_CLASS = "auto-row"


class RecordError(Exception):
    """记录的内容不合规定，或者要改的那条找不到。"""


@dataclass(frozen=True)
class DayRecords:
    """一天的记录。bad_lines：读不了的行数（比如写到一半断电），核对页上会写明。"""

    rows: List[Mapping]
    bad_lines: int = 0


def records_dir(env: Optional[Mapping[str, str]] = None) -> Path:
    env = os.environ if env is None else env
    override = env.get(ENV_OVERRIDE)
    if override:
        return Path(override)
    return applog.app_root(env) / RECORDS_DIR_NAME


def _resolve(directory: Optional[applog.PathLike]) -> Path:
    return Path(directory) if directory is not None else records_dir()


def day_file(day: date, directory: Optional[applog.PathLike] = None) -> Path:
    return _resolve(directory) / f"{day.isoformat()}.jsonl"


def page_file(day: date, directory: Optional[applog.PathLike] = None) -> Path:
    return _resolve(directory) / f"今日自动回复_{day.isoformat()}.html"


def parent_code(parent: str) -> str:
    """同一位家长代号不变，同一天的记录能看出是不是一个人。"""
    return "家长-" + hashlib.sha256(parent.encode("utf-8")).hexdigest()[:6]


def _log(message: str, log_directory: Optional[applog.PathLike]) -> None:
    applog.write(redact(message), log_directory)


def add_record(
    action: str,
    parent: str,
    text: str,
    decision: Decision,
    at: datetime,
    reply: Optional[str] = None,
    source: Optional[str] = None,
    known_names: Iterable[str] = (),
    directory: Optional[applog.PathLike] = None,
    log_directory: Optional[applog.PathLike] = None,
) -> str:
    """记一条，返回记录编号。action 是 SEND、REMIND 或 QUEUE。

    自动发的必须有回复内容和出处（完成标准 9）。known_names 传孩子名等，和备注名一起换掉。
    """
    if action not in _ACTIONS:
        raise RecordError(f"处理方式只能是 {_ACTIONS} 之一：{action}")
    if action == SEND and not (reply and source):
        raise RecordError("自动发的记录必须有回复内容和素材出处")

    names = [parent, *known_names]
    record_id = uuid.uuid4().hex[:12]
    row = {
        "id": record_id,
        "time": at.strftime(TIME_FORMAT),
        "parent": parent_code(parent),
        "text": redact(text, names),
        "category": decision.category,
        "confidence": decision.confidence,
        "action": action,
        "reply": redact(reply, names) if reply else None,
        "source": redact(source, names) if source else None,
        "check": None,
    }
    path = day_file(at.date(), directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    _log(f"record added: {action}", log_directory)
    return record_id


def read_day(day: date, directory: Optional[applog.PathLike] = None) -> DayRecords:
    path = day_file(day, directory)
    if not path.is_file():
        return DayRecords([])
    rows: List[Mapping] = []
    bad_lines = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                bad_lines += 1
    return DayRecords(rows, bad_lines)


def mark_check(
    record_id: str, result: str, day: date, directory: Optional[applog.PathLike] = None
) -> None:
    """写回二讲的核对结果（对／错）。读不了的行原样留着。"""
    if result not in (CHECK_RIGHT, CHECK_WRONG):
        raise RecordError(f"核对结果只能是 {CHECK_RIGHT} 或 {CHECK_WRONG}：{result}")
    path = day_file(day, directory)
    if not path.is_file():
        raise RecordError(f"{day} 没有记录")
    lines = path.read_text(encoding="utf-8").splitlines()
    found = False
    for index, line in enumerate(lines):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("id") == record_id:
            row["check"] = result
            lines[index] = json.dumps(row, ensure_ascii=False)
            found = True
            break
    if not found:
        raise RecordError(f"{day} 的记录里没有这条：{record_id}")
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    os.replace(temp, path)


# ---- 核对页 ----

_STYLE = """
body { margin: 0; padding: 16px; background: #fff; color: #1f2328;
  font: 14px/1.6 "Microsoft YaHei", "PingFang SC", sans-serif; }
h1 { font-size: 20px; margin: 0 0 8px; }
.note { color: #57606a; margin: 0 0 8px; }
.warn { color: #b42318; font-weight: 600; margin: 0 0 8px; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; min-width: 960px; width: 100%; }
th, td { border: 1px solid #d0d7de; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #f6f8fa; white-space: nowrap; }
td { white-space: pre-wrap; word-break: break-word; }
td:nth-child(1), td:nth-child(2), td:nth-child(4), td:nth-child(5), td:nth-child(9) { white-space: nowrap; }
"""

_COLUMNS = ("时间", "家长", "原话", "类别", "把握度", "回复内容", "素材出处", "撤回提醒", "核对结果")


def _cell(value) -> str:
    return "<td>" + html.escape("" if value is None else str(value)) + "</td>"


def _render_row(row: Mapping, now: datetime, recall_window_seconds: Optional[int]) -> str:
    sent_at = datetime.strptime(row["time"], TIME_FORMAT)
    confidence = row.get("confidence")
    cells = [
        row["time"][11:],
        row.get("parent"),
        row.get("text"),
        row.get("category"),
        "-" if confidence is None else f"{confidence:.2f}",
        row.get("reply"),
        row.get("source"),
        recall_notice(sent_at, now, recall_window_seconds).text,
        row.get("check") or _UNCHECKED_TEXT,
    ]
    row_id = html.escape(str(row.get("id", "")), quote=True)
    body = "".join(_cell(value) for value in cells)
    return f'<tr class="{AUTO_ROW_CLASS}" data-id="{row_id}">{body}</tr>'


def render_check_page(
    records: DayRecords,
    day: date,
    now: datetime,
    recall_window_seconds: Optional[int] = None,
) -> str:
    def rows_of(action: str) -> List[Mapping]:
        return [row for row in records.rows if row.get("action") == action]

    auto_rows = rows_of(SEND)
    summary = (
        f'自动发 <b id="auto-count">{len(auto_rows)}</b> 条，'
        f"转二讲 {len(rows_of(REMIND))} 条，排队 {len(rows_of(QUEUE))} 条。"
        f"生成于 {now.strftime(TIME_FORMAT)}。"
    )
    warn = (
        f'<p class="warn">有 {records.bad_lines} 行记录读不了，没算进上面的条数，请把记录文件传回排查。</p>'
        if records.bad_lines
        else ""
    )
    if auto_rows:
        header = "".join(f"<th>{name}</th>" for name in _COLUMNS)
        body = "\n".join(_render_row(row, now, recall_window_seconds) for row in auto_rows)
        content = f'<div class="scroll"><table><thead><tr>{header}</tr></thead><tbody>\n{body}\n</tbody></table></div>'
    else:
        content = '<p class="note">今天还没有自动回复。</p>'
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>今日自动回复 {day.isoformat()}</title>
<style>{_STYLE}</style></head><body>
<h1>今日自动回复 {day.isoformat()}</h1>
<p class="note">{summary}</p>
<p class="note">手机号、姓名、班级号已换成占位符，家长列是代号。请逐条看回复对不对，发错的按撤回提醒处理。</p>
{warn}{content}
</body></html>
"""


def write_check_page(
    day: Optional[date] = None,
    now: Optional[datetime] = None,
    recall_window_seconds: Optional[int] = None,
    directory: Optional[applog.PathLike] = None,
    log_directory: Optional[applog.PathLike] = None,
) -> Path:
    now = now or datetime.now()
    day = day or now.date()
    records = read_day(day, directory)
    path = page_file(day, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    page = render_check_page(records, day, now, recall_window_seconds)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    count = sum(1 for row in records.rows if row.get("action") == SEND)
    _log(f"check page written: {count} auto", log_directory)
    return path
