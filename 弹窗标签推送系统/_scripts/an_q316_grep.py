# Q316：核查盘点与阶段 3 里是否有「未登入」类标签名（只读）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _textify import textify, BASE
for rel in ['来源资料/claude_弹窗标签推送_盘点.html', '阶段3_现状盘点.html']:
    t = textify(os.path.join(BASE, rel)).splitlines()
    hits = [(i + 1, l) for i, l in enumerate(t) if any(k in l for k in ['未登入', '未登录', '登入天', '登录天', '天未'])]
    print('==', rel, len(hits))
    for i, l in hits[:12]:
        print(i, l[:200])
