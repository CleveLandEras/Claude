"""估算 pptx 每个文本框、表格是否超出：按字宽（中文 1em、西文 0.55em）折行，比较所需高度与给定高度；表格按行估算总高并检查是否越过页脚 6.85in。"""
import sys, math, unicodedata
from pptx import Presentation
from pptx.util import Emu
E = 914400

def cw(ch):
    return 1.0 if unicodedata.east_asian_width(ch) in ('W', 'F') else 0.55

def need_h(paras, width_in, default_size=12, line=1.25, margin=0.0):
    h = 0
    for runs, sz, ln in paras:
        size = sz or default_size
        w = sum(cw(c) for c in runs) * size / 72
        nl = max(1, math.ceil(w / max(width_in - margin, 0.1) - 1e-6)) if runs else 1
        h += nl * size / 72 * (ln or line) * 1.2
    return h

def paras_of(tf):
    out = []
    for p in tf.paragraphs:
        t = ''.join(r.text for r in p.runs)
        sz = max([r.font.size.pt for r in p.runs if r.font.size] or [12])
        ln = p.line_spacing if isinstance(p.line_spacing, float) else 1.2
        out.append((t, sz, ln))
    return out

prs = Presentation(sys.argv[1])
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            w = sh.width / E; h = sh.height / E
            nh = need_h(paras_of(sh.text_frame), w)
            if nh > h + 0.08 and nh > 0.35:
                print(f'S{i} 文本框溢出 need {nh:.2f} > {h:.2f} @y{sh.top/E:.2f}: {sh.text_frame.text[:40]!r}')
        if sh.has_table:
            tbl = sh.table; tot = 0
            for r in tbl.rows:
                rh = r.height / E; mx = rh
                for ci, c in enumerate(r.cells):
                    cwid = tbl.columns[ci].width / E - 0.2
                    nh = need_h(paras_of(c.text_frame), cwid, line=1.15) + 0.11
                    mx = max(mx, nh)
                tot += mx
            bottom = sh.top / E + tot
            flag = '  <-- 越过 6.85' if bottom > 6.8 else ''
            print(f'S{i} 表格 估算底边 {bottom:.2f}（给定 {sh.top/E + sh.height/E:.2f}）{flag}')
