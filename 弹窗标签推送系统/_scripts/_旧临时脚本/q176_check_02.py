# Q176 自检：决策项之后是否只多了更正记录一行；用 Python 复刻交互逻辑，对照 02 改前「按玩家看」7 行表的弹出数
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
new = open(BASE + '支撑文件/02_弹窗分人群定制方案.html', encoding='utf-8').read()
old = open(BASE + '_versions/02_pre_Q176.html', encoding='utf-8').read()

k = '<h2 class="sec">决策项</h2>'
n_tail = re.sub(r'\s+', '', re.sub(r'<script>.*?</script>', '', new.split(k)[1], flags=re.S))
o_tail = re.sub(r'\s+', '', old.split(k)[1])
row_start = new.index('<tr><td>2026-09-30</td><td>开头「按玩家看」「规则全表」；附录目录不变')
row_end = new.index('</tr>', row_start) + 5
row = re.sub(r'\s+', '', new[row_start:row_end])
print('决策项之后除新增更正记录一行外一致：', n_tail.replace(row, '') == o_tail)

# 复刻交互逻辑（与页面 JS 一一对应），输出 13 种组合
def lobby(idn, card, drop, after):
    gold = card == '金卡以上'
    L = []
    if (not after) or idn == '其余':
        L += ['月月抽', '限时挑战'] if gold else ['限时挑战', '卡别直升活动']
    elif idn == '新增':
        L += ['限时挑战']
    else:
        L += ['回流任务', '月月抽' if gold else '限时挑战']
    if after and gold and drop == '是':
        L.append('储值下滑相关礼包')
    else:
        L.append('首储礼包')
    if (not gold) and drop == '是':
        L.append('每日补给计划')
    return L

# 02 改前「按玩家看」：单次进大厅 改前 → 改后（普银储值下滑另列）
exp = {
    ('新增', '普银', '否'): (3, 2), ('新增', '普银', '是'): (4, 3),
    ('新增', '金卡以上', '否'): (3, 2), ('新增', '金卡以上', '是'): (3, 2),
    ('回流', '普银', '否'): (3, 3), ('回流', '普银', '是'): (4, 4),
    ('回流', '金卡以上', '否'): (3, 3), ('回流', '金卡以上', '是'): (3, 3),
    ('其余', '普银', '否'): (3, 3), ('其余', '普银', '是'): (4, 4),
    ('其余', '金卡以上', '否'): (3, 3), ('其余', '金卡以上', '是'): (3, 3),
}
bad = 0
for (i, c, d), (eb, ea) in exp.items():
    b, a = len(lobby(i, c, d, False)), len(lobby(i, c, d, True))
    ok = (b, a) == (eb, ea)
    bad += (not ok)
    print(i, c, '下滑' + d, '现在', b, '改后', a, '表内', eb, ea, 'OK' if ok else '不一致')
print('破产：1 → 1（表内 1 → 1），不一致组合数：', bad, '，共', len(exp) + 1, '种')
