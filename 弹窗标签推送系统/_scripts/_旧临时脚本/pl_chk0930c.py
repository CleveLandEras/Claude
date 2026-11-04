import os, re, glob
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def find(pat):
    r = glob.glob(base + pat)
    return r[0] if r else None

def text(p):
    if p.endswith('.html'):
        t = open(p, encoding='utf-8').read()
        t = re.sub(r'<[^>]+>', '', t)
        return t
    return open(p, encoding='utf-8').read()

def ctx(t, w, n=60, maxhits=8):
    out = []
    for m in re.finditer(re.escape(w), t):
        s = t[max(0, m.start()-n):m.end()+n].replace('\n', ' ')
        out.append(s)
        if len(out) >= maxhits: break
    return out

files = {
 '汇报': base + '决策汇报.html',
 '环节3': base + '环节3_方案.html',
 '02': find('支撑文件/02_*.html'),
 '04': find('支撑文件/04_*.md'),
 '05': find('支撑文件/05_*.md'),
 'A32': find('分析/A32*'),
 'A33': find('分析/A33*'),
}
print(files)
checks = {
 '汇报': ['只有 2 项', '推送条', '按 A29 重核', '「或」已上线', '依据：2 项', '依据：要新写的 SQL', '可以原样转发', '先别转发', '6 个百分点', '4 个百分点', '分桶·处理'],
 '环节3': ['只有 2 项', '推送条', '快显 0'],
 '02': ['金卡以上且储值未下滑', '12 → 32', '第 0 步'],
 '04': ['未分组时，弹窗调整的效果只能', '也没有分桶标签时'],
 '05': ['评估分母', '金卡以上且储值未下滑', '身份非新增、非回流', '非金卡以上'],
 'A32': ['押注相同', '同一押注四分档内', '+4.14', '不定'],
 'A33': ['评估分母'],
}
for k, ws in checks.items():
    p = files[k]
    if not p: print('MISSING', k); continue
    t = text(p)
    print('=====', k, os.path.basename(p))
    for w in ws:
        hits = ctx(t, w)
        print('--', w, len(re.findall(re.escape(w), t)))
        for h in hits[:4]:
            print('    ', h)

# 03 xlsx
import openpyxl
p3 = find('支撑文件/03_*.xlsx')
print('===== 03', p3)
wb = openpyxl.load_workbook(p3, data_only=True)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            if isinstance(v, str) and any(w in v for w in ['不依赖外部答复', '第 0 步', '金卡以上且储值未下滑', '谁写 SQL']):
                print(ws.title, c.coordinate, v[:300].replace('\n', ' '))
