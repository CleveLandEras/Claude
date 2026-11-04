"""转二讲提醒的内容（思考页 7.1 ④）。只生成文字，不弹窗：弹窗交 toast.show(title, body)。

提醒里带：家长备注名、收到时间、类别、依据、原话全文、建议答案草稿（有就带，标「未发送」）。
原话放在草稿前、其他几项之后：弹窗放不下时被截掉的是末尾，前面几项还在；全文靠待处理列表看。
这里的内容只显示给二讲，不写盘，所以不去标识化；写盘的是 records.py。
没做：未处理 15 分钟再提醒（这次范围只到内容生成）。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .classify import AUTO, SOURCE_MODEL, SOURCE_NO_MODEL, SOURCE_RULES, Decision

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class Alert:
    title: str
    body: str


def _dedupe(words) -> List[str]:
    return list(dict.fromkeys(words))


def _model_basis(decision: Decision) -> str:
    if decision.error:
        return f"模型这一步出错（{decision.error}），按拿不准转二讲"
    if not decision.scores:
        return "模型没有给出把握度，按拿不准转二讲"
    top = max(decision.scores, key=decision.scores.get)
    return f"模型把握度最高的是「{top}」（{decision.scores[top]:.2f}）"


def describe_basis(decision: Decision, guard_reason: Optional[str] = None) -> str:
    """依据：命中的词或模型判的结果。判成能自动回、但被防出错规则拦下时，也写明被什么拦下。"""
    if decision.source == SOURCE_RULES:
        words = _dedupe(hit.word for hit in decision.hits)
        basis = "命中词 " + "、".join(f"「{word}」" for word in words) if words else "规则层拦下"
    elif decision.source == SOURCE_MODEL:
        basis = _model_basis(decision)
    elif decision.source == SOURCE_NO_MODEL:
        basis = "没有模型，规则层没拦下的一律转二讲"
    else:
        basis = decision.source
    if decision.decision == AUTO and guard_reason:
        return f"{basis}；本可自动回，因为「{guard_reason}」没有发"
    return basis


def build_reminder(
    parent: str,
    text: str,
    decision: Decision,
    received_at: datetime,
    draft: Optional[str] = None,
    guard_reason: Optional[str] = None,
) -> Alert:
    lines = [
        f"家长：{parent}",
        f"收到时间：{received_at.strftime(TIME_FORMAT)}",
        f"类别：{decision.category}",
        f"依据：{describe_basis(decision, guard_reason)}",
        f"原话：{text}",
    ]
    if draft:
        lines.append(f"建议答案草稿（未发送）：{draft}")
    return Alert(title=f"需要您处理：{decision.category}", body="\n".join(lines))


def build_pause_alert(reason: str, parent: Optional[str] = None) -> Alert:
    """超限自动暂停时提醒二讲（第 6 节第 9 条）。"""
    lines = [f"原因：{reason}"]
    if parent:
        lines.append(f"家长：{parent}")
    lines.append("暂停期间只提醒、不自动发。确认没问题后请手动恢复。")
    return Alert(title="自动回复已暂停", body="\n".join(lines))
