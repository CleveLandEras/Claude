"""Q82 旧说法检索：在环节2 全文与决策汇报第二节中，去掉「存档」「更正记录」折叠框后，检索旧说法，输出所在 section 与前后文。不带参数运行。"""
import os, re
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
TERMS = ['第一档', '第二档', '暂列', '初排', '人数榜', '储值榜', '档位', '不能说它比高卡流失更大', '都取决于尺子', '只能靠推送',
         '五张卡', '月月抽', '谁大，取决于', '与这条链的关系取决于', '方案环节最重', '规划者写死', '待定', '边界项', '最大问题', '第一 档', 'Q72', 'Q11', '设计卡']
def strip_archive(s):
    # 去掉 summary 含「存档」或「更正记录」的 details 块
    out, i = [], 0
    for m in re.finditer(r'<details[^>]*>\s*<summary>(.*?)</summary>.*?</details>', s, re.S):
        if '存档' in m.group(1) or '更正记录' in m.group(1):
            out.append(s[i:m.start()]); i = m.end()
    out.append(s[i:])
    return ''.join(out)
def sections(s):
    return [(m.group(1), m.group(2)) for m in re.finditer(r'<section id="([^"]+)">(.*?)</section>', s, re.S)]
def txt(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x))
s2 = open(os.path.join(BASE, '环节2_问题诊断.html'), encoding='utf-8').read()
head = s2[:s2.find('<section')]
parts = [('首屏', head)] + sections(strip_archive(s2))
rep = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
r2 = dict(sections(strip_archive(rep))).get('s2', '')
parts.append(('汇报s2', r2))
for t in TERMS:
    print('=' * 50, t)
    for name, body in parts:
        tx = txt(body)
        for m in re.finditer(re.escape(t), tx):
            print(f'  [{name}] …{tx[max(0, m.start()-70):m.end()+70]}…')
