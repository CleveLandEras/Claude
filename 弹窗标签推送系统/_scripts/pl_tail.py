import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os, time
B = _ROOT + "/"
for d in ["", "过程记录/", "规则与交接/", "分析/", "_versions/"]:
    items = []
    for f in os.listdir(B + d):
        p = B + d + f
        if os.path.isfile(p):
            items.append((os.path.getmtime(p), d + f))
    items.sort(reverse=True)
    for m, f in items[:6]:
        print(time.strftime("%m-%d %H:%M", time.localtime(m)), f)
def tail(p, n):
    with open(B + p, encoding="utf-8") as f:
        L = f.readlines()
    print("=" * 20, p, len(L), "lines; from", max(0, len(L) - n) + 1)
    print("".join(L[-n:]))
tail("过程记录/审查记录.md", 12)
tail("过程记录/监督记录.md", 30)
