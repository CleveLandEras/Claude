"""Q23/Q27 定位：在 00、决策汇报、环节1、迭代记录中按关键词输出行号（只读）。不带参数运行。"""
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
targets = {
    '00_推进记录.md': ['## ', '### ', '| 22 ', '| 23 ', '| 10 ', '22.', '23.', '10.', '发给运营', '回填', '问题 22', '问题 23'],
    '决策汇报.html': ['发给运营', '<summary', '22.', '23.', '10.', '<details', '</details>', '问题 22'],
    '环节1_现状盘点.html': ['<h2', '<h3', '总充值金额', '身份、卡别', '推送系统清单', '标签口径', '维护渠道', '<table', '</table>'],
    '迭代记录.md': ['## ', '### '],
    '进展日志.md': ['## '],
}
for name, keys in targets.items():
    lines = open(B + name, encoding='utf-8').read().split('\n')
    print('=' * 30, name, '总行数', len(lines))
    for i, l in enumerate(lines, 1):
        s = l.strip()
        for k in keys:
            if (k.startswith('#') and s.startswith(k)) or (not k.startswith('#') and k in s):
                print(f'  {i}: [{k}] {s[:110]}')
                break
