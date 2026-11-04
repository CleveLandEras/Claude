import re
import openpyxl
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/08_弹窗效果评估方案.md', '分析/A36_验证计划.md']
kws = ['Q166 定稿中', '还在定', '保留并延长', '保留、延长', '保留，延长', '正在定', '待 Q166', '交设计者定', '交设计者（见审查',
       '÷ 曝光', '有人买', '护栏：M7', '兼护栏', '四条判读线', '人均购买人数', '购买率高于对照', '等设计者 Q160', '定稿中']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    print('==', f)
    for k in kws:
        ms = [m.start() for m in re.finditer(re.escape(k), t)]
        if ms:
            print('  ', k, len(ms))
            for p in ms[:3]:
                print('      ', t[max(0, p - 60):p + 60].replace('\n', ' '))
# 09 / 03 文本检索
for f in ['支撑文件/09_取数需求_上线前基线.xlsx', '支撑文件/03_弹窗配置单.xlsx']:
    wb = openpyxl.load_workbook(base + f)
    print('==', f)
    for ws in wb:
        if ws.title == '更正记录':
            continue
        for row in ws.iter_rows():
            for c in row:
                v = str(c.value or '')
                for k in kws:
                    if k in v:
                        print('  ', ws.title, c.coordinate, k, v[max(0, v.find(k) - 40):v.find(k) + 60])
# HTML 标签配对
for f in files[:3]:
    t = open(base + f, encoding='utf-8').read()
    for tag in ['div', 'table', 'tr', 'td', 'p', 'details', 'li', 'ul', 'section']:
        o = len(re.findall('<' + tag + r'[\s>]', t))
        c = len(re.findall('</' + tag + '>', t))
        if o != c:
            print('  标签不配对', f, tag, o, c)
print('done')
