import os, re, datetime
base = "/Users/decheng.huang/claude/弹窗标签推送系统/"
print("now", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
pat = r"首储|先后|同时命中|优先级|开放期|开放时间|写死|定向规则|全量"
for fn in ["claude_弹窗标签推送_盘点.html", "08_弹窗效果评估方案.md", "C2_新标签脚本草稿.md", "00_推进记录_本机补充.md"]:
    t = open(os.path.join(base, fn), encoding="utf-8").read()
    t = re.sub(r"<[^>]+>", " ", t)
    for m in re.finditer(pat, t):
        s = max(0, m.start() - 90); e = m.end() + 90
        print(fn, "|", re.sub(r"\s+", " ", t[s:e]))
print("done")
