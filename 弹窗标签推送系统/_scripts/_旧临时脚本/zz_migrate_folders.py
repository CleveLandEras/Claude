"""一次性：按存放规则整理文件夹，并改写 HTML / Markdown 中指向被移动文件的相对链接。由主对话 Claude 运行。"""
import os, re, shutil
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVES = {
    '支撑文件': ['00_推进记录.md', '01_取数需求_人群规模.xlsx', '02_弹窗分人群定制方案.html', '03_弹窗配置单.xlsx',
               '04_弹窗功能缺口需求.md', '05_标签需求.md', '06_推送现状整理.md', '07_推送需求.md',
               '08_弹窗效果评估方案.md', '09_取数需求_上线前基线.xlsx', 'C1_卡点解锁优先级.md', 'C2_新标签脚本草稿.md'],
    '过程记录': ['推进计划.md', '任务清单.md', '审查记录.md', '迭代记录.md', '监督记录.md'],
    '规则与交接': ['工作原则.md', '项目交接_对话要点.md', '目标脑图.md'],
    '来源资料': ['claude_弹窗标签推送_盘点.html', '02_弹窗分人群定制方案_Cowork原版.html'],
    '归档': ['晨间验收.html', '汇报_成果与待你回答.html', '迭代内容回顾.html', '00_推进记录_本机补充.md'],
}
# 旧位置（相对 BASE）→ 新位置
newloc = {}
for folder, names in MOVES.items():
    for n in names:
        if os.path.exists(os.path.join(BASE, n)):
            newloc[n] = f'{folder}/{n}'
# 不移动但会被链接的文件
for n in os.listdir(BASE):
    p = os.path.join(BASE, n)
    if os.path.isfile(p) and n not in newloc:
        newloc.setdefault(n, n)
for sub in ['分析', '数据']:
    for n in os.listdir(os.path.join(BASE, sub)):
        newloc.setdefault(f'{sub}/{n}', f'{sub}/{n}')

# 1. 移动
for folder, names in MOVES.items():
    os.makedirs(os.path.join(BASE, folder), exist_ok=True)
    for n in names:
        src = os.path.join(BASE, n)
        if os.path.exists(src):
            shutil.move(src, os.path.join(BASE, folder, n))
            print('移动', n, '→', folder)

# 2. 改写链接：对每个 html / md 文件，把指向旧位置的相对链接改成从它的新位置出发的相对路径
def fix(path):
    rel_dir = os.path.relpath(os.path.dirname(path), BASE)
    rel_dir = '' if rel_dir == '.' else rel_dir
    s = open(path, encoding='utf-8').read()
    orig = s
    def repl_target(target):
        t = target.split('#')[0]
        anchor = target[len(t):]
        if not t or t.startswith(('http', 'mailto', '#', 'data:')):
            return None
        # 链接写法都相对于文件原先所在位置；原先所有文件都在 BASE 或 分析/、数据/ 下
        norm = os.path.normpath(os.path.join(ORIG_DIR.get(path, rel_dir), t)).replace('\\', '/')
        norm = norm[2:] if norm.startswith('./') else norm
        if norm in newloc:
            new_abs = newloc[norm]
            new_rel = os.path.relpath(os.path.join(BASE, new_abs), os.path.join(BASE, rel_dir) if rel_dir else BASE)
            return new_rel + anchor
        return None
    def sub_attr(m):
        r = repl_target(m.group(2))
        return m.group(1) + (r if r else m.group(2)) + m.group(3)
    s = re.sub(r'((?:href|src)=")([^"]+)(")', sub_attr, s)
    if path.endswith('.md'):
        s = re.sub(r'(\]\()([^)\s]+)(\))', sub_attr, s)
    if s != orig:
        open(path, 'w', encoding='utf-8').write(s)
        print('改写链接', os.path.relpath(path, BASE))

# 记录每个文件移动前所在目录（相对 BASE），用于解析旧链接
ORIG_DIR = {}
for folder, names in MOVES.items():
    for n in names:
        ORIG_DIR[os.path.join(BASE, folder, n)] = ''
for root, dirs, files in os.walk(BASE):
    if any(x in root for x in ['_scripts', '_versions', '/数据']):
        continue
    for f in files:
        if f.endswith(('.html', '.md')):
            p = os.path.join(root, f)
            ORIG_DIR.setdefault(p, os.path.relpath(root, BASE) if root != BASE else '')
            fix(p)
