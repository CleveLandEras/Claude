# 只读：打印旧说法残留的上下文；打印当前 verdict 与新增卡推断句
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h2 = open(base + '环节2_问题诊断.html', encoding='utf-8').read()
rep = open(base + '决策汇报.html', encoding='utf-8').read()
def ctx(txt, kw, name):
    for m in re.finditer(re.escape(kw), txt):
        s = re.sub(r'<[^>]+>', '', txt[max(0, m.start()-120):m.end()+60]).replace('\n', ' ')
        # 标出所在大块：是否在 details（存档）或更正记录表内
        before = txt[:m.start()]
        in_det = before.count('<details') > before.count('</details>')
        in_corr = before.rfind('更正记录') > before.rfind('<section') if '更正记录' in before else False
        print(f'[{name}] {kw} | 存档框内={in_det} | 更正记录后={in_corr} | …{s}…')
for kw in ['人数榜第', '继承第一档', '执行时不改', '与这条链的关系取决于', '规划者写死', '规划者裁定', '共同抓手']:
    ctx(h2, kw, '环节2'); ctx(rep, kw, '汇报')
v = re.search(r'<div class="verdict">(.*?)</div>', rep, re.S).group(1)
print('\nVERDICT:', re.sub(r'<[^>]+>', '', v))
i = rep.find('02 新增卡')
print('\n新增卡:', re.sub(r'<[^>]+>', '', rep[i-200:i+200]))
print('\n汇报更正记录条数标题:', re.findall(r'汇报独有 \d+ 条', rep))
