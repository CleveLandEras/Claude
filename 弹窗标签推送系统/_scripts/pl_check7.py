import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import subprocess, pathlib
base = pathlib.Path(_ROOT + '')
r = subprocess.run(['python3', str(base / '_scripts/check_format.py')], capture_output=True, text=True, cwd=base)
out = r.stdout + r.stderr
lines = out.splitlines()
print('\n'.join(l for l in lines if '阶段7' in l or '✘' in l or '汇总' in l)[:3000])
print('---total lines', len(lines))
html = (base / '阶段7_方案验证.html').read_text(encoding='utf-8')
for k in ['14 个现有后台可做', '可全部消除', '漏洞少', '变为 26', '多不变', '待确认', '乙以']:
    print(k, html.count(k))
