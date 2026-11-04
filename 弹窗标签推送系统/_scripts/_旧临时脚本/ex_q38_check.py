"""Q38 回归检查：环节1 中若干数字出现次数、锚点与链接有效性。只读。"""
import re, os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
h = open(BASE + '环节1_现状盘点.html', encoding='utf-8').read()
b = open(BASE + '决策汇报.html', encoding='utf-8').read()
for t in ['31.49', '36.60', '48 人', '96.22%', '49.37%', '25.94%', '22.71%', '98.15%', '42,123', '24,068',
          '52 名金卡以上', '83 人', '异常账号', '身份间的差距大部分来自', '只作推断', '1,000 金币']:
    print(f'{t}: {h.count(t)}')
ids = set(re.findall(r'id="([^"]+)"', h))
bad = [a for a in re.findall(r'href="#([^"]+)"', h) if a not in ids]
print('环节1 内部锚点失效:', bad)
bad2 = [a for a in re.findall(r'href="环节1_现状盘点\.html#([^"]+)"', b) if a not in ids]
print('汇报指向环节1 的锚点失效:', bad2)
files = re.findall(r'href="((?:分析|支撑文件)/[^"#]+)"', h)
print('环节1 文件链接失效:', [f for f in files if not os.path.exists(BASE + f)])
