"""Q116 自查：02 正文检索禁用词与关键数字。只读，不带参数。"""
import re

p = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/02_弹窗分人群定制方案.html'
t = open(p, encoding='utf-8').read()
for w in ['降级', 'A26', '主线已变更', '待设计者裁定', '待自查', '待确认', '首期', '12 → 32', '开放期', 'A21', 'A31', 'A3', '审查']:
    idx = [m.start() for m in re.finditer(re.escape(w), t)]
    print(f'{w}：{len(idx)} 处')
    for i in idx[:6]:
        print('   …' + re.sub(r'<[^>]+>', '', t[max(0, i - 40): i + 60]).replace('\n', ' ') + '…')
print('长度', len(t))
