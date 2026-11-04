"""执行者用（Q91）：打印 03 各表全部单元格；02 的标题行与含「月月抽」「跳过」「12」「弹出」的行；04 的标题行。只读，不带参数。"""
import os
import re
import sys
from openpyxl import load_workbook
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wb = load_workbook(os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx'))
for s in wb.worksheets:
    print('=' * 40, s.title, s.max_row, 'x', s.max_column, '合并', list(s.merged_cells.ranges)[:10])
    for row in s.iter_rows():
        v = [f'{c.coordinate}={c.value}' for c in row if c.value is not None]
        if v:
            print('  ' + ' | '.join(v)[:600])
L = open(os.path.join(BASE, '支撑文件', '02_弹窗分人群定制方案.html'), encoding='utf-8').read().split('\n')
print('=' * 40, '02 行数', len(L))
for i, l in enumerate(L, 1):
    s = re.sub(r'<[^>]+>', '', l).strip()
    if re.search(r'<h[1-4]', l) or 'class="notice' in l:
        print(f'{i} H: {s[:150]}')
for i, l in enumerate(L, 1):
    s = re.sub(r'<[^>]+>', '', l).strip()
    if any(k in s for k in ['跳过月月抽', '不可参与', '每日最多', '弹出数', '次/日', '单次进大厅']):
        print(f'{i} K: {s[:220]}')
M = open(os.path.join(BASE, '支撑文件', '04_弹窗功能缺口需求.md'), encoding='utf-8').read().split('\n')
print('=' * 40, '04 行数', len(M))
for i, l in enumerate(M, 1):
    if l.startswith('#') or '功能' in l[:12]:
        print(i, l[:160])
