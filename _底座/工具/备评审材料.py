#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""备评审材料：分角色验收派评审之前，从现行对齐卡生成给评审的材料文件夹。

评审（五个角色、总验收人）只读这个文件夹和出处清单里列的文件，不进 ~/claude/_底座/。
做法见 ~/claude/_底座/分角色验收/做法.md 第 2 步。每次派评审前重跑，不手抄、不复用旧材料。

用法：
  python3 备评审材料.py <任务文件> <成品路径…> [--出处 <清单文件>] [--清单 1,2,5,10,17-21]
                        [--读者称呼 <称呼>] [--本项目 <一句>] [--别的项目 <一句>] [--渲染]
  python3 备评审材料.py <退回那一刻的卡> <成品路径…> --试卷 <题号>     考试用：只取卡上稳定的几条
  python3 备评审材料.py --自测

输出：/private/tmp/分角色验收/<任务名>/<MMDD_HHMM>/（考试是 考试_<题号>/<MMDD_HHMM>/），里面只有：
  成品/              成品复制件（文件夹整个复制）；.pptx 另出「_页面文字.txt」（不含备注）和「_全文.txt」（含备注）；
                     加 --渲染 时再用 看成品.py 出页面图
  对齐卡摘录.md      只取：目标（需求原文）、内容、要做的、读者、可用时间、我们是谁与产品性质、必答、完成标准、
                     这次不做、已替 Dk 定；--试卷 时只取目标（需求原文）、读者、可用时间、我们是谁与产品性质
  打分四档.md        读者换成卡上的读者
  验收清单原文.md    默认全部条目；--清单 收窄
  出处清单.md        --出处 给的清单；没给就写明「没有另给出处清单」
  总验收人说明.md    复制 ~/claude/_底座/分角色验收/总验收人说明.md
  派活/              6 份派活提示词：结构、读者、边界、依据、措辞（模板在 ~/claude/_底座/分角色验收/角色/）
                     和总验收人第一步（模板是本脚本里的 FIRST_STEP）

屏蔽词（只防「判过的要求」漏给评审）：
  硬屏蔽：摘录里含硬屏蔽词的整句剔掉，打印「已剔除 N 句」；剔不掉（词在条目名里、剔完「目标」或「读者」空了、
          剔完还有）就退出、返回码 2、不出材料。最后再查一遍除成品外的所有文件，还有就同样退出。
  只警告：打印出来由第二级看，不剔（这几个词常出现在正当的要求里）。
  成品本身命中任一种都只警告。
退出码：0 出了材料；1 用法或输入不对；2 屏蔽词剔不掉，没出材料。
"""
import argparse
import contextlib
import datetime
import io
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path('/Users/decheng.huang/claude/_底座')
METHOD_DIR = BASE / '分角色验收'
CHECKLIST = BASE / '验收清单.md'
REGISTRY = BASE / '项目登记.md'
LOOK_TOOL = BASE / '工具' / '看成品.py'
OUT_ROOT = Path('/private/tmp/分角色验收')
SELF_TASK = BASE / '任务' / '用好Claude' / '2026-11-02_分角色验收上场_验收官退场.md'

HARD = [r'连续.{0,3}(三|3|几|两|2).{0,2}次', r'低于 ?(7|七)', r'(7|七) ?分以下', r'几分算过', r'通过条件', r'第二级专用']
HARD_RE = re.compile('|'.join('(?:%s)' % p for p in HARD))
WARN_RE = re.compile(r'计数|校准|退回过的')
# 派活提示词里不许出现指向这些目录里文件的路径（只许在「不打开…」那句里点名目录本身）
FORBIDDEN_PATH_RE = re.compile(r'_底座/[^`\s）)」，、；。]|\.claude/(?:projects|skills|backups)/[^`\s）)」，、；。]')

KEEP = ('目标', '需求原文', '内容', '要做的', '读者', '可用时间', '我们是谁', '必答', '完成标准', '这次不做',
        '已替 Dk 定', '已替Dk定')
EXAM_KEEP = ('目标', '需求原文', '读者', '可用时间', '我们是谁')
ROLES = ('结构', '读者', '边界', '依据', '措辞')
MATERIAL_FILES = {'对齐卡摘录.md', '打分四档.md', '验收清单原文.md', '出处清单.md', '总验收人说明.md'}
PROMPT_FILES = {r + '.md' for r in ROLES} | {'总验收人第一步.md'}
PLACEHOLDERS = ('{成品清单}', '{读者一句}', '{可用时间}', '{本项目}', '{别的项目}', '{出处清单路径}', '{材料目录}')

FIRST_STEP = """开工先读磁盘上的 ~/.claude/CLAUDE.md（用简体中文回答）。

你是这份成品的总验收人。这一步先不看任何角色报告，只按读者的眼光看成品，打分并写下最大的问题；之后会把五个角色的报告发给你，再请你给最终结论。

成品（先通读全文再判）：
{成品清单}

这份成品的要求（对齐卡摘录）：{材料目录}/对齐卡摘录.md
怎么判（必读）：{材料目录}/总验收人说明.md
打分四档：{材料目录}/打分四档.md
验收清单原文：{材料目录}/验收清单原文.md

读者：{读者一句}
可用时间：{可用时间}

规矩：只读，不改任何文件；只读材料文件夹 {材料目录} 里的文件和出处清单 {出处清单路径} 里列的文件，不打开 `~/claude/_底座/`、`~/.claude/projects/`、`~/.claude/skills/`、`~/.claude/backups/` 下的任何文件。

交回（不超过 250 字）：「怎么判」里两件事各一句结果；分数（按打分四档）；最大的问题（一句）。
"""

SCORE_BANDS = ('9＝{称呼}按可用时间（{时间}）看完，能复述结论和下面每一块在说什么，没有一处要停下来问；'
               '7＝重点都看得懂，只剩措辞一类小毛病，不影响判断；'
               '5＝看得出在讲什么，但有一处要停下来问（说法看不懂、依据撑不住，或要自己拼出结论）；'
               '3＝要从头读到尾才知道想说什么，或混进了不该有的内容（过程、别的项目的事、编出来的规则）。')

TERM = set('。！？；!?;')
CLOSE = set('」』）)】”’')
PAIRS = (('「', '」'), ('（', '）'), ('『', '』'))


class Stop(Exception):
    """屏蔽词剔不掉、或输入不对：不出材料。"""
    def __init__(self, msg, code=2):
        super().__init__(msg)
        self.code = code


# ---------- 读卡 ----------

def read(p):
    return Path(p).read_text(encoding='utf-8', errors='replace')


def card_block(text):
    """对齐卡那一节；文件里没有「## 对齐卡」（例如考试用的卡摘录）时，从第一条「- **」起到下一个「## 」。"""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    m = re.search(r'^## 对齐卡.*$', text, re.M)
    if m:
        s = text[m.end():]
    else:
        m = re.search(r'^- \*\*', text, re.M)
        if not m:
            return ''
        s = text[m.start():]
    j = re.search(r'^## ', s, re.M)
    return s if not j else s[:j.start()]


def card_bullets(block):
    """[(条目名, 首行正文, [下面的行])]"""
    out, cur = [], None
    for line in block.split('\n'):
        m = re.match(r'^- \*\*(.+?)\*\*\s*[:：]?(.*)$', line)
        if m:
            cur = [m.group(1), m.group(2), []]
            out.append(cur)
        elif cur is not None and line.strip():
            cur[2].append(line)
    return out


def clean_name(n):
    """条目名里带日期的括号是过程记录（谁几点改的），去掉。"""
    return re.sub(r'（[^（）]*\d+/\d+[^（）]*）', '', n).strip()


def clean_text(t):
    return re.sub(r'[，,]\s*Dk \d+/\d+ [\dx:：]+ ?同意(改设计)?', '', t)


def project_of(text):
    m = re.search(r'^项目[:：]\s*(.+)$', text, re.M)
    return m.group(1).strip() if m else ''


# ---------- 剔句 ----------

def split_sentences(s):
    out, cur, i = [], '', 0
    while i < len(s):
        ch = s[i]
        cur += ch
        i += 1
        if ch in TERM:
            while i < len(s) and (s[i] in TERM or s[i] in CLOSE):
                cur += s[i]
                i += 1
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    return out


def leftovers(seg):
    """剔掉的句子里没配对的引号、括号留在原处，免得前后对不上。"""
    pre, post = '', ''
    for o, c in PAIRS:
        depth, lead = 0, 0
        for ch in seg:
            if ch == o:
                depth += 1
            elif ch == c:
                if depth:
                    depth -= 1
                else:
                    lead += 1
        pre += c * lead
        post += o * depth
    return pre + post


def strip_hits(body, removed, where):
    if not HARD_RE.search(body):
        return body
    kept = []
    for seg in split_sentences(body):
        if HARD_RE.search(seg):
            removed.append((where, seg.strip()))
            kept.append(leftovers(seg))
        else:
            kept.append(seg)
    return ''.join(kept)


def has_content(s):
    return bool(re.sub(r'[\s「」『』（）()。！？；，、：:!?;,.\-*0-9]', '', s))


LINE_PREFIX = re.compile(r'^(\s*(?:[-*+]|\d+[.、)）])?\s*)(.*)$')


def scrub_bullets(bullets, keep):
    """挑条目、清过程记录、剔含硬屏蔽词的句子。返回 (条目, 剔掉的句子)。剔不掉就 raise Stop。"""
    picked = [[clean_name(n), clean_text(t), [clean_text(x) for x in sub]]
              for n, t, sub in bullets if clean_name(n).startswith(keep)]
    removed = []
    for b in picked:
        name = b[0]
        if HARD_RE.search(name):
            raise Stop('剔不掉：屏蔽词在条目名「%s」里（改卡上这条的名字，或把这句挪出卡）' % name)
        b[1] = strip_hits(b[1], removed, name)
        new_sub = []
        for line in b[2]:
            m = LINE_PREFIX.match(line)
            prefix, body = m.group(1), m.group(2)
            body2 = strip_hits(body, removed, name)
            if body2 != body and not has_content(body2):
                continue
            new_sub.append(prefix + body2)
        b[2] = new_sub
    for need in (('目标', '需求原文'), ('读者',)):
        group = [b for b in picked if b[0].startswith(need)]
        if not group:
            raise Stop('卡上没有「%s」这一条' % '／'.join(need), code=1)
        if not any(has_content(b[1]) or any(has_content(x) for x in b[2]) for b in group):
            raise Stop('剔不掉：「%s」整条都含屏蔽词，剔完就空了' % '／'.join(need))
    return picked, removed


def render_card(bullets):
    lines = ['# 对齐卡（这一份成品的要求）', '']
    for n, t, sub in bullets:
        lines.append(('- **%s**：%s' % (n, t.strip())).rstrip())
        lines += sub
    return '\n'.join(lines) + '\n'


def field(bullets, prefix):
    for n, t, sub in bullets:
        if n.startswith(prefix):
            return ' '.join([t.strip()] + [x.strip() for x in sub]).strip()
    return ''


# ---------- 验收清单 ----------

def parse_items(spec):
    out = set()
    for part in re.split(r'[,，、\s]+', spec.strip()):
        if not part:
            continue
        m = re.match(r'^(\d+)\s*[-–~]\s*(\d+)$', part)
        if m:
            out.update(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
        else:
            raise Stop('--清单 看不懂：%s（写成 1,2,5,10,17-21）' % spec, code=1)
    return out


def fmt_items(nums):
    nums = sorted(nums)
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append('%d–%d' % (nums[i], nums[j]))
        else:
            parts += [str(n) for n in nums[i:j + 1]]
        i = j + 1
    return '、'.join(parts)


def checklist_text(wanted):
    lines, got, section = [], [], None
    for line in read(CHECKLIST).split('\n'):
        if line.startswith('## '):
            section = line
            continue
        m = re.match(r'^(\d+)\.\s', line)
        if m and (wanted is None or int(m.group(1)) in wanted):
            if section:
                lines += ['', section]
                section = None
            lines.append(line)
            got.append(int(m.group(1)))
    if wanted is not None and set(wanted) - set(got):
        raise Stop('验收清单里没有第 %s 条' % fmt_items(set(wanted) - set(got)), code=1)
    title = '全部 %d 条' % len(got) if wanted is None else '第 %s 条' % fmt_items(got)
    return '# 验收清单原文（%s）\n' % title + '\n'.join(lines) + '\n'


# ---------- 成品 ----------

def pptx_texts(src):
    from pptx import Presentation
    p = Presentation(str(src))
    page, full = ['页数 %d' % len(p.slides)], ['页数 %d' % len(p.slides)]
    for i, s in enumerate(p.slides, 1):
        head = '===== 第 %d 页' % i
        page.append(head)
        full.append(head)
        for sh in s.shapes:
            if sh.has_table:
                rows = ['  ' + ' | '.join(c.text.replace('\n', ' ') for c in r.cells) for r in sh.table.rows]
                page += ['[表格]'] + rows
                full += ['[表格]'] + rows
            elif sh.has_text_frame and sh.text_frame.text.strip():
                t = '[文字] ' + sh.text_frame.text.replace('\n', ' / ')
                page.append(t)
                full.append(t)
        if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
            full += ['[备注]', s.notes_slide.notes_text_frame.text]
        else:
            full.append('[备注] 无')
    return '\n'.join(page) + '\n', '\n'.join(full) + '\n'


def copy_products(products, dest, final_dir, render):
    """复制成品，返回给提示词用的清单行（路径写成材料文件夹的最终路径）。"""
    dest.mkdir()
    listing, used = [], set()
    for src in products:
        name = src.name
        k = 2
        while name in used:
            name = '%s_%d%s' % (src.stem, k, src.suffix)
            k += 1
        used.add(name)
        final = final_dir / '成品' / name
        if src.is_dir():
            shutil.copytree(src, dest / name)
            files = sorted(str(p.relative_to(src)) for p in src.rglob('*') if p.is_file())
            more = '等 %d 个文件' % len(files) if len(files) > 6 else ''
            listing.append('- %s/（文件夹：%s%s）' % (final, '、'.join(files[:6]), more))
            continue
        shutil.copy2(src, dest / name)
        ext = src.suffix.lower()
        if ext == '.pptx':
            listing.append('- %s（原件复制件）' % final)
            try:
                page, full = pptx_texts(src)
            except Exception as e:
                print('警告：%s 抽不出文字（%s），评审只能看原件' % (src, e))
            else:
                stem = Path(name).stem
                (dest / (stem + '_页面文字.txt')).write_text(page, encoding='utf-8')
                (dest / (stem + '_全文.txt')).write_text(full, encoding='utf-8')
                listing.append('- %s（只有页面上的字，不含备注）' % (final_dir / '成品' / (stem + '_页面文字.txt')))
                listing.append('- %s（页面＋备注里的讲稿和追问）' % (final_dir / '成品' / (stem + '_全文.txt')))
        elif ext in ('.png', '.jpg', '.jpeg'):
            listing.append('- %s（页面图）' % final)
        else:
            listing.append('- %s' % final)
        if render and ext in ('.pptx', '.html', '.htm', '.pdf'):
            out = dest / (Path(name).stem + '_页面图')
            out.mkdir()
            r = subprocess.run([sys.executable, str(LOOK_TOOL), str(src), str(out)], capture_output=True, text=True)
            if r.returncode == 0:
                listing.append('- %s/（页面图）' % (final_dir / '成品' / out.name))
            else:
                shutil.rmtree(out)
                print('警告：%s 渲染失败，没出页面图：%s' % (src, (r.stderr or r.stdout).strip()[-200:]))
    return '\n'.join(listing)


# ---------- 扫屏蔽词 ----------

def scan_text(text):
    hard, warn = [], []
    for i, line in enumerate(text.split('\n'), 1):
        if HARD_RE.search(line):
            hard.append((i, HARD_RE.search(line).group(0)))
        for m in WARN_RE.finditer(line):
            warn.append((i, m.group(0)))
    return hard, warn


def is_text(p):
    return p.suffix.lower() in ('.md', '.txt', '.html', '.htm', '.csv', '.json')


def other_projects(this):
    try:
        names = re.findall(r'^## (.+)$', read(REGISTRY), re.M)
    except OSError:
        return ''
    norm = lambda s: s.replace(' ', '')
    return '、'.join(n.strip() for n in names if norm(n) != norm(this) and n.strip() not in ('总的主会话', '产出汇报'))


# ---------- 主流程 ----------

def build(card_path, products, out_root=OUT_ROOT, sources=None, items=None, exam=None, call=None,
          this_proj=None, other_proj=None, render=False, method_dir=METHOD_DIR, now=None):
    card_path = Path(card_path).expanduser()
    if not card_path.is_file():
        raise Stop('任务文件不存在：%s' % card_path, code=1)
    prods = [Path(p).expanduser() for p in products]
    for p in prods:
        if not p.exists():
            raise Stop('成品不存在：%s' % p, code=1)
    if not prods:
        raise Stop('要给至少一个成品路径', code=1)
    out_root = Path(out_root).expanduser().resolve()
    if str(out_root).startswith(str(BASE)):
        raise Stop('输出不能放在 ~/claude/_底座/ 下（评审不进这里）', code=1)

    text = read(card_path)
    bullets = card_bullets(card_block(text))
    if not bullets:
        raise Stop('读不到对齐卡条目（要有「## 对齐卡」一节，或「- **条目名**：」开头的行）', code=1)
    picked, removed = scrub_bullets(bullets, EXAM_KEEP if exam else KEEP)
    card_md = render_card(picked)
    if HARD_RE.search(card_md):
        raise Stop('剔不掉：剔句之后摘录里还有「%s」' % HARD_RE.search(card_md).group(0))

    reader = field(picked, '读者')
    when = field(picked, '可用时间').rstrip('。') or '卡上没写可用时间'
    if not call:
        call = re.split(r'[｜|]', reader, 1)[0].strip().rstrip('。；，')
        if len(call) > 12:
            call = re.split(r'[，,；;：:]', call, 1)[0]
    proj = project_of(text)
    if not this_proj:
        this_proj = '%s这个项目里的这件任务（范围以对齐卡摘录的「要做的」「这次不做」为准）' % (proj or '本')
        print('提示：没传 --本项目，边界角色用的是默认写法')
    if not other_proj:
        others = other_projects(proj)
        other_proj = ('%s这几个项目里的事' % others) if others else '本项目以外的事'
        print('提示：没传 --别的项目，边界角色用的是默认写法：%s' % other_proj)

    now = now or datetime.datetime.now()
    group = ('考试_%s' % exam) if exam else card_path.stem
    final = out_root / group / now.strftime('%m%d_%H%M')
    k = 2
    while final.exists():
        final = out_root / group / ('%s_%d' % (now.strftime('%m%d_%H%M'), k))
        k += 1
    final.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='.备料_', dir=str(final.parent)))
    try:
        listing = copy_products(prods, tmp / '成品', final, render)
        (tmp / '对齐卡摘录.md').write_text(card_md, encoding='utf-8')
        (tmp / '打分四档.md').write_text('# 打分四档（读者角色和总验收人都用）\n\n%s\n'
                                       % SCORE_BANDS.format(称呼=call, 时间=when), encoding='utf-8')
        (tmp / '验收清单原文.md').write_text(checklist_text(items), encoding='utf-8')
        if sources:
            src_text = read(Path(sources).expanduser())
            if '_底座/' in src_text:
                print('警告：出处清单里有 ~/claude/_底座/ 下的文件，评审不进这里，读不到；要评审读的先复制到别处')
        else:
            src_text = '# 可查的出处\n\n这次没有另给出处清单。依据角色只核对成品里自己写明的出处和对齐卡摘录；查不到的写「找不到」。\n'
        (tmp / '出处清单.md').write_text(src_text, encoding='utf-8')
        shutil.copy2(Path(method_dir) / '总验收人说明.md', tmp / '总验收人说明.md')
        (tmp / '派活').mkdir()
        fills = {'{成品清单}': listing, '{读者一句}': reader.rstrip('。 '), '{可用时间}': when, '{本项目}': this_proj,
                 '{别的项目}': other_proj, '{出处清单路径}': str(final / '出处清单.md'), '{材料目录}': str(final)}
        templates = [(r, read(Path(method_dir) / '角色' / (r + '.md'))) for r in ROLES] + [('总验收人第一步', FIRST_STEP)]
        for name, tpl in templates:
            for k_, v in fills.items():
                tpl = tpl.replace(k_, v)
            left = re.findall(r'\{[^{}\s]{1,8}\}', tpl)
            if left:
                raise Stop('派活/%s.md 还有没填的占位符：%s' % (name, '、'.join(left)), code=1)
            if FORBIDDEN_PATH_RE.search(tpl):
                raise Stop('派活/%s.md 里有指向评审禁入目录的路径：%s' % (name, FORBIDDEN_PATH_RE.search(tpl).group(0)), code=1)
            (tmp / '派活' / (name + '.md')).write_text(tpl, encoding='utf-8')

        # 最后一遍：除成品外的所有文件
        warns = []
        for p in sorted(tmp.rglob('*')):
            if not p.is_file() or not is_text(p):
                continue
            rel = p.relative_to(tmp)
            hard, warn = scan_text(read(p))
            in_prod = rel.parts[0] == '成品'
            if hard and not in_prod:
                raise Stop('剔不掉：%s 第 %d 行有「%s」' % (rel, hard[0][0], hard[0][1]))
            for ln, w in hard:
                warns.append('警告：成品 %s 第 %d 行有屏蔽词「%s」（成品只警告）' % (rel, ln, w))
            by_line = {}
            for ln, w in warn:
                by_line.setdefault(ln, [])
                if w not in by_line[ln]:
                    by_line[ln].append(w)
            for ln, ws in by_line.items():
                warns.append('警告：%s 第 %d 行有%s，看一眼是不是在讲判过的要求'
                             % (rel, ln, ''.join('「%s」' % w for w in ws)))
        if re.search(r'_底座/[^`\s]', card_md):
            warns.append('警告：对齐卡摘录里提到 ~/claude/_底座/ 下的路径；评审不会去读，要它读的放进出处清单（不能在 _底座 下）')
        tmp.rename(final)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

    print('已剔除 %d 句（含硬屏蔽词的整句没进摘录）' % len(removed))
    for where, seg in removed:
        print('  剔：「%s」%s' % (where, seg if len(seg) <= 60 else seg[:60] + '…'))
    for w in warns:
        print(w)
    print('材料：%s' % final)
    for p in sorted(final.rglob('*')):
        if p.is_file():
            print('  %s' % p.relative_to(final))
    return final


# ---------- 自测 ----------

def self_test():
    ok_all = True

    def check(name, cond, detail=''):
        nonlocal ok_all
        if cond:
            print('过：%s' % name)
        else:
            ok_all = False
            print('不过：%s%s' % (name, ('\n    ' + detail.replace('\n', '\n    ')) if detail else ''))

    def run(card_text, root, card_name='卡.md', **kw):
        card = root.parent / card_name
        card.write_text(card_text, encoding='utf-8')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                out = build(card, [prod], out_root=root, other_proj='别的项目', this_proj='本项目', **kw)
                return 0, out, buf.getvalue()
            except Stop as e:
                return e.code, None, buf.getvalue() + str(e)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        prod = d / '成品样例.md'
        prod.write_text('# 弹窗改成按人群弹\n- 分论点一\n', encoding='utf-8')

        # ① 本任务文件当卡：「目标」里 Dk 原话「…连续三次…」那句要被剔掉，照常出材料
        fallback = ('# 任务\n\n项目：用好Claude\n\n## 对齐卡\n- **目标（Dk 原话）**：\n'
                    '  - 新的那套：「好 没问题 就按这套来，跑完之后让用好Claude看看有没有不合理的地方。'
                    '然后对我们要产出的事情要跑到连续三次总验收人都认为没问题才行，而且这个验收通过的规则不能告诉总验收人。」'
                    '「每跑完一次都要给用好Claude看看」\n  - 「不是合成一套新的，是新的那个应该登场，旧的应该落幕」\n'
                    '- **读者**：Dk｜看一页。\n- **可用时间**：约 5 分钟。\n\n## 交接记录\n- 无\n')
        card1 = read(SELF_TASK) if SELF_TASK.is_file() else fallback
        rc, out, log = run(card1, d / '出1', '本任务卡.md')
        ex = read(out / '对齐卡摘录.md') if out else ''
        m = re.search(r'已剔除 (\d+) 句', log)
        check('① 本任务文件当卡：Dk 原话里「连续三次」那句剔掉、照常出材料（%s）'
              % ('用真文件' if SELF_TASK.is_file() else '真文件不在，用内置片段'),
              rc == 0 and out and m and int(m.group(1)) >= 1 and '连续三次' not in ex
              and not HARD_RE.search(ex) and '不是合成一套新的' in ex and '**目标' in ex,
              log)

        # ②a 「低于 7」在普通句子里：剔掉那句，别的照留
        card2 = ('## 对齐卡\n- **目标（Dk 原话）**：「做一页汇报。」\n- **读者**：主管｜看 30 秒。\n'
                 '- **完成标准**：\n  1. 只讲核心。总验收人打分低于 7 分算不过。\n  2. 每句有出处。\n')
        rc, out, log = run(card2, d / '出2a')
        ex = read(out / '对齐卡摘录.md') if out else ''
        check('②a 「低于 7」在句子里：剔掉那句（已剔除 1 句），「只讲核心」「每句有出处」照留',
              rc == 0 and '已剔除 1 句' in log and '低于' not in ex and '只讲核心' in ex and '每句有出处' in ex, log)

        # ②b 「低于 7」在条目名里：剔不掉，退出、不出材料
        card3 = ('## 对齐卡\n- **目标**：「做一页汇报。」\n- **读者**：主管\n'
                 '- **完成标准（低于 7 分算不过）**：只讲核心。\n')
        rc, out, log = run(card3, d / '出2b')
        made = (d / '出2b').exists() and any(p.is_file() for p in (d / '出2b').rglob('*'))
        check('②b 「低于 7」在条目名里：剔不掉，返回码 2，不出材料', rc == 2 and out is None and not made, log)

        # ②c 「读者」整条都是屏蔽句：剔完就空，退出
        card4 = '## 对齐卡\n- **目标**：「做一页汇报。」\n- **读者**：总验收人打分低于 7 分按有问题处理。\n'
        rc, out, log = run(card4, d / '出2c')
        check('②c 「读者」整条被剔空：返回码 2，不出材料', rc == 2 and out is None, log)

        # ③ 输出文件夹里只有列出的那些文件
        rc, out, log = run(card2, d / '出3')
        if out:
            top = {p.name for p in out.iterdir()}
            prompts = {p.name for p in (out / '派活').iterdir()}
            prods = {p.name for p in (out / '成品').iterdir()}
            filled = all('{' not in read(p) for p in (out / '派活').iterdir())
            clean = all(not HARD_RE.search(read(p)) for p in out.rglob('*') if p.is_file() and '成品' not in p.parts)
            want_top = MATERIAL_FILES | {'成品', '派活'}
            check('③ 输出文件夹里只有：%s；派活/ 6 份；成品/ 只有成品；占位符全填；除成品外无屏蔽词'
                  % '、'.join(sorted(want_top)),
                  top == want_top and prompts == PROMPT_FILES and prods == {'成品样例.md'} and filled and clean,
                  'top=%s\nprompts=%s\nprods=%s\nfilled=%s clean=%s\n%s' % (top, prompts, prods, filled, clean, log))
        else:
            check('③ 输出文件夹里只有列出的那些文件', False, log)

        # ④ --清单 收窄，标题写成「第 1、2、5、10、17–21 条」
        rc, out, log = run(card2, d / '出4', items=parse_items('1,2,5,10,17-21'))
        cl = read(out / '验收清单原文.md') if out else ''
        nums = re.findall(r'^(\d+)\. ', cl, re.M)
        check('④ --清单 1,2,5,10,17-21：只出这 9 条，标题「第 1、2、5、10、17–21 条」',
              out and nums == ['1', '2', '5', '10', '17', '18', '19', '20', '21'] and '第 1、2、5、10、17–21 条' in cl, log)

        # ⑤ --试卷：只取稳定的几条（不取完成标准）
        rc, out, log = run(card2, d / '出5', exam='99')
        ex = read(out / '对齐卡摘录.md') if out else ''
        check('⑤ --试卷：摘录只有目标、读者，不带完成标准；放在 考试_99/ 下',
              out and '**目标' in ex and '**读者' in ex and '完成标准' not in ex and out.parent.name == '考试_99', log)

    print('自测：全过' if ok_all else '自测：不过')
    return 0 if ok_all else 1


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(
        prog='备评审材料.py',
        description='分角色验收派评审之前跑：从现行对齐卡生成给评审的材料文件夹（剔掉判过的要求）。')
    ap.add_argument('task', nargs='?', metavar='任务文件', help='现行任务文件（或 --试卷 时退回那一刻的卡）')
    ap.add_argument('products', nargs='*', metavar='成品路径', help='成品文件或文件夹，可以几个')
    ap.add_argument('--出处', dest='sources', help='出处清单文件：依据、边界角色可以读的文件')
    ap.add_argument('--清单', dest='items', help='只附验收清单这几条，如 1,2,5,10,17-21；不给就附全部')
    ap.add_argument('--试卷', dest='exam', metavar='题号', help='考试用：只取卡上稳定的几条，放 考试_<题号>/')
    ap.add_argument('--读者称呼', dest='call', help='打分四档里怎么称呼读者；不给就取卡上「读者」｜前面那段')
    ap.add_argument('--本项目', dest='this_proj', help='边界角色用：本项目是什么（一句）')
    ap.add_argument('--别的项目', dest='other_proj', help='边界角色用：别的项目指哪些（一句）')
    ap.add_argument('--渲染', dest='render', action='store_true', help='pptx、html、pdf 另用 看成品.py 出页面图')
    ap.add_argument('--输出根', dest='out_root', default=str(OUT_ROOT), help='默认 /private/tmp/分角色验收')
    ap.add_argument('--自测', dest='selftest', action='store_true', help='跑内置正反例')
    a = ap.parse_args()
    if a.selftest:
        return self_test()
    if not a.task or not a.products:
        ap.error('需要 <任务文件> 和至少一个 <成品路径>（或用 --自测）')
    try:
        build(a.task, a.products, out_root=a.out_root, sources=a.sources,
              items=parse_items(a.items) if a.items else None, exam=a.exam, call=a.call,
              this_proj=a.this_proj, other_proj=a.other_proj, render=a.render)
    except Stop as e:
        print(('不出材料：' if e.code == 2 else '出错：') + str(e))
        return e.code
    return 0


if __name__ == '__main__':
    sys.exit(main())
