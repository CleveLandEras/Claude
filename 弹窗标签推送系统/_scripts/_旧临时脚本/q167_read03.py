import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
print([ (c.coordinate, str(c.value)[:30]) for c in ws[4] if c.value])
for r in (5, 6, 7, 8, 9, 10, 13, 14):
    for col in 'BCDEFGHIJ':
        v = ws[f'{col}{r}'].value
        if v not in (None, ''):
            print(f'{col}{r}', '|', str(v)[:400])
    print('--')
ws = wb['提案（待主管定）']
for r in range(4, 14):
    print(r, '|', ws[f'A{r}'].value, '|', str(ws[f'B{r}'].value)[:700])
