"""审查者考试：生成一轮考试材料（题目、工作原则与审查清单的各版本、判例库合订本）。

用法：python3 _scripts/exam_build.py <轮次名> [--with-cases]
  轮次名：例如「基线」「改后1」；材料写到 归档/判例考试_至1014/考试材料/<轮次名>/
  --with-cases：审查方法要求读判例库时加上（改后各轮）；基线不加。
审查清单每次都从审查者的任务说明（定时任务 SKILL.md）现取，工作原则从 规则与交接/工作原则.md 现取。
考法见 归档/判例考试_至1014/考试说明.md。"""
import os, re, sys, json, html, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(BASE, '规则与交接', '判例库')
MAT = os.path.join(BASE, '归档', '判例考试_至1014', '考试材料')
SKILL = os.path.expanduser('~/.claude/scheduled-tasks/popup-tag-push-reviewer/SKILL.md')
PRINCIPLES = os.path.join(BASE, '规则与交接', '工作原则.md')
REF = os.path.join(BASE, '来源资料', '参考版面_通行证完整方案V10.html')

# 判例按你提出意见的先后排序（同一时刻的并列）
ORDER = ['07', '02', '01', '09', '10', '11', '08', '05', '06', '04', '03', '12']

# 考试单元：当时原文。strip＝举一反三考时要去掉的判例（本单元及之后的判例）
UNITS = {
 'U1': dict(src='归档/旧链_至1008/支撑文件/02_弹窗分人群定制方案.html', grade=['01'], fp=['02'],
            desc='02 弹窗分人群定制方案：方案线的方案稿，作者已提交，待 Dk 验收。'),
 'U2': dict(src='_versions/02_text.txt', grade=['02'], fp=[],
            desc='02 弹窗分人群定制方案（纯文本，缩进表示层级）：方案线的方案稿，作者已申请交 Dk 验收。'),
 'U3': dict(src='_versions/阶段1_需求分析_重排前_1008.html', grade=['08'], fp=[],
            desc='阶段 1 需求分析：作者已申请过审。'),
 'U4': dict(src='_versions/推进计划_核心论证版_1008.md', grade=['10', '11'], fp=[], plan=True,
            desc='推进计划：规划者维护，决定当前阶段和后续各阶段做什么。请重点审它的方向：在推进什么、排了什么、接下来打算产出什么。'),
 'U5': dict(src='_versions/改写前_1009/阶段8_结论汇总.html', grade=['03', '05', '06'], fp=[],
            desc='阶段 8 结论汇总：汇总前 7 个阶段的结论与待决事项，作者已申请过审。'),
 'U6': dict(src='_versions/去业务指标前_1009/弹窗标签推送方案_V1.html', grade=['03', '04'], fp=[], ref=True,
            desc='呈交版方案初稿：准备交给主管的完整方案。作者被要求参考附带参考稿的版面。'),
 'U7': dict(src='_versions/呈交版_购买前_1009.txt', grade=['12'], fp=[],
            desc='呈交版方案（纯文本）：准备交给主管的完整方案。'),
}
# 修正稿：改对后的现稿，只考误报
FIXED = {
 'F1': dict(src=['弹窗标签推送方案_V1.html'], fp=['01', '03', '04'], ref=True,
            desc='呈交版方案：准备交给主管的完整方案。作者被要求参考附带参考稿的版面。'),
 'F3': dict(src=['阶段1_需求分析.html'], fp=['08'], desc='阶段 1 需求分析：作者已申请过审。'),
 'F4': dict(src=['过程记录/推进计划.md', '阶段产出规划.html'], fp=['10', '11'], plan=True,
            desc='推进计划，以及它依据的阶段产出规划：规划者维护，决定当前阶段和后续各阶段做什么。请重点审方向：在推进什么、排了什么、接下来打算产出什么。'),
 'F5': dict(src=['阶段8_结论汇总.html'], fp=['03', '05', '06'], desc='阶段 8 结论汇总：汇总前 7 个阶段的结论与待决事项，作者已申请过审。'),
}
# 照章考的 U1 同时充当判例 02 的修正稿（02 终版已补全貌），见 UNITS['U1']['fp']

def first_case(u):
    return min(UNITS[u]['grade'], key=ORDER.index)

def strip_set(u):
    """举一反三：本单元最早判例及之后的判例全部去掉；U6 特例：判例 04 在 09:58 已有的部分保留。"""
    i = ORDER.index(first_case(u))
    s = set(ORDER[i:])
    if u == 'U6':
        s = {'03', '04late', '12'}
    return s

def earlier_cases(u):
    i = ORDER.index(first_case(u))
    s = [c for c in ORDER[:i]]
    if u == 'U6':
        s = [c for c in ORDER if c not in ('03', '04', '12')]
    return s

# ---------- 文本转换 ----------
def totext(p):
    s = open(p, encoding='utf-8').read()
    if not p.endswith('.html'):
        return s
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    for i in range(1, 5):
        s = re.sub(rf'<h{i}\b[^>]*>', '\n' + '#' * i + ' ', s)
    s = re.sub(r'<summary\b[^>]*>', '\n▸ ', s)
    s = re.sub(r'<(td|th)\b[^>]*>', ' | ', s)
    s = re.sub(r'<li\b[^>]*>', '\n- ', s)
    s = re.sub(r'<(br|/p|/tr|/h\d|/div|/summary|/table|/ul|/ol|/section|/details)[^>]*>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t　]+\n', '\n', s); s = re.sub(r'\n[ \t]+', '\n', s); s = re.sub(r'\n{2,}', '\n', s)
    return s.strip() + '\n'

# ---------- 工作原则：去掉某些判例对应的条目 ----------
def principles(strip):
    out = []
    for line in open(PRINCIPLES, encoding='utf-8').read().split('\n'):
        hit = lambda k: k in line
        if hit('**建能力，不是改配置') and '01' in strip: continue
        if hit('**核心先行，不追落地细节') and '11' in strip: continue
        if hit('**阶段产出规划先行') and '10' in strip: continue
        if hit('**活跃、付费不作为本方案的目标或指标出现') and '03' in strip: continue
        if (hit('**边界一：') or hit('**边界二：') or hit('- **不包括**：用于圈人')) and ({'03','12'} & strip): continue
        if hit('**平台业绩是做这件事的最终原因') and '03' in strip:   # 举一反三：还原到 10/9 之前的说法
            line = '- **目的是平台业绩。** 「终极目的是平台业绩，解决问题、提升体验只是过程指标」（9/28）。'
        if hit('**推进不等答案') and '09' in strip: continue
        if hit('**短期与长期不冲突') and '05' in strip: continue
        if hit('**需求往全面写') and '08' in strip: continue
        if hit('**最终呈交参考参考稿的版面'):
            if '04' in strip: continue
            if '04late' in strip: line = line.replace('；「让你参考版面，不要照抄，你怎么胡抄啊」', '')
        if hit('**措辞专业、简洁、直接，但不缺信息；看得懂。**') and '06' in strip: continue
        if hit('- （同上，10/8 原话）') and '06' in strip:
            line = line.replace('（同上，10/8 原话）', '**措辞专业、简洁、直接，但不缺信息。**')
        if hit('八个阶段（需求分析 →') and ({'10', '11'} & strip): continue
        if hit('旧链产出（`归档/旧链_至1008/`）') and '01' in strip: continue
        if hit('每次规划和审查都核对方向') and '01' in strip: continue
        if (hit('未知的事按名称、机制') or hit('重要又拿不到的数据，写成') or hit('问题可以在末尾列成')) and '09' in strip: continue
        if hit('需求和场景按理想状态写全') and '08' in strip: continue
        if hit('每个结论、每处设计写成「因为') and '01' in strip: continue
        if hit('审查者每次检查：'):
            parts = [('理由推不推得出', '01'), ('有没有越界写下一阶段或落地内容', '11'), ('结构与格式', None),
                     ('有没有停在「待确认」不给推断', '09')]
            keep = [p for p, c in parts if c is None or c not in strip]
            line = '- 审查者每次检查：' + '；'.join(keep) + '。'
        out.append(line)
    return '\n'.join(out)

# ---------- 审查清单：从审查者任务说明里现取 ----------
def checklist(strip):
    s = open(SKILL, encoding='utf-8').read()
    keep = []
    m = re.search(r'^你的价值在于.*$', s, flags=re.M)
    if m: keep.append(m.group(0))
    for title in ['第 2.5 步', '第 3 步', '第 4.5 步', '第 5 步']:
        m = re.search(rf'^## {re.escape(title)}.*?(?=^## )', s, flags=re.M | re.S)
        if m: keep.append(m.group(0).rstrip())
    t = '\n\n'.join(keep)
    if '01' in strip:
        t = re.sub(r'\*\*旧机制的教训：.*?\*\*', '', t)
        t = t.replace('**方向检查**：本阶段内容能否指回需求分析的目的和 5 项能力；不能的写「⚠ 方向偏离」。', '')
    lines = []
    for line in t.split('\n'):
        if re.match(r'^(8\. \*\*设计卡|9\. \*\*队列项)', line): continue
        if line.startswith('1. **理由推不推得出') and '01' in strip: continue
        if line.startswith('5. **越界') and '11' in strip: continue
        if line.startswith('11. **需求有没有预先删减') and '08' in strip: continue
        if line.startswith('10. **未知的处理') and '09' in strip: continue
        tags = re.findall(r'判例 (\d\d)', line)   # 审查方法里标了出处判例的问法，举一反三时随判例一起去掉
        if tags and any(t in strip for t in tags): continue
        lines.append(line)
    head = ('# 审查方法（测验版）\n\n（测验说明：本测验没有格式检查脚本、设计卡、队列和复算脚本，推进计划与阶段产出规划表只在题目列为待审文件时提供；'
            '方法里涉及缺少材料的检查跳过，其余照做。输出格式以题目为准，不写审查记录。）\n\n')
    return head + '\n'.join(lines) + '\n'

# ---------- 判例库合订本 ----------
def case_file(no):
    return glob.glob(os.path.join(LIB, f'判例_{no}_*.md'))[0]

def cases_bundle(nos):
    parts = ['# 判例库（合订本）\n\n每条判例是 Dk 退回过的一类问题。审查时把每条当检查项：看待审文件里有没有同类问题。\n']
    for no in sorted(nos):
        parts.append(open(case_file(no), encoding='utf-8').read())
    return '\n\n---\n\n'.join(parts)

# ---------- 题目 ----------
def prompt(files, plan, with_pred):
    lines = ['这是一次审查测验，用来检验审查方法，不是真实审查。', '',
             '规则：只读下面列出的文件，不读其他任何文件；不搜索、不浏览项目目录；不运行脚本；不写也不修改任何文件。', '',
             '项目背景：台湾老虎机类游戏平台的「弹窗、标签、推送」三项运营能力建设方案。作者是 agent 团队；读者是项目负责人 Dk，由他决定是否交给主管拍板。', '',
             '请完整阅读：']
    for i, (label, path, note) in enumerate(files, 1):
        lines.append(f'{i}. {label}：{path}' + (f'（{note}）' if note else ''))
    lines += ['', '任务：按审查方法审待审文件。假设你就是要拍板的 Dk 或主管，找出会让你不敢拍板的地方。', '',
              '只输出以下内容（中文，不要别的）：',
              '结论：通过 / 退回',
              '问题清单：按严重程度排序，最多 10 条；每条一行，格式「必须或建议｜位置｜问题（引原文）｜依据｜要求」']
    if plan:
        lines.append('对计划的意见：（没有就写「无」）')
    if with_pred:
        lines.append('Dk 最可能挑的 3 处：（每处一句）')
    return '\n'.join(lines) + '\n'

def build(rnd, with_cases):
    root = os.path.join(MAT, rnd)
    for d in ['文件', '原则', '清单', '判例', '题目']:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    def W(rel, text):
        p = os.path.join(root, rel)
        open(p, 'w', encoding='utf-8').write(text)
        return p
    ref = W('文件/参考稿.txt', totext(REF))
    p_full = W('原则/照章.md', principles(set()))
    c_full = W('清单/照章.md', checklist(set()))
    k_full = W('判例/全部.md', cases_bundle([c for c in ORDER])) if with_cases else None
    with_pred = '预判' in open(SKILL, encoding='utf-8').read() and with_cases
    runs = []
    def add(rid, mode, docs, desc, prin, chk, cases, grade, fp, plan, use_ref):
        files = [('审查方法', chk, None), ('工作原则', prin, None)]
        if cases: files.append(('判例库', cases, None))
        for i, d in enumerate(docs):
            files.append(('待审文件' if i == 0 else '待审文件（续）', d, desc if i == 0 else None))
        if use_ref: files.append(('参考稿', ref, '作者被要求参考它的版面'))
        q = W(f'题目/{rid}.md', prompt(files, plan, with_pred))
        runs.append(dict(id=rid, mode=mode, prompt=q, grade=grade, fp=fp))
    for u, cfg in UNITS.items():
        doc = W(f'文件/{u}_原文.txt', totext(os.path.join(BASE, cfg['src'])))
        add(f'{u}_照章', '照章', [doc], cfg['desc'], p_full, c_full, k_full, cfg['grade'], cfg['fp'], cfg.get('plan'), cfg.get('ref'))
        st = strip_set(u)
        p = W(f'原则/举一反三_{u}.md', principles(st))
        c = W(f'清单/举一反三_{u}.md', checklist(st))
        k = W(f'判例/举一反三_{u}.md', cases_bundle(earlier_cases(u))) if with_cases else None
        add(f'{u}_举一反三', '举一反三', [doc], cfg['desc'], p, c, k, cfg['grade'], [], cfg.get('plan'), cfg.get('ref'))
    for f, cfg in FIXED.items():
        docs = [W(f'文件/{f}_修正稿_{i}.txt', totext(os.path.join(BASE, s))) for i, s in enumerate(cfg['src'])]
        add(f'{f}_修正稿', '修正稿', docs, cfg['desc'], p_full, c_full, k_full, [], cfg['fp'], cfg.get('plan'), cfg.get('ref'))
    json.dump(runs, open(os.path.join(root, 'runs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{rnd}：{len(runs)} 道题，材料在 {root}')
    for r in runs:
        print(r['id'], r['mode'], '考', r['grade'], '误报', r['fp'])

if __name__ == '__main__':
    build(sys.argv[1], '--with-cases' in sys.argv)
