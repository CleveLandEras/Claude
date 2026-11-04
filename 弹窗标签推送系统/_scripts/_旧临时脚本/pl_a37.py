B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
p = '分析/A37_能力线现有能力.md'
with open(B + p, encoding='utf-8') as f:
    lines = f.readlines()
print('=====', p, len(lines))
keys = ['| K18 ', '| K33 ', '| K37 ', '| K88 ', '| K91 ', '| K28 ', '| K74 ', '| K81 ', '| K83 ', '| D12 ', '| D43 ',
        '同事草稿', '附录四', '已列全', '按日登录', '发送方式', '立即推送', '定时推送']
for i, l in enumerate(lines, 1):
    s = l.rstrip()
    if s.startswith('#') or any(k in s for k in keys):
        print(i, s[:600])
print('→有 count', sum(l.count('→有') for l in lines), '→没有 count', sum(l.count('→没有') for l in lines))
p = '过程记录/设计卡.md'
with open(B + p, encoding='utf-8') as f:
    lines = f.readlines()
print('=====', p, len(lines))
for i, l in enumerate(lines, 1):
    s = l.rstrip()
    if '⚠' in s or (s.startswith('#') and ('Q174' in s or 'Q175' in s)) or '同事草稿' in s:
        print(i, s[:500])
p = '过程记录/任务清单.md'
with open(B + p, encoding='utf-8') as f:
    lines = f.readlines()
print('=====', p, len(lines))
for i, l in enumerate(lines, 1):
    s = l.rstrip()
    if s.startswith('#') or '10-0' in s[:40]:
        print(i, s[:200])
