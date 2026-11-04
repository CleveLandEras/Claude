"""审查者用：判断本次要不要审查。执行者自上次审查以来满 2 轮、且没有另一个审查在进行时才审查（并上锁）。不带参数运行。"""
import os
from _textify import BASE
from _lock import acquire
d = os.path.join(BASE, '_versions')
stamp = os.path.join(d, 'reviewed', '_reviewed_at.txt')
last = open(stamp).read().strip() if os.path.exists(stamp) else ''
log = os.path.join(d, 'executor_rounds.log')
rounds = [l.strip() for l in open(log)] if os.path.exists(log) else []
since = [r for r in rounds if r[:16] > last[:16]] if last else rounds
print('上次审查：', last or '从未')
print('此后执行者完成轮数：', len(since))
if last and len(since) < 2:
    print('结论：跳过（不满两轮）')
else:
    ok, t = acquire('reviewer', 50)
    print('结论：审查（已上锁）' if ok else f'结论：跳过（另一次审查 {t} 开始，仍在进行）')
