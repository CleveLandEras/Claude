#!/usr/bin/env python3
# 只读：打印 02 开头到「决策项」之前的纯文本，以及各文件指向 02 锚点的链接
import re, os, glob
root = "/Users/decheng.huang/claude/弹窗标签推送系统/"
s = open(root + "支撑文件/02_弹窗分人群定制方案.html", encoding="utf-8").read()
body = re.sub(r"<style.*?</style>", "", s, flags=re.S)
i = body.find("决策项")
txt = re.sub(r"<[^>]+>", " ", body[:i])
print(re.sub(r"\s+", " ", txt)[:3000])
print("---- 02 内 id ----")
print(sorted(set(re.findall(r'id="([^"]+)"', s))))
print("---- 其他文件指向 02 的链接 ----")
for f in glob.glob(root + "**/*.*", recursive=True):
    if "归档" in f or "_versions" in f or not f.endswith((".html", ".md")):
        continue
    try:
        t = open(f, encoding="utf-8").read()
    except Exception:
        continue
    hits = set(re.findall(r'02_弹窗分人群定制方案\.html(#[^")\s]*)?', t))
    if hits:
        print(f.replace(root, ""), sorted(hits)[:12])
