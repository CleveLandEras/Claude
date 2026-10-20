"""执行者用：发现队列已空时运行，发出「需要规划」信号，规划者下次唤醒会立即规划。不带参数运行。
规划者上次已经回应过信号、之后执行者也没做成任何事时，不重复发（否则规划者和执行者会互相唤醒、一起空转）。"""
import os, json, datetime
from _textify import BASE
D = os.path.join(BASE, '_versions')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
sent_p = os.path.join(D, 'need_plan_sent.txt')
last_sent = open(sent_p).read().strip() if os.path.exists(sent_p) else ''
try:
    planned_at = json.load(open(os.path.join(D, 'plan_state.json'))).get('planned_at', '')
except (OSError, ValueError):
    planned_at = ''
try:
    idle = int(open(os.path.join(D, 'executor_idle.txt')).read().strip())
except (OSError, ValueError):
    idle = 0
if last_sent and planned_at > last_sent and idle > 0:
    print(f'不重复发信号：规划者 {planned_at[11:16]} 已回应过上次信号（{last_sent[11:16]}），之后仍没有新队列。等审查、设计卡或 Dk 的答复带来新输入')
else:
    open(os.path.join(D, 'need_plan.flag'), 'w').write(now)
    open(sent_p, 'w').write(now)
    print('已发出「需要规划」信号')
