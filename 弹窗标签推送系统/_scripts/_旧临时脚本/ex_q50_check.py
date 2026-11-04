"""Q50 回归核对：残留词检索（只看是否落在更正括注）、运营第 1 句汇报与 00 逐字一致。只读，不带参数。"""
import os, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ['决策汇报.html', '环节1_现状盘点.html', '分析/A1_用户价值结构.md', '分析/A3_回流与潜在付费画像.md',
         '分析/A7_目标人群重叠.md', '分析/A10_储值回馈比与礼包指纹.md', '分析/A11_会员等级.md', '支撑文件/00_推进记录.md']
TERMS = ['有没有包含代储或转帐', '是否含代储', '含不含代储', '待问题 25 a', '储值通路', '储值漏记', '储值若有漏记', '25 a、b',
         '卡别是怎么升的', 'Q51', '点数守恒', '另行分析', '另行估算']
for f in FILES:
    s = open(os.path.join(B, f), encoding='utf-8').read()
    for t in TERMS:
        for m in re.finditer(re.escape(t), s):
            ctx = s[max(0, m.start() - 40):m.end() + 30].replace('\n', ' ')
            print(f'[{f}] {t}：…{ctx}…')
# 运营 3 句逐字比对
rep = open(os.path.join(B, '决策汇报.html'), encoding='utf-8').read()
z00 = open(os.path.join(B, '支撑文件/00_推进记录.md'), encoding='utf-8').read()
a = re.search(r'<pre id="m1">(.*?)</pre>', rep, re.S).group(1).strip()
b = re.search(r'\*\*发给运营（3 句）\*\*\s*```\s*(.*?)```', z00, re.S).group(1).strip()
print('运营 3 句 汇报 = 00：', a == b)
print(a)
ra = re.search(r'对应原问题：第 1 句[^<\n]*', rep).group(0)
rb = re.search(r'对应原问题：第 1 句[^<\n]*', z00).group(0)
print('对应原问题一行一致：', ra == rb)
