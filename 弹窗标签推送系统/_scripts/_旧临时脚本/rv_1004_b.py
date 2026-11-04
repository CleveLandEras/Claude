# 只读：审查 2026-10-04 第二次核对。
import re, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def rd(p):
    with open(B + p, encoding='utf-8') as f:
        return f.read()

def strip(t):
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(t)

print('=' * 20, '02 交互脚本（含 序号/圆点 相关行）')
t02 = rd('支撑文件/02_弹窗分人群定制方案.html').split('\n')
for i, ln in enumerate(t02):
    if 660 <= i + 1 <= 760 and re.search(r'createElement|innerHTML|class|•|●|bullet|dot|\+ ?1', ln):
        print(i + 1, '|', ln.strip()[:240])
css = [(i + 1, ln.strip()[:200]) for i, ln in enumerate(t02) if re.search(r'\.pk|\.item|\.bul|\.dot|\.ord|counter', ln) and i < 200]
for c in css[:25]:
    print('css', c)

print('=' * 20, '两条未命中引文的片段')
srcs = {'盘点': strip(rd('来源资料/claude_弹窗标签推送_盘点.html')), '任务清单': rd('过程记录/任务清单.md'),
        'Cowork': rd('来源资料/Cowork汇总_背景信息_v2_20260928.md')}
for frag in ['才会消失', '才消失', '购买首储礼包后', '区间标签', '金卡及以上', '更优越', '排除名单', '按平台', '浏览器', '素材', '文案', '定时发送', '免打扰']:
    for n, t in srcs.items():
        for m in list(re.finditer(re.escape(frag), t))[:2]:
            print(frag, '|', n, '|', re.sub(r'\s+', ' ', t[max(0, m.start() - 60):m.start() + 70]))

print('=' * 20, '04 / 07 / 05 关键词')
for p, kws in [('支撑文件/04_弹窗功能缺口需求.md', ['限时加码', '不在', '排除', '先后']),
               ('支撑文件/07_推送需求.md', ['定时', '触发', '时段', '免打扰', '未知', '对照', '撤回', '停用']),
               ('支撑文件/05_标签需求.md', ['分桶·对照', '互补'])]:
    t = rd(p)
    for kw in kws:
        ms = list(re.finditer(re.escape(kw), t))
        print('--', p, kw, '出现', len(ms))
        for m in ms[:4]:
            print('    ', re.sub(r'\s+', ' ', t[max(0, m.start() - 50):m.start() + 90]))

print('=' * 20, '07 前置条件表')
t = rd('支撑文件/07_推送需求.md')
k = t.find('前置条件')
print(t[k:k + 2500])

print('=' * 20, 'C2 标题与待核对')
c2 = rd('支撑文件/C2_新标签脚本草稿.md')
for ln in c2.split('\n'):
    if ln.startswith('#') or '待核对' in ln or '未知' in ln or '待确认' in ln:
        print(ln[:220])

print('=' * 20, 'A37 中 登录记录 / 留存')
a = rd('分析/A37_能力线现有能力.md')
for kw in ['登录记录', '登入记录', '留存', '素材', '文案', '定时', '端', '「→']:
    print(kw, a.count(kw))
