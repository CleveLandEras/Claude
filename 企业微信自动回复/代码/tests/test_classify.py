"""串联层：判断顺序（思考页 7.1 ②）和阈值门。"""
import json

import pytest

from autoreply.classify import AUTO, SOURCE_MODEL, SOURCE_NO_MODEL, SOURCE_RULES, classify, decide
from autoreply.dataset_stats import ALL_LABELS, UNSURE_LABEL
from autoreply.model import FakeBackend, ModelResult, parse_scores
from autoreply.rules import HANDOFF


def scores_json(**overrides):
    scores = {label: 0.0 for label in ALL_LABELS}
    scores.update(overrides)
    return json.dumps({"scores": scores}, ensure_ascii=False)


# ---- 阈值门 ----


@pytest.mark.parametrize(
    "scores, decision, category",
    [
        # 只命中一类自动、转二讲都低于阈值：可以自动
        ({"上课时间": 0.95}, AUTO, "上课时间"),
        ({"请假调课": 0.9}, AUTO, "请假调课"),
        ({"回放链接": 0.95, "退费": 0.89}, AUTO, "回放链接"),
        # 刚好等于阈值算达到
        ({"作业截止": 0.9, "投诉": 0.1}, AUTO, "作业截止"),
        # 自动类把握度不够
        ({"上课时间": 0.89}, HANDOFF, UNSURE_LABEL),
        ({}, HANDOFF, UNSURE_LABEL),
        # 两类自动同时命中：思考页写「只命中一类」，整条转二讲
        ({"上课时间": 0.95, "回放链接": 0.95}, HANDOFF, UNSURE_LABEL),
        # 转二讲类达到阈值，哪怕自动类更高
        ({"上课时间": 0.99, "退费": 0.9}, HANDOFF, "退费"),
        ({"上课时间": 0.99, "带情绪": 0.95}, HANDOFF, "带情绪"),
        ({"上课时间": 0.99, "学科答疑": 0.95}, HANDOFF, "学科答疑"),
        ({"上课时间": 0.99, "续报": 0.95}, HANDOFF, "续报"),
        ({"上课时间": 0.99, "投诉": 0.95}, HANDOFF, "投诉"),
        # 「都不是／拿不准」达到阈值也挡下
        ({"上课时间": 0.99, UNSURE_LABEL: 0.9}, HANDOFF, UNSURE_LABEL),
        # 多个转二讲类：按提醒优先级显示
        ({"学科答疑": 0.9, "投诉": 0.9}, HANDOFF, "投诉"),
    ],
)
def test_gate(scores, decision, category):
    result = decide(parse_scores(scores_json(**scores)), 0.9)
    assert (result.decision, result.category, result.source) == (decision, category, SOURCE_MODEL)


@pytest.mark.parametrize("threshold", [0.0, 1.01, float("nan")])
def test_odd_threshold_never_auto(threshold):
    assert decide(parse_scores(scores_json(上课时间=1.0)), threshold).decision == HANDOFF


def test_model_error_hands_off():
    result = decide(ModelResult(UNSURE_LABEL, 0.0, {}, "timeout"), 0.5)
    assert (result.decision, result.category, result.error) == (HANDOFF, UNSURE_LABEL, "timeout")


def test_incomplete_scores_hand_off():
    assert decide(ModelResult("上课时间", 0.99, {"上课时间": 0.99}), 0.5).decision == HANDOFF


# ---- 判断顺序 ----


def test_rule_hit_stops_before_the_model():
    backend = FakeBackend(scores_json(上课时间=0.99))
    result = classify("我要退费", backend, 0.9)
    assert (result.decision, result.category, result.source) == (HANDOFF, "退费", SOURCE_RULES)
    assert result.hits
    assert backend.seen == []


@pytest.mark.parametrize("text", ["[图片]", "[语音]", "http://example.com/a", "[捂脸]", ""])
def test_non_text_stops_before_the_model(text):
    backend = FakeBackend(scores_json(上课时间=0.99))
    result = classify(text, backend, 0.9)
    assert (result.decision, result.category, result.source) == (HANDOFF, UNSURE_LABEL, SOURCE_RULES)
    assert backend.seen == []


def test_undecided_goes_to_the_model_and_can_be_auto():
    backend = FakeBackend(scores_json(上课时间=0.99))
    result = classify("下节课几点", backend, 0.9)
    assert (result.decision, result.category, result.confidence) == (AUTO, "上课时间", 0.99)
    assert backend.seen == ["下节课几点"]


def test_model_failure_hands_off():
    backend = FakeBackend("不是 JSON")
    result = classify("下节课几点", backend, 0.9)
    assert (result.decision, result.category, result.error) == (HANDOFF, UNSURE_LABEL, "bad_json")


def test_no_model_hands_off_what_rules_let_through():
    result = classify("下节课几点", None, None)
    assert (result.decision, result.category, result.source) == (HANDOFF, UNSURE_LABEL, SOURCE_NO_MODEL)


def test_no_rules_sends_everything_to_the_model():
    backend = FakeBackend(scores_json(退费=0.99))
    result = classify("我要退费", backend, 0.9, use_rules=False)
    assert (result.source, result.category) == (SOURCE_MODEL, "退费")
    assert backend.seen == ["我要退费"]


def test_known_names_reach_the_redactor():
    backend = FakeBackend(scores_json(作业截止=0.99))
    classify("思涵的作业几号交", backend, 0.9, known_names=["思涵"])
    assert "思涵" not in backend.seen[0]
