"""执行者用：每次醒来第一个运行（在 lock_exec.py 之前）。不带参数运行。
熔断：执行者连续空转后会进入休眠。休眠期间，推进计划、审查记录、设计卡、任务清单都没有更新，就输出「休眠中」，本次立即结束；任何一个有更新就自动唤醒。"""
import os, re, json, datetime
from _textify import BASE

D = os.path.join(BASE, '_versions')
P = os.path.join(BASE, '过程记录')
FMT = '%Y-%m-%d %H:%M:%S'
now = datetime.datetime.now()


def ts(s):
    s = (s or '').strip()
    for f in (FMT, '%Y-%m-%d %H:%M'):
        try:
            return datetime.datetime.strptime(s[:len(now.strftime(f))], f)
        except ValueError:
            pass
    return None


def read(p):
    return open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''


def mins(t):
    return (now - t).total_seconds() / 60 if t else None


def lock_alive(name, stale_min):
    t = ts(read(os.path.join(D, name + '.lock')))
    return t is not None and mins(t) < stale_min


planned_at = ts(json.loads(read(os.path.join(D, 'plan_state.json')) or '{}').get('planned_at'))

# 值守（掉线就拉起）已并入 dispatch.py：有事的角色由 dispatch 直接启动。

# ---------- 二、熔断 ----------
sp = os.path.join(D, 'executor_sleep.flag')
sleep_t = ts(read(sp))
if not sleep_t:
    print('结论：继续（执行者没有休眠）')
else:
    watched = ['推进计划.md', '审查记录.md', '设计卡.md', '任务清单.md']
    changed = [n for n in watched if os.path.exists(os.path.join(P, n))
               and os.path.getmtime(os.path.join(P, n)) > sleep_t.timestamp() + 1]  # 休眠标记只记到秒，留 1 秒余量
    if changed:
        os.remove(sp)
        # 唤醒后如果仍然没活，下一次空转就立即再休眠
        open(os.path.join(D, 'executor_idle.txt'), 'w').write('2')
        print(f'结论：唤醒，继续（休眠期间有更新：{"、".join(changed)}）')
    else:
        print(f'结论：休眠中（{sleep_t:%H:%M} 起推进计划、审查记录、设计卡、任务清单都没有更新），本次立即结束')
