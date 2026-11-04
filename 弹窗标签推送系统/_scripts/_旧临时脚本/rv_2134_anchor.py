# 只读：核对环节2 内部锚点、决策汇报指向环节2 的锚点是否存在；核对 D5 / 各节顺序
import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h2 = open(base + '环节2_问题诊断.html', encoding='utf-8').read()
rep = open(base + '决策汇报.html', encoding='utf-8').read()
ids = set(re.findall(r'id="([^"]+)"', h2))
print('环节2 id 数', len(ids))
inner = set(re.findall(r'href="#([^"]+)"', h2))
print('环节2 内部缺失锚点:', sorted(inner - ids))
ext = set(re.findall(r'href="环节2_问题诊断\.html#([^"]+)"', rep))
print('汇报→环节2 缺失锚点:', sorted(ext - ids))
# section 顺序
secs = re.findall(r'<section id="([^"]+)"', h2)
print('section 顺序:', secs)
# 每节标题
for m in re.finditer(r'<section id="([^"]+)">\s*<div class="no">([^<]+)</div>', h2):
    print(m.group(1), '|', m.group(2).strip())
# D5 所在
i = h2.find('id="d5"')
print('d5 位置上下文:', re.sub(r'<[^>]+>', '', h2[i-50:i+200]).replace('\n', ' ')[:200])
# 旧说法残留检查
for kw in ['第一档', '第二档', '人数榜第', '继承第一档', '执行时不改', '与这条链的关系取决于', '规划者写死', '规划者裁定', '共同抓手', '谁大，取决于']:
    cnt_h2 = h2.count(kw); cnt_rep = rep.count(kw)
    print(kw, '环节2', cnt_h2, '汇报', cnt_rep)
# 汇报 verdict
v = re.search(r'<div class="verdict">(.*?)</div>', rep, re.S).group(1)
print('verdict 含「五类人群」:', '五类人群' in v, '含「不需要开发」:', '不需要开发' in v)
print('汇报 新增卡「有依据」:', '第一屏少弹、弹对」有依据' in rep)
