import os, re
base = "/Users/decheng.huang/claude/弹窗标签推送系统/"
pat = r"近 ?4 ?个月|快照|历史|保留|排程|结果表|潜在流失|其余|ID7|独享礼包|投注|赌注|活跃"
for fn in ["claude_弹窗标签推送_盘点.html", "02_弹窗分人群定制方案_迭代稿.html", "C2_新标签脚本草稿.md", "00_推进记录_本机补充.md"]:
    t = open(os.path.join(base, fn), encoding="utf-8").read()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    print("=====", fn)
    last = -1000
    for m in re.finditer(pat, t):
        if m.start() - last < 120:
            continue
        last = m.start()
        s = max(0, m.start() - 90); e = m.end() + 110
        print("|", t[s:e])
print("done")
