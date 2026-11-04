# -*- coding: utf-8 -*-
"""T2 续：①影响项清单首列改为修订记录行号（1–16，比对.py 按它对修订记录）、问题组号移到末列；②补 7 块重走后补改（改法#写「重走补改」）。幂等。"""
import re
from pathlib import Path
B=Path(__file__).resolve().parent.parent
p=B/'影响项清单.md'
L=p.read_text(encoding='utf-8').split('\n')
FAMNO={f'M{i:02d}':i for i in range(1,17)}
out=[];rows=0;head_done=False
for l in L:
    if l.startswith('| 问题组号 |'):
        out.append('| 问题# | 文件 | 行号或控件编号 | 改法# | 文件分组 | 来源 | 问题组号 |'); continue
    if l.startswith('| 问题# |'):
        out.append(l); continue
    m=re.match(r'\| (G[^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| ([^|]*?) \| (.*) \|$',l)
    if m:
        g,f,loc,fam,grp,src=m.groups()
        mm=re.search(r'M\d\d',fam)
        out.append(f'| {FAMNO[mm.group(0)]} | {f} | {loc} | {fam} | {grp} | {src} | {g} |'); rows+=1; continue
    out.append(l)
# 补改（幂等：已有就不再加）
add=[(10,'10h_发送测试确认.html','113','样例日期统一 10/21','G006、G034、G037'),
     (10,'10h_发送测试确认.html','116–117','样例日期统一 10/21','G006、G034、G037'),
     (10,'10h_发送测试确认.html','119','样例日期统一 10/21','G006、G034、G037')]
for f in ['10a_弹窗列表.html','10a2_按活动筛选后改弹窗设置.html','10b_破产时页签.html','10n_场景设置.html']:
    ln={'10a_弹窗列表.html':76,'10a2_按活动筛选后改弹窗设置.html':77,'10b_破产时页签.html':73,'10n_场景设置.html':110}[f]
    add.append((11,f,str(ln),'列表头「人数为约数，10/21 更新」','G004、G017、G030'))
txt='\n'.join(out)
for q,f,loc,what,g in add:
    row=f'| {q} | 需求评审版_原型/{f} | {loc} | 重走补改 | 原型 | 重走补改：{what} | {g} |'
    if row not in txt: out.append(row)
p.write_text('\n'.join(out),encoding='utf-8')
