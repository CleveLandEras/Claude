base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['环节1_现状盘点.html', '决策汇报.html']:
    lines = open(base + f, encoding='utf-8').read().split('\n')
    print('=' * 20, f)
    for i, l in enumerate(lines):
        if '更正记录' in l and ('summary' in l or '<h' in l):
            print(i + 1, l[:600])
            for j in range(i + 1, min(i + 8, len(lines))):
                print(j + 1, lines[j][:400])
    # last rows of correction table: print lines containing <tr><td>70 or <td>7<
    for i, l in enumerate(lines):
        if '<td>70</td>' in l or '<td>69</td>' in l or '<td>7</td>' in l or '<td>6</td>' in l:
            print(i + 1, l[:1200])
    print(lines[-1][:0])
