import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['支撑文件/04_弹窗功能缺口需求.md', '支撑文件/05_标签需求.md', '支撑文件/07_推送需求.md']:
    t = open(base + f, encoding='utf-8').read()
    print('#####', f, len(t))
    for m in re.finditer(r'^#+ .*提案.*$', t, re.M):
        print(m.start(), repr(t[m.start():m.start() + 200]))
    print('tail:', repr(t[-400:]))
for f in ['分析/A26_方案池.md', '分析/A27_推送方案比较.md', '分析/A29_评估与可检测幅度.md', '分析/A33_人群圈选与交集.md']:
    t = open(base + f, encoding='utf-8').read()
    print('#####', f)
    print(t[:500])
