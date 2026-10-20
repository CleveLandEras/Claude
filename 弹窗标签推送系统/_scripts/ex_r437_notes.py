import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob, os
base = _ROOT + '/分析/'
note = ('> **10/9 夜更新说明（R437）**：文中把「新人群配置自主率／配置是否不依赖研发／后台配置操作与提单记录／验收一只收新人群配置是否要研发介入」'
        '当作指标或验收条件的写法，已按 Dk 意见作废：目标、验收、衡量里不设「不依赖研发」类条件。指标 1 现为「可单独配置且不影响其他人群的人群类数」，'
        '数据收集「后台配置操作与提单记录」已删；「标签由谁编写」改列阶段 8 第四节「可顺手核实」第 6 项，只影响排期依赖，不对应指标。以阶段 6、8 为准；本文原文不重写。\n')
for k in ['A69', 'A70', 'A73', 'A74', 'A75', 'A76']:
    p = glob.glob(base + k + '_*.md')[0]
    s = open(p, encoding='utf-8').read()
    if 'R437' in s:
        print('skip', p)
        continue
    lines = s.split('\n', 1)
    new = lines[0] + '\n\n' + note + ('\n' + lines[1].lstrip('\n') if len(lines) > 1 else '')
    open(p, 'w', encoding='utf-8').write(new)
    print('ok', os.path.basename(p))
