"""Q46 回归检查：运营 3 句在简报、决策汇报附录、00 现行版三处逐字一致；自查、推断两表的单元格文字 00 与汇报一致；汇报 pre 与按钮 id 对应。只读。"""
import html, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
brief = html.unescape(open(BASE + '简报/2026-09-28_对外问题的判断与建议.html', encoding='utf-8').read())
rep_raw = open(BASE + '决策汇报.html', encoding='utf-8').read()
rep = html.unescape(rep_raw)
zero = open(BASE + '支撑文件/00_推进记录.md', encoding='utf-8').read()


def pre(t, pid):
    m = re.search(r'<pre id="%s">(.*?)</pre>' % pid, t, re.S)
    return m.group(1) if m else None


b = pre(brief, 'm2')
r = pre(rep, 'm1')
i = zero.index('**发给运营（3 句）**')
z = zero[zero.index('```\n', i) + 4: zero.index('\n```', zero.index('```\n', i) + 4)]
print('简报 == 汇报:', b == r, '｜汇报 == 00:', r == z)
if r != z:
    print('汇报:', repr(r)); print('00  :', repr(z))

# 表格单元格
cells_rep = [html.unescape(re.sub('<[^>]+>', '', c)).strip() for c in re.findall(r'<td>(.*?)</td>', rep_raw[rep_raw.index('你自己查的 3 件'):rep_raw.index('推迟到方案环节（现在问了')])]
seg = zero[zero.index('**Dk 自查 3 件**'):zero.index('**推迟到方案环节**')]
cells_zero = []
for line in seg.split('\n'):
    if line.startswith('| ') and not line.startswith('|---') and not line.startswith('| 自查 |') and not line.startswith('| 问题 |'):
        cells_zero += [c.strip() for c in line.strip('|').split('|')]
print('表格单元格数 汇报/00:', len(cells_rep), len(cells_zero), '｜逐格一致:', cells_rep == cells_zero)
for a, c in zip(cells_rep, cells_zero):
    if a != c:
        print('  不一致:', a, '｜', c)
t1 = rep[rep.index('推迟到方案环节（现在问了也用不上）：') + len('推迟到方案环节（现在问了也用不上）：'):]
t1 = t1[:t1.index('</p>')]
t2 = zero[zero.index('**推迟到方案环节**：') + len('**推迟到方案环节**：'):]
t2 = t2[:t2.index('\n')]
print('推迟一句一致:', t1 == t2)
print('汇报 pre id:', re.findall(r'<pre id="(m\d)"', rep_raw), '按钮:', re.findall(r"cp\('(m\d)'", rep_raw))
for k in ['问题 25 d', 'VIP 名单', '待问题 7', '9-2', '9-3', '问题 24']:
    print(f'汇报出现「{k}」', rep.count(k), '次')
