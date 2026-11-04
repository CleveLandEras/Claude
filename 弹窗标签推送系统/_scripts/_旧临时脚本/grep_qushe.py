import os, re
base = "/Users/decheng.huang/claude/弹窗标签推送系统/"
for fn in ["claude_弹窗标签推送_盘点.html", "08_弹窗效果评估方案.md", "00_推进记录_本机补充.md", "02_弹窗分人群定制方案.html"]:
    t = open(os.path.join(base, fn), encoding="utf-8").read()
    for m in re.finditer(r"取舍|第八节|说明写法", t):
        s = max(0, m.start() - 80); e = m.end() + 80
        print(fn, "|", re.sub(r"\s+", " ", t[s:e]))
print("done")
