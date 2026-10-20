#!/usr/bin/env python3
# 原型分页截图（读者视角，评审用）：每页一张（或几段）1440 宽的截图，保留右侧说明栏、紫色编号、紫框、蓝色标记，折叠区保持收起。
# 用法：python3 _scripts/pl_原型截图_读者视角.py [输出目录] [页 id …]
#   默认输出到 分析/标准判卷/推送后台_原型评审_1017/页图/ ；页 id 不给则截全部：head（页首说明）、overview、p1…p19、p10a–c、p12a–d、p16a、tasks、appx
# 与 pl_原型截图.py 的区别：那份是给设计概要配图（去掉标注、1280 宽）；这份是读者看到的样子（带标注、1440 宽）。
# 做法：每页另存一份 HTML 到临时文件夹，只显示该页；用 pl_网页分段截图.swift（编译成可执行文件再跑，6 路并行）截图。
#   页高超过约 1700 像素时平均切成几段（切口选在文字行之间），存为 <页>_1.jpg、<页>_2.jpg……；一段就存 <页>.jpg。
#   图片宽度核对 1440（不是就用 sips 缩放）；写一份 目录.txt（每个文件的像素高）。
#   需要 macOS 的 swiftc、sips；不需要 pillow。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re, subprocess, tempfile, glob
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = _ROOT + '/'
SRC = BASE + '推送系统后台集成需求/3_原型.html'
SWIFT = BASE + '_scripts/pl_网页分段截图.swift'
OUT = BASE + '分析/标准判卷/推送后台_原型评审_1017/页图/'
args = sys.argv[1:]
if args and (args[0].startswith('/') or args[0].startswith('.')):
    OUT = args[0]
    args = args[1:]
if not OUT.endswith('/'):
    OUT += '/'
os.makedirs(OUT, exist_ok=True)

WIDTH, MAXSEG = 1440, 1500

html = open(SRC, encoding='utf-8').read()
# 10/19 起原型样式另存为同目录 原型样式.css；页面另存到别处截图时，把样式内联回页面，否则另存的页面没有样式
if '<link rel="stylesheet" href="原型样式.css">' in html:
    html = html.replace('<link rel="stylesheet" href="原型样式.css">', '<style>' + open(os.path.join(os.path.dirname(SRC), '原型样式.css'), encoding='utf-8').read() + '</style>', 1)
html = re.sub(r'(<details\b[^>]*?)\sopen(?=[\s>=])', r'\1', html)        # 折叠区一律收起
base_tag = '<base href="%s">' % (Path(SRC).parent.as_uri() + '/')
html = html.replace('<head>', '<head>' + base_tag, 1)

all_ids = ['head', 'overview'] + re.findall(r'<section id="(p\d+[a-d]?)"', html) + ['tasks', 'appx']
ids = args or all_ids


# 每页前面紧挨着的分部标题、分组条、任务入口条，读者翻到这一页时也看得到，一起留着
BANNERS = {}
_pend = []
for m in re.finditer(r'<(div class="(?:part|grp)" id="([^"]+)"|nav class="span-row[^"]*"|section id="([^"]+)")', html):
    if m.group(2):
        _pend.append('#' + m.group(2))
    elif m.group(3):
        BANNERS[m.group(3)] = _pend
        _pend = []
    else:
        _pend.append('nav.span-row')


def css_for(pid):
    if pid == 'head':
        hide = '.page > section, .page > .part, .page > .grp, .page > nav.span-row'
    else:
        keep = ''.join(':not(%s)' % b for b in ['section#' + pid] + BANNERS.get(pid, []))
        hide = '.page > *' + keep
    return '<style>%s{display:none !important}</style>' % hide


tmp = tempfile.mkdtemp(prefix='pl_reader_')
binary = os.path.join(tmp, 'seg')
r = subprocess.run(['swiftc', '-O', SWIFT, '-o', binary], capture_output=True, text=True)
if r.returncode != 0:
    print('编译失败', r.stderr[:500])
    sys.exit(1)


def shoot(pid):
    page = html.replace('</head>', css_for(pid) + '</head>', 1)
    hp = os.path.join(tmp, pid + '.html')
    open(hp, 'w', encoding='utf-8').write(page)
    for old in glob.glob(OUT + pid + '.jpg') + glob.glob(OUT + pid + '_*.jpg'):
        os.remove(old)                       # 上次的分段，段数可能不同
    p = subprocess.run([binary, hp, OUT + pid, str(WIDTH), str(MAXSEG)], capture_output=True, text=True, timeout=240)
    files = sorted(glob.glob(OUT + pid + '.jpg') + glob.glob(OUT + pid + '_*.jpg'),
                   key=lambda f: int(re.search(r'_(\d+)\.jpg$', f).group(1)) if re.search(r'_(\d+)\.jpg$', f) else 0)
    return pid, files, (p.stdout + p.stderr).strip()


def size_of(f):
    o = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', f], capture_output=True, text=True).stdout
    w = int(re.search(r'pixelWidth: (\d+)', o).group(1))
    h = int(re.search(r'pixelHeight: (\d+)', o).group(1))
    return w, h


with ThreadPoolExecutor(6) as ex:
    for pid, files, msg in ex.map(shoot, ids):
        if not files:
            print('失败', pid, msg[:200])
            continue
        for f in files:
            w, h = size_of(f)
            if w != WIDTH:
                subprocess.run(['sips', '--resampleWidth', str(WIDTH), f], capture_output=True)
# 目录：按文件夹里现有的图列（只截几页时也不丢别的页）
rows = []
for f in glob.glob(OUT + '*.jpg'):
    w, h = size_of(f)
    pid = re.sub(r'(_\d+)?\.jpg$', '', os.path.basename(f))
    seg = re.search(r'_(\d+)\.jpg$', f)
    rows.append((all_ids.index(pid) if pid in all_ids else 999, int(seg.group(1)) if seg else 0, os.path.basename(f), w, h))
rows.sort()
lines = ['页图：每页一张（或几段）1440 宽截图，保留右侧说明栏与全部标注，折叠区收起（折叠区里的文字看 页文本/）。',
         '超过约 1700 像素高的页平均切成几段（切口选在文字行之间），文件名 <页 id>_1.jpg、_2.jpg……，从上到下接着看；一段的页文件名就是 <页 id>.jpg。', '',
         '文件｜宽×高（像素）']
for _, _, n, w, h in rows:
    lines.append('%s｜%d×%d' % (n, w, h))
lines.append('')
lines.append('合计 %d 个文件' % len(rows))
open(OUT + '目录.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('页', len(ids), '文件', len(rows), '→', OUT)
