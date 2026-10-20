"""规划者用：判断本次是否需要（重新）规划，需要则上锁。不带参数运行。
触发条件（任一）：从未规划；执行者发出「需要规划」信号；队列中未完成项少于 3；上次规划后又完成了一次审查；
上次规划后执行者完成满 6 轮；任务清单第四节（答复登记）有变化；交付物文件集合有变化。"""
import os, re, json, hashlib
from _textify import BASE, deliverables
from _lock import acquire
D = os.path.join(BASE, '_versions'); os.makedirs(D, exist_ok=True)
state_p = os.path.join(D, 'plan_state.json')
st = json.load(open(state_p)) if os.path.exists(state_p) else {}
last = st.get('planned_at', '')

def sec4_hash():
    s = open(os.path.join(BASE, '过程记录', '任务清单.md'), encoding='utf-8').read()
    m = re.search(r'\n## 四、.*?(?=\n## )', s, re.S)
    return hashlib.md5((m.group(0) if m else '').encode()).hexdigest()

plan_p = os.path.join(BASE, '过程记录', '推进计划.md')
pending = len(re.findall(r'^- \[ \]', open(plan_p, encoding='utf-8').read(), re.M)) if os.path.exists(plan_p) else 0
rev_p = os.path.join(D, 'reviewed', '_reviewed_at.txt')
reviewed_at = open(rev_p).read().strip() if os.path.exists(rev_p) else ''
done_p = os.path.join(D, 'reviewed', '_review_done_at.txt')
review_done_at = open(done_p).read().strip() if os.path.exists(done_p) else ''
log = os.path.join(D, 'executor_rounds.log')
rounds = [l.strip() for l in open(log)] if os.path.exists(log) else []
rounds_since = len([r for r in rounds if r[:16] > last[:16]]) if last else len(rounds)
files = sorted(os.path.basename(p) for p in deliverables())

reasons = []
if not last: reasons.append('从未规划')
else:
    # 队列少但上次规划后执行者一轮都没做、也没有新审查时，重排也不会有新东西，不触发（防止规划者空转）
    if pending < 3 and (rounds_since > 0 or review_done_at[:16] > last[:16]): reasons.append(f'队列未完成项只剩 {pending} 项')
    if os.path.exists(os.path.join(D, 'need_plan.flag')): reasons.append('执行者发出「需要规划」信号（队列已空）')
    if review_done_at[:16] > last[:16]: reasons.append(f'上次规划后完成了审查（{review_done_at}）')
    if rounds_since >= 6: reasons.append(f'上次规划后执行者已完成 {rounds_since} 轮')
    if st.get('sec4') != sec4_hash(): reasons.append('答复登记（任务清单第四节）有变化')
    if st.get('files') != files: reasons.append('交付物文件有增减')
print('上次规划：', last or '从未')
print('队列未完成项：', pending, '｜上次规划后执行者轮数：', rounds_since)
if not reasons:
    print('结论：跳过（无触发条件）')
else:
    ok, t = acquire('planner', 50)
    print('触发原因：', '；'.join(reasons))
    print('结论：规划（已上锁）' if ok else f'结论：跳过（另一次规划 {t} 开始，仍在进行）')
