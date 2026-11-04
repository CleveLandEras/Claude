import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
p = base + '决策汇报.html'
s = open(p, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    if n != cnt:
        raise SystemExit('命中 %d 次（要 %d）：%s' % (n, cnt, old[:60]))
    s = s.replace(old, new)

CAP = '能力线（04、05、07 与数据能力）：优先级按能力线逻辑链重排（待做，排在 02、03 验收之后）'

# 0 第五节标题
rep('<h2>要决定 10 件：先定方案稿与配置单直接要用的 4 件（第 14、15、16、6 件），再看提案与研发排期（主管定），最后定上线后的标签与评估；多数推荐是条件式，四样外部答复到了按各件的判法收成一句</h2>',
    '<h2>要决定 10 件，分两组：方案线的先定（第 14、15、16、6 件，再是提案甲乙丙、上线后对照与承诺口径），能力线的（研发三份需求、标签、后台实验分流）优先级按能力线逻辑链重排，排在 02、03 验收之后；多数推荐是条件式，四样外部答复到了按各件的判法收成一句</h2>')

# 1 「你要定的事」列表
i = s.find('<div class="panel" id="to-me">')
j = s.find('</div>', i)
blk = s[i:j]
lis = re.findall(r'      <li>.*?</li>\n', blk, re.S)
assert len(lis) == 8, len(lis)
def li(key):
    for x in lis:
        if key in x:
            return x
    raise SystemExit('没找到 li ' + key)
plan_li = [li('#d14'), li('#d15'), li('#d16'), li('#d6'), li('#d1"'), li('#d11'), li('#d12')]
cap_li = [li('#d9')]
# 承诺口径一件加注
plan_li[-1] = plan_li[-1].replace('不用等。</li>', '不用等；口径按验证计划改写中（Q149）。</li>')
new_blk = ('<div class="panel" id="to-me">\n'
           '    <h3>你要定的事：每件一行（推荐、因为、等什么）；分两组，方案线的在前，前四件是方案稿和配置单直接要用的</h3>\n'
           '    <p class="small" style="margin:0 0 4px"><b>方案线（02、03、08、09；先定）</b></p>\n'
           '    <ol style="margin:0;padding-left:1.3em;font-size:14px">\n' + ''.join(plan_li) + '    </ol>\n'
           '    <p class="small" style="margin:10px 0 4px"><b>' + CAP + '</b>（第 5、8 件与 11③ 属主管定，见下表）</p>\n'
           '    <ol start="8" style="margin:0;padding-left:1.3em;font-size:14px">\n' + ''.join(cap_li) + '    </ol>\n  ')
s = s[:i] + new_blk + s[j:]

# 2 「要主管定」表
i = s.find('<h3>要主管定（主管只读首屏和这张表就能拍板）</h3>')
t0 = s.find('<table class="prog">', i)
t1 = s.find('</table>', t0)
tab = s[t0:t1]
lines = tab.split('\n')
head = lines[0] + '\n' + lines[1]
rows = [x for x in lines[2:] if x.strip().startswith('<tr><td>')]
assert len(rows) == 5, len(rows)
def row(prefix):
    for x in rows:
        if x.strip().startswith('<tr><td>' + prefix):
            return x
    raise SystemExit('没找到行 ' + prefix)
r_a = row('拍板'); r_1 = row('1（含'); r_5 = row('5</td>'); r_8 = row('8</td>'); r_11 = row('11③')
r_5 = r_5.replace('为什么要定：这三项的效果量级算不出，却要占研发排期；推到第二期是缩减，只能作提案',
                  '为什么要定：这三项是主管原计划里弹窗「数量整体可控」的开发项；推到第二期是缩减，只能作提案，依据待重写')
r_5 = r_5.replace('「推到第二期」是提案，待主管定（<a href="#d5">第 5 件</a>）</td>',
                  '「推到第二期」是提案，待主管定（<a href="#d5">第 5 件</a>）；优先级按能力线逻辑链重排（待做）</td>')
r_8 = r_8.replace('缩减是提案，判法见（<a href="#d8">第 8 件</a>、<a href="#d78">合看表</a>）</td>',
                  '缩减是提案，依据待重写、不作推荐（<a href="#d8">第 8 件</a>、<a href="#d78">合看表</a>）；优先级按能力线逻辑链重排（待做）</td>')
r_5 = r_5.replace('待做）</td><td>—</td>', '待做）</td><td>—</td>')
grp = lambda t: '      <tr><td colspan="4"><b>' + t + '</b></td></tr>'
new_tab = head + '\n' + grp('方案线（先定）') + '\n' + r_a + '\n' + r_1 + '\n' + grp(CAP) + '\n' + r_5 + '\n' + r_8 + '\n' + r_11 + '\n    '
s = s[:t0] + new_tab + s[t1:]

# 3 「你定」表
i = s.find('<h3>你定（前四件方案稿和配置单直接要用）</h3>')
t0 = s.find('<table class="prog">', i)
t1 = s.find('</table>', t0)
tab = s[t0:t1]
lines = tab.split('\n')
head = lines[0] + '\n' + lines[1]
rows = [x for x in lines[2:] if x.strip().startswith('<tr><td>')]
assert len(rows) == 10, len(rows)
def row2(prefix):
    for x in rows:
        if x.strip().startswith('<tr><td>' + prefix + '</td>'):
            return x
    raise SystemExit('没找到行 ' + prefix)
order_plan = ['14', '15', '16', '6', '4', '11①②', '13', '12']
order_cap = ['9', '10']
r12 = row2('12').replace('为什么要定：1–3% 的提升在现有人数下测不出', '为什么要定：1–3% 的提升在现有人数下看不出，承诺口径要写成验证计划（看什么、怎么判读、下一版怎么改；Q149 改写中）')
r10 = row2('10').replace('「首期基本不交」是提案（并入', '「首期基本不交」是依据待重写的提案（并入')
r11 = row2('11①②').replace('分桶标签不用开发，但要有人写 SQL</td>', '分桶标签不用开发，但要有人写 SQL；后台实验分流开发一件在能力线组</td>')
pl = []
for k in order_plan:
    x = {'12': r12, '11①②': r11}.get(k) or row2(k)
    pl.append(x)
cp = []
for k in order_cap:
    x = {'10': r10}.get(k) or row2(k)
    cp.append(x)
new_tab = head + '\n' + grp('方案线（先定；前四件是方案稿和配置单直接要用的）') + '\n' + '\n'.join(pl) + '\n' + grp(CAP) + '\n' + '\n'.join(cp) + '\n    '
s = s[:t0] + new_tab + s[t1:]

# 4 更正记录
rep('  </table></div></div></details>\n' + '<details id="archive-v3">',
    '''      <tr><td>79</td><td>第五节标题、「你要定的事」列表、「要主管定」表、「你定」表</td><td>10 件决策事项按旧原则混排，能力线（第 5、8、9、10 件、11③）的依据含已作废的判断</td><td>按方案线、能力线分两组，方案线（第 14、15、16、6、1 含 4、11①②、13、12 件）在前；能力线组每件标「优先级按能力线逻辑链重排（待做，排在 02、03 验收之后）」；第 5、8 件「为什么要定」去掉「效果量级算不出」，第 8、10 件提案标「依据待重写」；第 12 件注明口径按验证计划改写中（Q149）</td><td>工作原则 v3 第五节；推进计划 Q150、清点第 9 项</td></tr>
  </table></div></div></details>
<details id="archive-v3">''')
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('<details'), s.count('</details>'), s.count('<div'), s.count('</div>'), s.count('<table'), s.count('</table>'), s.count('<tr>'), s.count('</tr>'))
