"""去标识化：把消息发给外部模型之前，换掉手机号、姓名、班级号。

占位符写法（用尖括号，和表示图片、语音的方括号占位区分开）：
    <手机号>  11 位手机号，含带横线、空格、+86 前缀、全角数字的写法
    <姓名>    2～4 字中文名
    <班级号>  带编号的班，连同前面的年级或班型一起换，如「三年级2班」「春季提高3班」
重复运行结果不变。

姓名靠上下文认，不查名字库，普通词尽量不动：
- 明确说名字：孩子叫 XX、儿子叫 XX、名字是 XX
- 称呼：XX 妈妈／爸爸／家长／奶奶／爷爷／外婆／外公／姥姥／姥爷／同学／小朋友，
  中间可以有「的」；XX 妈、XX 爸（这两个要求 XX 像名字）
- 我家 XX、我儿子 XX、我女儿 XX；家长 XX、学生 XX（后两个要求 XX 像名字）
- 句首或标点后，像名字的词紧跟时间词或请假、上课：王小测明天请假
「像名字」＝百家姓开头、叠字小名（样样）或小 X（小明）。
认出一个名字后，这条消息里它的所有出现都换掉。

认不出的情况：句中没有上下文的裸名字（「小测退回去 8 元」「问下思涵的作业」）。
调用方知道这位家长的备注名和孩子名时，用 known_names 传进来，这些名字无条件换掉。
不处理：座机号、身份证号、微信号、地址、老师姓名。
"""
from __future__ import annotations

import re
from typing import Iterable, List, Set

PHONE = "<手机号>"
NAME = "<姓名>"
CLASS_NO = "<班级号>"

_SEP = "[-－—– \t　]?"
_DIGIT = "[0-9０-９]"
_PHONE_RE = re.compile(
    r"(?<![0-9０-９])"
    r"(?:[+＋]?(?:86|８６)" + _SEP + r")?"
    r"[1１][3-9３-９]" + _DIGIT + r"(?:" + _SEP + _DIGIT + r"){8}"
    r"(?![0-9０-９])"
)

_CN_NUM = "一二三四五六七八九十"
_CLASS_RE = re.compile(
    r"(?<![0-9上下这那每同哪第A-Za-z])"
    r"(?:[" + _CN_NUM + r"初高]+年级|[初高][一二三]"
    r"|(?:春季|秋季|寒假|暑假|暑期|周末)?(?:提高|尖子|培优|基础|创新|实验|精英|强化|竞赛|冲刺))?"
    r"(?:[" + _CN_NUM + r"][(（][0-9]+[)）]|[(（]?(?:[0-9]+|[" + _CN_NUM + r"]+|[A-Za-z][0-9]*)[)）]?)"
    r"[ \t　]?班(?!级|主任|长|会|车|次)"
    r"|班级?(?:号|编号)[ \t　]*[:：是为]?[ \t　]*[0-9A-Za-z-]+"
)

_SURNAMES_1 = (
    "王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余"
    "潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段雷钱汤尹黎易常武乔贺赖龚文"
)
_SURNAMES_2 = ("欧阳", "上官", "司马", "诸葛", "慕容", "东方", "令狐", "皇甫", "尉迟", "公孙", "夏侯", "端木")
_SURNAME_RE = "(?:" + "|".join(_SURNAMES_2) + "|[" + _SURNAMES_1 + "])"

# 百家姓开头或形如叠字、小 X 的普通词，不当名字。
_COMMON_WORDS = frozenset(
    """
    周一 周二 周三 周四 周五 周六 周日 周天 周末 周几 周围 高中 高年 高一 高二 高三 高分 高考
    何时 何况 谢谢 金额 金币 金色 方便 方法 方程 方向 方式 马上 白天 白板 白色 黄色 关于
    文章 文件 文字 文科 全部 全班 成绩 任课 任何 任务 万一 万分 余下 余额 余款 常常 常规 常用
    石头 江湖 龙年 宋体 钱包 段落 段考 易错 康复 武术 田径 夏令 夏天 孟子 孔子 唐诗 宋词 韩语
    范文 陆续 程度 曾经 许多 于是 郑重 胡乱 钟头 毛病 顾问 黎明 贺卡 熊猫 叶子 李子 王者 刘海
    陈述 孙子 孙女 董事 张贴 丁点 苏州 江苏
    嗯嗯 哈哈 呵呵 好好 刚刚 天天 明明 慢慢 偏偏 渐渐 往往 仅仅 妈妈 爸爸 爷爷 奶奶 哥哥 姐姐
    弟弟 妹妹 叔叔 宝宝 娃娃 人人 个个 星星 看看 想想 试试 等等 对对 是是 行行 早早 恰恰 悄悄
    稍稍 默默 匆匆 时时 处处 讲讲 算算 问问 聊聊 说说 谈谈 帮帮 麻麻 粑粑
    小孩 小学 小时 小班 小组 小伙 小姐 小程 小朋 小数 小说 小区 小考 小学生 小朋友 小孩子
    孩子 小孩子 学生 老师 同学 家长 娃儿 宝贝 其他 其它 别的 别人 人家 大家 各位 每位 所有 全体
    很多 好多 一些 有些 部分 有的 隔壁 这位 那位 这个 那个 哪个 几个 每个 一个 两个 我们 你们
    他们 她们 咱们 自己 本人 老生 新生 学员 初中生 高中生 中学生 男生 女生 男同 女同 老大 老二
    班上 班里 全校 校区 老公 老婆 娃他 孩他
    """.split()
)
# 以这些开头的也不当名字。不放「李子」「叶子」这类，李子涵是常见名字。
_COMMON_PREFIXES = (
    "周一", "周二", "周三", "周四", "周五", "周六", "周日", "周天", "周末", "周几",
    "高年", "高中", "何时", "谢谢", "方便", "马上", "全部", "全班", "任何", "万一",
    "电脑", "网络", "宽带", "附近", "老人", "亲戚", "客人", "楼下", "今年", "明年", "情况",
)

# 名字里基本不会出现的字。
_NOT_IN_NAME = frozenset("你我他她您们这那哪谁吗呢吧啊呀哦么说过不没")
# 「我家」后面紧跟这些字时，后面不是名字（我家住得远、我家没问题）。
_NOT_NAME_START = frozenset("住离在有没是就也都还不的要想人里边很太已可因")

# 向前读名字时，读到这些词就算名字结束（只从第 3 个字开始看，避免截断两字名）。
_NAME_END_RE = re.compile(
    "今天|今晚|今早|明天|明晚|明早|昨天|昨晚|后天|这周|本周|下周|上周|周[一二三四五六日天末]|星期|礼拜|最近"
    "|下节|上节|下次|上次|上课|上不了|来不了|生病|发烧|感冒|同学|老师|妈妈|爸爸|家长"
    "|[的了要想不没能会在是有和跟也还就又都很太已可因请说这那呢吗呀啊哦吧去]"
)

# 向后读名字时，这些词之后才是名字（我是王小测妈妈、三年级班王小测的家长）。
_NAME_LEAD_RE = re.compile("我是|这边是|您好|你好|老师好|老师|麻烦|转告|通知|告诉|孩子|这边|[是我叫班的给跟和帮替找问请]")

_TIME_WORDS = (
    "这周|本周|下周|上周|明天|明早|明晚|今天|今晚|今早|昨天|昨晚|后天|周[一二三四五六日天末]|星期|礼拜"
    "|最近|这个|这次|这节|这学期|下节|上节|下次|上次|请假|上课|上不了|来不了|生病|发烧|感冒"
)
_BOUNDARY = r"(?:^|(?<=[^一-龥0-9A-Za-z]))"
_BARE_NAME_RE = re.compile(
    _BOUNDARY + r"(" + _SURNAME_RE + r"[一-龥]{1,2}|([一-龥])\2|小[一-龥])(?=" + _TIME_WORDS + r")"
)

_EXPLICIT_PREFIX_RE = re.compile(
    r"(?:(?:孩子|小孩|娃|儿子|女儿|闺女|学生|学员)(?:的)?(?:名字|姓名)?叫"
    r"|(?:名字|姓名)[ \t]*(?:是|叫|:|：)[ \t]*|我叫)"
)
_FAMILY_PREFIX_RE = re.compile(r"(?:我家(?:孩子|小孩|娃|宝贝|宝宝)?|我(?:儿子|女儿|闺女))")
_ROLE_PREFIX_RE = re.compile(r"(?:家长|学生|学员)")

_ROLE_SUFFIX_RE = re.compile(
    r"([一-龥]{2,}?)(?:的)?(?:妈妈|爸爸|家长|奶奶|爷爷|外婆|外公|姥姥|姥爷|同学|小朋友)"
)
_SHORT_SUFFIX_RE = re.compile(r"([一-龥]{2,}?)(?<![妈爸])(?:妈(?!妈)|爸(?!爸))")


def _looks_like_name(word: str) -> bool:
    if re.match(_SURNAME_RE, word):
        return True
    if len(word) == 2 and word[0] == word[1]:
        return True
    return word[0] == "小" and len(word) == 2


def _plausible(word: str) -> bool:
    if not 2 <= len(word) <= 4 or word in _COMMON_WORDS:
        return False
    if word.startswith(_COMMON_PREFIXES):
        return False
    return not any(char in _NOT_IN_NAME for char in word)


def _read_forward(text: str, start: int) -> str:
    """从 start 起读一个名字：读到非汉字或结束词为止，最多 4 个字。"""
    match = re.compile("[一-龥]{1,8}").match(text, start)
    if not match:
        return ""
    run = match.group(0)
    if _NAME_END_RE.match(run):
        return ""
    end = _NAME_END_RE.search(run, 2)
    return (run[: end.start()] if end else run)[:4]


def _read_backward(run: str) -> str:
    """从称呼前的一串汉字里取名字：取最后一个引导词之后的部分。"""
    leads = list(_NAME_LEAD_RE.finditer(run))
    if leads:
        run = run[leads[-1].end():]
    if len(run) <= 4:
        return run
    tail = run[-4:]
    surname = re.search(_SURNAME_RE, tail)
    return tail[surname.start():] if surname else run[-3:]


def _find_names(text: str) -> Set[str]:
    names: Set[str] = set()

    for match in _EXPLICIT_PREFIX_RE.finditer(text):
        word = _read_forward(text, match.end())
        if _plausible(word):
            names.add(word)

    for match in _FAMILY_PREFIX_RE.finditer(text):
        word = _read_forward(text, match.end())
        if _plausible(word) and word[0] not in _NOT_NAME_START:
            names.add(word)

    for match in _ROLE_PREFIX_RE.finditer(text):
        word = _read_forward(text, match.end())
        if _plausible(word) and _looks_like_name(word):
            names.add(word)

    for match in _ROLE_SUFFIX_RE.finditer(text):
        word = _read_backward(match.group(1))
        if _plausible(word):
            names.add(word)

    for match in _SHORT_SUFFIX_RE.finditer(text):
        word = _read_backward(match.group(1))
        if _plausible(word) and _looks_like_name(word):
            names.add(word)

    for match in _BARE_NAME_RE.finditer(text):
        word = match.group(1)
        if _plausible(word):
            names.add(word)

    return names


def _replace_names(text: str, names: Iterable[str]) -> str:
    ordered: List[str] = sorted({name for name in names if name}, key=len, reverse=True)
    for name in ordered:
        text = text.replace(name, NAME)
    return text


def redact(text: str, known_names: Iterable[str] = ()) -> str:
    """换掉手机号、班级号和姓名，返回新文字。占位符写法见模块说明。

    known_names：已知的名字（家长备注名、孩子名），无条件换掉，用来补上下文认不出的裸名字。
    """
    result = _PHONE_RE.sub(PHONE, text)
    result = _CLASS_RE.sub(CLASS_NO, result)
    result = _replace_names(result, known_names)
    return _replace_names(result, _find_names(result))
