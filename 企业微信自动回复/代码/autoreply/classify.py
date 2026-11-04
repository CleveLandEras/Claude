"""把规则层和模型层串起来，判一条家长消息能不能自动回。

判断顺序照思考页 7.1 ②（任何一步命中转二讲就停）：
1、2. 规则层（rules.check，用原话判）：非文字、词表命中转二讲 5 类 → 转二讲。
3.    模型层（model.predict，发出前去标识化）：只有「只命中自动 4 类中的一类、把握度达到阈值、
      且转二讲 5 类的把握度都低于阈值」才算可以自动。
      「都不是／拿不准」达到阈值同样挡下：它也该转二讲（思考页 11/04 第二级改第 ③ 点）。
4.    素材里找不找得到答案是里程碑 3 的事。这里的 AUTO 意思是「可以进第 4 步」。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Optional, Tuple

from .dataset_stats import ALL_LABELS, AUTO_LABELS, UNSURE_LABEL
from .model import Backend, ModelResult, predict
from .rules import HANDOFF, Hit, check
from .rules_words import CATEGORY_PRIORITY

AUTO = "自动"

SOURCE_RULES = "规则层"
SOURCE_MODEL = "模型层"
SOURCE_NO_MODEL = "无模型"

_BLOCKING = CATEGORY_PRIORITY + (UNSURE_LABEL,)


@dataclass(frozen=True)
class Decision:
    """decision 是 AUTO 或 HANDOFF。

    category：判自动时是那一类，转二讲时是提醒里显示的类别。
    source：谁定的。confidence、scores 只有模型层判过才有。
    hits：规则层命中的词，放进提醒当依据。error：模型这一步出了什么错。
    """

    decision: str
    category: str
    source: str
    confidence: Optional[float] = None
    scores: Mapping[str, float] = field(default_factory=dict)
    hits: Tuple[Hit, ...] = ()
    error: Optional[str] = None


def decide(result: ModelResult, threshold: float) -> Decision:
    """把模型结果过阈值门。凑不齐条件的一律转二讲。"""
    scores = result.scores
    if result.error or set(scores) != set(ALL_LABELS):
        return Decision(HANDOFF, UNSURE_LABEL, SOURCE_MODEL, error=result.error or "bad_schema")

    auto_hits = [label for label in AUTO_LABELS if scores[label] >= threshold]
    blocking = [label for label in _BLOCKING if scores[label] >= threshold]
    if len(auto_hits) == 1 and not blocking:
        return Decision(AUTO, auto_hits[0], SOURCE_MODEL, scores[auto_hits[0]], scores)
    return Decision(
        HANDOFF,
        blocking[0] if blocking else UNSURE_LABEL,
        SOURCE_MODEL,
        result.confidence,
        scores,
    )


def classify(
    text: str,
    backend: Optional[Backend],
    threshold: Optional[float],
    known_names: Iterable[str] = (),
    use_rules: bool = True,
) -> Decision:
    """判一条消息（连发合并后的全文）。

    backend 为 None 表示没有模型：规则层没拦下的也转二讲，这是没有模型时最保守的做法。
    use_rules=False 只给 eval、tune 单独评模型层用，正式流程不要关。
    """
    if use_rules:
        rule = check(text)
        if rule.decision == HANDOFF:
            return Decision(HANDOFF, rule.category or UNSURE_LABEL, SOURCE_RULES, hits=rule.hits)
    if backend is None:
        return Decision(HANDOFF, UNSURE_LABEL, SOURCE_NO_MODEL)
    return decide(predict(text, backend, known_names), threshold)
