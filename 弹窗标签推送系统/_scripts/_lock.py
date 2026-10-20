"""简单文件锁：防止同一角色两轮重叠。锁超过 stale 分钟视为失效。"""
import os, datetime
from _textify import BASE
D = os.path.join(BASE, '_versions'); os.makedirs(D, exist_ok=True)
FMT = '%Y-%m-%d %H:%M:%S'
def path(name): return os.path.join(D, name + '.lock')
def acquire(name, stale_min):
    p = path(name); now = datetime.datetime.now()
    if os.path.exists(p):
        try:
            t = datetime.datetime.strptime(open(p).read().strip(), FMT)
            if (now - t).total_seconds() < stale_min * 60:
                return False, t.strftime(FMT)
        except Exception:
            pass
    open(p, 'w').write(now.strftime(FMT))
    return True, now.strftime(FMT)
def release(name):
    p = path(name)
    if os.path.exists(p): os.remove(p)
