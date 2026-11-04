"""只读：在 Claude Code 的文件历史里找「设计卡.md」被覆盖前的备份，列出候选（路径、大小、修改时间、是否含 Q199 卡）。"""
import os, glob, datetime
root = os.path.expanduser('~/.claude/file-history')
cands = []
for p in glob.glob(os.path.join(root, '**', '*'), recursive=True):
    if not os.path.isfile(p):
        continue
    try:
        s = open(p, encoding='utf-8').read()
    except Exception:
        continue
    if s.startswith('# 设计卡') and '## Q183｜' in s:
        cands.append((os.path.getmtime(p), p, len(s), '## Q199｜' in s, '→ 执行结果（Q187' in s))
for m, p, n, has199, has187 in sorted(cands):
    print(datetime.datetime.fromtimestamp(m).strftime('%m-%d %H:%M:%S'), n, 'Q199' if has199 else '-', 'Q187结果' if has187 else '-', p)
print('候选数：', len(cands))
