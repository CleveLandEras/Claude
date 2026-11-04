#!/usr/bin/env python3
"""把交付物渲染成读者看到的样子：逐屏截图＋全文文字。备评审材料.py 用它把成品渲染成页面图给评审看，评审不看源码。

用法：python3 看成品.py <文件> <输出目录>
  .html → Chrome 无界面截图，按一屏 1280×1400 切片
  .pptx → PowerPoint 导出逐页图（借弹窗项目已授权的渲染脚本），另存每页文字
  .pdf  → 逐页图
输出：<输出目录>/页_NN.png|jpg 和 <输出目录>/全文.txt；最后打印图片清单。
"""
import os
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PPTX_RENDER = "/Users/decheng.huang/claude/弹窗标签推送系统/_scripts/pl_pptx渲染.sh"
PDF_TO_IMG = "/Users/decheng.huang/claude/弹窗标签推送系统/_scripts/pl_pdf转图.swift"
WIDTH, SCREEN = 1280, 1400


def html(src, out):
    from PIL import Image
    full = os.path.join(out, "_整页.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={os.path.join(out, '_chrome')}", f"--screenshot={full}",
                    f"--window-size={WIDTH},20000", "file://" + os.path.abspath(src)],
                   capture_output=True, timeout=120)
    img = Image.open(full).convert("RGB")
    # 去掉底部大片空白：从下往上找第一行非纯色。
    px = img.load()
    bg = px[WIDTH - 1, img.height - 1]
    bottom = img.height
    for y in range(img.height - 1, 0, -8):
        if any(px[x, y] != bg for x in range(0, WIDTH, 16)):
            bottom = min(img.height, y + 40)
            break
    pages = []
    for i, top in enumerate(range(0, bottom, SCREEN), 1):
        p = os.path.join(out, f"页_{i:02d}.png")
        img.crop((0, top, WIDTH, min(top + SCREEN, bottom))).save(p)
        pages.append(p)
    os.remove(full)
    try:
        from html.parser import HTMLParser

        class T(HTMLParser):
            def __init__(self):
                super().__init__(); self.buf = []; self.skip = 0
            def handle_starttag(self, tag, a):
                if tag in ("script", "style"): self.skip += 1
            def handle_endtag(self, tag):
                if tag in ("script", "style"): self.skip -= 1
                if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "section"): self.buf.append("\n")
            def handle_data(self, d):
                if not self.skip and d.strip(): self.buf.append(d.strip() + " ")
        t = T(); t.feed(open(src, encoding="utf-8", errors="ignore").read())
        open(os.path.join(out, "全文.txt"), "w").write("".join(t.buf))
    except Exception:
        pass
    return pages


def pptx(src, out):
    try:
        from pptx import Presentation
        lines = []
        for i, s in enumerate(Presentation(src).slides, 1):
            lines.append(f"\n===== 第 {i} 页 =====")
            for sh in s.shapes:
                if sh.has_text_frame and sh.text_frame.text.strip():
                    lines.append(sh.text_frame.text.strip())
                if getattr(sh, "has_table", False) and sh.has_table:
                    for r in sh.table.rows:
                        lines.append(" | ".join(c.text for c in r.cells))
        open(os.path.join(out, "全文.txt"), "w").write("\n".join(lines))
    except Exception as e:
        print("文字提取失败：", e)
    img_dir = os.path.join(out, "图")
    subprocess.run(["zsh", PPTX_RENDER, os.path.abspath(src), img_dir], capture_output=True, timeout=900)
    return sorted(os.path.join(img_dir, f) for f in os.listdir(img_dir)) if os.path.isdir(img_dir) else []


def pdf(src, out):
    subprocess.run(["swift", PDF_TO_IMG, os.path.abspath(src), out], capture_output=True, timeout=600)
    return sorted(os.path.join(out, f) for f in os.listdir(out) if f.lower().endswith((".jpg", ".png")))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    ext = os.path.splitext(src)[1].lower()
    pages = {".html": html, ".htm": html, ".pptx": pptx, ".pdf": pdf}.get(ext, lambda s, o: [])(src, out)
    if not pages:
        print("没有生成图片（不支持的格式或渲染失败）；文字类文件直接读原文。")
    for p in pages:
        print(p)
    if os.path.exists(os.path.join(out, "全文.txt")):
        print(os.path.join(out, "全文.txt"))


if __name__ == "__main__":
    main()
