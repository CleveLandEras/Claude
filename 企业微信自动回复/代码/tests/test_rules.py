"""规则层单测。判断顺序见思考页 7.1 ②。

断言只针对这里写死的句子，不依赖 测试集/合成.jsonl 的标注（那份在另行核对）。
"""
import re

import pytest

from autoreply import dataset_stats
from autoreply.rules import HANDOFF, UNDECIDED, check, is_pure_non_text
from autoreply.rules_words import CATEGORY_PRIORITY, HANDOFF_PATTERNS, MASKS, UNSURE_LABEL


def _handoff_categories(text):
    return {hit.category for hit in check(text).hits}


# ---------- 词表本身 ----------


def test_categories_match_the_test_set_names():
    assert set(CATEGORY_PRIORITY) == set(dataset_stats.HANDOFF_LABELS)
    assert set(HANDOFF_PATTERNS) == set(dataset_stats.HANDOFF_LABELS)
    assert UNSURE_LABEL == dataset_stats.UNSURE_LABEL


def test_all_patterns_compile():
    for patterns in HANDOFF_PATTERNS.values():
        for pattern in patterns:
            re.compile(pattern)
    for pattern in MASKS:
        re.compile(pattern)


# ---------- 转二讲 5 类：字面和刁钻说法 ----------


@pytest.mark.parametrize(
    "category, text",
    [
        ("学科答疑", "这道题怎么做"),
        ("学科答疑", "第三题不会，能讲一下吗"),
        ("学科答疑", "老师 这题 咋做"),
        ("学科答疑", "今天讲的通分没听懂"),
        ("学科答疑", "这个字读第几声"),
        ("学科答疑", "作业第三题什么时候讲？孩子不会"),
        ("学科答疑", "时间状语从句是啥"),
        ("学科答疑", "火车几点到站这道题怎么算"),
        ("续报", "续费有优惠吗"),
        ("续报", "序报是不是这周截止"),
        ("续报", "续"),
        ("续报", "这学期快结束了吧，下学期还是您带吗？"),
        ("续报", "孩子挺喜欢这个课的，后面还有吗"),
        ("续报", "老同学是不是有什么政策呀"),
        ("续报", "寒假有课吗？孩子闲着也是闲着"),
        ("退费", "我想退费"),
        ("退费", "腿费怎么弄"),
        ("退费", "tuifei找谁"),
        ("退费", "最后一节课是几号？上完我们就不来了，后面的费用想问问"),
        ("退费", "合同到什么时候截止？想提前结束"),
        ("退费", "还剩几节课没上？想算下能拿回来多少"),
        ("退费", "课时有效期到哪天？过期的能折现吗"),
        ("退费", "如果现在不上了，后面那几节是怎么算的"),
        ("投诉", "我要投诉"),
        ("投诉", "我去消协问问"),
        ("投诉", "老师，我想了解一下你们这边有没有更高一级的联系方式"),
        ("投诉", "也不是要怎么样，就是想让上面知道一下这个情况"),
        ("投诉", "这个问题我已经录屏保存了，先跟您说一声"),
        ("投诉", "回放总出问题，这个是哪个部门管的"),
        ("投诉", "和报名时候介绍的好像不太一样，想找人沟通一下"),
        ("带情绪", "你们怎么回事"),
        ("带情绪", "有没有人管啊？？？"),
        ("带情绪", "呵呵"),
        ("带情绪", "回放呢？说好的回放呢？"),
        ("带情绪", "又改时间？你们课表是闹着玩的吗"),
        ("带情绪", "请假还要提前24小时？孩子发烧能提前知道吗？"),
        ("带情绪", "请问贵司的课到底是几点上呢？谢谢🙂"),
        ("带情绪", "辛苦老师百忙之中看一眼，今晚到底有没有课"),
        ("带情绪", "这个回放是给人看的吗，声音都听不清"),
    ],
)
def test_handoff_sentences_hit_their_category(category, text):
    result = check(text)
    assert result.decision == HANDOFF
    assert category in _handoff_categories(text), result.hits
    assert result.hits


def test_hit_reports_the_matched_word():
    result = check("老师，我想退费")
    assert result.category == "退费"
    assert any(hit.word == "退费" for hit in result.hits)


def test_priority_when_several_categories_hit():
    """提醒里显示的类别按 投诉 > 退费 > 带情绪 > 续报 > 学科答疑，全部命中都保留。"""
    result = check("不退钱我就投诉你们")
    assert result.decision == HANDOFF
    assert result.category == "投诉"
    assert {"投诉", "退费"} <= _handoff_categories("不退钱我就投诉你们")


def test_mixed_message_is_handed_off_as_a_whole():
    """事务句带一句转二讲，整条转二讲（思考页 7.1 ②）。"""
    result = check("这周作业几号交？你们通知也太乱了吧！！")
    assert result.decision == HANDOFF
    assert result.category == "带情绪"


def test_merged_lines_are_read_together():
    assert check("老师\n作业啥时候交\n这个字读第几声").decision == HANDOFF


def test_full_width_and_spaces_do_not_hide_a_word():
    assert check("退 费").category == "退费"
    assert check("TUIFEI").category == "退费"
    assert check("太过分了！！").category == "带情绪"
    assert check("太过分了!!").category == "带情绪"


# ---------- 非文字 ----------


@pytest.mark.parametrize(
    "text",
    ["[图片]", "[语音]", "[文件]", "[捂脸]", "👍", "🙏🙏", "https://example.com/abc", "", "   ", "？？"],
)
def test_pure_non_text_goes_to_unsure(text):
    result = check(text)
    assert result.decision == HANDOFF
    assert result.category == UNSURE_LABEL
    assert result.hits
    assert is_pure_non_text(text)


def test_non_text_is_judged_before_the_word_list():
    """第 1 步先于第 2 步：纯表情哪怕是负面表情，也归「都不是／拿不准」。"""
    result = check("😡")
    assert result.category == UNSURE_LABEL


@pytest.mark.parametrize("text", ["[链接] 看下这个", "下节课几点上 [图片]", "回放发下 www.example.com"])
def test_attachment_beside_text_is_handed_off_as_unsure(text):
    result = check(text)
    assert result.decision == HANDOFF
    assert result.category == UNSURE_LABEL


def test_attachment_beside_text_takes_category_from_text():
    assert check("老师，这道题怎么做？[图片]").category == "学科答疑"
    assert check("[图片] 这题").category == "学科答疑"
    assert check("[文件] 我要投诉").category == "投诉"


@pytest.mark.parametrize(
    "text", ["上课实践是几点来着[捂脸]", "好的[玫瑰]", "回放发下🙏", "明早的课是8点吗😊"]
)
def test_sticker_beside_text_counts_as_text(text):
    assert not is_pure_non_text(text)
    assert check(text).decision == UNDECIDED


# ---------- 未决：规则层不判自动类 ----------


@pytest.mark.parametrize(
    "text",
    [
        # 这些写词表时没看过，防止词表太宽
        "下周二的课还是老时间吗",
        "今晚是哪个老师上",
        "这周有几节课",
        "直播入口发一下",
        "明天上午有课没",
        "昨天那节回放有了吗",
        "回放怎么看",
        "录播在哪",
        "回放还能看几天",
        "错过的课哪里能补看",
        "回放链接失效了",
        "作业周几交",
        "这周的作业最晚啥时候",
        "作业晚交一天行吗",
        "数学作业周四交对吧",
        "作文几号交",
        "明晚有事请个假",
        "调到下周可以吗",
        "孩子不舒服了，今晚请假",
        "请假需要提前几天",
        "这周五来不了",
        "周二的课能换到周四吗",
        "孩子今天不舒服，上不了课",
        "老师好，请问周日上午的课是几点呀",
        "麻烦发一下回放，谢谢老师",
        "不好意思，这周作业哪天交",
        "谢谢老师，下节课是周几",
    ],
)
def test_plain_affairs_stay_undecided(text):
    result = check(text)
    assert result.decision == UNDECIDED, result.hits
    assert result.category is None
    assert result.hits == ()


@pytest.mark.parametrize(
    "text",
    [
        "今晚不上了，家里有事，明天见",
        "孩子感冒了，今天不上了，请个假",
        "退出直播间了，回放在哪看",
        "老师，退回来的作业要几号前重新交",
        "错题本什么时候交",
        "报名时说的周六上课，这周还是周六吧",
        "孩子生气不肯上，今晚先请个假吧",
        "老师，昨天孩子学校有活动回来晚了，回放发一下",
        "请假后课程还能补吗？",
    ],
)
def test_words_that_only_look_like_handoff_stay_undecided(text):
    assert check(text).decision == UNDECIDED, check(text).hits


@pytest.mark.parametrize(
    "text, category",
    [
        ("今晚不上了，我要退费", "退费"),
        ("退出直播间了，我要投诉", "投诉"),
        ("错题本我们不交了，你们怎么回事", "带情绪"),
    ],
)
def test_masks_do_not_hide_a_real_handoff_word(text, category):
    assert category in _handoff_categories(text)


def test_undecided_is_the_only_non_handoff_outcome():
    """规则层只给转二讲或未决两种结果，不判自动类。"""
    for text in ["下节课几点", "回放发下", "作业几号交", "请个假"]:
        result = check(text)
        assert result.decision == UNDECIDED
        assert result.category not in dataset_stats.AUTO_LABELS
