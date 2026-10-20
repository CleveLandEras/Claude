"""执行者用：每轮结束前运行一次，记录本轮完成并释放锁。不带参数运行。"""
import os, datetime
from _textify import BASE
from _lock import release
d = os.path.join(BASE, '_versions'); os.makedirs(d, exist_ok=True)
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
open(os.path.join(d, 'executor_rounds.log'), 'a').write(now + '\n')
open(os.path.join(d, 'executor_idle.txt'), 'w').write('0')  # 有实质工作，空转计数清零
release('executor')
print('已记录执行者轮次并释放锁：', now)
