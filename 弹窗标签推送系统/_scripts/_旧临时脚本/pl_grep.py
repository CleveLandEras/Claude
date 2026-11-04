import re
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
terms = ['SQL', '负反馈', '106', '推荐礼包', '现有功能', '群组', '进入大厅', '返回大厅', '约 100', '国家', '自查 ④', '会员等级', '副产品', '升卡门槛', '直接排期', '配置解决']
for fn in ['环节1_现状盘点.html', '决策汇报.html', '分析/A11_会员等级.md', '分析/A8_卡别与最后登录.md']:
    t = open(B + fn, encoding='utf-8').read()
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print('=====', fn, len(t))
    for w in terms:
        idx = [m.start() for m in re.finditer(re.escape(w), t)]
        print('--', w, len(idx))
        for i in idx[:4]:
            print('   ', t[max(0, i - 90):i + 110])
