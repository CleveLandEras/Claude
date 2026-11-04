#!/bin/bash
# 改记忆：思考页 7.2 ＋ 必答⑦（「功能框架怎么写」那条被 Dk 推翻的记忆）。
# 默认只打印要做的改动（预演），不碰任何文件；加 --执行 才真改。
# 删一律 mv 进同一记忆文件夹的 _已并入全局规则_1029/，不硬删。
# 用法：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改记忆.sh            （预演）
#       bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改记忆.sh --执行     （真改）
exec /usr/bin/python3 -I - "$@" <<'PY'
import difflib, glob, os, re, subprocess, sys

DO = '--执行' in sys.argv
H = os.path.expanduser('~')
PR = f'{H}/.claude/projects'
C = f'{PR}/-Users-decheng-huang-claude/memory'
P = f'{PR}/-Users-decheng-huang-claude---------/memory'
D = f'{PR}/-Users-decheng-huang-Documents-dy/memory'
S1 = glob.glob(f'{PR}/*scratch-2026-10-27-02b1c4/memory')[0]
S2 = glob.glob(f'{PR}/*scratch-2026-10-29-7cf6e4/memory')[0]
ARCH = '_已并入全局规则_1029'

ops = []
def edit(p, old, new): ops.append(('edit', p, old, new))
def drop_paras(p, prefixes, tail): ops.append(('drop', p, prefixes, tail))
def body(p, text, desc=None): ops.append(('body', p, text, desc))
def keep_para(p, prefix): ops.append(('keep', p, prefix))
def write(p, text): ops.append(('write', p, text))
def mv(p): ops.append(('mv', p))

# ---------- claude 记忆（#44–52；#49 即必答⑦）----------
M = f'{C}/MEMORY.md'
edit(M, '这里只记项目事实和少数情境做法。', '这里只记事实（谁、在哪、一次性决定），做法和规则在规则文件里（见 `_底座/规则体系说明.md`）。')
edit(M, '；对方案只用 需求评审材料.pptx（12 页），待 Dk 验收；10/29 还没和主管对过，夜里四份草稿不进验收、等主管反馈', '')
edit(M, '金好运/星城/豪神 10/09 录屏报告待 Dk 验收；流程、工具与 10/13 方案口径要点', '金好运/星城/豪神 10/09 录屏报告的位置；做法见 竞品跟踪分析/先看这里.md')
edit(M, '崔峰龙是 Dk 的主管；讲协作要点名具体的人和步骤', '崔峰龙是 Dk 的主管')
edit(M, '工作区 商城/，先读 先看这里.md', '工作区 商城/，入口 先看这里.md')
edit(M, '- [评审版 10/28 本机改稿](review-draft-v9-local.md) — 评审版_定稿改_1027/ 改完待 Dk 验收；现状看先看这里.md 顶部，接着改看该文件夹 README 与重截拼装脚本\n', '')
edit(M, '；Jira 与 Confluence 只读\n', '\n')
edit(M, '- [功能框架怎么写](function-framework-means-pages.md) — 给主管：业务模块›功能›设计点，设计点挂为什么与参照；不按页面、不写操作清单和规则口径；脑图要能点开收起\n', '')
edit(M, '- [方法论对话不动手](methodology-session-not-executor.md) — 旁支对话里只给方法论和结论，发给对应执行对话去改；不在这里问要不要我改\n', '')
body(f'{C}/activity-config-tool-project.md',
     '需求表项目名「入口调整」（P0），最终目标是「活动灵活配置使用，通过配置满足各情况下营运需求」，不是只调入口。'
     '正本在 `/Users/decheng.huang/claude/商城/`，不进 git。'
     '入口是 `商城/先看这里.md`，现状、已定的设计、Dk 的决定和做法都在里面；10/29 起这里不再记这个项目的状态。\n')
body(f'{C}/competitor-tracking-project.md',
     '目录 `/Users/decheng.huang/claude/竞品跟踪分析/`，入口 `先看这里.md`（报告在哪、跟踪怎么做都在里面，10/29 从这条记忆挪过去）。'
     '三款竞品：金好运（录屏1）、星城（录屏2，已更名「星城」）、豪神娱乐城（录屏3）。\n',
     '竞品跟踪分析项目（金好运、星城、豪神 10/09 录屏）在哪；做法见该文件夹 先看这里.md')
body(f'{C}/dk-product-newcomer.md',
     'Dk（Jira 显示名 Decheng Huang(黄德成)）2026-10-28 自述「我属于新人也不够了解」团队工作模式。按 Jira 月度集合，产品部只有 Dk 和崔峰龙两人；'
     '崔峰龙是 Dk 的主管（Dk 10/29 确认：「是主管」），材料里的「主管」就是他一个人。'
     'Dk 的职责（Dk 10/29 原话）：「他接产品部的所有活，而我的职责是尽可能给他分担，目前我只分担了一小部分」——产品部的活都在 Dk 可分担的范围内。'
     'Dk 在 Jira 上名下目前只有日报。写规格、拆单、验收由开发部策划（EP，顾亿颉一组）完成，排版本由于金伶负责。'
     '详细分工在 `~/claude/团队工作模式/`；写团队协作建议的做法见它的 `先看这里.md`「依据与边界」。\n')
drop_paras(f'{C}/claude-usage-diagnosis-1029.md', ['**How to apply:**'], '接到改工作方式这类话题怎么做，见 `~/claude/用好Claude/先看这里.md`。')
edit(f'{C}/claude-usage-diagnosis-1029.md', '别再往 `~/.claude` 加第三套叫法。', '')
mv(f'{C}/function-framework-means-pages.md')   # 必答⑦：Dk 10/29 18:0x 已推翻；第二段不补进判例 56
mv(f'{C}/methodology-session-not-executor.md')
mv(f'{C}/review-draft-v9-local.md')
body(f'{C}/team-working-mode-folder.md',
     '2026-10-28 Dk 要我讲清「团队工作模式」，并要求把结果「归属到一个地方」。现在统一放在 `/Users/decheng.huang/claude/团队工作模式/`'
     '（入口 `先看这里.md`，主报告 `2026-10-28_团队工作模式.html`，JQL 与来源在 `数据/查询与来源.md`），根目录 CLAUDE.md 已登记为跨项目参考资料。'
     '查的是 Jira 的 RICH 项目和 Confluence 的 JD 空间「Jira Documentation」。这个文件夹写什么、怎么维护，见它的 `先看这里.md`「依据与边界」。\n',
     '团队分工、需求链路、版本节奏、Jira 用法的总结统一放在工作区根目录 团队工作模式/')

# ---------- 弹窗记忆（#54–64）----------
M = f'{P}/MEMORY.md'
edit(M, '这里只记弹窗项目的事实和做法。原记忆文件在 `_已并入全局规则_1029/`，只作出处。回复一律用简体中文。',
     '这里只记弹窗项目的事实，做法和规则在规则文件里（见 `~/claude/_底座/规则体系说明.md`）。原记忆文件在 `_已并入全局规则_1029/`，只作出处。')
edit(M, '「现行说法」为准；结构先行、边界看得见、现状与做法成对、不写元信息', '「现行说法」为准')
for line in ['- [主对话只做决策与核对](main-context-orchestrate-only.md)', '- [需求先写全再分档](requirements-full-then-trim.md)',
             '- [后台界面静态展示](backend-ui-static-readable-display.md)', '- [屡退的设计交新代理重做](fresh-agent-for-visual-design.md)',
             '- [直接改原文件；固定目录渲染](edit-in-place-render-fixed-folder.md)', '- [日志新在上、时间取时钟](logs-newest-first-real-clock.md)']:
    ops.append(('dropline', M, line))
ops.append(('setline', M, '- [控制 token；暂停要停用定时任务](token-and-scheduled-task-cost.md)',
            '- [暂停要停用定时任务](token-and-scheduled-task-cost.md) — 放暂停文件停不了定时任务，要停用'))
edit(M, '推送前刷新仓库里的记忆快照与汇报技能', '推送前刷新仓库里的汇报技能副本')
edit(f'{P}/popup-project-02-rejected-capability-reframe.md', "→ the checklist's 第六节 进度", '→ 过程记录/进度_*.md')
keep_para(f'{P}/writing-and-layout.md', 'Source of truth:')
ops.append(('cut', f'{P}/writing-and-layout.md', ' Precedence:', ' Which file wins on conflict: `规则与交接/标准体系.md` 〇.2 (business rules in 已定事项 rank above the writing standard); internal codes: global rule 26.\n'))
body(f'{P}/popup-project-02-rejected-capability-reframe.md',
     'Project `/Users/decheng.huang/claude/弹窗标签推送系统/`: popup / tag / push capability for a Taiwan slot-game platform; Dk reports to his boss 主管. '
     'Status is kept only in the project files, not here.\n\n'
     'Where things are: `先看这里.md` (deliverables and status) → `规则与交接/标准体系.md` 第〇节 (where every rule and record lives, precedence, how to work) → '
     'progress files `过程记录/进度_弹窗标签推送方案.md` and `过程记录/进度_推送系统后台集成需求.md`; the checklists `规则与交接/标准_*.md` keep only the standard; '
     '`过程记录/对话分工.md`; nightly notes `过程记录/夜间推进_<MMDD>夜.md`.\n\n'
     'Two workstreams: 弹窗标签推送方案 (deck `弹窗标签推送方案/弹窗标签推送方案.pptx`); 推送系统后台集成需求 (stages in `规则与交接/推送系统后台集成需求.md` §八; '
     '需求评审 uses the prototype `3_原型.html` since 10/16; the design overview `5_设计概要.pptx` is paused).\n\n'
     'Standing setup: business rules `规则与交接/已定事项.md`; writing `写作标准_合并版.md`; nightly scheduled task `popup-tag-push-night-global` 19:00–08:30, '
     'disabled as of 10/19 (gate `_scripts/夜间_闸门.py`; `暂停.txt` does not affect it); evaluation bank `规则与交接/评审题库/`. '
     'The 10/14 calibration lesson and the 10/16 self-loop conditions moved to 工作原则 乙·5 on 10/29.\n')
drop_paras(f'{P}/transcripts-include-queued-messages.md', ['**Why:**', '**How to apply:**'], '引用 Dk 以前的话怎么查，见弹窗 `规则与交接/工作原则.md` 乙·5「引用 Dk 以前说的话」。')
edit(f'{P}/huashu-design-not-installed.md', 'pl_pptx渲染.sh workflow ([[edit-in-place-render-fixed-folder]]).', 'pl_pptx渲染.sh workflow (fixed render folder, see the project CLAUDE.md).')
drop_paras(f'{P}/huashu-design-not-installed.md', ['**How to apply:**'], '以后要用时怎么装，见弹窗 `规则与交接/工作原则.md` 乙·4。')
ops.append(('desc', f'{P}/huashu-design-not-installed.md', '"10/15 Dk decided not to install the huashu-design skill (先不装，以后要做弹窗效果图或演示动画时再说); how to install it then: 弹窗 工作原则 乙·4"'))
ops.append(('desc', f'{P}/writing-and-layout.md', '"Where Dk\'s writing, wording and layout rules live: 弹窗标签推送系统/规则与交接/写作标准_合并版.md (现行说法 wins; maintain only this .md); which file wins on conflict: 标准体系 〇.2"'))
ops.append(('desc', f'{P}/github-repo-sync.md', '"Dk\'s private GitHub repo Clarelive/Claude mirrors ~/claude; local git repo lives at ~/claude with a whitelist .gitignore; the report-format skill is copied into the repo as a snapshot (the memory snapshot 规则与交接/记忆_快照/ is frozen at 10/20)"'))
mv(f'{P}/main-context-orchestrate-only.md')
mv(f'{P}/requirements-full-then-trim.md')
mv(f'{P}/backend-ui-static-readable-display.md')
mv(f'{P}/fresh-agent-for-visual-design.md')      # 已并进 工作原则 甲·2
mv(f'{P}/edit-in-place-render-fixed-folder.md')   # 固定目录渲染已写进 弹窗 CLAUDE.md
mv(f'{P}/logs-newest-first-real-clock.md')        # 后半句已并进 工作原则 甲·3
body(f'{P}/token-and-scheduled-task-cost.md',
     '放暂停文件（`暂停.txt`）停不了定时任务：10/10–10/12 四个定时任务照样每几分钟醒一次读暂停文件，空耗约 46 小时。要停就把每个定时任务设成 `enabled: false`（可恢复）。\n',
     '放暂停文件停不了定时任务，要停用（10/10–10/12 的实例）')
edit(f'{P}/github-repo-sync.md',
     '- Snapshots that do not sync by themselves: this memory folder → `弹窗标签推送系统/规则与交接/记忆_快照/`; `~/.claude/skills/report-format` → `弹窗标签推送系统/.claude/skills/report-format/`. Refresh them before pushing when they change.',
     '- The report-format copy does not sync by itself: `~/.claude/skills/report-format` → `弹窗标签推送系统/.claude/skills/report-format/`; refresh it before pushing when it changes. `规则与交接/记忆_快照/` is frozen at 10/20 and is not refreshed.')

# ---------- 抖音记忆（#68–77；做法已写进 ~/Documents/dy/CLAUDE.md）----------
write(f'{D}/MEMORY.md',
      "- [Douyin account experiment](douyin-account-experiment.md) — user handed Claude their 抖音 account on 2026-10-27; content is Claude's call; new session starts from dy/现状.md\n"
      '- 做法都在 `~/Documents/dy/CLAUDE.md`（10/29 从记忆挪过去；原文件在 `_已并入全局规则_1029/`）。\n')
body(f'{D}/douyin-account-experiment.md',
     'On 2026-10-27 the user handed their Douyin (抖音) account to Claude as an experiment: 「纯粹想看看你会用账号做什么，会做成什么样」. '
     'The folder /Users/decheng.huang/Documents/dy is the workspace.\n\n'
     'Arrangement the user set: they scan the QR login and enter any CAPTCHA themselves; Claude operates through the built-in browser on creator.douyin.com; '
     'the user may offer theme suggestions as reference only. The user has a Grok bot with its own virtual computer that can scroll the Douyin app and download videos.\n\n'
     "The user's goal is curiosity about Claude's own choices, not growth targets. How Claude works on this account (publish confirmations, AI label, comments, Grok, entry files): `~/Documents/dy/CLAUDE.md`.\n")
for n in ['douyin-self-direction', 'douyin-comment-reply-limit', 'douyin-not-work-mode', 'douyin-editing-not-style',
          'douyin-no-third-party-accounts', 'douyin-workflow-measure-references', 'douyin-one-browser-agent', 'reply-in-chinese']:
    mv(f'{D}/{n}.md')

# ---------- 两份 scratch 记忆（#78–82）----------
write(f'{S1}/MEMORY.md', '')
mv(f'{S1}/supervision-dont-let-sessions-idle.md')
mv(f'{S1}/progress-report-as-timeline.md')         # 已并进 report-format「讲进度时」
write(f'{S2}/MEMORY.md', '- [Session scope: mind-map tool only](session-scope-mindmap-tool.md) — this session is only the paste-mind-map tool\n')
body(f'{S2}/session-scope-mindmap-tool.md',
     "This session's job is the 粘贴即脑图 tool (Dk pastes mind-map code, gets a usable map). Dk, 10/29: 「之后不要再做和你定位无关的事情」. "
     'Where out-of-scope work goes: global rule 2 in `~/.claude/CLAUDE.md`.\n',
     'This session is only the paste-mind-map tool for Dk')

# ---------- 计算 ----------
def split_fm(t):
    m = re.match(r'(---\n.*?\n---\n)(.*)', t, re.S)
    return (m.group(1), m.group(2)) if m else ('', t)

new, err, moves = {}, [], []
def cur(p):
    if p not in new:
        new[p] = open(p, encoding='utf-8').read()
    return new[p]
for op in ops:
    k, p = op[0], op[1]
    if k == 'mv':
        if os.path.exists(p): moves.append(p)
        else: err.append(f'要挪的文件不存在：{p}')
        continue
    if not os.path.exists(p) and k != 'write':
        err.append(f'文件不存在：{p}'); continue
    if k == 'write':
        if os.path.exists(p): cur(p)
        new[p] = op[2]; continue
    t = cur(p)
    if k == 'edit':
        n = t.count(op[2])
        if n != 1: err.append(f'原句命中 {n} 次（要 1 次）：{os.path.basename(p)}｜{op[2][:50]}'); continue
        new[p] = t.replace(op[2], op[3], 1)
    elif k == 'dropline' or k == 'setline':
        L = t.split('\n'); hit = [i for i, l in enumerate(L) if l.startswith(op[2])]
        if len(hit) != 1: err.append(f'行命中 {len(hit)} 次：{op[2][:50]}'); continue
        if k == 'dropline': del L[hit[0]]
        else: L[hit[0]] = op[3]
        new[p] = '\n'.join(L)
    elif k == 'body':
        fm, _ = split_fm(t)
        if op[3]: fm = re.sub(r'^description: .*$', 'description: ' + op[3].replace('\\', '\\\\'), fm, count=1, flags=re.M)
        new[p] = fm + '\n' + op[2]
    elif k == 'desc':
        if len(re.findall(r'^description: .*$', t, flags=re.M)) != 1: err.append(f'描述行不唯一：{os.path.basename(p)}'); continue
        new[p] = re.sub(r'^description: .*$', lambda m: 'description: ' + op[2], t, count=1, flags=re.M)
    elif k == 'cut':
        i = t.find(op[2])
        if i < 0 or t.count(op[2]) != 1: err.append(f'截断点命中 {t.count(op[2])} 次：{op[2]}'); continue
        new[p] = t[:i] + op[3]
    elif k == 'keep':
        fm, b = split_fm(t); paras = [x for x in b.split('\n\n') if x.strip().startswith(op[2])]
        if len(paras) != 1: err.append(f'段落命中 {len(paras)} 次：{op[2]}'); continue
        new[p] = fm + '\n' + paras[0].strip() + '\n'
    elif k == 'drop':
        fm, b = split_fm(t); paras = b.split('\n\n'); keep = []
        for x in paras:
            if any(x.strip().startswith(pre) for pre in op[2]): continue
            keep.append(x)
        if len(keep) != len(paras) - len(op[2]): err.append(f'要删的段落没找全：{os.path.basename(p)}'); continue
        new[p] = fm + '\n\n'.join(keep).rstrip('\n') + '\n\n' + op[3] + '\n'

# ---------- 打印 ----------
orig = {}
for p in new:
    orig[p] = open(p, encoding='utf-8').read() if os.path.exists(p) else ''
changed = [p for p in new if new[p] != orig[p]]
nidx0 = sum(1 for p in changed if os.path.basename(p) == 'MEMORY.md')
print(f'==== 改写 {len(changed)} 个文件（正文 {len(changed) - nidx0}、索引 {nidx0}）====')
for p in changed:
    print(f'\n## {p.replace(H, "~")}')
    for l in difflib.unified_diff(orig[p].splitlines(), new[p].splitlines(), lineterm='', n=0):
        if not l.startswith(('---', '+++', '@@')): print('  ' + l[:220])
print(f'（--执行 时先把这 {len(changed)} 个文件的改前原文复制进各自 {ARCH}/，文件名加 _改前_1029）')
print(f'\n==== 挪进 {ARCH}/ 共 {len(moves)} 个文件 ====')
moved_names = {os.path.basename(m)[:-3] for m in moves}
SKIP = ('_已并入', '记忆_快照', '/归档/', 'worktrees', '/_底座/任务/', '/backups/')
roots = [f'{H}/claude', f'{H}/Documents/dy', f'{H}/.claude/skills', f'{H}/.claude/agents', f'{H}/.claude/hooks', f'{H}/.claude/CLAUDE.md'] + glob.glob(f'{PR}/*/memory')
for m in moves:
    name = os.path.basename(m)[:-3]
    r = subprocess.run(['grep', '-rl', '--include=*.md', '--include=*.py', '--include=*.json', name] + roots, capture_output=True, text=True)
    hits = [h for h in r.stdout.split('\n') if h and not any(s in h for s in SKIP) and h != m and os.path.basename(h)[:-3] not in moved_names
            and (name in new.get(h, open(h, encoding='utf-8', errors='ignore').read()))]
    print(f'  {m.replace(H, "~")}  →  {ARCH}/' + (f'    仍被引用：{", ".join(x.replace(H, "~") for x in hits)}' if hits else ''))

print('\n==== 核对 ====')
card = f'{H}/claude/弹窗标签推送系统/规则与交接/类型卡/原型.md'
print('  原型卡有「静态」：', '有' if '静态' in open(card, encoding='utf-8').read() else '没有（按思考页不补；「静态」原文在需求评审材料卡里）')
print('  判例 56：不补记忆第二段（Dk 10/29 18:0x 已推翻「设计点挂为什么与参照」，原话在 _底座/纠正记录.md，由每周「整理纠正」并进判例）')
if err:
    print('\n==== 有问题，没改任何文件 ===='); [print('  ✘ ' + e) for e in err]; sys.exit(1)
if not DO:
    print('\n预演完毕，没有改任何文件。确认后运行：bash ~/claude/_底座/任务/2026-10-29_规则体系分层整理/改记忆.sh --执行'); sys.exit(0)
for p in changed:
    a = os.path.join(os.path.dirname(p), ARCH); os.makedirs(a, exist_ok=True)
    bak = os.path.join(a, os.path.basename(p)[:-3] + '_改前_1029.md')
    if orig[p] and not os.path.exists(bak): open(bak, 'w', encoding='utf-8').write(orig[p])
for p in changed:
    open(p, 'w', encoding='utf-8').write(new[p])
for m in moves:
    a = os.path.join(os.path.dirname(m), ARCH); os.makedirs(a, exist_ok=True)
    dst = os.path.join(a, os.path.basename(m))
    if os.path.exists(dst): dst = dst[:-3] + '_1029b.md'
    os.rename(m, dst)
nidx = sum(1 for p in changed if os.path.basename(p) == 'MEMORY.md')
print(f'\n已执行：改写 {len(changed)} 个（正文 {len(changed) - nidx}、索引 {nidx}）、挪走 {len(moves)} 个。')
PY
