"""Q25 ③：在环节1、决策汇报、分析/A1–A9 中检索旧说法残留（只读）。不带参数运行。
每处命中输出前后文，由人工判断是否在更正说明或附录原话内。"""
import glob, os, re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
terms = ['按身份断层', '差别不大', '现成标签可', '待主管', '7 天内', '25,962', '10,120', '下限 9,786', '至少 9,786',
         '量级不变', '530 人是银卡以上', '推送用户结构与弹窗线一致', '最后登录越近', '待登记', '相当一部分', '约 12 个',
         '多数比较里仍有', '押注解释不了大部分', '不是个别账号', '高卡用户更偏 web', '高价值用户受影响更大', '占三成储值',
         '因为卡别越高越偏 web', '15,000.5']
files = [B + '环节1_现状盘点.html', B + '决策汇报.html'] + sorted(glob.glob(B + '分析/A*.md'))


def text(p):
    s = open(p, encoding='utf-8').read()
    if p.endswith('.html'):
        s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
        s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return s.replace('\n', ' ')


T = {os.path.relpath(p, B): text(p) for p in files}
for t in terms:
    hits = []
    for name, s in T.items():
        i = s.find(t)
        while i != -1:
            hits.append(f'  [{name}] …{s[max(0, i-70):i+len(t)+50]}…')
            i = s.find(t, i + len(t))
    print(f'== {t}：{len(hits)} 处')
    for h in hits:
        print(h)
