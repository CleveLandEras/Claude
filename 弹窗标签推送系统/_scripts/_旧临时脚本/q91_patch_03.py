"""Q91 补丁：03 规则表 K8 措辞改清楚（「新增第 12 行」易误读为新增人群）。不带参数。"""
import os
from openpyxl import load_workbook
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, '支撑文件', '03_弹窗配置单.xlsx')
wb = load_workbook(P)
ws = wb['规则']
ws['K8'].value = '不变；序号 8（N1，在场高卡储值弹窗）上线时，本规则对象改为普卡、银卡两条规则，避免高卡同时命中多弹 1 个'
wb.save(P)
print(load_workbook(P)['规则']['K8'].value)
