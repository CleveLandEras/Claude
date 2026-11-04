import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['环节3_方案.html', '支撑文件/04_弹窗功能缺口需求.md', '支撑文件/07_推送需求.md']
terms = ['→ 丙', '条件式推荐', '按工作原则 v2 重理', '范围外的机会', '理由弱', '理由不成立', '不独立成立', '只能按成本和风险排']
for f in files:
    s = open(base + f, encoding='utf-8').read()
    print('#####', f)
    for t in terms:
        for m in re.finditer(re.escape(t), s):
            print('##', t, m.start(), s[max(0, m.start()-70):m.end()+90].replace('\n', ' '))
s = open(base + '决策汇报.html', encoding='utf-8').read()
a = s.find('id="archive-v3"')
c = s.find('更正记录', 100000)
print('archive at', a, 'first corrections after 100000 at', c)
for t in ['晚一步', '首期基本不交', '有用非必要', '有用」而非']:
    for m in re.finditer(t, s):
        print('## 汇报', t, m.start(), s[max(0, m.start()-150):m.end()+150].replace('\n', ' '))
