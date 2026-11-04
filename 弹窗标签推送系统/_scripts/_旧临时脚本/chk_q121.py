"""Q121 自查：07 正文（提案之前）检索「首期」「推后」「A27 重核」「待确认」；06、07 通路数。只读，不带参数。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/支撑文件/'
t = open(B + '07_推送需求.md', encoding='utf-8').read()
i = t.index('## 提案')
body, prop = t[:i], t[i:]
for w in ['首期', '推后', 'A27 重核', '待确认', '缩小']:
    print(f'{w}: 正文 {body.count(w)}；提案 {prop.count(w)}')
    for k in [j for j in range(len(body)) if body.startswith(w, j)][:3]:
        print('   …', body[max(0, k - 30): k + 40].replace('\n', ' '))
for ch in ['快显', '手机推播', '短信', 'Facebook', 'LINE']:
    print(ch, '07 出现', t.count(ch), '；06 出现', open(B + '06_推送现状整理.md', encoding='utf-8').read().count(ch))
