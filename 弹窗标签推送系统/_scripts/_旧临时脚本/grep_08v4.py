import os
D = "/Users/decheng.huang/claude/弹窗标签推送系统/"
KEYS = ["快照", "留存", "全程开放", "本指标", "本脚本", "本方案"]
for f in ["02_弹窗分人群定制方案_迭代稿.html", "08_弹窗效果评估方案.md", "C1_卡点解锁优先级.md", "C2_新标签脚本草稿.md", "00_推进记录_本机补充.md"]:
    with open(os.path.join(D, f), encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            for k in KEYS:
                if k in line:
                    print(f, i, k, line.strip()[:160])
                    break
from openpyxl import load_workbook
wb = load_workbook(D + "09_取数需求_上线前基线.xlsx")
for s in wb.worksheets:
    for row in s.iter_rows():
        for c in row:
            if isinstance(c.value, str) and any(k in c.value for k in KEYS):
                print("09", s.title, c.coordinate, c.value[:160])
