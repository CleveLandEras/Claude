"""Q112 定位 2：各文件更正记录 / 修改说明的位置与最后一条（只读）。"""
import os
import openpyxl
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
files = ['环节3_方案.html', '分析/A26_方案池.md', '分析/A28_标签取舍.md', '分析/A31_决策点选项.md',
         '支撑文件/02_弹窗分人群定制方案.html']
for f in files:
    p = os.path.join(BASE, f)
    lines = open(p, encoding='utf-8').read().split('\n')
    print('=' * 50, f)
    for i, l in enumerate(lines, 1):
        if any(k in l for k in ('更正记录', '修改说明', '修改记录')):
            print(f'  L{i}: {l[:160]}')
    # 最后 12 行里带 <tr><td> 数字的
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s.startswith('<tr><td>') and s[8:10].strip().rstrip('<').isdigit():
            last = (i, s[:200])
    try:
        print('  最后编号行', last)
    except NameError:
        pass
    last = None
wb = openpyxl.load_workbook(os.path.join(BASE, '支撑文件/03_弹窗配置单.xlsx'))
ws = wb['更正记录']
print('03 更正记录 max_row', ws.max_row, 'max_col', ws.max_column)
for r in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
    print('  ', [str(x)[:50] if x is not None else None for x in r])
