#!/usr/bin/env python3
"""功能框架大纲 → 能点开、收起的脑图：一份 Markdown（贴进 XMind、markmap 等脑图工具），一份网页（markmap 渲染）。

用法：python3 _scripts/pl_功能框架脑图.py [大纲路径] [打开时展开几层]
默认读：评审版_定稿改_1027/推送系统后台集成需求/功能框架_大纲.md（格式见 pl_功能框架导图.py），展开 4 层
写：同目录「xxx_脑图.md」「xxx_脑图.html」，xxx 是大纲文件名去掉「_大纲」；网页标题取大纲的中心主题
每个节点「短名：说明〔标签〕」拆成：节点「短名【标签】」，说明按「；」拆成它的子节点，原来的子节点排在后面；「做法」「为什么」「参照」「代价」「好处」「依据」「理由」开头的说明，和挂着它们的节点，整句当节点名，不拆。
脚本最后核对：大纲里每段文字都出现在 Markdown 里，否则报错退出。
网页从 jsDelivr 加载 markmap，打开时要联网。
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('daotu', HERE / 'pl_功能框架导图.py')
daotu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daotu)

SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else daotu.SRC
EXPAND = int(sys.argv[2]) if len(sys.argv) > 2 else 4
STEM = SRC.stem.replace('_大纲', '')
if STEM.endswith('_脑图'):
    sys.exit(f'{SRC.name} 本身就是脑图代码，直接改它即可，不用再生成；要另出网页，传入一份「_大纲.md」')
OUT_MD = SRC.with_name(f'{STEM}_脑图.md')
OUT_HTML = SRC.with_name(f'{STEM}_脑图.html')
MARKMAP = 'https://cdn.jsdelivr.net/npm/markmap-autoloader@0.18.10'


KEEP_WHOLE = ('做法', '为什么', '参照', '代价', '好处', '依据', '理由')  # 这几类说明整句当节点名，不拆


def whole(node):
    """「为什么」「参照」本身，以及挂着它们的设计点，整句当节点名。"""
    return daotu.short(node.text) in KEEP_WHOLE or any(daotu.short(c.text) in KEEP_WHOLE for c in node.children)


def label(node):
    if daotu.short(node.text) in KEEP_WHOLE:
        return node.text
    name = node.text if whole(node) else daotu.short(node.text)
    tags = ''.join(f'【{t}】' for t in node.tags)
    return f'{name} {tags}' if tags else name


def details(node):
    if '：' not in node.text or whole(node):
        return []
    return [p.strip() for p in node.text.split('：', 1)[1].split('；') if p.strip()]


def lines(node, depth):
    pad = '  ' * depth
    out = [f'{pad}- {label(node)}']
    out += [f'{pad}  - {d}' for d in details(node)]
    for c in node.children:
        out += lines(c, depth + 1)
    return out


def build(root):
    md = [f'# {root.text}', '']
    for b in root.children:
        md += lines(b, 0)
    return '\n'.join(md) + '\n'


def check(root, md):
    missing = []
    for n in daotu.walk(root):
        name = daotu.short(n.text)
        if name.count('（') != name.count('）'):
            sys.exit(f'节点名被括号里的冒号切断：{name}（把括号里的「：」改掉）')
        parts = [label(n).split(' 【')[0]] + details(n) + [f'【{t}】' for t in n.tags]
        missing += [p for p in parts if p not in md]
    if missing:
        sys.exit('Markdown 里缺：' + '；'.join(missing[:10]))


def page(md, title):
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
html,body{{margin:0;height:100%;background:#fff;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
.markmap{{position:fixed;inset:0}}
.markmap>svg{{width:100%;height:100%}}
.hint{{position:fixed;left:16px;bottom:12px;font-size:12px;color:#868b92;background:rgba(255,255,255,.9);padding:4px 8px;border-radius:4px}}
</style>
<script src="{MARKMAP}"></script>
</head><body>
<div class="markmap"><script type="text/template">
---
markmap:
  initialExpandLevel: {EXPAND}
  maxWidth: 360
  colorFreezeLevel: 2
---
{md}</script></div>
<div class="hint">点节点前的圆点展开、收起；滚轮缩放，拖动平移</div>
</body></html>
'''


def main():
    root = daotu.parse(SRC)
    md = build(root)
    check(root, md)
    OUT_MD.write_text(md, encoding='utf-8')
    OUT_HTML.write_text(page(md, root.text), encoding='utf-8')
    print(f'已写出 {OUT_MD}\n已写出 {OUT_HTML}\n核对通过：大纲每段文字都在 Markdown 里；共 {len(md.splitlines())} 行')


if __name__ == '__main__':
    main()
