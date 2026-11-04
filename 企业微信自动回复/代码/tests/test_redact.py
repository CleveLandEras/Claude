"""去标识化单测：11 位手机号、2～4 字中文名、班级号，以及普通词不被换掉。"""
import json
import re
from pathlib import Path

import pytest

from autoreply.redact import CLASS_NO, NAME, PHONE, redact

TEST_SET = Path(__file__).resolve().parent.parent / "测试集" / "合成.jsonl"


# ---------- 手机号 ----------


@pytest.mark.parametrize(
    "number",
    [
        "13000000001",
        "130-0000-0005",
        "130 0000 0005",
        "1300 000 0005",
        "130－0000－0005",
        "+86 13000000001",
        "86-13000000001",
        "１３００００００００１",
        "19912345678",
    ],
)
def test_phone_numbers_are_replaced(number):
    assert redact(f"电话{number}，谢谢") == f"电话{PHONE}，谢谢"


def test_several_phones_in_one_message():
    text = "13000000001 或者 130-0000-0002\n13000000003"
    assert redact(text) == f"{PHONE} 或者 {PHONE}\n{PHONE}"


@pytest.mark.parametrize(
    "text",
    [
        "打12315",
        "练习册第12页第4题",
        "1300000000",  # 10 位
        "130000000012",  # 12 位
        "12000000001",  # 不是手机号段
        "下午3点到5点半",
        "2026-11-04 13:00",
        "1/2+1/3 等于多少",
    ],
)
def test_other_numbers_stay(text):
    assert redact(text) == text


# ---------- 姓名：2、3、4 字，各种上下文 ----------


@pytest.mark.parametrize(
    "text, expected",
    [
        # 2 字
        ("孩子叫小明", f"孩子叫{NAME}"),
        ("我家样样今天请假", f"我家{NAME}今天请假"),
        ("样样妈妈", f"{NAME}妈妈"),
        # 3 字
        ("孩子叫王小测，三年级", f"孩子叫{NAME}，三年级"),
        ("我是王小测妈妈，电话给您", f"我是{NAME}妈妈，电话给您"),
        ("赵例例爸爸，请问续报怎么弄", f"{NAME}爸爸，请问续报怎么弄"),
        ("我家王小测明天请假", f"我家{NAME}明天请假"),
        ("我家孩子王小测明天请假", f"我家孩子{NAME}明天请假"),
        ("李小样家长想退费", f"{NAME}家长想退费"),
        ("我是王小测的家长", f"我是{NAME}的家长"),
        ("联系我，家长赵例例", f"联系我，家长{NAME}"),
        ("王小测同学今天没来", f"{NAME}同学今天没来"),
        ("我儿子李小样想请假", f"我儿子{NAME}想请假"),
        ("小明妈，回放发下", f"{NAME}妈，回放发下"),
        # 4 字
        ("孩子叫欧阳小明", f"孩子叫{NAME}"),
        ("欧阳小明妈妈", f"{NAME}妈妈"),
        ("我家司马小测今天请假", f"我家{NAME}今天请假"),
        ("孩子的名字叫李小样", f"孩子的名字叫{NAME}"),
        # 句首的名字紧跟时间词
        ("王小测这周上课时间有变吗", f"{NAME}这周上课时间有变吗"),
        ("样样昨天请假了，回放在哪看", f"{NAME}昨天请假了，回放在哪看"),
        ("作业几号交？王小测最近是不是退步了", f"作业几号交？{NAME}最近是不是退步了"),
    ],
)
def test_names_in_context_are_replaced(text, expected):
    assert redact(text) == expected


def test_every_occurrence_of_a_found_name_is_replaced():
    assert redact("我是样样妈妈，样样下节课是什么时候？") == f"我是{NAME}妈妈，{NAME}下节课是什么时候？"


def test_two_character_name_is_not_cut_by_end_words():
    """结束词只从第 3 个字开始看，两字名不会被截断。"""
    assert redact("孩子叫李想") == f"孩子叫{NAME}"


def test_known_names_are_replaced_without_context():
    assert redact("问下思涵的作业", known_names=["思涵"]) == f"问下{NAME}的作业"
    assert redact("小测退回去8元", known_names=["小测"]) == f"{NAME}退回去8元"


def test_longer_known_name_wins():
    assert redact("王小测和小测", known_names=["小测", "王小测"]) == f"{NAME}和{NAME}"


# ---------- 普通词不换 ----------


@pytest.mark.parametrize(
    "text",
    [
        "孩子爸爸要安排接送",
        "您加一下孩子爸爸的微信吧",
        "隔壁班家长说有活动，我们还能参加吗",
        "其他家长也都有这个感觉",
        "家长您好，体验课限时免费",
        "家长群里都在说",
        "你们想过家长的感受吗",
        "我家没问题，就是想问下这周课几点",
        "我家住得远，能调课吗",
        "我家孩子今天请假",
        "我家里有事，今晚来不了",
        "老同学是不是有什么政策呀",
        "谢谢老师",
        "谢谢今天的课",
        "周日这节课几点",
        "周末这周有课吗",
        "高年级这周上课吗",
        "老师明天上课吗",
        "孩子今天请假",
        "妈妈明天来接",
        "刚刚上课的回放有吗",
        "小孩今天发烧",
        "小朋友今天请假",
        "这个同学",
        "下节课几点上",
        "作文题目我们选好了，几号前交呀",
        "您这边要是忙不过来，回放我们就不要了",
    ],
)
def test_ordinary_words_stay(text):
    assert redact(text) == text


# ---------- 班级号 ----------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("三年级2班这周的课是周几？", f"{CLASS_NO}这周的课是周几？"),
        ("春季提高3班今晚有课吗", f"{CLASS_NO}今晚有课吗"),
        ("我们是3班的", f"我们是{CLASS_NO}的"),
        ("三年级（2）班", CLASS_NO),
        ("初二3班", CLASS_NO),
        ("三(2)班", CLASS_NO),
        ("A班的", f"{CLASS_NO}的"),
        ("班级号：12345", CLASS_NO),
        ("班号 A-102", CLASS_NO),
    ],
)
def test_class_numbers_are_replaced(text, expected):
    assert redact(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "春季班什么时候开始报",
        "能换到周末班吗",
        "寒假班还能报吗",
        "全年班和单期班哪个划算",
        "这个班换了几个老师",
        "报错班了，能退吗",
        "老生续班能打折吗",
        "这班主任是谁",
    ],
)
def test_class_words_without_number_stay(text):
    assert redact(text) == text


# ---------- 组合、幂等 ----------


def test_phone_name_and_class_in_one_message():
    text = "我是三年级2班王小测妈妈，电话130-0000-0001"
    assert redact(text) == f"我是{CLASS_NO}{NAME}妈妈，电话{PHONE}"


def test_class_then_name_without_separator():
    assert redact("春季提高3班李小样今晚请假") == f"{CLASS_NO}{NAME}今晚请假"


def test_running_twice_changes_nothing():
    text = "我是三年级2班王小测妈妈，电话130-0000-0001，孩子叫王小测"
    once = redact(text)
    assert redact(once) == once


# ---------- 整份合成测试集：思考页里程碑 4 第 3 步也要搜不到手机号 ----------


def _test_set_texts():
    return [
        json.loads(line)["text"]
        for line in TEST_SET.read_text(encoding="utf-8").split("\n")
        if line.strip()
    ]


def test_no_phone_left_in_the_test_set():
    for text in _test_set_texts():
        assert not re.search(r"1[3-9]\d(?:[- ]?\d){8}", redact(text)), text


def test_no_full_name_left_in_the_test_set():
    for text in _test_set_texts():
        assert not re.search(r"王小测|李小样|赵例例", redact(text)), text
