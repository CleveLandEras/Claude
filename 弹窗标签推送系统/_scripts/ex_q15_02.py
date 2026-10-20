import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base = _ROOT + '/支撑文件/'
t = open(base + '02_弹窗分人群定制方案.html', encoding='utf-8').read()
txt = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
txt = re.sub(r'</(tr|p|li|h\d|div)>', '\n', txt)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = re.sub(r'[ \t]+', ' ', txt)
lines = [l.strip() for l in txt.split('\n') if l.strip()]
print('02 行数', len(lines))
for i, l in enumerate(lines[:110]):
    print(i, l[:220])
print('\n===== 07')
t7 = open(base + '07_推送需求.md', encoding='utf-8').read()
for l in t7.split('\n'):
    if re.search(r'标签|群组|定向|人群', l):
        print('-', l[:300])
