# 规划者只读：检索阶段产出中关于弹窗/推送效果数据（发送、曝光、点击）"查不到/缺失/没有"类表述
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, glob, os
root = _ROOT + ''
terms = ['查不到', '查不了', '无从查', '没有曝光', '无曝光', '曝光点击', '曝光、点击', '点击记录', '发送记录', '到达记录',
         '埋点', '本地没有', '缺失', '无记录', '没有记录', '看不到效果', '效果数据', '建议补充', '要新增的数据收集', '数据收集']
files = sorted(glob.glob(os.path.join(root, '阶段[1-8]_*.html')))
for f in files:
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=' * 60)
    print(os.path.basename(f), len(t))
    counts = {k: t.count(k) for k in terms}
    print({k: v for k, v in counts.items() if v})
    for k in ['查不到', '查不了', '没有曝光', '无曝光', '点击记录', '发送记录', '埋点', '无记录', '没有记录', '效果数据', '缺失']:
        for m in list(re.finditer(re.escape(k), t))[:6]:
            s = max(0, m.start() - 90); e = min(len(t), m.end() + 90)
            print('  [' + k + '] …' + t[s:e] + '…')
