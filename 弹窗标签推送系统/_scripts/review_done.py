"""审查者用：审查结束时运行，释放审查锁，并记下审查结束时间（规划者按它判断「上次规划后完成了审查」）。不带参数运行。"""
import os, datetime
from _textify import BASE
from _lock import release
release('reviewer')
d = os.path.join(BASE, '_versions', 'reviewed'); os.makedirs(d, exist_ok=True)
open(os.path.join(d, '_review_done_at.txt'), 'w').write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('审查锁已释放，已记录审查结束时间')
