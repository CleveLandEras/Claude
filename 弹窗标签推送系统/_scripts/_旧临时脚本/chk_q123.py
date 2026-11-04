"""Q123 自查：08、09 检索「首期停用」「降级」「A26」；汇报里的「首期停用」。只读，不带参数。"""
import re, openpyxl
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
t8 = open(B + '支撑文件/08_弹窗效果评估方案.md', encoding='utf-8').read()
i = t8.index('## 更正记录') if '## 更正记录' in t8 else len(t8)
body8 = t8[:i]
wb = openpyxl.load_workbook(B + '支撑文件/09_取数需求_上线前基线.xlsx')
for w in ['首期停用', '降级', 'A26']:
    n8 = body8.count(w)
    n9 = 0
    for ws in wb.worksheets:
        if ws.title == '更正记录':
            continue
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and w in c.value:
                    n9 += 1
                    print('  09', ws.title, c.coordinate, c.value[:60])
    print(f'{w}: 08 正文 {n8}；09（不含更正记录）{n9}')
    for m in re.finditer(re.escape(w), body8):
        print('  08 …', body8[max(0, m.start() - 30): m.start() + 40].replace('\n', ' '))
g = open(B + '决策汇报.html', encoding='utf-8').read()
for w in ['首期停用']:
    idx = [m.start() for m in re.finditer(w, g)]
    print(f'汇报 {w}: {len(idx)} 处')
    for k in idx:
        print('  …', re.sub(r'<[^>]+>', '', g[max(0, k - 60): k + 60]).replace('\n', ' '))
