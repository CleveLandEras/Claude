import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '环节3_方案.html']:
    s = open(B + f, encoding='utf-8').read()
    for t in ['details', 'section', 'table', 'div', 'ol', 'p']:
        o = len(re.findall(rf'<{t}[\s>]', s))
        c = len(re.findall(rf'</{t}>', s))
        if o != c:
            print(f'{f}: <{t}> 开 {o} 闭 {c}')
    ids = set(re.findall(r'id="([^"]+)"', s))
    miss = [h for h in re.findall(r'href="#([^"]+)"', s) if h not in ids]
    print(f'{f}: 页内锚点缺失 {miss}')
    print(f'{f}: 「本节是问题诊断之前写的」{s.count("本节是问题诊断之前写的")} 处；「168 人」{s.count("168 人")} 处')
s3 = open(B + '环节3_方案.html', encoding='utf-8').read()
print('环节3 id s1 存在', 'id="s1"' in s3, '；A25 链接', 'A25_改善幅度.md' in s3)
