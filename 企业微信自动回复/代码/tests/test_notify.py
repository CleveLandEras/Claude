"""转二讲提醒的内容：5 类各 1 条，检查思考页 7.1 ④ 列的几项都在。只生成内容，不弹窗。"""
from datetime import datetime

import pytest

from autoreply import toast
from autoreply.classify import AUTO, SOURCE_MODEL, SOURCE_NO_MODEL, Decision, classify
from autoreply.guards import REASON_RATE_PARENT, REASON_TEACHER
from autoreply.model import ModelResult
from autoreply.notify import build_pause_alert, build_reminder, describe_basis
from autoreply.rules import HANDOFF

RECEIVED = datetime(2026, 11, 4, 10, 15, 30)
PARENT = "测试家长甲"

FIVE_CATEGORIES = [
    ("学科答疑", "这道题第三问怎么做", "二次函数那道题看草稿"),
    ("续报", "下学期续费有优惠吗", None),
    ("退费", "我要退费，请尽快处理", None),
    ("投诉", "我要投诉你们，太过分了", None),
    ("带情绪", "你们太不负责任了！！！", None),
]


@pytest.mark.parametrize("category,text,draft", FIVE_CATEGORIES)
def test_each_handoff_category_has_all_items(category, text, draft):
    decision = classify(text, None, None)
    assert decision.decision == HANDOFF
    assert decision.category == category

    alert = build_reminder(PARENT, text, decision, RECEIVED, draft=draft)

    assert category in alert.title
    assert f"家长：{PARENT}" in alert.body
    assert f"原话：{text}" in alert.body
    assert f"类别：{category}" in alert.body
    assert "收到时间：2026-11-04 10:15:30" in alert.body
    basis_line = next(line for line in alert.body.splitlines() if line.startswith("依据："))
    assert decision.hits and decision.hits[0].word in basis_line
    if draft:
        assert f"建议答案草稿（未发送）：{draft}" in alert.body
    else:
        assert "未发送" not in alert.body


def test_full_text_is_kept_for_long_and_merged_messages():
    text = "老师\n" + "我想问一下孩子最近的情况。" * 100 + "\n结尾这句要退费"
    decision = classify(text, None, None)
    alert = build_reminder(PARENT, text, decision, RECEIVED)
    assert text in alert.body


def test_other_items_come_before_original_text():
    decision = classify("我要退费", None, None)
    alert = build_reminder(PARENT, "我要退费", decision, RECEIVED, draft="草稿")
    labels = [line.split("：")[0] for line in alert.body.splitlines()]
    assert labels == ["家长", "收到时间", "类别", "依据", "原话", "建议答案草稿（未发送）"]


def test_basis_when_model_gives_scores():
    scores = {"退费": 0.72, "上课时间": 0.1}
    decision = Decision(HANDOFF, "退费", SOURCE_MODEL, 0.72, scores)
    assert "退费" in describe_basis(decision)
    assert "0.72" in describe_basis(decision)


def test_basis_when_model_failed():
    decision = Decision(HANDOFF, "都不是／拿不准", SOURCE_MODEL, error="timeout")
    assert "timeout" in describe_basis(decision)


def test_basis_when_no_model():
    decision = Decision(HANDOFF, "都不是／拿不准", SOURCE_NO_MODEL)
    assert "没有模型" in describe_basis(decision)


def test_basis_when_auto_was_blocked_by_guard():
    decision = Decision(AUTO, "上课时间", SOURCE_MODEL, 0.97, {"上课时间": 0.97})
    alert = build_reminder(
        PARENT, "下节课几点", decision, RECEIVED, draft="周六 9 点", guard_reason=REASON_TEACHER
    )
    assert "上课时间" in alert.title
    assert REASON_TEACHER in alert.body
    assert "建议答案草稿（未发送）：周六 9 点" in alert.body


def test_guard_reason_ignored_for_real_handoff():
    decision = classify("我要退费", None, None)
    assert REASON_TEACHER not in describe_basis(decision, REASON_TEACHER)


def test_pause_alert_says_why_and_how_to_resume():
    alert = build_pause_alert(REASON_RATE_PARENT, PARENT)
    assert "暂停" in alert.title
    assert REASON_RATE_PARENT in alert.body
    assert PARENT in alert.body
    assert "手动恢复" in alert.body


def test_pause_alert_without_parent():
    alert = build_pause_alert(REASON_RATE_PARENT)
    assert "家长：" not in alert.body


class RecordingPopup:
    def __init__(self):
        self.shown = []

    def show(self, title, body):
        self.shown.append((title, body))


def test_reminder_fits_existing_popup_backend_without_logging_text(tmp_path):
    text = "我要退费，电话 13000000009"
    alert = build_reminder(PARENT, text, classify(text, None, None), RECEIVED)
    popup = RecordingPopup()

    assert toast.show(alert.title, alert.body, backend=popup, directory=tmp_path) is True
    assert popup.shown == [(alert.title, alert.body)]
    log_text = (tmp_path / "autoreply.log").read_text(encoding="utf-8")
    assert "13000000009" not in log_text
    assert PARENT not in log_text
