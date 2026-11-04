"""Q118 自查：03 检索「降级」「A26」「去留」，规则表批次列与空格。只读，不带参数。"""
import openpyxl
P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
for w in ['降级', 'A26', '去留', '不进首期', 'R128', '待设计者裁定']:
    n = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and w in c.value:
                    n += 1
                    print(f'   {w} @ {ws.title}!{c.coordinate}: {c.value[:50]}')
    print(w, n)
ws = wb['规则']
for r in range(5, 14):
    empty = [c for c in 'ABCDEFGHIJK' if ws[f'{c}{r}'].value in (None, '')]
    print(r, ws[f'E{r}'].value, '批次=', str(ws[f'K{r}'].value)[:14], '空格列', empty)
