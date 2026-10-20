# 措辞审查用：列出 pptx 里所有带中文逗号的文字（含标题、副标题、卡片、分隔页），逐句判断逗号两边是否有关系
# 用法：python pl_逗号句清单.py deck.pptx
# 两边是因果、条件、承接、补充、对比 → 逗号可用；两件互不相关的事 → 改分号、分行，或写成「两项：A、B」
import sys, re
from pptx import Presentation

for i, s in enumerate(Presentation(sys.argv[1]).slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            t = ''.join(r.text for r in p.runs).strip()
            if '，' in t and not re.search(r'第 \d+ 页', t):
                kind = '标题' if 0.9 < sh.top / 914400 < 1.1 else ('副标题' if 1.55 < sh.top / 914400 < 1.75 else '')
                print('p%-3d %-4s %s' % (i, kind, t))
