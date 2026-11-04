"""头像和封面（深色）。

    python make_brand.py avatar
    python make_brand.py cover 001 "宁可更疼，" "也不想等。" "等待" 不想等   # 最后是要划红线的词

封面出两张：cover_横.png（4:3，横屏视频用）和 cover_竖.png（3:4，主页格子用）。
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from notebook import SS, font, wavy  # noqa: E402
from dark import BG, DIM, INK, RED  # noqa: E402


def dark_bg(w, h, seed=1):
    """黑底，中间稍亮一点，加颗粒。"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h * 0.45) / (h * 0.75)) ** 2)
    vign = np.clip(1.0 + 0.35 * (0.6 - r), 0.75, 1.15)
    grain = rng.normal(0, 1.6, (h, w)).astype(np.float32)
    base = np.array(BG, np.float32)[None, None, :] * vign[..., None] + grain[..., None]
    return Image.fromarray(np.uint8(np.clip(base, 0, 255)))


def underline(d, xa, xb, y, width, seed, amp=7, period=46):
    pts = wavy(xa, xb, y, amp=amp, period=period, seed=seed)
    d.line(pts, fill=RED, width=width, joint='curve')


def avatar(path):
    # 字体按超采样倍数建好，这里直接在 2160 画布上画，最后缩到 1080
    S = 2160
    img = dark_bg(S, S, seed=3)
    d = ImageDraw.Draw(img)
    f = font('black', 430)  # 实际像素 = 430 * SS；头像会被裁成圆，字要留边
    d.text((S / 2, S / 2 - 40), '听', font=f, fill=INK, anchor='mm')
    w = f.getlength('听')
    underline(d, S / 2 - w * 0.34, S / 2 + w * 0.34, S / 2 + w * 0.5, 22, seed=7, amp=16, period=150)
    img.resize((1080, 1080), Image.LANCZOS).save(path)


def cover(path, size, no, line1, line2, topic, marks=()):
    W, H = size
    w, h = W * SS, H * SS
    img = dark_bg(w, h, seed=5)
    d = ImageDraw.Draw(img)
    d.text((70 * SS, 90 * SS), f'人间旁听生 · 笔记 {no}', font=font('sans', 30), fill=DIM, anchor='ls')
    d.text(((W - 70) * SS, 90 * SS), 'AI 生成', font=font('sans', 30), fill=DIM, anchor='rs')
    size1 = 124 if W > H else 112
    f = font('black', size1)
    y1, y2 = H * 0.42, H * 0.42 + size1 * 1.45
    d.text((w / 2, y1 * SS), line1, font=f, fill=INK, anchor='ms')
    d.text((w / 2, y2 * SS), line2, font=f, fill=INK, anchor='ms')
    x0 = w / 2 - f.getlength(line2) / 2
    for word in marks:
        i = line2.find(word)
        if i >= 0:
            xa = x0 + f.getlength(line2[:i])
            underline(d, xa + 6, xa + f.getlength(word) - 6, (y2 + size1 * 0.3) * SS, 10, seed=sum(map(ord, word)))
    d.text((w / 2, (y2 + size1 * 1.6) * SS), topic, font=font('bold', 52), fill=DIM, anchor='ms')
    img.resize((W, H), Image.LANCZOS).save(path)


if __name__ == '__main__':
    if sys.argv[1] == 'avatar':
        avatar(os.path.join(HERE, 'avatar.png'))
    elif sys.argv[1] == 'cover':
        no, l1, l2, topic, *marks = sys.argv[2:]
        out = os.path.join(HERE, '..', 'videos', [x for x in os.listdir(os.path.join(HERE, '..', 'videos'))
                                                  if x.startswith(no)][0], 'out')
        for name, size in (('cover_横.png', (1440, 1080)), ('cover_竖.png', (1080, 1440))):
            cover(os.path.join(out, name), size, no, l1, l2, topic, marks)
            print(os.path.abspath(os.path.join(out, name)))
