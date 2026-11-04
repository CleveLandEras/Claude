# 审查 2026-09-30 11:49：02 全文与 03 规则表检索（只读，只打印）
import re
R = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/'
t = re.sub(r'<[^>]+>', ' ', open(R + '02_弹窗分人群定制方案.html', encoding='utf-8').read())
t = re.sub(r'\s+', ' ', t)
for w in ['不能承诺', '不承诺', '不能用储值证明', '整体回退', '一起回到', '按分到该组', '破产位曝光', 'Dk 可改']:
    hs = [m.start() for m in re.finditer(re.escape(w), t)]
    print(f'〈{w}〉{len(hs)}')
    for h in hs[:5]:
        print('   …' + t[max(0, h - 60):h + 60] + '…')
try:
    import openpyxl
    wb = openpyxl.load_workbook(R + '03_弹窗配置单.xlsx', read_only=True)
    for ws in wb.worksheets:
        n = 0
        for row in ws.iter_rows(values_only=True):
            for v in row:
                if isinstance(v, str) and ('分桶' in v or '对照' in v):
                    n += 1
                    if n <= 8:
                        print(ws.title, '|', v[:160])
        print('工作表', ws.title, '含「分桶/对照」格数', n)
except Exception as e:
    print('03 读取失败', e)
