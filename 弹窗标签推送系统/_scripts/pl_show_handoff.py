import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import pathlib
p = pathlib.Path(_ROOT + '/归档/规则_旧/项目交接_对话要点.md')
lines = p.read_text(encoding='utf-8').splitlines()
for i, l in enumerate(lines):
    if '18:2x 进展' in l or '18:0x' in l and 'V2' in l:
        for j in range(max(0, i-3), min(len(lines), i+6)):
            print(j+1, lines[j])
        print('-----')
# also list V2 script slide titles
s = pathlib.Path(_ROOT + '/_scripts/an_呈交版V2_生成.py')
print('script exists', s.exists(), s.stat().st_size if s.exists() else 0)
