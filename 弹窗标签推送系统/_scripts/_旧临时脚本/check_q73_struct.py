"""Q73 结构核对：环节2 页内锚点是否都有目标、id 是否重复、section 顺序、每节 h4 顺序、数字集合与整合前备份比对。不带参数运行。"""
import os, re, collections
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '环节2_问题诊断.html')
s = open(p, encoding='utf-8').read()
ids = re.findall(r'\sid="([^"]+)"', s)
dup = [k for k, v in collections.Counter(ids).items() if v > 1]
print('id 数', len(ids), '重复 id', dup)
hrefs = set(re.findall(r'href="#([^"]+)"', s))
print('页内锚点无目标', sorted(h for h in hrefs if h not in ids))
print('section 顺序', re.findall(r'<section id="([^"]+)"', s))
for m in re.finditer(r'<section id="([^"]+)">(.*?)</section>', s, re.S):
    h4 = re.findall(r'<h4>([^<]+)</h4>', m.group(2))
    print(m.group(1), '｜'.join(h4))
# 与外部文件的链接：决策汇报等是否链到环节2 的锚点
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    t = open(os.path.join(BASE, f), encoding='utf-8').read()
    anc = set(re.findall(r'环节2_问题诊断\.html#([A-Za-z0-9_-]+)', t))
    print(f, '指向环节2 的锚点', sorted(anc), '无目标', sorted(a for a in anc if a not in ids))
# 数字集合比对（与 _versions 下备份，如有）
nums = lambda x: collections.Counter(re.findall(r'\d[\d,]*\.?\d*', re.sub(r'<[^>]+>', ' ', x)))
bk = os.path.join(BASE, '_versions', '环节2_问题诊断_preQ73.html')
if os.path.exists(bk):
    b = open(bk, encoding='utf-8').read()
    nb, ns = nums(b), nums(s)
    lost = {k: nb[k] - ns[k] for k in nb if ns[k] == 0}
    new = {k: ns[k] for k in ns if nb[k] == 0}
    print('整合前有、现在完全没有的数字', lost)
    print('现在有、整合前没有的数字', new)
else:
    print('无整合前备份，跳过数字比对')
