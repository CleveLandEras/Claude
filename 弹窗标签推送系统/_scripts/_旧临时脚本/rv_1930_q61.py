# 只读：审查 19:24 轮，检查 Q61 正文 / 更正记录分开计数
import re, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
pats = ['原写', '更正：', '更正）', '按审查', 'R\\d+ 更正', '（已改）', '原来用的']
for fn in ['决策汇报.html', '环节1_现状盘点.html']:
    t = open(base + fn, encoding='utf-8').read()
    # 去标签
    txt = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
    txt = re.sub(r'<[^>]+>', '\n', txt)
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    idx = [i for i, l in enumerate(lines) if l.startswith('更正记录')]
    cut = idx[-1] if idx else len(lines)
    body, rec = lines[:cut], lines[cut:]
    print('=' * 60)
    print(fn, '总行', len(lines), '更正记录起始行', cut)
    # 汇报：第一节范围
    if fn == '决策汇报.html':
        s2 = [i for i, l in enumerate(body) if l.startswith('二 · 问题诊断')]
        s5 = [i for i, l in enumerate(body) if '现在只需发运营' in l]
        print('第二节起', s2, '附录起', s5)
    for p in pats:
        hits = [(i, l) for i, l in enumerate(body) if re.search(p, l)]
        print('正文', p, len(hits))
        for i, l in hits[:40]:
            m = re.search(p, l)
            a = max(0, m.start() - 60)
            print('   ', i, l[a:m.end() + 60].replace('\n', ' '))
    # 更正记录条数：以 纯数字行 计
    nums = [l for l in rec if re.fullmatch(r'\d+', l)]
    print('更正记录编号行数', len(nums), '最后', nums[-1] if nums else None)
    # 模糊搜索若干旧句
    for key in ['决定 C', '两个字段的口径问运营', '各勾了『进入大厅』『返回大厅』中的哪一个', '像是升卡门槛之一', '84.39', '推理方向反了', '靠转入的币在玩的人最多约 2%', '能否由「推断」改「已证实」']:
        print('  旧句', key, '正文', sum(key in l for l in body), '记录', sum(key in l for l in rec))
