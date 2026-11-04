# 用法：python3 pl_评审版原型页截图.py <页名> [页名…]   如 10_规则编辑
# 截 需求评审版_原型/<页>.html（1280 宽、2 倍像素），拼成整页，缩到宽 2112，写到 需求评审版_图/<页>.jpg；不产生中间文件。
import os, sys, subprocess, tempfile
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = R + '/评审版_定稿改_1027/推送系统后台集成需求/'
TOOL = R + '/_scripts/pl_网页截图测量.swift'
for pid in sys.argv[1:]:
    with tempfile.TemporaryDirectory() as t:
        o = t + '/' + pid + '.jpg'
        subprocess.run(['swift', TOOL, D + '需求评审版_原型/' + pid + '.html', o, '1280'], capture_output=True)
        tiles = []; i = 0
        while os.path.exists('%s/%s_%d.jpg' % (t, pid, i)):
            tiles.append(Image.open('%s/%s_%d.jpg' % (t, pid, i)).convert('RGB')); i += 1
        if not tiles: print('失败', pid); continue
        im = Image.new('RGB', (tiles[0].width, sum(x.height for x in tiles)), 'white'); y = 0
        for x in tiles: im.paste(x, (0, y)); y += x.height
        h = round(im.height * 2112 / im.width)
        im = im.resize((2112, h), Image.LANCZOS)
        from PIL import ImageChops
        bb = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
        if bb: im = im.crop((0, 0, min(2112, bb[2] + 20), min(h, bb[3] + 20)))
        im.save(D + '需求评审版_图/' + pid + '.jpg', quality=92)
        print(pid, 2112, h)
