#!/usr/bin/env python3
# 把已写入原型的措辞改动（分析/标准判卷/推送后台_原型措辞/改动_*.json）列成改前、改后对照页。
# 用法：python3 _scripts/pl_原型措辞对照.py C0 C1 …   （只列给出的段）
import json, sys, re, html, pathlib
B = pathlib.Path(__file__).resolve().parent.parent
D = B / '分析/标准判卷/推送后台_原型措辞'
src = (B / '推送系统后台集成需求/3_原型.html').read_text(encoding='utf-8')
secs = [(m.start(), m.group(1)) for m in re.finditer(r'<section id="([^"]+)"', src)]
name = {'overview': '全景', 'tasks': '按任务走一遍', 'appx': '附录'}
txt = lambda s: html.escape(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip())
rows = []
for seg in sys.argv[1:]:
    for it in json.load(open(D / f'改动_{seg}.json', encoding='utf-8')):
        pos = src.find(it['new'])
        sid = max([s for s in secs if s[0] <= pos], default=(0, '页首'))[1] if pos >= 0 else '?'
        where = name.get(sid, f'第 {sid[1:]} 页' if sid.startswith('p') else sid)
        rows.append(f"<tr><td>{where}</td><td>{txt(it['old'])}</td><td>{txt(it['new'])}</td><td>{html.escape(it.get('why', ''))}</td></tr>")
css = 'body{font:14px/1.6 -apple-system,"PingFang SC",sans-serif;margin:24px 32px;background:#fff;color:#222}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:6px 8px;vertical-align:top;text-align:left}th{background:#f4f4f4}td:nth-child(1){white-space:nowrap}td:nth-child(2){color:#888}'
out = D / '改动对照.html'
out.write_text(f'<!doctype html><meta charset="utf-8"><title>原型措辞改动对照</title><style>{css}</style><h1>原型措辞改动对照（{len(rows)} 处）</h1><table><tr><th>位置</th><th>改前</th><th>改后</th><th>原因</th></tr>{"".join(rows)}</table>', encoding='utf-8')
print(out, len(rows))
