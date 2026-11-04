#!/usr/bin/env python3
# 只读：列出 02 的标题结构与各节字数，03 的工作表名与行数
import re, os
base = "/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/"
p = base + "02_弹窗分人群定制方案.html"
s = open(p, encoding="utf-8").read()
print("02 总字符", len(s))
body = re.sub(r"<style.*?</style>", "", s, flags=re.S)
pos = [(m.start(), m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()) for m in re.finditer(r"<(h[1-4])[^>]*>(.*?)</\1>", body, flags=re.S)]
for i, (st, tag, txt) in enumerate(pos):
    end = pos[i + 1][0] if i + 1 < len(pos) else len(body)
    seg = re.sub(r"<[^>]+>", "", body[st:end])
    print(tag, len(seg), txt[:80])
for m in re.finditer(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>", body, flags=re.S):
    print("details:", re.sub(r"<[^>]+>", "", m.group(1)).strip()[:80])
try:
    import openpyxl
    wb = openpyxl.load_workbook(base + "03_弹窗配置单.xlsx")
    for ws in wb.worksheets:
        print("03 sheet", ws.title, ws.max_row, ws.max_column)
    ws = wb.worksheets[0]
    for r in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 40), values_only=True):
        vals = [str(v)[:40] for v in r[:12] if v is not None]
        if vals:
            print(" | ".join(vals))
except Exception as e:
    print("03 读取失败", e)
