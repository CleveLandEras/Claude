import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['环节3_方案.html', '决策汇报.html']
terms = ['÷ 曝光', '有人买', '护栏：M7', '兼护栏', '四条判读线', '人均购买人数', '购买率高于对照',
         '等设计者 Q160', '保留、延长', '保留并延长', '待 Q166', 'Q166', '截尾', '验收看哪几处', '第 0–13 日']
for f in files:
    t = open(base + f, encoding='utf-8').read()
    # 去掉折叠框（存档）内容的粗略处理：标记 details 内位置
    spans = [(m.start(), m.end()) for m in re.finditer(r'<details.*?</details>', t, re.S)]
    print('=' * 30, f, len(t))
    for term in terms:
        for m in re.finditer(re.escape(term), t):
            inside = any(a <= m.start() < b for a, b in spans)
            s = t[max(0, m.start() - 60): m.end() + 60].replace('\n', ' ')
            print(f'[{term}]', '存档内' if inside else '可见', '…' + s + '…')
