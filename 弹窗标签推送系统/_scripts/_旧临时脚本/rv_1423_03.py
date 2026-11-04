import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p, data_only=True)
ws = wb['排序明细']
n = 0
for r in ws.iter_rows(max_col=12, values_only=True):
    v = [str(c)[:120] for c in r if c is not None]
    if v:
        print(' | '.join(v))
        n += 1
    if n > 80:
        break
