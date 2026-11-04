#!/usr/bin/env python3
"""比对功能框架（弹窗、推播、上限与勿扰、数据和查询里属于推播和弹窗的部分）和功能清单脑图第 4、5 层。

框架的「功能」= 第 2 层页面（如 新建推播、单条弹窗规则）；「设置项」= 页面下第 3 层节点。
少数分组节点用它的子节点当设置项（见 EXPAND）。短信、快显专属的设置项不进脑图（见 is_sms_or_kuaixian）。
节点名规范化：去空白、去括号里的标签；带「：」的取冒号前的名称，冒号前只是渠道名（推播、短信、弹窗、快显）时取冒号后。
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/decheng.huang/claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求")
FRAME = ROOT / "功能框架_脑图.md"
MAP = ROOT / "功能清单_两份汇报_脑图.md"

# 框架里要覆盖的页面：第 1 层模块 -> 第 2 层页面
SCOPE = {
    "游戏外推送": ["新建推播", "推播列表"],
    "游戏内推送": ["弹窗场景设置", "弹窗规则列表", "新建弹窗规则", "活动或礼包的弹窗设置"],
    "每人每天上限与夜间勿扰": ["每人每天上限设置", "夜间勿扰设置"],
    "数据": ["总览", "明细表", "对比", "单条推播、短信", "单条弹窗规则",
             "弹窗场景与快显显示位置数据", "活动汇总", "每人每天收到几条"],
    "查询": ["玩家查询"],  # 独立的「操作纪录」模块不在范围（卡上只写数据和玩家查询）
}

# 用子节点当设置项的分组节点（页面, 路径...）
EXPAND = {
    ("新建推播", "发送方式"),
    ("新建推播", "发送方式", "定时"),
    ("新建推播", "发送方式", "条件触发"),
    ("新建弹窗规则", "弹哪些活动或礼包"),
    ("玩家查询", "推播、短信、快显"),
    ("玩家查询", "弹窗"),
}

# 脑图第 4 层功能 -> 框架页面
FUNC_PAGE = {
    ("弹窗", "设多条规则都符合时弹哪条"): "弹窗场景设置",
    ("弹窗", "新建弹窗规则"): "新建弹窗规则",
    ("弹窗", "排场景内规则先后"): "弹窗规则列表",
    ("弹窗", "设场景的每天上限"): "弹窗场景设置",
    ("弹窗", "设场景的弹出间隔"): "弹窗场景设置",
    ("弹窗", "设活动或礼包的次数和间隔"): "活动或礼包的弹窗设置",
    ("弹窗", "设活动或礼包的弹窗设置"): "活动或礼包的弹窗设置",
    ("弹窗", "选规则弹哪些活动或礼包"): "新建弹窗规则",
    ("弹窗", "上架前测试和预览"): "新建弹窗规则",
    ("弹窗", "管弹窗规则列表"): "弹窗规则列表",
    ("弹窗", "看弹窗总览"): "总览",
    ("弹窗", "看单条规则数据"): "单条弹窗规则",
    ("弹窗", "看场景数据"): "弹窗场景与快显显示位置数据",
    ("弹窗", "查某个玩家为什么没弹"): "玩家查询",
    ("推播", "圈发送对象"): "新建推播",
    ("推播", "填推播内容并测试"): "新建推播",
    ("推播", "设定时发送"): "新建推播",
    ("推播", "设条件触发"): "新建推播",
    ("推播", "设夜间勿扰"): "夜间勿扰设置",
    ("推播", "管推播列表和排期"): "推播列表",
    ("推播", "设每人每天上限"): "每人每天上限设置",
    ("推播", "设类别、权重并确认发布"): "新建推播",
    ("推播", "看每人每天收到几条"): "每人每天收到几条",
    ("推播", "看推播总览"): "总览",
    ("推播", "筛选推送明细"): "明细表",
    ("推播", "对比几条推送"): "对比",
    ("推播", "看单条推播数据"): "单条推播、短信",
    ("推播", "标推播所属活动"): "新建推播",
    ("推播", "看活动汇总"): "活动汇总",
    ("推播", "查某个玩家为什么没收到"): "玩家查询",
}

# 脑图里改成能看出所指的名称：脑图名 -> 框架名
ALIAS = {
    "列表显示的字段": "每行",
    "每行一条推送": "每行",
    "按渠道分行": "行",
    "按会员编号、昵称、手机号查": "输入",
    "从哪里打开": "入口",
    "适用渠道": "适用",
    "按发送方式分页签": "页签",
}

EXPECTED_Q = {
    "弹窗": [
        "给谁弹：场景内按人群配规则，同属几群只弹最前一条",
        "弹多少：每天上限、场景间隔、活动次数三层限量",
        "怎么配：每个活动只配一次，各规则共用",
        "怎么验：上架前可测可预览，上架后可查没弹原因",
    ],
    "推播": [
        "发给谁：按群组圈人，发前看到人数",
        "什么时候发：定时或条件触发，夜里不发营销",
        "发多少：营销每人每天限量，重要的优先",
        "怎么看效果：可筛选、可对比，逐条看到达和没发原因",
    ],
}

CHANNELS = {"推播", "短信", "弹窗", "快显"}


def rawnorm(s):
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"（[^（）]*）|\([^()]*\)", "", s)
    return s


def name(s):
    t = rawnorm(s)
    if "：" in t:
        pre, post = t.split("：", 1)
        if set(pre.split("、")) <= CHANNELS:
            return post
        return pre
    return t


def is_sms_or_kuaixian(s):
    t = rawnorm(s)
    return ("短信" in t or "快显" in t) and not ("推播" in t or "弹窗" in t)


def parse_list(path):
    """返回节点列表：dict(depth, text, line, children)；depth 0 为最外层「- 」。"""
    roots, stack = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"^( *)- (.*)$", line)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        node = {"depth": depth, "text": m.group(2).strip(), "line": i, "children": []}
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()
        (stack[-1]["children"] if stack else roots).append(node)
        stack.append(node)
    return roots


def frame_settings():
    keys, excluded, pages_found = {}, [], set()
    frame_dups = []
    for sec in parse_list(FRAME):
        sec_name = next((k for k in SCOPE if rawnorm(sec["text"]).startswith(k)), None)
        if not sec_name:
            continue
        for page in sec["children"]:
            pname = rawnorm(page["text"])
            if pname not in SCOPE[sec_name]:
                continue
            pages_found.add(pname)

            def collect(node, path):
                for c in node["children"]:
                    p = path + (name(c["text"]),)
                    if (pname,) + p in EXPAND:
                        collect(c, p)
                        continue
                    if is_sms_or_kuaixian(c["text"]):
                        excluded.append((pname, c["text"], c["line"]))
                        continue
                    k = (pname, name(c["text"]))
                    if k in keys:
                        frame_dups.append((k, keys[k], c["line"]))
                    else:
                        keys[k] = c["line"]

            collect(page, ())
    return keys, excluded, pages_found, frame_dups


def map_nodes():
    text = MAP.read_text(encoding="utf-8")
    h1 = [l for l in text.splitlines() if l.startswith("# ")]
    roots = parse_list(MAP)
    l3, l4, l5, problems = [], [], [], []
    for b in roots:
        for q in b["children"]:
            l3.append((b["text"], q["text"]))
            for f in q["children"]:
                l4.append((b["text"], f["text"], f["line"]))
                for s in f["children"]:
                    l5.append((b["text"], f["text"], s["text"], s["line"]))
                    if s["children"]:
                        problems.append(f"第 {s['line']} 行下面还有第 6 层")
    return h1, roots, l3, l4, l5, problems


def main():
    fkeys, excluded, pages_found, frame_dups = frame_settings()
    h1, roots, l3, l4, l5, problems = map_nodes()

    # 结构检查
    if h1 != ["# 推送统一后台"]:
        problems.append(f"第 1 层应只有「# 推送统一后台」，实际 {h1}")
    if [b["text"] for b in roots] != ["弹窗", "推播"]:
        problems.append(f"第 2 层应为 弹窗、推播，实际 {[b['text'] for b in roots]}")
    for br, qs in EXPECTED_Q.items():
        got = [q for b, q in l3 if b == br]
        if got != qs:
            problems.append(f"{br} 的第 3 层和约定不一致：{got}")
    missing_pages = sorted({p for ps in SCOPE.values() for p in ps} - pages_found)
    if missing_pages:
        problems.append(f"框架里没找到这些页面：{missing_pages}")

    # 第 4 层
    func_cnt = Counter((b, f) for b, f, _ in l4)
    func_dup = [k for k, n in func_cnt.items() if n > 1]
    func_unmapped = [(b, f, ln) for b, f, ln in l4 if (b, f) not in FUNC_PAGE]
    covered_pages = {FUNC_PAGE[(b, f)] for b, f, _ in l4 if (b, f) in FUNC_PAGE}
    page_uncovered = sorted(pages_found - covered_pages)

    # 第 5 层
    mkeys = defaultdict(list)
    for b, f, s, ln in l5:
        page = FUNC_PAGE.get((b, f))
        if page:
            mkeys[(page, ALIAS.get(s, name(s)))].append(ln)
    missing = sorted(set(fkeys) - set(mkeys), key=lambda k: fkeys[k])
    dup = {k: v for k, v in mkeys.items() if len(v) > 1}
    extra = {k: v for k, v in mkeys.items() if k not in fkeys}

    print(f"层级节点数：第 3 层 {len(l3)}，第 4 层 {len(l4)}，第 5 层 {len(l5)}")
    print(f"框架范围内设置项 {len(fkeys)} 个（另排除短信、快显专属 {len(excluded)} 个）；框架页面 {len(pages_found)} 个")
    print()
    print(f"【框架有、图里缺】{len(missing)}")
    for k in missing:
        print(f"  {k[0]} / {k[1]}（框架第 {fkeys[k]} 行）")
    print(f"【图里重复】{len(dup)}")
    for k, v in dup.items():
        print(f"  {k[0]} / {k[1]}（脑图第 {v} 行）")
    print(f"【图里有、框架没有】{len(extra)}")
    for k, v in extra.items():
        print(f"  {k[0]} / {k[1]}（脑图第 {v} 行）")
    print(f"【第 4 层功能名重复】{len(func_dup)}  {func_dup if func_dup else ''}")
    print(f"【第 4 层功能没对上框架页面】{len(func_unmapped)}  {func_unmapped if func_unmapped else ''}")
    print(f"【框架页面没有对应功能】{len(page_uncovered)}  {page_uncovered if page_uncovered else ''}")
    print(f"【框架自身同页重名】{len(frame_dups)}  {frame_dups if frame_dups else ''}")
    print(f"【结构问题】{len(problems)}")
    for p in problems:
        print(f"  {p}")
    print()
    print("排除的短信、快显专属设置项：")
    for p, t, ln in excluded:
        print(f"  {p} / {t}（框架第 {ln} 行）")
    same = Counter(ALIAS.get(s, name(s)) for _, _, s, _ in l5)
    shared = sorted(n for n, c in same.items() if c > 1)
    print()
    print(f"同名但属不同页面的设置项（框架里本来是不同页面的同名字段，不算重复）：{len(shared)} 个：{'、'.join(shared)}")

    bad = missing or dup or extra or func_dup or func_unmapped or page_uncovered or problems
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
