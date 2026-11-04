"""把被误覆盖的「设计卡.md」从本会话的文件历史备份恢复（只在当前内容仍是占位符时才写）。"""
import os
src = os.path.expanduser('~/.claude/file-history/65da5fd1-8802-46e2-a29e-3cdb389d7642/90485ef7d752df0e@v1')
dst = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '过程记录', '设计卡.md')
cur = open(dst, encoding='utf-8').read()
bak = open(src, encoding='utf-8').read()
assert cur.strip() == 'PLACEHOLDER', '当前内容不是占位符，不覆盖'
assert bak.startswith('# 设计卡') and '## Q199｜' in bak
open(dst, 'w', encoding='utf-8').write(bak)
print('已恢复', len(bak), '字符；末尾 80 字：', bak[-80:].replace('\n', ' '))
