"""执行者用：本次会话没有找到实质工作时，用它代替 round_done.py 结束。不带参数运行。
释放执行锁；空转不计入执行者轮次（不会触发审查、规划）；连续空转 3 次就进入休眠，直到推进计划、审查记录、设计卡或任务清单有更新。"""
import os, datetime
from _textify import BASE
from _lock import release

D = os.path.join(BASE, '_versions')
ip = os.path.join(D, 'executor_idle.txt')
try:
    n = int(open(ip).read().strip()) + 1
except (OSError, ValueError):
    n = 1
open(ip, 'w').write(str(n))
release('executor')
if n == 1:
    print('连续第 1 次空转：可以在进展日志写一行「等待：缺什么、谁来补」。执行锁已释放')
else:
    print(f'连续第 {n} 次空转：不要写进展日志、任务清单。执行锁已释放')
if n >= 3:
    open(os.path.join(D, 'executor_sleep.flag'), 'w').write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('已熔断：执行者进入休眠，推进计划、审查记录、设计卡、任务清单任何一个有更新就会自动唤醒')
