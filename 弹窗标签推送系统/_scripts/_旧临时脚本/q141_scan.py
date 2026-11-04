"""Q141 只读扫描：在目标交付文件里列出约束 87 的说法所在行（HTML/MD 按行号，xlsx 按单元格）。不带参数运行。"""
import os, re
import openpyxl
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
terms = ['原样转发', '可以转发', '可转发', '可交研发', '可交数据组', '可以上线', '今天就能发', '可以直接交', '已可交数据组', '可直接交', '可原样', '可以发给', '可交运营', '直接发']
files = ['决策汇报.html', '环节1_现状盘点.html', '环节2_问题诊断.html', '环节3_方案.html',
         '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/03_弹窗配置单.xlsx',
         '支撑文件/04_弹窗功能缺口需求.html', '支撑文件/05_标签需求文档.html', '支撑文件/07_推送需求文档.html',
         '支撑文件/08_埋点与评估指标.html', '支撑文件/09_数据需求清单.xlsx']
sd = os.path.join(BASE, '支撑文件')
real = sorted(os.listdir(sd))
print('支撑文件目录：', real)
files = [f for f in files if os.path.exists(os.path.join(BASE, f))]
extra = [os.path.join('支撑文件', n) for n in real if n[:2] in ('04', '05', '07', '08', '09') and os.path.join('支撑文件', n) not in files]
files += extra
for f in files:
    p = os.path.join(BASE, f)
    print('=' * 50, f)
    if f.endswith('.xlsx'):
        wb = openpyxl.load_workbook(p)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str):
                        for t in terms:
                            if t in c.value:
                                i = c.value.find(t)
                                print(f'  [{ws.title}!{c.coordinate}] [{t}] …{c.value[max(0,i-60):i+60]}…'.replace('\n', ' '))
    else:
        for n, line in enumerate(open(p, encoding='utf-8'), 1):
            for t in terms:
                if t in line:
                    i = line.find(t)
                    print(f'  L{n} [{t}] …{line[max(0,i-70):i+70].strip()}…')
