#!/usr/bin/env python3
# Q171：02 五张卡与提案乙的验证计划逐字移到附录七，卡内只留一句主指标 + 判读日。
import re, shutil, os

BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
P = BASE + '支撑文件/02_弹窗分人群定制方案.html'
BK = BASE + '_versions/02_pre_Q171.html'

txt = open(P, encoding='utf-8').read()
if not os.path.exists(BK):
    shutil.copyfile(P, BK)
orig = open(BK, encoding='utf-8').read()

pat_card = re.compile(r'<p class="fld">验证计划（通用判读规则见附录六）</p>\s*<ul>(.*?)</ul>', re.S)
pat_prop = re.compile(r'<p class="fld">提案乙的验证计划（选定后适用；通用判读规则见附录六）</p>\s*<ul>(.*?)</ul>', re.S)

cards = pat_card.findall(orig)
props = pat_prop.findall(orig)
assert len(cards) == 5, len(cards)
assert len(props) == 1, len(props)

names = ['第一张卡　活动位按玩家身份拆分', '第二张卡　潜在流失定向覆盖全部卡别', '第三张卡　潜在付费沿用储值位首储礼包',
         '第四张卡　破产位排序以破产礼包优先', '第五张卡　弹出总量按人群控制']
one_liners = [
    '<b>主指标</b>：新增用户 7 日留存、回流用户 7 日留存（各按分到该组的全部队列人数算） · <b>判读日</b>：第 1 期末与合并 3 期终判，均为该期队列最后一日 + 13 日（见附录七）',
    '<b>主指标</b>：被圈入用户观察月的人均储值（按分到该组的全部圈入者算，含没买的人） · <b>判读日</b>：第 1 期末、合并 3 期终判（见附录七）',
    '<b>性质</b>：监测项，不设处理组，没有方案效果可判；监测该人群购买首储礼包的人数占比 · <b>判读日</b>：无（见附录七）',
    '<b>主指标</b>：破产者人均储值（全部渠道，按人算区间） · <b>判读日</b>：第 1 期末、合并 3 期终判（见附录七）',
    '<b>性质</b>：配置核对，不设处理组；各人群人均每日活动类弹窗曝光与上表逐格对照 · <b>判读日</b>：每期都看（见附录七）',
]
prop_line = '<b>主指标</b>：在场高卡（去大户）的人均储值，按分到该组的全部人算，含没付费的人 · <b>判读日</b>：第 1 期末、合并 3 期终判（见附录七）'

# 1) 卡内：把验证计划块换成一句，放到「主要改动」之后（card-body 内）；details 里的验证块删除
new = txt
idx = 0
def repl_card(m):
    global idx
    idx += 1
    return ''
new = pat_card.sub(repl_card, new)
assert idx == 5
new = pat_prop.sub('', new)

# details 摘要改名
new = new.replace('<summary>前置条件、主要风险、验证计划</summary>', '<summary>前置条件、主要风险</summary>')
new = new.replace('<summary>做法、代价与风险、选项、与五张卡的关系、提案乙的验证计划</summary>',
                  '<summary>做法、代价与风险、选项、与五张卡的关系</summary>')

# 在每张卡 card-body 末尾（紧接 </div>\n      <details class="more">）插入一句
parts = new.split('      </div>\n      <details class="more"><summary>前置条件、主要风险</summary>')
assert len(parts) == 6, len(parts)
out = parts[0]
for i in range(5):
    out += ('        <p class="fld">验证计划</p>\n        <ul><li>' + one_liners[i] + '</li></ul>\n'
            '      </div>\n      <details class="more"><summary>前置条件、主要风险</summary>' + parts[i + 1])
new = out

# 提案：在「做法、代价与风险」details 之前的 card-body 里，加一句（放在依据 ul 之后）
anchor = '      </div>\n      <details class="more"><summary>做法、代价与风险、选项、与五张卡的关系</summary>'
assert new.count(anchor) == 1
new = new.replace(anchor, '        <p class="fld">提案乙的验证计划（选定后适用）</p>\n        <ul><li>' + prop_line + '</li></ul>\n' + anchor)

# 2) 附录七
apx = '\n    <details class="apx"><summary>七　各卡验证计划</summary><div class="body">\n'
apx += '      <p style="margin:6px 0 0;max-width:42em">下面是五张卡与提案乙的验证计划全文，判读规则通用部分见附录六。</p>\n'
for n, u in zip(names, cards):
    apx += '      <h4>' + n + '</h4>\n      <ul>' + u + '</ul>\n'
apx += '      <h4>提案乙（选定后适用）</h4>\n      <ul>' + props[0] + '</ul>\n'
apx += '    </div></details>\n'

end_marker = '    </div></details>\n  </section>\n\n</div>\n</body>'
assert new.count(end_marker) == 1
new = new.replace(end_marker, '    </div></details>\n' + apx + '  </section>\n\n</div>\n</body>')

# 目录
new = new.replace('<li>验证计划的通用判读规则</li></ol>', '<li>验证计划的通用判读规则</li><li>各卡验证计划</li></ol>')

open(P, 'w', encoding='utf-8').write(new)

# 3) 逐字比对
final = open(P, encoding='utf-8').read()
m7 = final.split('<summary>七　各卡验证计划</summary>')[1]
diff = 0
for u in cards + props:
    if ('<ul>' + u + '</ul>') not in m7:
        diff += 1
print('原验证计划块数', len(cards) + len(props), '附录七逐字包含', len(cards) + len(props) - diff, '差异', diff)
# 卡内不再残留「验证计划（通用判读规则见附录六）」
print('卡内残留标题数', final.count('验证计划（通用判读规则见附录六）'))
print('目录含七', '各卡验证计划</li></ol>' in final)
