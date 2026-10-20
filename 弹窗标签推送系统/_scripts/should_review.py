"""审查者用：判断本次要不要审查（要审查时上锁）。不带参数运行。
触发（任一）：① 上次审查后执行者满 2 轮；② 推进计划写了「申请过审」，而审查记录最后一节还没有「过审审核」；
③ 上次审查后执行者至少做了 1 轮，并且执行者已经休眠（不会再有第 2 轮，不能干等）。
2026-10-08 加 ②③：之前只看轮数，执行者没活休眠后审查永远不触发，过审审核卡了一个多小时。"""
import os, re
from _textify import BASE
from _lock import acquire
d = os.path.join(BASE, '_versions')
stamp = os.path.join(d, 'reviewed', '_reviewed_at.txt')
last = open(stamp).read().strip() if os.path.exists(stamp) else ''
log = os.path.join(d, 'executor_rounds.log')
rounds = [l.strip() for l in open(log)] if os.path.exists(log) else []
since = [r for r in rounds if r[:16] > last[:16]] if last else rounds
plan_p = os.path.join(BASE, '过程记录', '推进计划.md')
plan = open(plan_p, encoding='utf-8').read() if os.path.exists(plan_p) else ''
rec_p = os.path.join(BASE, '过程记录', '审查记录.md')
rec = open(rec_p, encoding='utf-8').read() if os.path.exists(rec_p) else ''
secs = re.split(r'\n(?=## )', rec)
last_sec = secs[-1] if secs else ''
applied = bool(re.search(r'^结论：[^\n]*申请过审', plan, re.M))
has_verdict = bool(re.search(r'过审审核[：:]\s*\**\s*(通过|不通过)', last_sec))
import datetime as _dt
try:
    _rv = _dt.datetime.strptime(last[:16], '%Y-%m-%d %H:%M').timestamp() if last else 0
except ValueError:
    _rv = 0
plan_newer = os.path.getmtime(plan_p) > _rv + 60 if os.path.exists(plan_p) else False
# 申请过审，且（最后一节没有真正的通过/不通过结论，或推进计划在上次审查之后又改过）→ 待过审审核
gate_pending = applied and (not has_verdict or plan_newer)
asleep = os.path.exists(os.path.join(d, 'executor_sleep.flag'))
print('上次审查：', last or '从未')
print('此后执行者完成轮数：', len(since), '｜执行者休眠：', '是' if asleep else '否', '｜待过审审核：', '是' if gate_pending else '否')
reasons = []
if not last or len(since) >= 2: reasons.append('执行者满两轮')
if gate_pending: reasons.append('推进计划申请过审，还没有过审审核')
if len(since) >= 1 and asleep: reasons.append('执行者已休眠，剩下的改动不会再凑满两轮')
if not reasons:
    print('结论：跳过（不满两轮，也没有待做的过审审核）')
else:
    ok, t = acquire('reviewer', 50)
    print('触发原因：', '；'.join(reasons))
    print('结论：审查（已上锁）' if ok else f'结论：跳过（另一次审查 {t} 开始，仍在进行）')
