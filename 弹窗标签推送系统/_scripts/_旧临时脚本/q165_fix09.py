"""Q165：09 表14 说明里「区分保留延长与换便宜一级」改为终判写法（约束 107）；更正记录一行。不带参数；可重复运行。"""
import openpyxl
from copy import copy

P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/09_取数需求_上线前基线.xlsx'
wb = openpyxl.load_workbook(P)
done = []
ws = wb['表14 提案乙过程指标']
v = ws['B5'].value or ''
if '区分保留延长与换便宜一级的礼包' in v:
    ws['B5'].value = v.replace('区分保留延长与换便宜一级的礼包', '区分保留（第 1 期末延长；合并 3 期终判继续运行，判读期结束）与换便宜一级的礼包')
    done.append('表14 B5')
cw = wb['更正记录']
if not any((cw.cell(r, 5).value or '').startswith('Q165') for r in range(1, cw.max_row + 1)):
    r = cw.max_row + 1
    row = ('2026-09-30', '表14 用途说明',
           '「区分保留延长与换便宜一级的礼包」：02 附录六写合并 3 期终判之后不再延长，这里写延长，读者会读出两种判读期',
           '「区分保留（第 1 期末延长；合并 3 期终判继续运行，判读期结束）与换便宜一级的礼包」；条件与去向不变',
           'Q165；约束 107')
    for i, x in enumerate(row, start=1):
        c = cw.cell(row=r, column=i)
        c.value = x
        c._style = copy(cw.cell(row=r - 1, column=i)._style)
    done.append('更正记录一行')
wb.save(P)
print('已改：', done or '无')
print(ws['B5'].value)
for n in ['表1', '表2', '表3', '表5', '表6', '表7', '表13', '表14', '表15', '表16']:
    print(n, '在' if any(s.startswith(n + ' ') for s in wb.sheetnames) else '缺！')
