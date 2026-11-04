import re, openpyxl

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def cells(row_html):
    out = []
    for m in re.finditer(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S):
        out.append(m.group(1))
    return out

def strip(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'[ \t]+', ' ', s).strip()

def first_line(s):
    # 单元格里第一个 <br> 之前
    return strip(re.split(r'<br\s*/?>', s)[0])

def table_rows(html, start_marker, end_marker='</table>'):
    seg = html.split(start_marker, 1)[1].split(end_marker, 1)[0]
    rows = re.findall(r'<tr>(.*?)</tr>', seg, re.S)
    return [cells(r) for r in rows if '<td' in r]

h02 = open(BASE + '支撑文件/02_弹窗分人群定制方案.html', encoding='utf-8').read()
href = open(BASE + '简报/弹窗规则全景.html', encoding='utf-8').read()

r02 = table_rows(h02, '<h2 class="sec">规则全表</h2>')
rref = table_rows(href, '<h2>每条规则的对象、弹几个、完整内容顺序</h2>')
assert len(r02) == 9 and len(rref) == 9, (len(r02), len(rref))

def key(c0):
    return strip(re.split(r'<br', c0)[0])

d02 = {key(r[0]): r for r in r02}
dref = {key(r[0]): r for r in rref}
assert set(d02) == set(dref), (set(d02) ^ set(dref))

print('== 02 规则全表 ↔ 参考稿 规则全表（按规则、字段逐项）')
def norm(s):
    return strip(s).replace('\n', ' ')

def seq_main(cell):
    # 内容顺序：第一个 <br> 之前；去掉「（不变）」
    t = first_line(cell)
    return t.replace('（不变）', '')

diffs = []
for k in d02:
    a, b = d02[k], dref[k]
    fields = [('改动', norm(a[1]), norm(b[1])), ('对象', norm(a[2]), norm(b[2])), ('每次弹', norm(a[3]), norm(b[3])),
              ('顺序', seq_main(a[4]), seq_main(b[4])), ('上线条件', first_line(a[5]), first_line(b[5]))]
    for f, x, y in fields:
        ok = (x == y)
        if not ok:
            diffs.append((k, f, x, y))
print('出入项数：', len(diffs))
for k, f, x, y in diffs:
    print(' -', k, f)
    print('     02 ：', x)
    print('     参考：', y)

# ---- 03 最终规则全表 ↔ 02
wb = openpyxl.load_workbook(BASE + '支撑文件/03_弹窗配置单.xlsx')
ws = wb['最终规则全表']
r03 = {}
for r in range(5, 14):
    r03[r - 4] = [ws.cell(r, c).value for c in range(1, 11)]
order02 = ['ID5 活动类弹窗', '新增用户活动弹窗', '回流用户活动弹窗', 'ID6 通用弹窗', '通用弹窗·金卡以上', '高卡储值下滑',
           'ID10 普卡储值衰退 50%', 'ID11 银卡储值衰退 50%', 'ID7 破产储值弹窗']
ID6 = '首储礼包 → 独享礼包 → 惊喜三选一 → 限时加码礼包 → 生涯限购 → 每日礼包 → 平台限量/专属礼包'
print()
print('== 03 最终规则全表 ↔ 02 规则全表')
print('规则 | 每次弹 02/03 | 顺序 | 改动 | 对象 | 上线条件')
bad = 0
for i, k in enumerate(order02, 1):
    row = r03[i]
    a = d02[k]
    n_pop_02 = strip(a[3]); n_pop_03 = str(row[6])
    s02 = seq_main(a[4])
    s03 = str(row[7])
    if k in ('通用弹窗·金卡以上',):
        seq_ok = ('与 ID6 相同' in s02) and (ID6 in s03)
    elif k == '高卡储值下滑':
        seq_ok = ('与储值下滑相关的一项' in s02 and '与 ID6 相同' in s02 and '与储值下滑相关的一项' in s03 and ID6 in s03)
    elif k == 'ID11 银卡储值衰退 50%':
        seq_ok = (s02 == '同 ID10' and s03 == '每日补给计划')
    elif k == 'ID10 普卡储值衰退 50%':
        seq_ok = s02.startswith('每日补给计划') and s03 == '每日补给计划'
    else:
        seq_ok = (s02 == s03)
    chg_ok = strip(a[1]) == row[4]
    # 对象：人工映射（语义一致）
    obj_map = {
        'ID5 活动类弹窗': ('全部玩家，排除新增、回流', '全部玩家，排除：新增、回流'),
        '新增用户活动弹窗': ('新增', '新增'),
        '回流用户活动弹窗': ('回流', '回流'),
        'ID6 通用弹窗': ('全部玩家，排除金卡以上', '全部玩家，排除：金卡、白金卡、钻石卡、黑卡、至尊卡'),
        '通用弹窗·金卡以上': ('金卡以上，排除储值下滑', '任一满足：金卡、白金卡、钻石卡、黑卡、至尊卡；排除：当月储值额小于上月储值额 50%'),
        '高卡储值下滑': ('金卡以上且储值下滑', '全部满足：当月储值额小于上月储值额 50%；任一满足：金卡、白金卡、钻石卡、黑卡、至尊卡'),
        'ID10 普卡储值衰退 50%': ('普卡且储值下滑', '普卡 · 当月储值额小于上月储值额 50%'),
        'ID11 银卡储值衰退 50%': ('银卡且储值下滑', '银卡 · 当月储值额小于上月储值额 50%'),
        'ID7 破产储值弹窗': ('全部玩家', '全部玩家'),
    }
    e02, e03 = obj_map[k]
    obj_ok = (strip(a[2]) == e02) and (row[5] == e03)
    cond02 = first_line(a[5])
    cond03 = str(row[9])
    if cond02.startswith('第一批'):
        cond_ok = cond03.startswith('第一批')
    elif cond02.startswith('等标签条件'):
        cond_ok = cond03.startswith('等三处标签条件')
    elif cond02.startswith('等价格'):
        cond_ok = cond03.startswith('等独享礼包、破产礼包价格')
    elif cond02.startswith('无需操作'):
        cond_ok = cond03 == '无需操作'
    else:
        cond_ok = False
    flags = [n_pop_02 == n_pop_03, seq_ok, chg_ok, obj_ok, cond_ok]
    bad += flags.count(False)
    print(k, '|', '一致' if flags[0] else '出入', '|', '一致' if flags[1] else '出入', '|', '一致' if flags[2] else '出入', '|',
          '一致' if flags[3] else '出入', '|', '一致' if flags[4] else '出入')
print('02↔03 出入格数：', bad, '（共 9 行 × 5 项）')

# ---- 按玩家看 02 ↔ 参考稿
print()
print('== 02「按玩家看」↔ 参考稿「二 · 按玩家看」')
p02 = table_rows(h02, '<h2 class="sec">按玩家看</h2>')
pref = table_rows(href, '<h2>每次进大厅最多弹几个、弹哪几条</h2>')
print('行数', len(p02), len(pref))
pd = 0
for a, b in zip(p02, pref):
    for j, (x, y) in enumerate(zip(a, b)):
        if norm(x) != norm(y):
            pd += 1
            print(' - 行', norm(a[0]), '列', j, ':', norm(x), '|', norm(y))
print('出入格数：', pd)
