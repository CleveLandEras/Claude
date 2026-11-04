BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for f, keys in [('决策汇报.html', ['验收看哪几处', '02 方案稿（待 Dk 验收）', '附件的状态', '03 配置单（待']),
                ('环节3_方案.html', ['<h1', '第二节', '摘要，以第五节', '完整规则', '更正记录'])]:
    lines = open(BASE + f, encoding='utf-8').read().split('\n')
    print('==', f, len(lines), '行')
    for i, l in enumerate(lines, 1):
        for k in keys:
            if k in l:
                print(i, k, '|', l[:160].replace('\n', ' '))
                break
