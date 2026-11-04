# -*- coding: utf-8 -*-
"""Q154 补：03 新增行名称改为含「ID5 处理版」字样（便于检索与运营对照）。不带参数；可重复运行。"""
import openpyxl
p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/03_弹窗配置单.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['规则']
for r in range(5, 20):
    v = ws.cell(r, 5).value
    if isinstance(v, str) and v.startswith('活动类弹窗·处理版'):
        ws.cell(r, 5).value = 'ID5 处理版（复制 ID5 的活动类弹窗）'
        print('已改第', r, '行')
wb.save(p)
hits = [(w.title, c.coordinate) for w in wb.worksheets for row in w.iter_rows() for c in row if isinstance(c.value, str) and 'ID5 处理版' in c.value]
print(hits)
