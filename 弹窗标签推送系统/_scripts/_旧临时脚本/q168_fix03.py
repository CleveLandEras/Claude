import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
mark = '（判读日 = 队列最后一日 + 13 日）'
for r in (5, 6, 7):
    v = ws[f'L{r}'].value
    if mark in v:
        print(f'L{r} 已含，跳过')
        continue
    assert v.startswith('第一张卡｜'), v[:20]
    ws[f'L{r}'] = '第一张卡' + mark + v[len('第一张卡'):]

wc = wb['更正记录']
old = '；L 列没有写「过 →」「看不出 →」去向与判读时点，按设计卡未补'
new = '；L5–L7 序号 1–3 补「（判读日 = 队列最后一日 + 13 日）」（推进计划 Q168）；L 列没有写「过 →」「看不出 →」去向，按设计卡未补'
done = False
for r in range(2, wc.max_row + 1):
    v = str(wc.cell(r, 4).value or '')
    if 'Q166' in str(wc.cell(r, 5).value) and old in v:
        wc.cell(r, 4).value = v.replace(old, new)
        done = True
print('更正记录改写', done)
wb.save(p)

wb2 = openpyxl.load_workbook(p)
w = wb2['规则']
for r in (5, 6, 7):
    print(f'L{r}', w[f'L{r}'].value[:70])
print('K5 含分桶·对照', '分桶·对照' in w['K5'].value)
print('更正记录行数', wb2['更正记录'].max_row)
