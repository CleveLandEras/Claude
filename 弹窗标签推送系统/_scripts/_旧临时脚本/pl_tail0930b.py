import os, re
B = "/Users/decheng.huang/claude/弹窗标签推送系统/"
def tail(p, n):
    with open(B + p, encoding="utf-8") as f:
        L = f.readlines()
    print("=" * 20, p, len(L))
    for x in L[-n:]:
        print(x.rstrip()[:900])
tail("进展日志.md", 10)
# design cards headers
with open(B + "过程记录/设计卡.md", encoding="utf-8") as f:
    L = f.readlines()
print("=" * 20, "设计卡 headers")
for i, x in enumerate(L):
    if x.startswith("## ") or "⚠ 设计意见" in x:
        print(i + 1, x.rstrip()[:200])
# review record: after 10:29?
with open(B + "过程记录/审查记录.md", encoding="utf-8") as f:
    L = f.readlines()
print("review lines", len(L))
# file mtimes
for d in ["", "分析/", "支撑文件/", "过程记录/"]:
    for fn in sorted(os.listdir(B + d)):
        p = B + d + fn
        if os.path.isfile(p):
            import time
            t = os.path.getmtime(p)
            if t > time.time() - 3 * 3600:
                print(time.strftime("%m-%d %H:%M", time.localtime(t)), d + fn)
