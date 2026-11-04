"""R231：只读。打印审查记录 R231 全文、03 规则表 K5–K14 与 G14 的现文、汇报第 17 件所在句。不改文件。"""
import openpyxl

base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t = open(base + '过程记录/审查记录.md', encoding='utf-8').read()
i = t.find('### R231')
print(t[i:i + 2600])
print('=' * 60)
wb = openpyxl.load_workbook(base + '支撑文件/03_弹窗配置单.xlsx')
print(wb.sheetnames)
ws = wb['规则']
for r in range(5, ws.max_row + 1):
    a = ws.cell(r, 1).value
    if a is None:
        continue
    print(r, '序号', a, '| G:', str(ws.cell(r, 7).value)[:160], '| K:', str(ws.cell(r, 11).value)[:900])
