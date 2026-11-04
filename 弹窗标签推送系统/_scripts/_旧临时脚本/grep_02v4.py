# 只读检索：02 迭代稿 v4 差距评估用
import re, pathlib
base = pathlib.Path('/Users/decheng.huang/claude/弹窗标签推送系统')
kw = ['回流', '首储', '开放期', '已经先存储了', '月月抽', '问题 2', '跳过']
def text(p):
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return [re.sub(r'\s+', ' ', l).strip() for l in s.splitlines()]
for name in ['claude_弹窗标签推送_盘点.html']:
    lines = text(base / name)
    print('=====', name)
    for i, l in enumerate(lines):
        if l and any(k in l for k in kw):
            print(i, l[:300])
for name in ['08_弹窗效果评估方案.md', 'C2_新标签脚本草稿.md', 'C1_卡点解锁优先级.md']:
    print('=====', name)
    for i, l in enumerate((base / name).read_text(encoding='utf-8').splitlines()):
        if any(k in l for k in ['首储', '开放', '已经先存储了', '月月抽', '从未储值']):
            print(i + 1, l[:300])
