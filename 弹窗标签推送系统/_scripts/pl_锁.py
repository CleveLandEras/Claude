# 多个对话并行时，改共享文件前加锁（规则见 规则与交接/标准体系.md 第〇节「多个对话并行」）
# 用法：python3 _scripts/pl_锁.py 加 <文件名> <谁在改> [失效分钟=60]
#       python3 _scripts/pl_锁.py 放 <文件名>
#       python3 _scripts/pl_锁.py 看
# 锁放在 _versions/<文件名>.lock，内容是时间和「谁在改」；超过失效分钟视为残留，可以接手
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, datetime
BASE = _ROOT + ''
D = os.path.join(BASE, '_versions')
FMT = '%Y-%m-%d %H:%M:%S'
cmd = sys.argv[1] if len(sys.argv) > 1 else '看'

def path(name):
    return os.path.join(D, os.path.basename(name) + '.lock')

if cmd == '加':
    name, who = sys.argv[2], sys.argv[3]
    stale = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    p, now = path(name), datetime.datetime.now()
    if os.path.exists(p):
        t, _, holder = open(p, encoding='utf-8').read().partition('｜')
        try:
            age = (now - datetime.datetime.strptime(t.strip(), FMT)).total_seconds() / 60
        except ValueError:
            age = stale + 1
        if age < stale and holder.strip() != who:
            print('被锁：%s 自 %s 起在改，先做别的' % (holder.strip(), t.strip()))
            sys.exit(1)
    open(p, 'w', encoding='utf-8').write('%s｜%s' % (now.strftime(FMT), who))
    print('已加锁：%s｜%s' % (os.path.basename(name), who))
elif cmd == '放':
    p = path(sys.argv[2])
    if os.path.exists(p):
        os.remove(p)
    print('已放锁：%s' % os.path.basename(sys.argv[2]))
else:
    for f in sorted(os.listdir(D)):
        if f.endswith('.lock'):
            print(f[:-5], '｜', open(os.path.join(D, f), encoding='utf-8').read().strip())
