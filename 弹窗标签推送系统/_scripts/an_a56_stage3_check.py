# 阶段3 整合核对：只读。①第七节 25 个场景判定计数；②正文内部编号；③首屏数字与第七节计数是否一致
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + "/"
html = open(base + "阶段3_现状盘点.html", encoding="utf-8").read()
body = re.sub(r"<style.*?</style>", "", html, flags=re.S)
text = re.sub(r"<[^>]+>", "", body)

# 第七节：从「七」节起到「八」节前
i = body.index('<span class="sec-no">七</span>')
j = body.index('<span class="sec-no">八</span>')
sec7 = body[i:j]
rows = re.findall(r'<tr><td><span class="chip">(\d+)</span>(.*?)</td><td><span class="tag [^"]*">([^<]+)</span></td>', sec7)
print("第七节场景行数", len(rows), "编号", sorted(int(r[0]) for r in rows) == list(range(1, 26)))
from collections import Counter
c = Counter(r[2] for r in rows)
for k, v in c.items():
    print(" ", k, v)
print("合计", sum(c.values()))

# 首屏
kpi = re.findall(r'<div class="l">([^<]+)</div><div class="n">([^<]+)</div><div class="d">([^<]*)</div>', body)
for k in kpi:
    print("KPI", k)

# 内部编号
pat = re.compile(r"(?<![A-Za-z0-9])([QRK]\d{2,3}|A\d{2})(?![A-Za-z0-9])")
print("正文内部编号命中", pat.findall(text))
print("待写占位残留", text.count("待写"))
print("正文汉字数", len(re.findall(r"[一-鿿]", text)))
