#!/usr/bin/env python3
"""把验收官答卷里的问题排成一页，让 Dk 逐条点「同意／不同意」。

用法：python3 做校准页.py <答卷文件夹> <输出文件夹>
输出文件夹里要有：
  稿件信息.json：需求原文；每份稿的序号、全名、时间、读者、用途、补充；不判的条目及原因；要改的内部说法。
  图/<稿件键>/：pNN.png 或 sNN.jpg 按页码配图；只有一张图的稿件放 图/<稿件键>.jpg（在小节开头放一次）；
  <稿件键>_页码对照.json（可选）：{"页码": ["图文件名", …]}，用于分段截图的稿件。
答卷文件名以「稿件<键>」开头（键如 甲乙丙丁），条目格式是「N. [类别] 位置｜原文…｜问题…｜依据…｜建议…」或分行写。
"""
import glob
import html
import json
import os
import re
import sys

ITEM = re.compile(r'^\s*(?:\*\*)?(\d{1,2})\.\s*(?:\*\*)?\s*\[([^\]]+)\]\s*(.*)')
END = re.compile(r'^\s*(?:##\s*)?(清单结果|没法判断|相关文件)')
LABEL = re.compile(r'^[\s\-*]*(?:\*\*)?(位置|本稿原文|原文|问题|依据|建议|改法)(?:\*\*)?\s*[:：]?\s*')
FIELD = {'位置': '位置', '本稿原文': '稿件原文', '原文': '稿件原文', '问题': '验收官说的问题',
         '依据': '依据', '建议': '建议', '改法': '建议'}
ORDER = ['位置', '稿件原文', '验收官说的问题', '依据', '建议']


def parse(path):
    items, cur, on = [], None, False
    for line in open(path, encoding='utf-8'):
        if '会被退回的问题' in line:
            on = True
            continue
        if not on:
            continue
        if END.match(line):
            break
        m = ITEM.match(line)
        if m:
            cur = {'n': int(m.group(1)), 'cat': m.group(2), 'text': [m.group(3).strip().strip('*')]}
            items.append(cur)
        elif cur is not None and line.strip():
            cur['text'].append(line.rstrip())
    return items


def fields(lines):
    """把一条意见拆成 位置／稿件原文／验收官说的问题／依据／建议。"""
    pieces = []
    for line in lines:
        starts_label = bool(re.match(r'^\s*[-*]\s*(\*\*)?(位置|本稿原文|原文|问题|依据|建议|改法)', line))
        parts, buf, depth = [], '', 0
        for ch in line:  # 引号「」里的｜是原文的一部分，不拆
            depth += (ch == '「') - (ch == '」')
            if ch == '｜' and depth <= 0:
                parts.append(buf); buf = ''
            else:
                buf += ch
        parts.append(buf)
        for k, part in enumerate(parts):
            new = k > 0 or starts_label or not pieces
            pieces.append((new, part))
    out, cur = {}, None
    for new, part in pieces:
        if not part.strip():
            continue
        m = LABEL.match(part)
        label = None
        if m and new and (part[m.end() - 1:m.end()] in '：:' or part[m.end():m.end() + 1] in '「“第' or m.group(1) in ('原文', '本稿原文')):
            label = FIELD[m.group(1)]
            part = part[m.end():]
        elif m and new and m.group(1) == '问题':
            label = FIELD['问题']
        if label is None and new:
            label = '位置' if not out else ('验收官说的问题' if cur in (None, '位置', '稿件原文') else cur)
        if label is None:
            label = cur or '验收官说的问题'
        out.setdefault(label, []).append(part.strip(' ｜'))
        cur = label
    return {k: '\n'.join(v).strip() for k, v in out.items()}


def pages(text):
    """按出现顺序取页码；跨度超过 3 页的范围（如「第 17–29 页没看到」）不取。"""
    out = []
    pat = re.compile(r'第?\s*(\d{1,2})\s*[–-]\s*(\d{1,2})\s*页|第\s*([\d、，,\s]+?)\s*页|页\s*(\d{1,2})')
    for m in pat.finditer(text):
        if m.group(1):
            a, b = int(m.group(1)), int(m.group(2))
            nums = list(range(a, b + 1)) if 0 <= b - a <= 3 else []
        elif m.group(3):
            nums = [int(x) for x in re.findall(r'\d{1,2}', m.group(3))]
        else:
            nums = [int(m.group(4))]
        for n in nums:
            if n not in out:
                out.append(n)
    return out[:6]


def main():
    src, out = sys.argv[1], sys.argv[2]
    meta = json.load(open(os.path.join(out, '稿件信息.json'), encoding='utf-8'))
    skip, swaps = meta.get('不判', {}), meta.get('改说法', {})
    cards, sections, skipped = [], [], []
    gist_file = os.path.join(out, '重点.json')
    gist = json.load(open(gist_file, encoding='utf-8')) if os.path.exists(gist_file) else None
    paths = sorted(glob.glob(os.path.join(src, '稿件*.md')),
                   key=lambda p: meta['稿件'].get(os.path.basename(p)[2], {}).get('序', 99))
    for path in paths:
        key = os.path.basename(path)[2]
        info = meta['稿件'][key]
        no = info['序']
        single = os.path.join(out, '图', key + '.jpg')
        img_dir = os.path.join(out, '图', key)
        pmap_file = os.path.join(out, f'{key}_页码对照.json')
        pmap = json.load(open(pmap_file, encoding='utf-8')) if os.path.exists(pmap_file) else {}
        who = f'当时的读者：{html.escape(info["读者"])}｜用途：{html.escape(info["用途"])}' + (f'｜{html.escape(info["补充"])}' if info.get('补充') else '')
        if gist:
            sec = [f'<h2 class="sh"><span class="no">第 {no} 份</span>{html.escape(info["名"])}（{html.escape(info["时间"])}）<small>{who}</small></h2>']
            if os.path.exists(single):
                sec.append(f'<details class="ev"><summary>看这份稿</summary><div class="pics one"><img class="zoom" loading="lazy" src="图/{key}.jpg" alt="稿件图"></div></details>')
        else:
            sec = [f'<h2><span class="no">第 {no} 份</span>{html.escape(info["名"])}（{html.escape(info["时间"])}）</h2>', f'<p class="meta">{who}</p>']
            if os.path.exists(single):
                sec.append(f'<div class="pics one"><img class="zoom" loading="lazy" src="图/{key}.jpg" alt="稿件图"></div>')
        n_items = 0
        for it in parse(path):
            sid = f'{key}-{it["n"]}'
            iid = f'{no}-{it["n"]}'
            if sid in skip:
                skipped.append(f'{iid}：{skip[sid]}')
                continue
            if gist and iid not in gist['条目']:
                continue
            n_items += 1
            raw = '\n'.join(it['text'])
            for a, b in swaps.items():
                raw = raw.replace(a, b)
            f = fields(raw.split('\n'))
            imgs, caps = [], {}

            def cap(c, p=None):
                m = re.match(r'段(\d+)', c)
                if m:
                    return f'原型截图第 {int(m.group(1))} 段' + (f'（含第 {p} 页）' if p else '')
                m = re.match(r'[ps](\d+)', c)
                return f'第 {int(m.group(1))} 页' if m else ''
            override = meta.get('配图覆盖', {}).get(sid)
            if override:
                for c in override:
                    rel = f'图/{key}/{c}'
                    if os.path.exists(os.path.join(out, rel)):
                        imgs.append(rel); caps[rel] = cap(c)
            elif not os.path.exists(single):
                for p in pages(raw):
                    cands = pmap.get(str(p), []) or [f'p{p:02d}.png', f's{p:02d}.jpg']
                    for c in cands:
                        rel = f'图/{key}/{c}'
                        if os.path.exists(os.path.join(out, rel)) and rel not in imgs:
                            imgs.append(rel); caps[rel] = cap(c, p if pmap else None)
            rows = ''
            for k in ORDER:
                if k in f and f[k] and k != '建议':
                    rows += f'<div class="row"><span class="k">{k}</span><div class="v">{html.escape(f[k])}</div></div>'
            sugg = f'<details><summary>验收官的修改建议</summary><div class="v">{html.escape(f["建议"])}</div></details>' if f.get('建议') else ''
            pics = ''.join(f'<figure><img class="zoom" loading="lazy" src="{i}" alt="{caps.get(i, "相关页")}"><figcaption>{caps.get(i, "")}</figcaption></figure>' for i in imgs[:6])
            if gist:
                g = gist['条目'][iid]
                sec.append(f'''<div class="item" data-id="{iid}">
  <div class="line"><span class="id">{iid}</span><span class="gist">{html.escape(g["重点"])}<small class="where">在哪：{html.escape(g["在哪"])}</small></span>
    <span class="btns"><label><input type="radio" name="{iid}" value="同意"> 同意</label><label><input type="radio" name="{iid}" value="不同意"> 不同意</label></span></div>
  <input type="text" class="why" placeholder="不同意：一句话说哪里不对（可空）">
  <details class="ev"><summary>展开看证据</summary>{rows}{sugg}{'<div class="pics">' + pics + '</div><p class="hint">点图放大，再点缩回</p>' if pics else ''}</details>
</div>''')
                cards.append(iid)
                continue
            sec.append(f'''<div class="card item" data-id="{iid}">
  <div class="top"><span class="id">{iid}</span><span class="tag">{html.escape(it["cat"])}</span></div>
  {rows}{sugg}
  {'<div class="pics">' + pics + '</div><p class="hint">点图放大，再点缩回</p>' if pics else ''}
  <div class="vote">
    <label><input type="radio" name="{iid}" value="同意"> 同意：这处确实该改</label>
    <label><input type="radio" name="{iid}" value="不同意"> 不同意：不算问题或不值得改</label>
    <input type="text" class="why" placeholder="不同意时写一句哪里不对（可空）">
  </div>
</div>''')
            cards.append(iid)
        if n_items:
            sections.append('\n'.join(sec))
    if gist:
        page = (COMPACT.replace('{{N}}', str(len(cards))).replace('{{DONE}}', str(gist.get('已判', 0)))
                .replace('{{REQ}}', html.escape(meta['需求原文']))
                .replace('{{BODY}}', '\n'.join(sections))
                .replace('{{IDS}}', json.dumps(cards, ensure_ascii=False)))
        dest = os.path.join(out, '判这一页.html')
        open(dest, 'w', encoding='utf-8').write(page)
        print(dest, len(cards), '条（精简版）')
        return
    page = (TEMPLATE.replace('{{N}}', str(len(cards)))
            .replace('{{REQ}}', html.escape(meta['需求原文']))
            .replace('{{SKIP}}', html.escape('；'.join(skipped)))
            .replace('{{BODY}}', '\n'.join(sections))
            .replace('{{IDS}}', json.dumps(cards, ensure_ascii=False)))
    dest = os.path.join(out, '判这一页.html')
    open(dest, 'w', encoding='utf-8').write(page)
    print(dest, len(cards), '条；不判：', '、'.join(skipped))


TEMPLATE = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>验收官校准</title>
<style>
:root{--ground:#f3f2ef;--surface:#fff;--ink:#1b1d21;--ink-2:#4a4f56;--muted:#868b92;--line:#e2e0db;--accent:#9a6f24;--blue:#1f63a8;--blue-soft:#e4eef8;--green:#2f6b52;--green-soft:#e2efe8;--red:#a8382b;--red-soft:#f7e6e2;
--sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;--serif:"Songti SC","Noto Serif SC",Georgia,serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#131518;--surface:#1b1e22;--ink:#e9e8e4;--ink-2:#b9bdc2;--muted:#8a9098;--line:#2e3339;--accent:#d6ab5c;--blue:#7ab0e0;--blue-soft:#1b2b3a;--green:#7dbb9c;--green-soft:#1c3128;--red:#e48e7f;--red-soft:#3a211c}}
:root[data-theme="dark"]{--ground:#131518;--surface:#1b1e22;--ink:#e9e8e4;--ink-2:#b9bdc2;--muted:#8a9098;--line:#2e3339;--accent:#d6ab5c;--blue:#7ab0e0;--blue-soft:#1b2b3a;--green:#7dbb9c;--green-soft:#1c3128;--red:#e48e7f;--red-soft:#3a211c}
*{box-sizing:border-box} body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6}
.wrap{max-width:1000px;margin:0 auto;padding:40px 24px 120px}
h1{font-family:var(--serif);font-size:26px;margin:0 0 8px} .sub{color:var(--ink-2);margin:0 0 12px}
.req{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:6px;padding:12px 16px;margin:0 0 10px;font-size:14.5px}
.note{font-size:13.5px;color:var(--muted);margin:0 0 8px}
h2{font-family:var(--serif);font-size:19px;margin:44px 0 6px;display:flex;gap:12px;align-items:baseline} h2 .no{font-family:var(--sans);font-size:13px;font-weight:700;color:var(--accent);white-space:nowrap}
.meta{color:var(--ink-2);font-size:14px;margin:0 0 14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:16px 18px;margin:0 0 12px}
.top{display:flex;gap:10px;align-items:center;margin-bottom:8px} .id{font-weight:700;color:var(--accent)} .tag{font-size:12px;font-weight:700;padding:2px 8px;border-radius:3px;background:var(--blue-soft);color:var(--blue)}
.row{display:grid;grid-template-columns:110px 1fr;gap:10px;padding:6px 0;border-top:1px dashed var(--line)} .row:first-of-type{border-top:0}
.k{font-size:13px;color:var(--muted);font-weight:600} .v{white-space:pre-wrap;font-size:14.5px}
details{margin:6px 0} details summary{cursor:pointer;color:var(--muted);font-size:13px} details .v{color:var(--ink-2);margin-top:6px}
.pics{display:flex;gap:10px;margin:10px 0 0;flex-wrap:wrap} .pics figure{margin:0;flex:0 1 calc(50% - 5px);max-width:calc(50% - 5px);min-width:0} .pics figure img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;cursor:zoom-in;display:block} .pics figcaption{font-size:12px;color:var(--muted);margin-top:3px} .pics figure.big{flex-basis:100%;max-width:100%}
.pics.one img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;cursor:zoom-in}
.pics figure.big img{cursor:zoom-out}
.hint{font-size:12px;color:var(--muted);margin:4px 0 0}
.vote{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;border-top:1px solid var(--line);padding-top:10px;margin-top:10px}
.vote label{cursor:pointer} .why{flex:1;min-width:220px;padding:6px 8px;border:1px solid var(--line);border-radius:4px;background:var(--surface);color:var(--ink);font:inherit}
.item.yes{border-left:4px solid var(--green)} .item.no{border-left:4px solid var(--red)}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--surface);border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:14px;align-items:center;justify-content:center}
button{font:inherit;font-weight:700;padding:8px 16px;border-radius:4px;border:0;background:var(--blue);color:#fff;cursor:pointer}
#out{width:100%;height:120px;margin-top:12px;font:13px var(--sans);display:none}
@media (max-width:720px){.wrap{padding:28px 16px 140px}.row{grid-template-columns:1fr;gap:2px}.pics figure{flex-basis:100%;max-width:100%}}
</style></head><body><div class="wrap">
<h1>验收官多报的 {{N}} 条问题，你认不认</h1>
<p class="sub">下面 4 份是你 10/10–10/14 退回过的旧稿。验收官审它们时，除了你当时指出的问题，还多报了这 {{N}} 条。每条只点「同意」或「不同意」，约 20 分钟；中途关掉不丢。点完按底部「复制结果」，把结果贴给「用好 Claude：进度沟通」。你的判断用来量验收官会不会乱报，以后它按你的标准收紧或放宽。</p>
<div class="req">{{REQ}}</div>
<p class="note">不在这里的几条，你当时已经指出过，不用判——{{SKIP}}。编号「份-条」只用来对结果。</p>
{{BODY}}
<textarea id="out" readonly></textarea>
</div>
<div class="bar"><span id="cnt"></span><button id="copy">复制结果</button></div>
<script>
const IDS={{IDS}}; const KEY='calib_1029_v2';
let saved={}; try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}}
function paint(){let n=0;document.querySelectorAll('.item').forEach(c=>{const v=(saved[c.dataset.id]||{}).v;c.classList.toggle('yes',v==='同意');c.classList.toggle('no',v==='不同意');if(v)n++});document.getElementById('cnt').textContent='已判 '+n+' / '+IDS.length}
document.querySelectorAll('.item').forEach(c=>{const id=c.dataset.id,s=saved[id]||{};
 c.querySelectorAll('input[type=radio]').forEach(r=>{if(r.value===s.v)r.checked=true;r.addEventListener('change',()=>{saved[id]=Object.assign(saved[id]||{},{v:r.value});save();paint()})});
 const w=c.querySelector('.why');w.value=s.w||'';w.addEventListener('input',()=>{saved[id]=Object.assign(saved[id]||{},{w:w.value});save()})});
document.querySelectorAll('img.zoom').forEach(i=>i.addEventListener('click',()=>(i.closest('figure')||i).classList.toggle('big')));
document.getElementById('copy').addEventListener('click',()=>{const lines=IDS.map(id=>{const s=saved[id]||{};return id+' '+(s.v||'未判')+(s.w?'：'+s.w:'')});
 const t='验收官校准 10/29\\n'+lines.join('\\n');const o=document.getElementById('out');o.style.display='block';o.value=t;o.select();
 try{navigator.clipboard.writeText(t).then(()=>{document.getElementById('copy').textContent='已复制'},()=>{document.getElementById('copy').textContent='请手动复制下框文字'})}catch(e){document.getElementById('copy').textContent='请手动复制下框文字'}});
paint();
</script></body></html>'''




_HEAD, _REST = TEMPLATE.split('<h1>', 1)
_TAIL = '<div class="bar">' + _REST.split('<div class="bar">', 1)[1]
COMPACT = _HEAD.replace('</style>', """
.wrap{max-width:1040px}
h2.sh{font-size:16px;margin:22px 0 8px;flex-wrap:wrap} h2.sh small{font-family:var(--sans);font-size:12.5px;color:var(--muted);font-weight:400}
.item{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:8px 12px;margin:0 0 6px}
.line{display:flex;align-items:flex-start;gap:12px}
.line .id{min-width:38px;padding-top:1px}
.gist{flex:1;font-weight:600;font-size:15px;line-height:1.5}
.where{display:block;font-weight:400;font-size:12.5px;color:var(--muted)}
.btns{display:flex;gap:6px;white-space:nowrap}
.btns label{cursor:pointer;padding:3px 10px;border:1px solid var(--line);border-radius:4px;font-size:13.5px}
.item.yes .btns label:first-child{border-color:var(--green);color:var(--green)} .item.no .btns label:last-child{border-color:var(--red);color:var(--red)}
.item .why{display:none;width:100%;margin-top:6px} .item.no .why{display:block}
details.ev{margin:4px 0 0 50px} details.ev summary{font-size:12.5px} details.ev .row{grid-template-columns:96px 1fr}
@media (max-width:720px){.line{flex-wrap:wrap}.btns{width:100%}details.ev{margin-left:0}}
</style>""") + """<h1>剩下 {{N}} 条，看第一行就能判</h1>
<p class="sub">已判 {{DONE}} 条，已存。每条第一行是验收官说的问题和在哪；你觉得这处确实该改就点「同意」，不算问题或不值得改就点「不同意」（可写一句理由）。要看原文和截图，点「展开看证据」。点完按底部「复制结果」，贴给「用好 Claude：进度沟通」。</p>
<details class="ev" style="margin:0 0 6px"><summary>主管的需求原文</summary><div class="req">{{REQ}}</div></details>
{{BODY}}
<textarea id="out" readonly></textarea>
</div>
""" + _TAIL


if __name__ == '__main__':
    main()
