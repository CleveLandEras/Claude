# 只读：审查 19:3x 轮，核对 Q62（环节1 缺口表等级门槛一行、更正记录条数、残留说法）
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for fn in ['环节1_现状盘点.html', '决策汇报.html', '支撑文件/00_推进记录.md']:
    t = open(base + fn, encoding='utf-8').read()
    txt = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
    txt = re.sub(r'<[^>]+>', '\n', txt)
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    idx = [i for i, l in enumerate(lines) if l.startswith('更正记录')]
    cut = idx[-1] if idx else len(lines)
    body, rec = lines[:cut], lines[cut:]
    print('=' * 60)
    print(fn, '正文行', len(body), '记录行', len(rec))
    for key in ['约 750', '750 / 5,000 / 10,000', '754 / 5,023 / 10,023', '下限', '能否由', '已证实」', '仍缺的只有', '67 条', '66 条']:
        hits = [(i, l) for i, l in enumerate(body) if key in l]
        print(' 正文', key, len(hits))
        for i, l in hits[:8]:
            p = l.find(key)
            print('    ', i, l[max(0, p - 70):p + 70])
    if rec:
        nums = [(i, l) for i, l in enumerate(rec) if re.fullmatch(r'\d+', l)]
        print(' 记录纯数字行', [l for i, l in nums])
        # 打印 67 条附近
        for i, l in nums:
            if l in ('66', '67', '68', '69', '70'):
                print('  --', l, '|', ' | '.join(rec[i + 1:i + 5])[:300])
