# 用法：python3 -I 打包单文件.py 报告.html 输出.html
# 把外链样式和图片嵌进 HTML，得到一个可单独打开、转发的文件
import base64
import os
import re
import sys

src, out = sys.argv[1], sys.argv[2]
base = os.path.dirname(os.path.abspath(src))
h = open(src, encoding="utf-8").read()


def css(m):
    p = os.path.join(base, m.group(1))
    return "<style>\n" + open(p, encoding="utf-8").read() + "\n</style>"


h = re.sub(r'<link rel="stylesheet" href="([^"]+)">', css, h)


def img(m):
    p = os.path.join(base, m.group(1))
    data = base64.b64encode(open(p, "rb").read()).decode()
    return 'data-p="' + m.group(1) + '" src="data:image/jpeg;base64,' + data + '"'


h = re.sub(r'src="(素材/[^"]+\.jpg)"', img, h)
# 原路径留在 data-p 里，附录 B 画面清单按它分组
open(out, "w", encoding="utf-8").write(h)
print(f"ok {os.path.getsize(out) / 1e6:.1f} MB -> {out}")
