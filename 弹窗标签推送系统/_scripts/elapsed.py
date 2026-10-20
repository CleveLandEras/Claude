"""执行者用：输出本次会话从拿到锁起已经工作了多少分钟，以及是否还可以开始新的工作单元（45 分钟内可以）。不带参数运行。"""
import os, datetime
from _textify import BASE
p = os.path.join(BASE, '_versions', 'executor.lock')
if not os.path.exists(p):
    print('没有执行锁'); raise SystemExit
t = datetime.datetime.strptime(open(p).read().strip(), '%Y-%m-%d %H:%M:%S')
m = (datetime.datetime.now() - t).total_seconds() / 60
print(f'本次会话已工作 {m:.0f} 分钟；', '可以开始新的工作单元' if m < 45 else '不要再开始新的工作单元，收尾结束')
