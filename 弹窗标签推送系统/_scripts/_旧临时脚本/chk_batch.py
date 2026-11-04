"""检索「一次生成」「不刷新」「不依赖外部答复」「第 0 步」在汇报、02、03、08、09、A29、A31、05 中的位置。只读，不带参数。"""
import glob
import re
import openpyxl

B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = [B + '决策汇报.html', B + '支撑文件/02_弹窗分人群定制方案.html', B + '支撑文件/08_弹窗效果评估方案.md', B + '支撑文件/05_标签需求.md',
         B + '分析/A29_评估与可检测幅度.md', B + '分析/A31_决策点选项.md', B + '分析/A33_人群圈选与交集.md', B + '支撑文件/C2_新标签脚本草稿.md']
words = ['一次生成', '不刷新', '不依赖外部答复', '第 0 步']
for f in files:
    t = open(f, encoding='utf-8').read()
    for w in words:
        for m in re.finditer(re.escape(w), t):
            print(f.replace(B, ''), '|', w, '|', re.sub(r'<[^>]+>', '', t[max(0, m.start() - 40): m.start() + 50]).replace('\n', ' '))
for f in [B + '支撑文件/03_弹窗配置单.xlsx', B + '支撑文件/09_取数需求_上线前基线.xlsx']:
    wb = openpyxl.load_workbook(f)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    for w in words + ['分组']:
                        if w in c.value and (w != '分组' or ws.title == '通用口径'):
                            print(f.replace(B, ''), ws.title, c.coordinate, '|', w, '|', c.value[:70])
