"""只读：检查决策汇报.html 与环节2、环节3 中页内锚点（href="#x"）是否都有对应 id。"""
import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f in ['决策汇报.html', '环节2_问题诊断.html', '环节3_方案.html']:
    s = open(base + f, encoding='utf-8').read()
    ids = set(re.findall(r'id="([^"]+)"', s))
    refs = set(re.findall(r'href="#([^"]+)"', s))
    miss = sorted(refs - ids)
    print(f, '锚点', len(refs), '缺失', miss)
