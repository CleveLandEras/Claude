import os
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "迭代记录.md")
with open(p, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if line.startswith("## ") or "v1.2.3" in line:
            print(i, line.rstrip()[:80])
