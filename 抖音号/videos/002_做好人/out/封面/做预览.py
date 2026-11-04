# 封面自查图：中间裁切预览、手机上的缩略图（1 倍 = 点，3 倍 = 手机真实像素）。
# 用法：python3 previews.py <竖封面.png> <横封面.png> <输出目录> [邻居封面.png]
import sys, os
from PIL import Image, ImageDraw, ImageFont

V, H, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
NEI = sys.argv[4] if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
def font(n): return ImageFont.truetype(FONT, n)
BG = (236, 237, 240)
INK = (30, 32, 38)

v = Image.open(V).convert('RGB')   # 1080×1440
h = Image.open(H).convert('RGB')   # 1440×1080

def frame(img, boxes):
    """原图上画 80% 安全框（虚线白）和各裁切框（彩色实线）"""
    im = img.copy()
    d = ImageDraw.Draw(im)
    w, hh = im.size
    x0, y0, x1, y1 = w * 0.1, hh * 0.1, w * 0.9, hh * 0.9
    for i in range(0, int(x1 - x0), 24):
        d.line([(x0 + i, y0), (x0 + i + 12, y0)], fill=(255, 255, 255), width=3)
        d.line([(x0 + i, y1), (x0 + i + 12, y1)], fill=(255, 255, 255), width=3)
    for i in range(0, int(y1 - y0), 24):
        d.line([(x0, y0 + i), (x0, y0 + i + 12)], fill=(255, 255, 255), width=3)
        d.line([(x1, y0 + i), (x1, y0 + i + 12)], fill=(255, 255, 255), width=3)
    for (bx, by, bw, bh, col) in boxes:
        d.rectangle([bx, by, bx + bw - 1, by + bh - 1], outline=col, width=6)
    return im

def center_crop(img, rw, rh):
    w, hh = img.size
    if w / hh > rw / rh:   # 太宽：裁左右
        cw = round(hh * rw / rh); x = (w - cw) // 2
        return img.crop((x, 0, x + cw, hh)), (x, 0, cw, hh)
    ch = round(w * rh / rw); y = (hh - ch) // 2
    return img.crop((0, y, w, y + ch)), (0, y, w, ch)

def sheet(img, name, crops, title):
    """左：原图（白虚线 = 中间 80%，彩框 = 裁切范围）；右：各裁切结果，统一高 900"""
    boxes = []
    outs = []
    COLS = [(255, 196, 0), (0, 200, 255)]
    for i, (rw, rh, label) in enumerate(crops):
        c, b = center_crop(img, rw, rh)
        boxes.append((*b, COLS[i]))
        outs.append((c, label, COLS[i]))
    H0 = 900
    items = [(frame(img, boxes), '原图：白虚线 = 中间 80%，彩框 = 中间裁切', (255, 255, 255))] + outs
    scaled = [(im.resize((round(im.width * H0 / im.height), H0), Image.LANCZOS), lab, col) for im, lab, col in items]
    W = sum(s.width for s, _, _ in scaled) + 60 * (len(scaled) + 1)
    out = Image.new('RGB', (W, H0 + 200), BG)
    d = ImageDraw.Draw(out)
    d.text((60, 30), title, fill=INK, font=font(40))
    x = 60
    for s, lab, col in scaled:
        out.paste(s, (x, 120))
        d.rectangle([x, 120 + H0 + 14, x + 40, 120 + H0 + 30], fill=col if col != (255, 255, 255) else (120, 120, 130))
        d.text((x + 52, 120 + H0 + 8), lab, fill=INK, font=font(28))
        x += s.width + 60
    out.save(os.path.join(OUT, name))

sheet(v, '裁切预览_竖版.png', [(9, 16, '中间裁成 9:16（810×1440）'), (1, 1, '中间裁成 1:1（1080×1080）')],
      '竖版 3:4 封面：从中间裁成 9:16、1:1 以后')
sheet(h, '裁切预览_横版.png', [(1, 1, '中间裁成 1:1（1080×1080）'), (9, 16, '中间裁成 9:16（608×1080）')],
      '横版 4:3 封面：从中间裁成 1:1、9:16 以后')

# —— 手机缩略图：按 390×844 点的手机画；k = 1（点）或 3（手机真实像素）——
def heart_count(d, x, y, k, txt):
    # 平台在格子左下盖的赞数：一个小心形 + 数字（心形自己画，字体里没有 ♡）
    r = 3 * k
    cx, cy = x + r * 2, y + 7 * k
    d.ellipse([cx - 2 * r, cy - r * 1.6, cx, cy + r * 0.4], fill=(255, 255, 255))
    d.ellipse([cx, cy - r * 1.6, cx + 2 * r, cy + r * 0.4], fill=(255, 255, 255))
    d.polygon([(cx - 2 * r + 0.3 * k, cy - 0.1 * r), (cx + 2 * r - 0.3 * k, cy - 0.1 * r), (cx, cy + 2.2 * r)], fill=(255, 255, 255))
    d.text((x + 6 * r, y), txt, fill=(255, 255, 255), font=font(int(11 * k)), stroke_width=max(1, k // 2), stroke_fill=(0, 0, 0))

def phone(k):
    W, Hh = 390 * k, 844 * k
    ph = Image.new('RGB', (W, Hh), (22, 24, 30))
    d = ImageDraw.Draw(ph)
    return ph, d

def grid_page(k):
    """个人主页作品九宫格：3 列，间隔 1 点，格子 3:4"""
    ph, d = phone(k)
    d.text((16 * k, 52 * k), '屏幕那头', fill=(255, 255, 255), font=font(int(20 * k)))
    d.text((16 * k, 82 * k), '作品 2    喜欢    收藏', fill=(200, 200, 210), font=font(int(14 * k)))
    top = 112 * k
    gap = 1 * k
    cw = (390 * k - 2 * gap) // 3
    ch = round(cw * 4 / 3)
    nei = Image.open(NEI).convert('RGB') if NEI else None
    cells = [v, nei]
    for i in range(9):
        x = (i % 3) * (cw + gap); y = top + (i // 3) * (ch + gap)
        if i < len(cells) and cells[i] is not None:
            ph.paste(cells[i].resize((cw, ch), Image.LANCZOS), (x, y))
            heart_count(d, x + 6 * k, y + ch - 20 * k, k, '12' if i == 0 else '1,024')
        else:
            d.rectangle([x, y, x + cw - 1, y + ch - 1], fill=(48, 50, 58))
    d.text((8 * k, 820 * k), f'示意：主页作品格 {cw // k}×{ch // k} 点（3 列）；左下赞数是平台盖的', fill=(150, 150, 160), font=font(int(10 * k)))
    return ph

def search_page(k):
    """搜索结果：上面一张横卡片（综合页，整宽），下面两列竖卡片（视频页）"""
    ph, d = phone(k)
    d.rounded_rectangle([12 * k, 50 * k, 378 * k, 84 * k], radius=17 * k, fill=(48, 50, 58))
    d.text((26 * k, 58 * k), '被坑多了 变狠', fill=(220, 220, 228), font=font(int(15 * k)))
    # 横卡片：整宽 366 点，4:3
    x0, y0 = 12 * k, 98 * k
    cw = 366 * k; ch = round(cw * 3 / 4)
    ph.paste(h.resize((cw, ch), Image.LANCZOS), (x0, y0))
    d.text((x0, y0 + ch + 8 * k), 'Vibe知识大赏｜被坑多了，人会变狠吗？我替你跑了300代', fill=(240, 240, 245), font=font(int(13 * k)))
    # 两列竖卡片：每张 177 点宽，3:4
    y1 = y0 + ch + 40 * k
    cw2 = 177 * k; ch2 = round(cw2 * 4 / 3)
    for i in range(2):
        x = 12 * k + i * (cw2 + 12 * k)
        if i == 0:
            ph.paste(v.resize((cw2, ch2), Image.LANCZOS), (x, y1))
        else:
            d.rectangle([x, y1, x + cw2 - 1, y1 + ch2 - 1], fill=(48, 50, 58))
    d.text((8 * k, 820 * k), '示意：横卡片 366×275 点、两列竖卡片 177×236 点（估算，未真机核对）', fill=(150, 150, 160), font=font(int(10 * k)))
    return ph

def small_cards(k):
    """更小的地方：搜索列表左边的小图（横 120 点宽）、网页搜索卡片（横 240 点宽）"""
    W = 390 * k
    im = Image.new('RGB', (W, 300 * k), (22, 24, 30))
    d = ImageDraw.Draw(im)
    a = h.resize((120 * k, 90 * k), Image.LANCZOS)
    im.paste(a, (12 * k, 16 * k))
    d.text((142 * k, 20 * k), 'Vibe知识大赏｜被坑多了，', fill=(240, 240, 245), font=font(int(13 * k)))
    d.text((142 * k, 40 * k), '人会变狠吗？我替你跑了300代', fill=(240, 240, 245), font=font(int(13 * k)))
    d.text((142 * k, 70 * k), '屏幕那头 · 12 赞', fill=(150, 150, 160), font=font(int(11 * k)))
    b = h.resize((240 * k, 180 * k), Image.LANCZOS)
    im.paste(b, (12 * k, 116 * k))
    d.text((8 * k, 300 * k - 16 * k), '示意：列表小图 120×90 点；网页卡片 240×180 像素', fill=(150, 150, 160), font=font(int(10 * k)))
    return im

for k, tag in [(1, '1倍'), (3, '3倍')]:
    g = grid_page(k); s = search_page(k); c = small_cards(k)
    pad = 20 * k
    out = Image.new('RGB', (g.width + s.width + c.width + pad * 4, max(g.height, s.height) + pad * 2 + 30 * k), BG)
    d = ImageDraw.Draw(out)
    d.text((pad, pad // 2), f'按手机实际大小缩（390 点宽，{tag}）：左 主页九宫格｜中 搜索结果｜右 更小的列表图', fill=INK, font=font(int(14 * k)))
    out.paste(g, (pad, pad + 30 * k)); out.paste(s, (pad * 2 + g.width, pad + 30 * k)); out.paste(c, (pad * 3 + g.width + s.width, pad + 30 * k))
    out.save(os.path.join(OUT, f'缩略图预览_{tag}.png'))
print('ok')
