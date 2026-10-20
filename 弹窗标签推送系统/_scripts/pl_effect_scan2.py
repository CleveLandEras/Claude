# 规划者只读：列出阶段 3–8 中含「记录」「关闭事件」「召回后」「到达率」「无数据」的片段，评估 Dk 10/10 答复的回溯范围
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
root = _ROOT + ''
keys = ['召回后', '关闭事件', '关闭记录', '到达率', '无数据', '无发送', '整体层面', '数据无记载', '已有记录', '有记录', '记录缺失', '效果查不到', '缺曝光']
for f in sorted(glob.glob(os.path.join(root, '阶段[1-8]_*.html'))):
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=' * 60)
    print(os.path.basename(f), {k: t.count(k) for k in keys if t.count(k)})
    seen = []
    for k in keys:
        for m in re.finditer(re.escape(k), t):
            if any(abs(m.start() - s) < 120 for s in seen):
                continue
            seen.append(m.start())
            s = max(0, m.start() - 70); e = min(len(t), m.end() + 70)
            print('  [' + k + '] …' + t[s:e] + '…')
