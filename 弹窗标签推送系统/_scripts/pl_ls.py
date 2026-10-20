import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import os
root = _ROOT + ''
for sub in ['', '过程记录', '规则与交接', '分析']:
    d = os.path.join(root, sub)
    print('==', sub or '根目录')
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            import time
            print(time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(p))), f)
