"""执行者用：连续工作时，每完成一个工作单元（但会话还要继续）运行一次：记录一轮，不释放锁。不带参数运行。"""
import os, datetime
from _textify import BASE
d = os.path.join(BASE, '_versions')
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
open(os.path.join(d, 'executor_rounds.log'), 'a').write(now + '\n')
open(os.path.join(d, 'executor_idle.txt'), 'w').write('0')  # 有实质工作，空转计数清零
print('已记录一个工作单元（锁保留，会话继续）：', now)
