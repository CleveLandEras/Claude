# 由 分析/夜间改动_内容清单_1016.json 生成 简报/2026-10-16_昨晚具体改动.html（逐块写清昨晚在推送后台设计里改了什么）
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import json, html, collections

SRC = _ROOT + '/分析/夜间改动_内容清单_1016.json'
OUT = _ROOT + '/简报/2026-10-16_昨晚具体改动.html'
REAL = {'Dk原话', 'Jira', '事故', '现行规则', '同事草稿'}
NAME = {'Dk原话': '你的原话', 'Jira': 'Jira 工单', '事故': '事故单', '现行规则': '现行规则', '同事草稿': '同事草稿',
        '对标': '对标', '同行审': 'AI 同行审', '推断': '推断'}

D = json.load(open(SRC, encoding='utf-8'))
blocks = [b for b in D if b['块'] != '昨晚改掉的原设计']
changed = next((b['条目'] for b in D if b['块'] == '昨晚改掉的原设计'), [])
items = [x for b in blocks for x in b['条目']]
n, n_real = len(items), sum(x['出处类型'] in REAL for x in items)
cnt = collections.Counter(x['出处类型'] for x in items)
e = html.escape


def chip(t):
    cls = 'real' if t in REAL else 'weak'
    return f'<span class="chip {cls}">{e(NAME.get(t, t))}</span>'


maxb = max(len(b['条目']) for b in blocks)
bars = ''
for b in blocks:
    r = sum(x['出处类型'] in REAL for x in b['条目'])
    w = len(b['条目']) - r
    bars += (f'<div class="bar"><span class="bl">{e(b["块"])}</span><div class="tr">'
             f'<div class="seg real" style="width:{r / maxb * 100:.1f}%">{r or ""}</div>'
             f'<div class="seg weak" style="width:{w / maxb * 100:.1f}%">{w or ""}</div></div>'
             f'<span class="bn">{len(b["条目"])}</span></div>')

sections = ''
for b in blocks:
    r = sum(x['出处类型'] in REAL for x in b['条目'])
    rows = ''.join(
        f'<div class="item"><div class="what">{e(x["改了什么"])}</div>'
        f'<div class="meta">{chip(x["出处类型"])}<span class="why">{e(x["为什么"])}</span>'
        f'<span class="where">{e(x["在哪"])}</span></div></div>' for x in b['条目'])
    sections += (f'<section><h2>{e(b["块"])}：补了 {len(b["条目"])} 项，'
                 f'{r} 项有现实出处</h2>{rows}</section>')

ch_rows = ''.join(
    f'<tr><td>{e(x.get("项目", ""))}</td><td class="old">{e(x.get("原来", ""))}</td>'
    f'<td>{e(x.get("现在", ""))}</td><td>{chip(x["出处类型"])} {e(x["为什么"])}</td></tr>' for x in changed)

weak_desc = '、'.join(f'{NAME[k]} {cnt[k]}' for k in ('同行审', '对标', '推断') if cnt.get(k))
real_desc = '、'.join(f'{NAME[k]} {cnt[k]}' for k in ('Dk原话', 'Jira', '事故', '现行规则', '同事草稿') if cnt.get(k))

page = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>昨晚具体改动</title><style>
:root{{--bg:#fbfaf7;--card:#fff;--ink:#1f1e1b;--mute:#6b6a64;--line:#e6e4dc;--real:#0f6e56;--realbg:#e1f5ee;--weak:#854f0b;--weakbg:#faeeda}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:36px 40px 60px}}
h1{{font-size:26px;font-weight:600;margin:0 0 6px}} .sub{{color:var(--mute);margin:0 0 22px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:26px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px}}
.kpi b{{display:block;font-size:24px}} .kpi span{{color:var(--mute);font-size:13px}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 22px;margin-bottom:28px}}
.panel h3{{margin:0 0 12px;font-size:15px}}
.bar{{display:grid;grid-template-columns:170px 1fr 36px;gap:10px;align-items:center;margin:7px 0;font-size:14px}}
.tr{{display:flex;gap:2px;height:20px}} .seg{{height:20px;border-radius:3px;color:#fff;font-size:12px;display:flex;align-items:center;justify-content:center}}
.seg.real{{background:var(--real)}} .seg.weak{{background:#ba7517}} .bn{{color:var(--mute);text-align:right}}
.legend{{display:flex;gap:18px;font-size:13px;color:var(--mute);margin-top:10px}} .legend i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}}
section{{margin-top:30px}} h2{{font-size:18px;font-weight:600;margin:0 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
.item{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:8px 0}}
.what{{font-size:15px}} .meta{{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;margin-top:6px;font-size:13px;color:var(--mute)}}
.where{{color:#8a887f}}
.chip{{font-size:12px;padding:1px 8px;border-radius:6px;white-space:nowrap}} .chip.real{{background:var(--realbg);color:var(--real)}} .chip.weak{{background:var(--weakbg);color:var(--weak)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;font-size:14px}}
th,td{{text-align:left;padding:9px 12px;border-top:1px solid var(--line);vertical-align:top}} th{{background:#f3f1ea;font-weight:600;border-top:none}}
td.old{{color:var(--mute)}}
</style></head><body><main>
<h1>昨晚在推送后台设计里补了 {n} 项，只有 {n_real} 项有现实出处</h1>
<p class="sub">其余 {n - n_real} 项来自 {weak_desc}；有现实出处的是 {real_desc}。下面逐块写清每项改了什么、为什么、在原型和需求文档的哪里。</p>
<div class="kpis"><div class="kpi"><b>{n} 项</b><span>新增或补强的设计</span></div>
<div class="kpi"><b>{n_real} 项</b><span>有现实出处</span></div>
<div class="kpi"><b>{n - n_real} 项</b><span>只来自同行审、对标或推断</span></div>
<div class="kpi"><b>{len(changed)} 处</b><span>改掉了原来的设计</span></div></div>
<div class="panel"><h3>各块补了几项、多少有现实出处</h3>{bars}
<div class="legend"><span><i style="background:var(--real)"></i>有现实出处（你的原话、Jira、事故单、现行规则、同事草稿）</span><span><i style="background:#ba7517"></i>只有 AI 同行审、对标或推断</span></div></div>
{sections}
<section><h2>改掉的原设计：{len(changed)} 处</h2><table><tr><th style="width:16%">项目</th><th style="width:24%">原来</th><th style="width:30%">现在</th><th>为什么</th></tr>{ch_rows}</table></section>
</main></body></html>'''
open(OUT, 'w', encoding='utf-8').write(page)
print(OUT, n, n_real, len(changed))
