# Q9：核对决策汇报附录每条消息与 00 第五节原话是否逐字一致（只读）
import re, html
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
md = open(base + '00_推进记录.md', encoding='utf-8').read()
sec = md.split('## 五、对外问题清单')[1].split('### 推送第二、三步追问')[0]
parts = re.split(r'^### ', sec, flags=re.M)
blocks = {}
for p in parts[1:]:
    title = p.splitlines()[0].strip()
    m = re.search(r'```\n(.*?)\n```', p, flags=re.S)
    if m:
        blocks[title] = m.group(1)
rep = open(base + '决策汇报.html', encoding='utf-8').read()
pres = {k: html.unescape(v) for k, v in re.findall(r'<pre id="(m\d)">(.*?)</pre>', rep, flags=re.S)}
pair = {
    'm1': '发给研发（问题 2–7、9）',
    'm2': '发给标签维护人（问题 11）',
    'm3': '发给数据团队（问题 23）',
    'm4': '发给运营（问题 8、10、22）',
    'm5': '发给礼包配置负责人（问题 1）',
}
for k, t in pair.items():
    a = blocks.get(t)
    b = pres.get(k)
    if a is None or b is None:
        print(k, t, '缺失', a is None, b is None)
        continue
    same = a == b
    print(k, t, '一致' if same else '不一致', len(a), len(b))
    if not same:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print('  首个差异位置', i, repr(a[max(0, i-20):i+20]), '|', repr(b[max(0, i-20):i+20]))
                break
print('00 第五节原话块：', list(blocks.keys()))
