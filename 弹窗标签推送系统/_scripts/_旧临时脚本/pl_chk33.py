import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html', '分析/A35_赠点规模与02成本影响.md', '分析/A32_问题空间扫描.md']
terms = ['9.4 倍', '集中在两头', '上界约 5,146', '没有『必须』退回', '没有「必须」退回', '核对到 10:42', '11:08 复核通过', '306,859,994', '9/29 写法', '现行 02', '不进排序', '分母效应', '根因']
for f in files:
    t = open(os.path.join(base, f), encoding='utf-8').read()
    t2 = re.sub(r'<[^>]+>', '', t)
    print('==', f)
    for w in terms:
        c = t2.count(w)
        if c:
            idx = [m.start() for m in re.finditer(re.escape(w), t2)]
            ctx = [t2[max(0, i - 40):i + 40].replace('\n', ' ') for i in idx[:4]]
            print('  ', w, c)
            for x in ctx:
                print('      …', x)
rv = open(base + '过程记录/审查记录.md', encoding='utf-8').read()
for r in ['R193', 'R194', 'R195', 'R196', 'R197']:
    i = rv.find('### ' + r)
    seg = rv[i:i + 4000]
    end = seg.find('\n### ', 5)
    if end > 0:
        seg = seg[:end]
    j = seg.find('- 已处理')
    print(r, 'handled' if j >= 0 else 'NOT handled')
    if j >= 0:
        print('   ', seg[j:j + 500].split('\n')[0])
