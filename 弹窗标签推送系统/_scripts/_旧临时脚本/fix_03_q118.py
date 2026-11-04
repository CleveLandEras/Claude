"""Q118 补丁 2：03 更正记录 C2、C5 去掉「降级」「不进首期」字样（检索标准为 0）。只改这两格。不带参数。"""
import openpyxl
P = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(P)
ws = wb['更正记录']
ws['C2'].value = '「去留」列：逐行写去留判断与理由'
ws['C5'].value = '活动位三行各带一条去留标注'
wb.save(P)
print(ws['C2'].value, '|', ws['C5'].value)
