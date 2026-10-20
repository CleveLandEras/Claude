"""进展日志写入（供 log_<角色>.py 调用）：读 _versions/log_<角色>.txt 的四行（阶段 / 做了什么 / 为什么 / 结果或发现），
自动加上本机当前时间和角色，插到进展日志表格的最上面（最新的在上）。写完清空输入文件。
顺带自愈：如果有人把行追加到了表格最底下（最旧那一行之后），把它们挪到最上面。"""
import os, re, datetime, fcntl
from _textify import BASE
LOG = os.path.join(BASE, '进展日志.md')
OLDEST = '| 09-28 00:46–03:44 |'   # 表格里最旧的一行，排在最底下
ROLEFILE = {'规划者': 'planner', '执行者': 'executor', '设计者': 'designer', '审查者': 'reviewer'}

def _cell(s):
    return s.strip().replace('|', '／').replace('\n', ' ')

def add(role):
    src = os.path.join(BASE, '_versions', f'log_{ROLEFILE[role]}.txt')
    lines = [l for l in open(src, encoding='utf-8').read().splitlines() if l.strip()] if os.path.exists(src) else []
    with open(os.path.join(BASE, '_versions', '进展日志.lock'), 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        rows = open(LOG, encoding='utf-8').read().split('\n')
        sep = next(i for i, l in enumerate(rows) if l.startswith('|---'))
        # 自愈：最旧一行之后出现的行，按原顺序倒过来挪到表头下面
        try:
            o = next(i for i, l in enumerate(rows) if l.startswith(OLDEST))
            stray = [l for l in rows[o + 1:] if l.startswith('| ')]
            if stray:
                rest = [l for l in rows[o + 1:] if not l.startswith('| ')]
                rows = rows[:sep + 1] + stray[::-1] + rows[sep + 1:o + 1] + rest
                sep = next(i for i, l in enumerate(rows) if l.startswith('|---'))
                print(f'自愈：把追加在底部的 {len(stray)} 行挪到了最上面')
        except StopIteration:
            pass
        if lines:
            if len(lines) < 4:
                print('结论：没写入（输入文件要四行：阶段 / 做了什么 / 为什么 / 结果或发现）')
            else:
                stage, did, why, res = lines[0], lines[1], lines[2], ' '.join(lines[3:])
                t = datetime.datetime.now().strftime('%m-%d %H:%M')
                row = f'| {t} | {role} | {_cell(stage)} | {_cell(did)} | {_cell(why)} | {_cell(res)} |'
                rows.insert(sep + 1, row)
                open(src, 'w', encoding='utf-8').write('')
                print('已写入进展日志最上面：', row[:80])
        open(LOG, 'w', encoding='utf-8').write('\n'.join(rows))
