"""选题单闸门：执行对话开工前先跑，输出“通过”才能开工。

检查四样：
1. “前提条目”表里每一行都有方法、证据文件、外部核对结果，审核结论写的是“过”；
2. 证据文件真实存在（路径相对项目根目录，多个用“；”隔开）；
3. 至少有话题人群、平台观众、前置事实、选题本身这四类前提各一条；
4. 模式是 A 时，“号主看过”一节里写了日期。
用法：.venv/bin/python -I tools/选题单检查.py videos/00X_xxx/选题单.md
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEED_TYPES = ["话题人群", "平台观众", "前置事实", "选题本身"]


def section(text, title):
    m = re.search(r"^## " + re.escape(title) + r".*?$(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def rows(table_text):
    out = []
    for line in table_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0] == "编号":
            continue
        out.append(cells)
    return out


def main(path):
    text = open(path, encoding="utf-8").read()
    problems = []
    table = rows(section(text, "前提条目"))
    if not table:
        problems.append("没有找到“前提条目”表")
    types_seen = set()
    for r in table:
        if len(r) < 7:
            problems.append(f"{r[0] if r else '?'}：列数不够")
            continue
        no, claim, kind, method, files, check, verdict = r[:7]
        if not claim:
            continue
        types_seen.add(kind)
        for name, val in (("方法", method), ("证据文件", files), ("外部核对结果", check)):
            if not val or val in ("—", "-"):
                problems.append(f"{no}：缺{name}")
        for f in [x.strip() for x in files.split("；") if x.strip() and x.strip() not in ("—", "-")]:
            f = f.strip("`")
            if not os.path.exists(os.path.join(ROOT, f)):
                problems.append(f"{no}：证据文件不存在：{f}")
        if not verdict.startswith("过"):
            problems.append(f"{no}：审核结论不是“过”（现在是“{verdict or '空'}”）")
    for t in NEED_TYPES:
        if t not in types_seen:
            problems.append(f"缺少“{t}”类前提")
    if re.search(r"模式：\s*A", text):
        seen = section(text, "号主看过")
        if not re.search(r"日期：[ \t]*[^\s<]", seen):
            problems.append("模式 A：号主还没看过（“号主看过”一节没有日期）")
    if problems:
        print("不通过")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("通过")


if __name__ == "__main__":
    main(sys.argv[1])
