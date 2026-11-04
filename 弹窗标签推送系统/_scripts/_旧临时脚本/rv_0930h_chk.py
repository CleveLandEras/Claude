"""审查 09-30 11:19 只读核对：05 交集读法、各需求版本号、09 表名、汇报「原样转发」现行位置。只打印。"""
import os, re
from _textify import BASE, textify
def T(f):
    return textify(os.path.join(BASE, f)).replace('\n', ' ⏎ ')
def ctx(s, t, w=160, k=10):
    i = s.find(t); n = 0
    while i != -1 and n < k:
        n += 1
        print(f'   …{s[max(0, i-w):i+len(t)+w]}…')
        i = s.find(t, i + len(t))
    if n == 0: print('   无命中')
s05 = T('支撑文件/05_标签需求.md')
print('== 05 交集'); ctx(s05, '交集', 140, 12)
print('== 05 必建'); ctx(s05, '必建', 120)
for f in ['支撑文件/04_弹窗功能缺口需求.md', '支撑文件/05_标签需求.md', '支撑文件/07_推送需求.md']:
    s = T(f)
    vers = re.findall(r'\| (\d\.\d) \| 2026', s)
    print('==', f, '版本行', vers)
s09 = T('支撑文件/09_取数需求_上线前基线.xlsx')
print('== 09 工作表', re.findall(r'## 工作表 ([^⏎]+)', s09))
print('== 09 表10'); ctx(s09, '表10', 100, 3)
s = T('决策汇报.html')
print('== 汇报 原样转发 位置')
for m in re.finditer('原样转发', s):
    i = m.start()
    print('  pos', i, '…', s[max(0, i-60):i+30])
print('== 汇报 总长', len(s), ' 更正记录起点', s.find('更正记录（顶部总结论'))
print('== 汇报 存档：原交主管的一段 起点', s.find('存档：原交主管的一段'))
print('== 汇报 验收小表'); ctx(s, 'Dk 验收时要看的几处', 60, 2)
s02 = T('支撑文件/02_弹窗分人群定制方案.html')
print('== 02 主要风险 新补 统计：点数本地估不出/未知'); ctx(s02, '点数', 80, 12)
print('== 02 状态字样'); ctx(s02, '待 Dk 验收', 60, 3); ctx(s02, '交主管拍板', 60, 3)
s2 = T('环节2_问题诊断.html')
print('== 环节2 D7 标题'); ctx(s2, '现行 02 已不多弹', 200, 3)
print('== 环节2 多弹一个'); ctx(s2, '多弹一个', 200, 5)
