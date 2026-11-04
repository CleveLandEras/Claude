"""规划第三十六次只读抽查：审查记录最近两节、各文件修改时间、A36 是否存在。"""
import os, glob, time, re
B = '/Users/decheng.huang/claude/弹窗标签推送系统'
r = open(os.path.join(B, '过程记录', '审查记录.md'), encoding='utf-8').read()
idx = [m.start() for m in re.finditer(r'^## ', r, re.M)]
print('审查记录节数', len(idx))
for s in idx[-2:]:
    print('-' * 60)
    seg = r[s:]
    nxt = [i for i in idx if i > s]
    if nxt: seg = r[s:nxt[0]]
    print(seg[:14000])
print('=' * 60)
fs = []
for p in glob.glob(os.path.join(B, '**', '*'), recursive=True):
    if os.path.isfile(p) and not any(x in p for x in ('/_versions/', '/数据/', '/归档/', '/_scripts/')):
        fs.append((os.path.getmtime(p), p))
for t, p in sorted(fs)[-25:]:
    print(time.strftime('%m-%d %H:%M', time.localtime(t)), os.path.relpath(p, B))
