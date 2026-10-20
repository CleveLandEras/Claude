"""规划者用：写完推进计划后运行，记录规划时间与当前状态并释放锁。不带参数运行。"""
import os, re, json, hashlib, datetime
from _textify import BASE, deliverables
from _lock import release
D = os.path.join(BASE, '_versions')
s = open(os.path.join(BASE, '过程记录', '任务清单.md'), encoding='utf-8').read()
m = re.search(r'\n## 四、.*?(?=\n## )', s, re.S)
st = {'planned_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      'sec4': hashlib.md5((m.group(0) if m else '').encode()).hexdigest(),
      'files': sorted(os.path.basename(p) for p in deliverables())}
json.dump(st, open(os.path.join(D, 'plan_state.json'), 'w'), ensure_ascii=False)
release('planner')
f = os.path.join(D, 'need_plan.flag')
if os.path.exists(f): os.remove(f)
print('规划已记录并释放锁：', st['planned_at'])
