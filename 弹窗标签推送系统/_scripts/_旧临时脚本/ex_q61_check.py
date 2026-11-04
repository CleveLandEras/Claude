"""Q61 检查（只读）：① 环节1 全文、决策汇报第一节与附录的正文（不含「更正记录」details）里剩余「原写」「更正」（不含「更正版」）字样；
② 两份更正记录的条目数；③ details 开闭配对；④ 环节1 是否定义了 .small 样式；⑤ 首屏关键说法在正文、汇报中的出现（SQL、106、129、652、4 个还是 5 个、结算延迟）。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def body_and_record(s):
    m = re.search(r'<details[^>]*><summary>更正记录.*?</details>', s, re.S)
    rec = m.group(0) if m else ''
    return s.replace(rec, ''), rec

def residue(t, label):
    t2 = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    hits = []
    for m in re.finditer(r'原写|更正(?!版)|上一版|前一版|第一版|曾写|作废|已改）|原来用的|原表|原标题|原判断', t2):
        hits.append(re.sub(r'<[^>]+>', '', t2[max(0, m.start() - 50):m.end() + 30]).replace('\n', ' '))
    print(f'{label}：剩余 {len(hits)} 处')
    for h in hits: print('   …', h, '…')

h1 = open(os.path.join(BASE, '环节1_现状盘点.html'), encoding='utf-8').read()
rp = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
b1, r1 = body_and_record(h1)
residue(b1, '环节1 正文')
br, rr = body_and_record(rp)
# 汇报第一节 = 第一个 <section 到第二个 <section；附录 = <!-- 附 --> 之后
secs = [m.start() for m in re.finditer(r'<section', br)]
sec1 = br[secs[0]:secs[1]] if len(secs) > 1 else ''
app = br[br.find('<!-- 附 -->'):]
residue(sec1, '汇报第一节')
residue(app, '汇报附录')
residue(br[secs[1]:br.find('<!-- 附 -->')], '汇报第二至四节（冻结，仅统计）')
print('环节1 更正记录条数', len(re.findall(r'<tr><td>\d+</td>', r1)))
print('汇报 更正记录条数', len(re.findall(r'<tr><td>\d+</td>', rr)))
for name, s in [('环节1', h1), ('汇报', rp)]:
    print(name, 'details 开', s.count('<details'), '闭', s.count('</details>'), '| p 开', len(re.findall(r'<p[ >]', s)), '闭', s.count('</p>'))
print('环节1 定义 .small：', bool(re.search(r'\.small\s*\{', h1)))
summ = h1[h1.find('<div class="summary">'):h1.find('</ol>')]
for k in ['SQL', '106', '129', '652', '4 个还是 5 个', '结算延迟', '倾向近两个月']:
    print(f'[{k}] 首屏 {summ.count(k)}｜环节1 正文 {b1.count(k) - summ.count(k)}｜汇报第一节 {sec1.count(k)}')
