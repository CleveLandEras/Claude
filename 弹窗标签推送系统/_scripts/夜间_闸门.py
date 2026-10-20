"""夜间全局推进的开工闸门（10/14 建；10/15 改：每晚都开工，不再因「判过无事可做」跳过，也不再等其他对话停手）。
定时任务每次唤醒先运行它，按第一行结论行动。

用法（在项目根目录运行）：
  python3 _scripts/夜间_闸门.py              检查，不改任何东西
  python3 _scripts/夜间_闸门.py start        开工占锁
  python3 _scripts/夜间_闸门.py touch        续锁（每做完一件事、或每 30 分钟运行一次）
  python3 _scripts/夜间_闸门.py end          收工放锁（工作没做完也照样放，下一次唤醒接手）

检查结论（第一行）：
  TEST     不在夜间窗口（白天手动试运行）：只做自检
  BUSY     另一轮夜间推进正在进行：本次不开工
  PROCEED  开工。后面列出其他对话近 30 分钟改过的文件和未失效的锁，这些文件今晚先不碰
  WRAPUP   收尾时段：只做晨间收尾
第二、三行给出今晚的日志与简报路径。

夜间窗口：每天 19:00 到次日 08:30；07:00 起收尾。
"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import datetime as dt
import glob
import json
import os
import sys

BASE = _ROOT + ''
STATE_DIR = os.path.join(BASE, '_versions', '夜间推进')
LOCK = os.path.join(STATE_DIR, 'lock')
STATE = os.path.join(STATE_DIR, '状态.json')

START_H = 19
WRAP_HM = (7, 0)
END_HM = (8, 30)
RECENT_MIN = 30       # 其他对话近这么多分钟改过的文件，今晚先不碰
LOCK_STALE_MIN = 60   # 夜间锁超过这么久没续，视为上一轮已中断

SKIP_DIRS = {'.claude', '.git'}


def _now():
    # 测试用：环境变量 NIGHT_NOW="2026-10-15 20:00" 可模拟时间
    v = os.environ.get('NIGHT_NOW')
    return dt.datetime.fromisoformat(v) if v else dt.datetime.now()


def night_of(now):
    """属于哪一晚：19:00 以后算当天，08:30 以前算前一天；其余时间不在窗口内，返回 None。"""
    t = (now.hour, now.minute)
    if now.hour >= START_H:
        return now.date()
    if t < END_HM:
        return now.date() - dt.timedelta(days=1)
    return None


def paths(night):
    morning = night + dt.timedelta(days=1)
    log = f'过程记录/夜间推进_{night.strftime("%m%d")}夜.md'
    brief = f'简报/{morning.isoformat()}_夜间推进.html'
    return log, brief


def own_prefixes(night):
    log, brief = paths(night)
    return (os.path.join(BASE, '_versions', '夜间推进'),
            os.path.join(BASE, log), os.path.join(BASE, brief))


def load_state():
    try:
        with open(STATE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=1)


def fmt(t):
    return t.strftime('%m-%d %H:%M')


def recent_changes(since, own, run_started=None):
    """since 之后被改动的文件；不含夜间推进自己的日志、简报、状态，以及本轮开工后的改动（那是夜间自己改的）。"""
    hits = []
    cutoff = since.timestamp()
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name == '.DS_Store' or name.startswith('~$') or name.endswith('.lock'):
                continue
            p = os.path.join(root, name)
            if p.startswith(own):
                continue
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if m > cutoff and not (run_started and m >= run_started.timestamp()):
                hits.append((m, os.path.relpath(p, BASE)))
    hits.sort(reverse=True)
    return hits


def other_locks(now):
    out = []
    for p in glob.glob(os.path.join(BASE, '_versions', '*.lock')):
        try:
            t, _, who = open(p, encoding='utf-8').read().partition('｜')
            age = (now - dt.datetime.strptime(t.strip(), '%Y-%m-%d %H:%M:%S')).total_seconds() / 60
        except Exception:
            continue
        if age < 60 and '夜间' not in who:
            out.append(f'锁 {os.path.basename(p)[:-5]}（{who.strip()}，{age:.0f} 分钟前）')
    return out


def lock_age_min(now):
    if not os.path.isdir(LOCK):
        return None
    return (now.timestamp() - os.path.getmtime(LOCK)) / 60


def check():
    now = _now()
    night = night_of(now)
    if night is None:
        return 'TEST', [f'现在 {fmt(now)}，不在夜间窗口（每天 19:00–次日 08:30）']
    log, brief = paths(night)
    head = [f'日志 {log}', f'简报 {brief}']

    age = lock_age_min(now)
    if age is not None and age < LOCK_STALE_MIN:
        return 'BUSY', [f'另一轮正在进行（锁 {age:.0f} 分钟前续过）']
    notes = [f'上一轮的锁已 {age:.0f} 分钟未续，视为中断，接手它的进度'] if age is not None else []

    if (now.hour, now.minute) >= WRAP_HM and now.hour < START_H:
        return 'WRAPUP', head + notes

    st = load_state()
    started = dt.datetime.fromisoformat(st['lock_started']) if st.get('lock_started') and age is not None else None
    active = recent_changes(now - dt.timedelta(minutes=RECENT_MIN), own_prefixes(night), started)
    avoid = [f'{dt.datetime.fromtimestamp(m).strftime("%H:%M")}  {p}' for m, p in active[:20]] + other_locks(now)
    if avoid:
        notes += ['其他对话近期在改下列文件，今晚先不碰（改之前再查一次）：'] + avoid
    return 'PROCEED', head + notes


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    now = _now()
    if cmd == 'check':
        verdict, lines = check()
        print(verdict)
        for l in lines:
            print('  ' + l)
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    if cmd == 'start':
        age = lock_age_min(now)
        if age is not None and age >= LOCK_STALE_MIN:
            os.rmdir(LOCK)
        try:
            os.mkdir(LOCK)
        except FileExistsError:
            print('BUSY')
            return
        st = load_state()
        st['lock_started'] = now.isoformat(timespec='seconds')
        save_state(st)
        print('LOCKED', fmt(now))
    elif cmd == 'touch':
        if os.path.isdir(LOCK):
            os.utime(LOCK)
        else:
            os.mkdir(LOCK)
        print('TOUCHED', fmt(now))
    elif cmd == 'end':
        st = load_state()
        st['last_end'] = now.isoformat(timespec='seconds')
        st.setdefault('runs', []).append({'start': st.get('lock_started'), 'end': st['last_end']})
        st['runs'] = st['runs'][-60:]
        save_state(st)
        if os.path.isdir(LOCK):
            os.rmdir(LOCK)
        print('RELEASED', fmt(now))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
