import openpyxl, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
wb = openpyxl.load_workbook(BASE + '支撑文件/09_取数需求_上线前基线.xlsx', data_only=True)
print(wb.sheetnames)
n = 0
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if isinstance(v, str) and re.search(r'待确认|待核对|快照|无按日|埋点|购买入口|表名|不可得', v):
                print(f'[{ws.title}!{c.coordinate}]', v[:260].replace('\n', ' '))
                n += 1
print('命中格数', n)
