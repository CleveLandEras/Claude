"""R122–R124 回归检查（只读）：残留句只在更正记录；锚点存在；核对表 / 更正条数。"""
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
rep = open(BASE + '决策汇报.html', encoding='utf-8').read()
e2 = open(BASE + '环节2_问题诊断.html', encoding='utf-8').read()

def body_vs_fix(s, marker):
    i = s.find(marker)
    return s[:i], s[i:]

rb, rf = body_vs_fix(rep, '<summary>更正记录（顶部总结论')
eb, ef = body_vs_fix(e2, '<summary>更正记录（')
for t in ['都是按上面的诊断推出来的', '按推荐，其余照原设计', '统一后台（07）要开发', '推送定向要不要开发']:
    print('汇报', t, '正文', rb.count(t), '更正记录', rf.count(t))
for t in ['正文按档位排序', '按正文顺序，每条可跳转）', '推送（D8、E2）']:
    print('环节2', t, '正文', eb.count(t), '更正/核对', ef.count(t))
print('汇报提示行数', rep.count('方案环节会重写本节'))
ids = set(re.findall(r'id="([^"]+)"', e2))
links = re.findall(r'href="#([^"]+)"', e2)
print('环节2 缺失锚点', sorted({l for l in links if l not in ids}))
ids_r = set(re.findall(r'id="([^"]+)"', rep))
print('汇报 缺失锚点', sorted({l for l in re.findall(r'href="#([^"]+)"', rep) if l not in ids_r}))
m = re.search(r'更正记录（顶部总结论.*?</table>', rep, re.S)
print('汇报更正行数', len(re.findall(r'<tr><td>\d+</td>', m.group(0))))
m = re.search(r'<summary>更正记录（\d+ 条）</summary>.*?</table>', e2, re.S)
print('环节2 更正行数', len(re.findall(r'<tr><td>\d+</td>', m.group(0))))
# 折叠框条目顺序
m = re.search(r'各节一句话.*?</ol>', e2, re.S)
print('折叠框顺序', re.findall(r'<li>(?:<b>总述</b> · )?<a href="#([^"]+)"', m.group(0)), '条数', m.group(0).count('<li>'))
for k in ['核对', '33 + 2', '35 行', '33 行']:
    for mm in re.finditer(re.escape(k), e2):
        print('  环节2 「%s」：…%s…' % (k, e2[max(0, mm.start()-60):mm.end()+40].replace('\n', ' ')))
