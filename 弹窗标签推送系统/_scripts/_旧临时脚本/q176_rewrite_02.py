# Q176：02 开头「按玩家看」「规则全表」改为「选一类玩家，看改前 / 改后」写法
# 备份 -> 替换 -> 自检。只改组织方式，规则、对象、弹出数、排序、上限、上线条件不动（约束 118、119）
import re, shutil, os, sys

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
SRC = BASE + '支撑文件/02_弹窗分人群定制方案.html'
BAK = BASE + '_versions/02_pre_Q176.html'

if os.path.exists(BAK):
    print('备份已存在，说明已跑过；为避免重复改写，停止')
    sys.exit(0)
shutil.copyfile(SRC, BAK)
html = open(BAK, encoding='utf-8').read()

# ---------- 取出旧的两节，原样复用 ----------
a = html.index('  <section>\n    <h2 class="sec">按玩家看</h2>')
b = html.index('  <section>\n    <h2 class="sec">规则全表</h2>')
c = html.index('  <section>\n    <h2 class="sec">决策项</h2>')
old_players = html[a:b]
old_rules = html[b:c]

# 7 行表（原样），只按 R241 补三处括注
tbl_start = old_players.index('<div class="tablewrap"><table>')
tbl_end = old_players.index('</table></div>', tbl_start) + len('</table></div>')
table7 = old_players[tbl_start:tbl_end]
foot7 = old_players[tbl_end:old_players.index('</section>')].strip()

t = table7
# 新增·普卡银卡：11 → 10（储值下滑 31 → 30）
old1 = '<td class="n">11 → <b>10</b></td></tr>'
assert t.count(old1) == 1
t = t.replace(old1, '<td class="n">11 → <b>10</b><br><span class="mini">（储值下滑 31 → 30）</span></td></tr>')
# 回流、其余·普卡银卡：11 → 11（储值下滑 31 → 31）
old2 = '<td class="n">11 → 11</td></tr>'
assert t.count(old2) == 2
t = t.replace(old2, '<td class="n">11 → 11<br><span class="mini">（储值下滑 31 → 31）</span></td></tr>')
table7_new = t

# 规则全表：只改标题
rules_new = old_rules.replace('<h2 class="sec">规则全表</h2>', '<h2 class="sec">规则全表（每条规则的完整顺序与上线条件）</h2>')
assert rules_new != old_rules

# ---------- 新增样式 ----------
css = """
  /* Q176：选一类玩家，看改前 / 改后（前缀 pk-，不影响其他部分） */
  .pk-pick{background:var(--surface); border:1px solid var(--line); padding:14px 16px; margin:0 0 14px;}
  .pk-row{display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:0 0 8px;}
  .pk-row:last-child{margin:0;}
  .pk-row .pk-k{width:6em; font-size:13.5px; color:var(--muted);}
  .pk-opt{all:unset; cursor:pointer; padding:5px 14px; border:1px solid var(--line); border-radius:16px; font-size:14px; background:var(--surface); color:var(--ink);}
  .pk-opt.on{background:var(--ink); color:var(--surface); border-color:var(--ink);}
  .pk-opt:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}
  .pk-cmp{display:grid; grid-template-columns:1fr 1fr; gap:12px;}
  .pk-col{background:var(--surface); border:1px solid var(--line); padding:14px 16px;}
  .pk-col h3{font-size:14px; margin:0 0 10px; color:var(--muted); font-weight:650;}
  .pk-col.after h3{color:var(--ok);}
  .pk-pop{display:flex; gap:10px; align-items:flex-start; margin:0 0 8px; padding:8px 10px; border-radius:4px; background:var(--surface-2);}
  .pk-pop .pk-n{flex:none; width:22px; height:22px; border-radius:50%; background:var(--ink); color:var(--surface); font-size:12px; display:flex; align-items:center; justify-content:center; font-weight:700; margin-top:1px;}
  .pk-pop b{display:block; font-size:14.5px;}
  .pk-pop span.pk-s{font-size:12.5px; color:var(--muted);}
  .pk-pop.chg{background:var(--ok-soft);} .pk-pop.chg .pk-n{background:var(--ok); color:#fff;}
  .pk-total{font-size:14px; margin:10px 0 0; padding-top:8px; border-top:1px solid var(--line);} .pk-total b{font-size:18px;}
  .pk-why{background:var(--warn-soft); padding:10px 14px; margin:12px 0 0; font-size:14px; border-radius:3px;}
  @media (max-width:620px){ .pk-cmp{grid-template-columns:1fr;} }
"""
assert html.count('  :focus-visible{outline:2px solid var(--accent); outline-offset:2px;}') == 1
html_css = html.replace('  :focus-visible{outline:2px solid var(--accent); outline-offset:2px;}',
                        css.rstrip('\n') + '\n\n  :focus-visible{outline:2px solid var(--accent); outline-offset:2px;}')

# ---------- 新增部分 ----------
new_sections = '''  <section>
    <h2 class="sec">选一类玩家，看进大厅会弹出什么</h2>
    <p class="sub">左边是现在，右边是改完以后，绿色是变了的。对比前提：当天第一次进大厅、各活动都在开放期；礼包位弹的是排最前、而且这个玩家还能买的那一个。</p>
    <noscript><p class="sub">脚本未运行时，请看下方折叠的「逐类明细」，内容相同。</p></noscript>
    <div class="pk-pick">
      <div class="pk-row"><span class="pk-k">身份</span><span id="pk-g1"></span></div>
      <div class="pk-row"><span class="pk-k">卡别</span><span id="pk-g2"></span></div>
      <div class="pk-row"><span class="pk-k">储值下滑</span><span id="pk-g3"></span></div>
      <div class="pk-row"><span class="pk-k">时机</span><span id="pk-g4"></span></div>
    </div>
    <div class="pk-cmp">
      <div class="pk-col"><h3>现在</h3><div id="pk-before"></div></div>
      <div class="pk-col after"><h3>改完以后</h3><div id="pk-after"></div></div>
    </div>
    <div class="pk-why" id="pk-why"></div>
  </section>

  <section>
    <h2 class="sec">9 条规则一览</h2>
    <p class="sub">改完以后一共 9 条规则，含没有改的 ID10、ID11。</p>
    <div class="tablewrap"><table>
      <thead><tr><th>规则</th><th>给谁</th><th class="n">弹几个</th><th>改动</th></tr></thead>
      <tbody>
        <tr><td>新增用户活动弹窗</td><td>新增</td><td class="n">1</td><td><span class="st snew">新建</span></td></tr>
        <tr><td>回流用户活动弹窗</td><td>回流</td><td class="n">2</td><td><span class="st snew">新建</span></td></tr>
        <tr><td>ID5 活动类弹窗</td><td>其余玩家（非新增、非回流）</td><td class="n">2</td><td><span class="st smod">改对象</span></td></tr>
        <tr><td>ID6 通用弹窗</td><td>普卡、银卡</td><td class="n">1</td><td><span class="st smod">改对象</span></td></tr>
        <tr><td>通用弹窗·金卡以上</td><td>金卡以上，储值没下滑</td><td class="n">1</td><td><span class="st snew">新建</span></td></tr>
        <tr><td>高卡储值下滑</td><td>金卡以上，储值下滑</td><td class="n">1</td><td><span class="st snew">新建</span></td></tr>
        <tr><td>ID10 普卡储值衰退 50%</td><td>普卡，储值下滑</td><td class="n">1</td><td><span class="st ssame">不变</span></td></tr>
        <tr><td>ID11 银卡储值衰退 50%</td><td>银卡，储值下滑</td><td class="n">1</td><td><span class="st ssame">不变</span></td></tr>
        <tr><td>ID7 破产储值弹窗</td><td>所有人，破产时</td><td class="n">1</td><td><span class="st smod">改顺序</span></td></tr>
      </tbody>
    </table></div>
    <p class="sub" style="margin-top:8px">「储值下滑」指标签「当月储值额小于上月储值额 50%」（口径见第二张卡前置条件）；「金卡以上」指金卡、白金卡、钻石卡、黑卡、至尊卡；新增、回流、其余三种身份互斥。每条规则的完整顺序与上线条件见下面的「规则全表」。</p>
    <details class="apx">
      <summary>逐类明细（含每日上限）</summary>
      <div class="body">
        <p class="sub">每类玩家改完以后，单次进大厅最多弹几个、每日活动类最多几次（都是后台规则按配置推算的上限）。</p>
        ''' + table7_new + '''
        ''' + foot7 + '''
      </div>
    </details>
  </section>

'''

script = r'''
<script>
(function(){
  var S={id:'其余',card:'普银',drop:'否',when:'进大厅'};
  var G=[['pk-g1','id',['新增','回流','其余']],['pk-g2','card',['普银','金卡以上']],['pk-g3','drop',['否','是']],['pk-g4','when',['进大厅','破产']]];
  var LBL={'普银':'普卡、银卡','金卡以上':'金卡以上'};
  var GIFT='首储礼包（没买过的人），买过就是独享礼包';
  function lobby(after){
    var L=[],gold=S.card==='金卡以上';
    if(!after||S.id==='其余'){
      (gold?['月月抽','限时挑战']:['限时挑战','卡别直升活动']).forEach(function(x){L.push({t:x,s:'ID5 活动类弹窗',c:false});});
    }else if(S.id==='新增'){
      L.push({t:'限时挑战',s:'新增用户活动弹窗 · 只弹 1 个',c:true});
    }else{
      L.push({t:'回流任务',s:'回流用户活动弹窗 · 回流任务排第 1',c:true});
      L.push({t:gold?'月月抽':'限时挑战',s:'回流用户活动弹窗',c:true});
    }
    if(after&&gold&&S.drop==='是') L.push({t:'储值下滑相关礼包',s:'高卡储值下滑 · 运营指定的一项礼包',c:true});
    else L.push({t:GIFT,s:after&&gold?'通用弹窗·金卡以上（内容和原来一样）':(gold?'ID6 通用弹窗':(after?'ID6 通用弹窗（对象改为排除金卡以上，内容不变）':'ID6 通用弹窗')),c:false});
    if(!gold&&S.drop==='是') L.push({t:'每日补给计划',s:'ID10、ID11 储值衰退 50% · 现状就有',c:false});
    return L;
  }
  function bankrupt(after){
    return [{t:after?'首储礼包 → 破产礼包 → 独享礼包 …':'首储礼包 → 独享礼包 → 破产礼包 …',s:'ID7 破产储值弹窗'+(after?' · 破产礼包提到独享礼包前面':''),c:after}];
  }
  function render(el,L){
    document.getElementById(el).innerHTML=L.map(function(p,i){
      return '<div class="pk-pop'+(p.c?' chg':'')+'"><div class="pk-n">'+(i+1)+'</div><div><b>'+p.t+'</b><span class="pk-s">'+p.s+'</span></div></div>';
    }).join('')+'<div class="pk-total">一次最多弹 <b>'+L.length+'</b> 个</div>';
  }
  function draw(){
    var bank=S.when==='破产',gold=S.card==='金卡以上';
    render('pk-before',bank?bankrupt(false):lobby(false));
    render('pk-after',bank?bankrupt(true):lobby(true));
    var w;
    if(bank) w='只有买过首储礼包、独享礼包还能买的人会感觉到变化：破产时先看到破产礼包。前提是破产礼包比独享礼包便宜，否则这一条不上。';
    else if(S.id==='新增') w='新增用户的活动弹窗从 2 个减到 1 个，第一次进大厅少一个打扰；去掉了他们多半参加不了的月月抽和回流任务。';
    else if(S.id==='回流') w='回流用户最先看到回流任务（原来排第 7，常常轮不到）。数量不变。';
    else w='其余玩家的活动弹窗不变。';
    if(!bank&&gold&&S.drop==='是') w+=' 储值在下滑的高卡，礼包弹窗换成一项和储值下滑相关的礼包，之前没有任何规则照顾他们。数量不增加。';
    document.getElementById('pk-why').textContent=w;
  }
  G.forEach(function(g){
    var box=document.getElementById(g[0]);
    g[2].forEach(function(o){
      var b=document.createElement('button');
      b.type='button';b.className='pk-opt'+(S[g[1]]===o?' on':'');b.textContent=LBL[o]||o;
      b.onclick=function(){S[g[1]]=o;Array.prototype.forEach.call(box.children,function(x){x.classList.toggle('on',x===b);});draw();};
      box.appendChild(b);
    });
  });
  draw();
})();
</script>
'''

# 更正记录：加一行
log_anchor = '</tbody>\n      </table></div>\n    </div></details>\n\n    <details class="apx"><summary>五　提案的数字出处</summary>'
assert html_css.count(log_anchor) == 1
log_row = '''          <tr><td>2026-09-30</td><td>开头「按玩家看」「规则全表」；附录目录不变</td><td>「按玩家看」是 7 行 × 6 列的表、「规则全表」是 9 行 × 6 列的表，Dk 14:27 说全景仍难读：要一格一格对，看不出某一类玩家进大厅改前改后到底弹哪几个</td><td>规则结构之后依次为：「选一类玩家，看进大厅会弹出什么」（身份 × 卡别 × 储值下滑 × 时机，左现在、右改完以后，变了的标绿，每栏「一次最多弹 N 个」，一句「为什么这样改」）→「9 条规则一览」（4 列）→ 折叠框「逐类明细（含每日上限）」（原 7 行表，脚本不运行时也能读）→「规则全表（每条规则的完整顺序与上线条件）」（原表）。规则、对象、每次弹出数、排序、每日上限、上线条件一个没动；普卡银卡三行补括注：新增「11 → 10（储值下滑 31 → 30）」，回流、其余「11 → 11（储值下滑 31 → 31）」（=活动类每日上限 + ID10、ID11 每日补给计划 20，与第五张卡总量表一致）</td><td>Dk 9/30 14:27；推进计划 Q176；审查 R241</td></tr>
'''
html_log = html_css.replace(log_anchor, log_row + '        ' + log_anchor)

# ---------- 拼装：用新的两块换掉旧的「按玩家看」「规则全表」 ----------
# 原顺序：[按玩家看][规则全表][决策项...]；新顺序：[选一类][9 条规则一览+折叠明细][规则全表][决策项...]
a2 = html_log.index('  <section>\n    <h2 class="sec">按玩家看</h2>')
b2 = html_log.index('  <section>\n    <h2 class="sec">规则全表</h2>')
c2 = html_log.index('  <section>\n    <h2 class="sec">决策项</h2>')
out = html_log[:a2] + new_sections + rules_new + html_log[c2:]
# 脚本放在 </body> 前
assert out.count('</div>\n</body>') == 1
out = out.replace('</div>\n</body>', '</div>' + script + '</body>')

open(SRC, 'w', encoding='utf-8').write(out)

# ---------- 自检 ----------
res = []
def cnt(tag):
    return len(re.findall('<' + tag + r'[\s>]', out)), out.count('</' + tag + '>')
for tag in ['div', 'section', 'details', 'table', 'tr', 'ul', 'ol', 'li', 'summary', 'span', 'button', 'noscript', 'script']:
    o, c_ = cnt(tag)
    res.append((tag, o, c_, 'OK' if o == c_ else 'MISMATCH'))
for r in res: print(r)

# 规则全表：除标题外逐字一致
rules_in_out = out[out.index('  <section>\n    <h2 class="sec">规则全表'):out.index('  <section>\n    <h2 class="sec">决策项</h2>')]
print('规则全表除标题外与原版一致：', rules_in_out.replace('（每条规则的完整顺序与上线条件）', '') == old_rules)
# 7 行表：去掉三处括注后一致
back = table7_new.replace('<br><span class="mini">（储值下滑 31 → 30）</span>', '').replace('<br><span class="mini">（储值下滑 31 → 31）</span>', '')
print('7 行表去括注后与原版一致：', back == table7)
# 新增部分禁用词
newpart = new_sections + script
bad = ['本方案', '待确认', '可以上线', '分桶·处理', '处理版', '默认配法', '退路']
print('新增部分禁用词：', [w for w in bad if w in newpart])
# 弹窗名与原文可对应
names = ['月月抽', '限时挑战', '卡别直升活动', '回流任务', '每日补给计划', '首储礼包', '独享礼包', '破产礼包']
print('弹窗名在改前版本存在：', all(n in html for n in names))
# 其余部分（决策项起）不变
print('决策项之后（除更正记录一行）一致：', out.split('<h2 class="sec">决策项</h2>')[1].replace(log_row, '') == html.split('<h2 class="sec">决策项</h2>')[1])

# 尝试用 node 跑交互逻辑（若有）
import subprocess, shutil as sh, json
node = sh.which('node')
print('node：', node)
if node:
    js = script.split('<script>')[1].split('</script>')[0]
    open(BASE + '_scripts/_q176_logic.js', 'w', encoding='utf-8').write(js)
