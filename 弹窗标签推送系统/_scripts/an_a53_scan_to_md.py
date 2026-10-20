# 把 an_a52 的分母扫描明细写进 A49 补五，并核对「成稿值」是否真在成稿 HTML 文字里出现（R306）
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import io, re, contextlib, os
base = _ROOT + "/"
src = open(base + "_scripts/an_a52_denominator_scan.py", encoding="utf-8").read()
ns = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(src, ns)
rows = ns["rows"]
html = open(base + "阶段2_人群分析.html", encoding="utf-8").read()
text = re.sub(r"<[^>]+>", "", html)

def found(shown):
    forms = [f"{shown:.2f}%", f"{shown:.1f}%", f"{round(shown)}%"]
    for f in forms:
        if f in text:
            return f
    return None

lines = []
bad_calc = 0
missing = 0
for sec, what, n, d, den, shown in rows:
    v = 100.0 * n / d
    ok = abs(v - shown) <= 0.06 if shown < 100 else abs(v - shown) <= 0.1
    f = found(shown)
    if not ok:
        bad_calc += 1
    if f is None:
        missing += 1
    lines.append(f"| {sec} | {what} | {n:,} / {d:,} | {den} | {v:.2f}% | {shown}% | {'一致' if ok else '不一致'} | {f if f else '成稿文字中未检索到'} |")

out = []
out.append("")
out.append("## 补五：分母扫描明细（R306，脚本 `an_a53_scan_to_md.py`，读 `an_a52_denominator_scan.py` 的行并检索成稿 HTML 文字）")
out.append("")
out.append(f"共 {len(rows)} 行：复算与记录值不一致 {bad_calc} 行；成稿文字中检索不到该数值（含 2 位、1 位、整数三种写法）{missing} 行。「记录值」来自 an_a52 脚本内手抄的常量，「成稿中的写法」是在成稿 HTML 去标签文字中实际检索到的写法，二者相互独立。")
out.append("")
out.append("| 节 | 说法 | 分子 / 分母 | 分母含义 | 复算 | 记录值 | 复算对比 | 成稿中的写法 |")
out.append("|---|---|---|---|---:|---:|---|---|")
out.extend(lines)
out.append("")
p = base + "分析/A49_阶段2自查.md"
cur = open(p, encoding="utf-8").read()
if "## 补五：分母扫描明细" in cur:
    cur = cur.split("\n## 补五：分母扫描明细")[0].rstrip("\n") + "\n"
open(p, "w", encoding="utf-8").write(cur + "\n".join(out))
print("rows", len(rows), "bad_calc", bad_calc, "missing_in_html", missing)
for l in lines:
    if "未检索到" in l or "不一致" in l:
        print(l)
