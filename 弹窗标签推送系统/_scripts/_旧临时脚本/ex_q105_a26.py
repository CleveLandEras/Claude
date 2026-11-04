"""只读：打印 A26 中含 Dev1–Dev3、N5、单项次数 的行。"""
p = '/Users/decheng.huang/claude/弹窗标签推送系统/分析/A26_方案池.md'
for i, l in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
    if any(k in l for k in ['Dev1', 'Dev2', 'Dev3', 'N5', '单项次数']):
        print(i, '|', l[:900])
