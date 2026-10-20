import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
p = _ROOT + '/阶段7_方案验证.html'
s = open(p, encoding='utf-8').read()

a = s.index('<section class="sec" id="s4">')
b = s.index('</section>', a)
sec = s[a:b]

has = {1: '无', 2: '有', 3: '有', 4: '部分有', 5: '部分有', 6: '部分有', 7: '有', 8: '有', 9: '有',
       10: '有', 11: '无', 12: '无', 13: '无', 14: '部分有'}
cls = {'无': 't-con', '部分有': 't-sug', '有': 't-goal'}

sec = sec.replace('<tr><th>序</th><th>方案未覆盖的情形</th><th>类别</th><th>原因</th></tr>',
                  '<tr><th>序</th><th>方案未覆盖的情形</th><th>归类</th><th>方案内有无对应设计项</th><th>原因</th></tr>')


def rep(m):
    n = int(m.group(1))
    v = has[n]
    return m.group(0).replace('</td><td>', '</td><td>', 1)


rows = re.findall(r'<tr><td class="no">(\d+)</td>.*?</tr>', sec)
out = []
pos = 0
for m in re.finditer(r'<tr><td class="no">(\d+)</td>(.*?)</tr>', sec):
    n = int(m.group(1))
    body = m.group(2)
    # body: <td>情形</td><td>归类</td><td>原因</td>
    cells = re.findall(r'<td>.*?</td>', body)
    assert len(cells) == 3, (n, cells)
    v = has[n]
    newcell = '<td><span class="tag %s">%s</span></td>' % (cls[v], v)
    new = '<tr><td class="no">%d</td>%s%s%s%s</tr>' % (n, cells[0], cells[1], newcell, cells[2])
    out.append((m.start(), m.end(), new))
for st, en, new in reversed(out):
    sec = sec[:st] + new + sec[en:]

s = s[:a] + sec + s[b:]

s = s.replace('<h2>边界：方案未覆盖的情形 14 条，数据缺口 9 条，设计缺口只有 1 条（自助改图文没有对应设计项）</h2>',
              '<h2>边界：方案未覆盖的情形 14 条；按归类数据缺口 9 条、设计缺口 1 条，按方案内有无对应设计项，无 4 条、部分有 4 条、有 6 条</h2>')
s = s.replace('类别：设计缺口＝方案内无对应设计项；数据缺口＝缺依据数据；合规未知＝资料无合规记载；成本取舍＝设计有意收窄，留给与上级取舍。',
              '归类（作者划分）：设计缺口＝方案内无对应设计项，且不是被有意收窄；数据缺口＝缺依据数据；合规未知＝资料无合规记载；成本取舍＝设计有意收窄，留给与上级取舍。有无对应设计项（另一种口径）：有＝35 个设计项里有直接对应项；部分有＝只有相关项；无＝没有对应项。')
s = s.replace('<p class="note">设计缺口只列不补，阶段 6 不在本阶段改动；限制主要来自数据与确认，而不是设计本身的漏洞。</p>',
              '<p class="note">两种口径各自成立，差别来自归类定义：被归为数据缺口或成本取舍的情形中，第 12、13 条在方案内同样没有对应设计项。因此不据计数判断设计本身的好坏；设计缺口只列不补，阶段 6 不在本阶段改动。</p>')
s = s.replace('<span class="d">14 条，数据缺口占 9 条</span>', '<span class="d">14 条，按归类数据缺口 9；按有无设计项，无 4</span>')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
