"""Q108 整合扫描：决策汇报里的过时状态句候选（只读）。按行号列出；更正记录（summary 含「更正记录」之后）单独标注。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
p = os.path.join(BASE, '决策汇报.html')
lines = open(p, encoding='utf-8').read().split('\n')
corr_start = next((i for i, l in enumerate(lines, 1) if '<summary>更正记录' in l), 10**9)
terms = ['再定', '在写', '读法', '到决策点', '环节4', '方案环节', '待规划者', '随后续', '进行中', '待审', '审查后', '整合', '第 2 件', '第 3 件', '第 2、3 条', '第五节第 1、2 条', '第五节第 3 条', '13 个待决', '已有推荐', '件在写', '选项和推荐', '原决定 A', '原决定 C']
for t in terms:
    hits = []
    for i, l in enumerate(lines, 1):
        if i >= corr_start:
            continue
        for m in re.finditer(re.escape(t), l):
            j = m.start()
            hits.append(f'  L{i}: …{re.sub("<[^>]+>", "", l[max(0, j-70):j+len(t)+50])}…')
    print(f'[{t}] {len(hits)} 处（更正记录以外）')
    for h in hits[:12]:
        print(h)
print('更正记录起始行', corr_start)
