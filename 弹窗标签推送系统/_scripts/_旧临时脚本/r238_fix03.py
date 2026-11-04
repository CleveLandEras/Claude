import openpyxl

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
v = ws['A2'].value
anchor = '各多复制 1 条规则作处理版；'
add = '第 0 步查出带排除的对象不能用时，各卡对照版的对象都改用互补标签「分桶·对照」（与「分桶·处理」同一次分桶生成，共用 1 个，见 K5）；'
assert anchor in v, 'anchor missing'
assert add not in v, 'already applied'
ws['A2'].value = v.replace(anchor, anchor + add, 1)
wb.save(p)
print('ok')
