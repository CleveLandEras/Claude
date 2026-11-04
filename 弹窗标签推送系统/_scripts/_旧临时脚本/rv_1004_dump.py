# 只读：审查 2026-10-04 用。打印设计卡 Q174/Q175、审查记录末节、进展日志末尾、若干核对。
import re, os, html
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'

def rd(p):
    with open(B + p, encoding='utf-8') as f:
        return f.read()

def strip(t):
    t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(t)

def nows(t):
    return re.sub(r'\s+', '', t)

print('=' * 30, '设计卡 Q174 / Q175')
dk = rd('过程记录/设计卡.md')
heads = [(m.start(), m.group(0)) for m in re.finditer(r'^#{1,3} .*$', dk, flags=re.M)]
for i, (pos, h) in enumerate(heads):
    if 'Q174' in h or 'Q175' in h:
        end = heads[i + 1][0] if i + 1 < len(heads) else len(dk)
        # 延伸到下一个同级或更高级标题
        lvl = len(h.split(' ')[0])
        j = i + 1
        while j < len(heads) and len(heads[j][1].split(' ')[0]) > lvl:
            j += 1
        end = heads[j][0] if j < len(heads) else len(dk)
        print('--- 标题:', h, '长度', end - pos)
        print(dk[pos:end][:14000])

print('=' * 30, '审查记录 末节')
sc = rd('过程记录/审查记录.md')
k = sc.rfind('\n## 2026-09-30 14:56')
if k < 0:
    k = max(0, len(sc) - 15000)
print(sc[k:][:22000])
print('最大 R 编号:', max(int(x) for x in re.findall(r'### R(\d+)', sc)))
print('审查节标题（末 4 个）:', re.findall(r'^## .*$', sc, flags=re.M)[-4:])

print('=' * 30, '进展日志 末尾')
jz = rd('进展日志.md').rstrip().split('\n')
for ln in jz[-7:]:
    print(ln[:700])

print('=' * 30, '监督记录 末尾')
try:
    jd = rd('过程记录/监督记录.md')
    print(jd[-2500:])
except Exception as e:
    print('读不到', e)

print('=' * 30, '首屏句比对')
for p in ['决策汇报.html', '环节3_方案.html']:
    t = strip(rd(p))
    for m in re.finditer('改完以后的完整规则见', t):
        print(p, '|', re.sub(r'\s+', ' ', t[m.start():m.start() + 110]))

print('=' * 30, '「按玩家看」出现处')
for p in ['决策汇报.html', '环节3_方案.html', '支撑文件/02_弹窗分人群定制方案.html', '支撑文件/08_弹窗效果评估方案.md', '分析/A36_验证计划.md']:
    try:
        t = strip(rd(p))
    except Exception as e:
        print(p, '读不到', e); continue
    for m in re.finditer('按玩家看', t):
        print(p, '|', re.sub(r'\s+', ' ', t[max(0, m.start() - 70):m.start() + 50]))

print('=' * 30, '02 交互图：序号 / 圆点')
t02 = rd('支撑文件/02_弹窗分人群定制方案.html')
for i, ln in enumerate(t02.split('\n')):
    if re.search(r'圆点|序号|\.num|class="n"|idx ?\+ ?1|i ?\+ ?1|①|②|③|dot', ln):
        print(i + 1, '|', ln.strip()[:260])

print('=' * 30, '引文核对（去空白后子串匹配）')
srcs = {}
for name, p in [('盘点', '来源资料/claude_弹窗标签推送_盘点.html'), ('任务清单', '过程记录/任务清单.md'), ('06', '支撑文件/06_推送现状整理.md'), ('数据说明', '数据/说明.md')]:
    try:
        srcs[name] = nows(strip(rd(p)))
    except Exception as e:
        print(name, '读不到', e)
for fn in os.listdir(B + '来源资料'):
    if 'Cowork' in fn and fn.endswith('.md'):
        srcs['Cowork:' + fn] = nows(rd('来源资料/' + fn))
qs = ['不做区分', '这类状态不能作为时机，只能作为人群圈选条件', '写死在客户端，调整需走开发',
      '可限单个弹窗每日次数上限与冷却时间', '不支持负反馈降权', '无法做到连续关闭 N 次后自动静默',
      '实验分流支持，开发成本未评估', '多条规则命中时叠加触发', '各自售价未取得，是排储值类顺序的直接输入',
      '每个功能各一套，没有统一入口', '发送量与到达率无数据', '内容只说明升级，不说明有奖可领', '点击不跳转',
      '最快 25 分钟一次', '计划增加交集', '不必逐个索取标签人数', '总控弹窗数量也需要人均曝光数',
      '弹窗埋点现在有的有、有的没有', '排序列表是优先级链', '原文含繁体与机翻痕迹', '支持 And、排除、or',
      '有没有限制一个用户一天最多收几条', '这 7 天排序会跳过它取下一位', '已经先存储了', '是否购买过首储礼包',
      '各通路能否按标签定向、有没有数据，仍然未知', '快显还要从写死改为可配置', '交集是重点，是必经之路',
      '标签定义表单里可以直接写 SQL', '群组内是否支持排除，截图未显示', '仍待答', '平台各处埋点完善',
      '弹窗触发时机是 5 个', '只有购买首储礼包后才会消失', '非五通路，供对照', '可以覆盖不用 App 的人',
      '高卡下降有没有人跟进', '已上线（从 05 删去）', '按推断推进', '对象列填', '弹窗对象可选',
      '储值品项设定 / 储值活动设定 / 产包设定 / 推荐礼包管理', '最後提醒', '身份和卡别都是取数当时的值，没有历史',
      '当时打开平台的人都看得到', '能否按名单、群组发送未知', '标签状态', '没有统一入口', '是不是『金卡及以上』这种区间标签',
      '740', '没有结果']
for q in qs:
    hit = [n for n, t in srcs.items() if nows(q) in t]
    print('有' if hit else '【无】', '|', q, '|', '、'.join(hit))

print('=' * 30, 'A37 自检')
a = rd('分析/A37_能力线现有能力.md')
p1 = a.split('## 第二部分')[0]
p2 = a.split('## 第二部分')[1].split('## 需求无对应动作')[0]
rows = [r for r in p1.split('\n') if re.match(r'\| D\d+ \|', r)]
print('动作行数', len(rows))
cov = [r for r in rows if r.rstrip(' |').split('|')[-1].strip().startswith('未覆盖')]
print('未覆盖行数', len(cov))
ds = set(re.match(r'\| (D\d+)', r).group(1) for r in rows)
krows = [r for r in p2.split('\n') if re.match(r'\| K\d+ \|', r)]
print('K 行数', len(krows))
used = set()
for r in krows:
    used |= set(re.findall(r'D\d+', r.split('|')[3]))
print('没有任何 K 项引用的动作:', sorted(ds - used))
print('K 引用了不存在的动作:', sorted(used - ds))
print('含「且 / ，也 / ，数据组能」的 K 项（一句两问）:')
for r in krows:
    c = r.split('|')[2]
    if re.search(r'，且|，也能|，数据组能|，排程', c):
        print('  ', r.split('|')[1].strip(), c.strip())
print('第一、二部分与反例检查中的「→有」数:', a.count('→有'))
