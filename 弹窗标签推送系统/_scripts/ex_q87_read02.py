import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob
import os
import sys
sys.path.insert(0, _ROOT + '/_scripts')
from _textify import BASE, textify  # noqa: E402

for p in sorted(glob.glob(os.path.join(BASE, '支撑文件', '02_*.html'))):
    s = textify(p)
    print(os.path.relpath(p, BASE), len(s))
    print(s[:30000])
