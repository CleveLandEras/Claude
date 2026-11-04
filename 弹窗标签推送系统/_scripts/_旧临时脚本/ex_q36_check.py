"""Q36 整合检查：首屏删掉的细节是否在正文里仍有；首屏链接的锚点是否存在；旧说法残留。只读。"""
import re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(BASE + '环节1_现状盘点.html', encoding='utf-8').read()
i, j = h.index('<div class="summary">'), h.index('</div>', h.index('<div class="summary">'))
summary, body = h[i:j], h[j:]
terms = ['1,420', '14.41%', '757', '6.16%', '普卡与银卡之间', '56.28%', '9,786', '3,638', '问题 12', '3.87%', '23.82%',
         '2.86%', '18,265', '30.93%', '11.21%', '84.92%', '89.78%', '24,068', '1,904', '12–21', '750', '19 个百分点', '18.74',
         '25.94%', '67.85%', '13,424']
for t in terms:
    print('%-12s 首屏 %d  正文 %d' % (t, summary.count(t), body.count(t)))
ids = set(re.findall(r'id="([^"]+)"', h))
links = re.findall(r'href="#([^"]+)"', h)
bad = sorted(set(l for l in links if l not in ids))
print('首屏条目数', summary.count('<li>'), ' 链接到不存在锚点的:', bad)
for t in ['得到过活动赠点', '缺 5 类', '用户已经分成付费能力差异很大的几群人', '31.49', '第二节第 5 小节']:
    print('残留 %-24s 环节1 %d' % (t, h.count(t)))
r = open(BASE + '决策汇报.html', encoding='utf-8').read()
for t in ['得到过活动赠点', '缺 5 类', '31.49', '第二节第 5 小节']:
    print('残留 %-24s 汇报 %d' % (t, r.count(t)))
xl = re.findall(r'环节1_现状盘点\.html#([^"]+)"', r)
print('汇报指向环节1 的锚点 %d 个，不存在的: %s' % (len(xl), sorted(set(a for a in xl if a not in ids))))
import os
fl = re.findall(r'href="(分析/[^"#]+|支撑文件/[^"#]+)"', h + r)
print('分析/支撑文件链接 %d 个，文件不存在的: %s' % (len(fl), sorted(set(f for f in fl if not os.path.exists(BASE + f)))))
# 找出现旧说法的上下文
for t in ['得到过活动赠点', '缺 5 类']:
    for m in re.finditer(t, h):
        print('  环节1 上下文:', h[max(0, m.start() - 60):m.start() + 40].replace('\n', ' '))
    for m in re.finditer(t, r):
        print('  汇报 上下文:', r[max(0, m.start() - 60):m.start() + 40].replace('\n', ' '))
