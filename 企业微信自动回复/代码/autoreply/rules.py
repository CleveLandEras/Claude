"""规则层：先把明显该转二讲的消息拦下，拦不下的返回「未决」留给模型层。

判断顺序照思考页 7.1 ②（任何一步命中转二讲就停）：
1. 不是文字（图片、语音、文件、表情、链接）→ 转二讲，类别「都不是／拿不准」。
   一条里文字和图片、文件、链接并存时也转二讲，因为工具读不了那部分（第 6 节第 4 条）；
   类别按文字判（测试集/说明.md 第 5 条），文字没命中就是「都不是／拿不准」。
   表情夹在文字里（「好的[玫瑰]」）算文字。
2. 词表命中转二讲 5 类任一 → 转二讲，给出全部命中的类别和词。
不命中返回「未决」。规则层自己不判自动类，这是模型层的事。

词表在 rules_words.py。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional, Tuple

from .rules_words import ATTACHMENT_TAGS, CATEGORY_PRIORITY, HANDOFF_PATTERNS, MASKS, UNSURE_LABEL

HANDOFF = "转二讲"
UNDECIDED = "未决"

_COMPILED = {
    category: tuple(re.compile(pattern) for pattern in patterns)
    for category, patterns in HANDOFF_PATTERNS.items()
}
_COMPILED_MASKS = tuple(re.compile(pattern) for pattern in MASKS)

_TAG = re.compile(r"\[[^\[\]]{1,10}\]")
_ATTACHMENT = re.compile(r"\[(?:" + "|".join(ATTACHMENT_TAGS) + r")\]")
_URL = re.compile(
    r"https?://[a-z0-9./?=&_%#:~+-]+"
    r"|www\.[a-z0-9./?=&_%#:~+-]+"
    r"|[a-z0-9-]+\.(?:com|cn|net|org|cc|top|vip)(?:/[a-z0-9./?=&_%#:~+-]*)?"
)
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF️‍]"
)


@dataclass(frozen=True)
class Hit:
    """命中一处：哪一类，命中的字（统一写法后的原文片段，放进提醒当依据）。"""

    category: str
    word: str


@dataclass(frozen=True)
class RuleResult:
    """decision 是 HANDOFF 或 UNDECIDED。

    category 是提醒里显示的类别，未决时为 None；hits 是全部命中，未决时为空。
    """

    decision: str
    category: Optional[str] = None
    hits: Tuple[Hit, ...] = ()


def normalize(text: str) -> str:
    """全角转半角、英文转小写、去掉所有空白。词表都按这个写法写。"""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text).lower())


def _is_only_punctuation_or_symbol(text: str) -> bool:
    return all(unicodedata.category(char)[0] in "PSZC" for char in text)


def is_pure_non_text(text: str) -> bool:
    """去掉占位、表情、链接、标点后什么都不剩（空消息也算：读不到文字）。"""
    normalized = normalize(text)
    rest = _URL.sub("", _TAG.sub("", normalized))
    return _is_only_punctuation_or_symbol(_EMOJI.sub("", rest))


def _non_text_hits(normalized: str) -> Tuple[Hit, ...]:
    words = [match.group(0) for match in _ATTACHMENT.finditer(normalized)]
    words += [match.group(0) for match in _URL.finditer(normalized)]
    return tuple(Hit(UNSURE_LABEL, word) for word in words)


def _word_hits(normalized: str) -> Tuple[Hit, ...]:
    for mask in _COMPILED_MASKS:
        normalized = mask.sub("\x00", normalized)
    hits = []
    for category in CATEGORY_PRIORITY:
        for pattern in _COMPILED[category]:
            match = pattern.search(normalized)
            if match:
                hits.append(Hit(category, match.group(0)))
    return tuple(hits)


def check(text: str) -> RuleResult:
    """判一条家长消息（连发合并后的全文）。用原话判，不要先去标识化。"""
    normalized = normalize(text)
    non_text = _non_text_hits(normalized)

    if is_pure_non_text(text):
        return RuleResult(HANDOFF, UNSURE_LABEL, non_text or (Hit(UNSURE_LABEL, "非文字"),))

    words = _word_hits(normalized)
    if words:
        return RuleResult(HANDOFF, words[0].category, words + non_text)
    if non_text:
        return RuleResult(HANDOFF, UNSURE_LABEL, non_text)
    return RuleResult(UNDECIDED)
