import os
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "迭代记录.md")
for i, l in enumerate(open(p, encoding="utf-8"), 1):
    if l.startswith("## ") or l.startswith("### v"):
        print(i, l.rstrip()[:80])
