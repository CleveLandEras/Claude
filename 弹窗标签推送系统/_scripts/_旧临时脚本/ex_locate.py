"""执行者定位：读 _versions/locate.txt（第一行文件相对路径，其后每行一个检索词），打印行号与片段。只读。"""
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
lines = open(BASE + '_versions/locate.txt', encoding='utf-8').read().splitlines()
files, terms = [], []
for l in lines:
    if l.startswith('F:'):
        files.append(l[2:].strip())
    elif l.strip():
        terms.append(l.strip())
for f in files:
    txt = open(BASE + f, encoding='utf-8').read().splitlines()
    print('=====', f, '共', len(txt), '行')
    for t in terms:
        for i, l in enumerate(txt, 1):
            if t in l:
                j = l.find(t)
                print(f'  [{t}] L{i}: …{l[max(0, j - 60): j + 100]}…')
