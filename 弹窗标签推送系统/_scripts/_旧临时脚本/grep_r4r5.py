import re
BASE = "/Users/decheng.huang/claude/弹窗标签推送系统/"
for fn, pats in [
    ("02_弹窗分人群定制方案.html", ["44,027", "70% / 50% / 25%", "三档"]),
    ("C2_新标签脚本草稿.md", ["【待核对：会员编号】", "JOIN"]),
]:
    lines = open(BASE + fn, encoding="utf-8").read().split("\n")
    for i, l in enumerate(lines, 1):
        if any(p in l for p in pats):
            print(fn, i, l.strip()[:600])
