# 只读：统计决策汇报与环节1 正文里「更正括注」的数量与字数占比
import re, os
root = '/Users/decheng.huang/claude/弹窗标签推送系统/'
pat = re.compile(r'（[^（）]{0,400}?(原写|更正|按审查)[^（）]{0,400}?）')
for f in ['决策汇报.html', '环节1_现状盘点.html']:
    s = open(os.path.join(root, f), encoding='utf-8').read()
    body = re.sub(r'<style.*?</style>', '', s, flags=re.S)
    text = re.sub(r'<[^>]+>', '', body)
    text = re.sub(r'\s+', ' ', text)
    ms = pat.findall(text)
    spans = [m.group(0) for m in pat.finditer(text)]
    corr_len = sum(len(x) for x in spans)
    print(f, '正文字数', len(text), '更正括注数', len(spans), '括注字数', corr_len, '占比 %.1f%%' % (100 * corr_len / len(text)))
