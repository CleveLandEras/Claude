import re, os
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def vis(t):
    t = re.sub(r'<details[\s\S]*?</details>', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    return t
words = ['理由弱', '理由不成立', '不独立成立', '只能按成本和风险排', '条件式推荐', '→ 丙', '不承诺用储值证明', '不能承诺', '可代替随机分组', '按工作原则 v2 重理', '判读']
files = ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/08_弹窗效果评估方案.md', '支撑文件/04_弹窗功能缺口需求.md', '支撑文件/07_推送需求.md', '支撑文件/05_标签需求.md']
sd = sorted(os.listdir(B + '支撑文件'))
print('支撑文件:', sd)
for f in files:
    p = B + f
    if not os.path.exists(p):
        # try match by prefix
        pre = os.path.basename(f)[:3]
        m = [x for x in sd if x.startswith(pre)]
        if not m:
            print('缺', f); continue
        p = B + '支撑文件/' + m[0]
    t = open(p, encoding='utf-8').read()
    v = vis(t) if p.endswith('.html') else t
    # cut correction record if present
    for mk in ['更正记录', '修改记录']:
        i = v.rfind(mk)
        if i > len(v) * 0.6:
            v = v[:i]; break
    print('==', os.path.basename(p), {w: v.count(w) for w in words})
print('A36 存在:', os.path.exists(B + '分析/A36_验证计划.md'))
