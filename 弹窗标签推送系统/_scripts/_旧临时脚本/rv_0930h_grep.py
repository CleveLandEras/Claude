"""审查 09-30 11:19 只读检索：在指定交付物中查词，只打印。"""
import os
from _textify import BASE, textify
files = ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html',
         '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/03_弹窗配置单.xlsx',
         '支撑文件/04_弹窗功能缺口需求.md', '支撑文件/05_标签需求.md', '支撑文件/07_推送需求.md',
         '支撑文件/08_弹窗效果评估方案.md', '支撑文件/09_取数需求_上线前基线.xlsx',
         '分析/A35_赠点规模与02成本影响.md', '分析/A32_问题空间扫描.md', '分析/A34_大户落位与缺席大户.md']
terms = ['原样转发', '可交研发', '可交数据组', '今天就能发', '直接复制发出', '可以直接交', '可以上线',
         '放出前', '原方案只让', '集中在两头', '9.4 倍', '9.4倍', '57 人', '有用、不是非有不可', '不是非有不可',
         '退路标签', 'M7', '表 10', 'v2.3', '版本', '5,146', '5,145', '11:08 新退回', '分母效应']
texts = {}
for f in files:
    p = os.path.join(BASE, f)
    try:
        texts[f] = textify(p).replace('\n', ' ⏎ ')
    except Exception as e:
        print(f, '读取失败', e)
for t in terms:
    print('=' * 50, t)
    for f, s in texts.items():
        i = s.find(t); n = 0
        while i != -1 and n < 8:
            n += 1
            print(f'  [{f}] …{s[max(0, i-110):i+len(t)+110]}…')
            i = s.find(t, i + len(t))
