"""Q122 第一部分补充：列名多写法合并检索（简繁体、简称），报各列在分析文件与支撑文件、环节文件里的出现文件数。只读，不带参数。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import glob

B = _ROOT + '/'
groups = {
    '分析/': glob.glob(B + '分析/*.md'),
    '环节与汇报': [B + '决策汇报.html'] + glob.glob(B + '环节*.html'),
}
cols = {
    '会员编号': ['会员编号'], '注册时间': ['注册时间', '注册日', '注册满', '注册天数'],
    '登入平台': ['登入平台', '登录平台', '平台'], '最後登入時間': ['最後登入', '最后登录', '最后登入', '最后一次登录'],
    '卡别': ['卡别'], '会员等级': ['会员等级'], '总充值金额': ['总充值', '累计储值'],
    '游戏总押注': ['总押注', '累计押注', '押注'], '游戏总输赢': ['总输赢', '游戏输赢'],
    'RTP': ['RTP'], '活动赠点': ['活动赠点'], '充值赠点': ['充值赠点'],
    '储值回馈比': ['储值回馈比', '回馈比'], '活动咬分比': ['咬分比'], '身份': ['身份'],
}
txt = {}
for g, fs in groups.items():
    for f in fs:
        txt[f] = open(f, encoding='utf-8').read()
for c, kws in cols.items():
    line = []
    for g, fs in groups.items():
        n = sum(1 for f in fs if any(k in txt[f] for k in kws))
        line.append(f'{g} {n}/{len(fs)}')
    print(f'{c}：' + '；'.join(line))
