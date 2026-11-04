"""Q119 自查：全文检索「换主线」「首期不交」「首期缩小」「推后」「首期基本不」出现的位置与上下文。只读，不带参数。"""
import re
p = '/Users/decheng.huang/claude/弹窗标签推送系统/决策汇报.html'
t = open(p, encoding='utf-8').read()
for w in ['换主线', '首期不交', '首期缩小', '推后', '首期基本不', '推到第二期', '主线换']:
    idx = [m.start() for m in re.finditer(re.escape(w), t)]
    print(f'== {w}：{len(idx)} 处')
    for i in idx:
        ctx = re.sub(r'<[^>]+>', '', t[max(0, i - 50): i + 50]).replace('\n', ' ')
        # 判定所在区域
        before = t[:i]
        area = '存档/更正/折叠' if (before.count('<details') > before.count('</details>')) else '正文'
        print(f'   [{i}] {area}: …{ctx}…')
