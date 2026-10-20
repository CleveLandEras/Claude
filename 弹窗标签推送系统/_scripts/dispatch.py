"""调度：判断现在哪些角色有事可做，只启动有事的角色，避免空转。不带参数运行。
任何角色在本次工作结束前运行一次（执行者在开工前也运行一次），对输出里每一行「启动：<任务 ID>」用 run_scheduled_task 启动它（不启动自己）。
输出「全体空转」时：没有任何角色有事可做，由执行者按说明暂停自动运行，等 Dk 或主对话带来新输入。
只读判断，不上锁；同一个角色 3 分钟内只启动一次（给它时间上锁）。"""
import os, re, json, hashlib, datetime
from _textify import BASE, deliverables

D = os.path.join(BASE, '_versions')
P = os.path.join(BASE, '过程记录')
FMT = '%Y-%m-%d %H:%M:%S'
now = datetime.datetime.now()
T = {'executor': 'popup-tag-push-iterate', 'planner': 'popup-tag-push-planner',
     'designer': 'popup-tag-push-designer', 'reviewer': 'popup-tag-push-reviewer'}
NAME = {'executor': '执行者', 'planner': '规划者', 'designer': '设计者', 'reviewer': '审查者'}


def read(p):
    return open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''


def ts(s):
    s = (s or '').strip()
    for f in (FMT, '%Y-%m-%d %H:%M'):
        try:
            return datetime.datetime.strptime(s[:len(now.strftime(f))], f)
        except ValueError:
            pass
    return None


def alive(name, stale):
    t = ts(read(os.path.join(D, name + '.lock')))
    return t is not None and (now - t).total_seconds() < stale * 60


plan = read(os.path.join(P, '推进计划.md'))
cards = set(re.findall(r'^## (Q\d+)', read(os.path.join(P, '设计卡.md')), re.M))
items = re.findall(r'^- \[ \] (Q\d+)｜([^｜\n]*)', plan, re.M)
need_design = [q for q, t in items if t.strip().startswith('需设计') and q not in cards]
executable = [q for q, t in items if not (t.strip().startswith('需设计') and q not in cards)]

st = json.loads(read(os.path.join(D, 'plan_state.json')) or '{}')
last_plan = st.get('planned_at', '')
rounds = [l.strip() for l in read(os.path.join(D, 'executor_rounds.log')).splitlines() if l.strip()]
reviewed_at = read(os.path.join(D, 'reviewed', '_reviewed_at.txt'))
review_done_at = read(os.path.join(D, 'reviewed', '_review_done_at.txt'))
since_review = [r for r in rounds if r[:16] > reviewed_at[:16]] if reviewed_at else rounds
since_plan = [r for r in rounds if r[:16] > last_plan[:16]] if last_plan else rounds

s = read(os.path.join(P, '任务清单.md'))
m = re.search(r'\n## 四、.*?(?=\n## )', s + '\n## ', re.S)
sec4 = hashlib.md5((m.group(0) if m else '').encode()).hexdigest()
files = sorted(os.path.basename(p) for p in deliverables())

why = {}
# 审查者：执行者自上次审查以来满两轮
if len(since_review) >= 2 and not alive('reviewer', 50):
    why['reviewer'] = f'执行者自上次审查以来完成 {len(since_review)} 轮'
# 规划者：与 should_plan.py 的触发条件一致
pr = []
if not last_plan:
    pr.append('从未规划')
else:
    if os.path.exists(os.path.join(D, 'need_plan.flag')): pr.append('执行者发出「需要规划」信号')
    if len(items) < 3 and (since_plan or review_done_at[:16] > last_plan[:16]): pr.append(f'队列只剩 {len(items)} 项且有新进展')
    if review_done_at[:16] > last_plan[:16]: pr.append('上次规划后完成了审查')
    if len(since_plan) >= 6: pr.append(f'上次规划后执行者完成 {len(since_plan)} 轮')
    if st.get('sec4') != sec4: pr.append('答复登记有变化')
    if st.get('files') != files: pr.append('交付物文件有增减')
if pr and not alive('planner', 50):
    why['planner'] = '；'.join(pr)
# 设计者：有需设计、还没有卡的队列项
if need_design and not alive('designer', 50):
    why['designer'] = f'{"、".join(need_design[:3])} 等设计卡'
# 执行者：队列里有能做的项
if executable and not alive('executor', 60):
    why['executor'] = f'队列里有 {len(executable)} 项可做（{"、".join(executable[:3])}）'

# 同一角色 3 分钟内只启动一次
sp = os.path.join(D, 'dispatch_state.json')
state = json.loads(read(sp) or '{}')
launched = []
for k, w in why.items():
    last = ts(state.get(k))
    if last and (now - last).total_seconds() < 180:
        print(f'刚启动过，不重复：{NAME[k]}（{last:%H:%M}）')
        continue
    state[k] = now.strftime(FMT)
    launched.append(k)
    print(f'启动：{T[k]}｜{NAME[k]}：{w}')
json.dump(state, open(sp, 'w'), ensure_ascii=False)

busy = [NAME[k] for k in T if alive(k, 60 if k == 'executor' else 50)]
if not why and not busy:
    print('全体空转：没有任何角色有事可做（队列无可做项、无待审查、无待设计、无需重新规划）')
elif not why:
    print('无需启动其他角色；正在运行：' + '、'.join(busy))
