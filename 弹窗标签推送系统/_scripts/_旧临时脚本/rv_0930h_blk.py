"""审查 09-30 11:19 只读：打印汇报交主管块全文、第 8 件开头、05 提案节；环节3 目录级小标题。只打印。"""
import os, re
from _textify import BASE, textify
def T(f):
    return textify(os.path.join(BASE, f)).replace('\n', ' ⏎ ')
s = T('决策汇报.html')
i = s.find('拟交主管的一段（待 Dk 验收')
print('== 交主管块'); print(s[i:i+2600])
i = s.find('第 8 件 · ')
print('== 第 8 件'); print(s[i:i+1500])
s05 = T('支撑文件/05_标签需求.md')
i = s05.find('## 提案')
print('== 05 提案'); print(s05[i:i+1400])
s3 = textify(os.path.join(BASE, '环节3_方案.html'))
print('== 环节3 长度', len(s3))
print(s3[:6000])
