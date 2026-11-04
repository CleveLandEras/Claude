"""Q85 核对：环节3 锚点可跳转；口径约束与推进计划逐条一致；汇报第三节只多一句链接（只读）。"""
import os, re, html
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = open(os.path.join(BASE, '环节3_方案.html'), encoding='utf-8').read()
plan = open(os.path.join(BASE, '过程记录', '推进计划.md'), encoding='utf-8').read()

ids = set(re.findall(r'id="([^"]+)"', h))
hrefs = re.findall(r'href="#([^"]+)"', h)
print('锚点 id：', sorted(ids))
print('内部链接缺失：', [x for x in hrefs if x not in ids] or '无')
for s in ['s1', 's2', 's3', 's4', 's5', 'm']:
    print(s, '存在' if s in ids else '缺失')
print('深色模式块：', 'prefers-color-scheme: dark' in h, 'data-theme="dark"' in h)

# 推进计划口径约束
seg = plan.split('环节3 必须遵守的口径约束')[1].split('## 一、')[0]
prules = re.findall(r'^(\d+(?:、\d+)?)\. (.+)$', seg, re.M)
hrules = [(k, html.unescape(re.sub(r'<[^>]+>', '', v))) for k, v in
          re.findall(r'<li><span class="k">([^<]+)</span><span>(.*?)</span></li>', h)]
print('计划条数', len(prules), '文件条数', len(hrules))
bad = 0
for (pk, pv), (hk, hv) in zip(prules, hrules):
    if pk != hk or pv.strip() != hv.strip():
        bad += 1; print('不一致：', pk, '|', pv, '||', hk, '|', hv)
print('逐条不一致数：', bad)

r = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
print('汇报链接环节3 次数：', r.count('href="环节3_方案.html"'))
