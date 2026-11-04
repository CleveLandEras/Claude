# 需求评审版拼装：把 评审版_定稿改_1027/推送系统后台集成需求/需求评审版源.html 里引用的 需求评审版_图/*.jpg 转成 base64 内嵌，
# 生成单文件 评审版_定稿改_1027/推送系统后台集成需求/3_原型_需求评审版.html（样式已在源文件内嵌）。
# 用法：python3 _scripts/an_需求评审版拼装.py
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re, base64, os

BASE = _ROOT + '/评审版_定稿改_1027/推送系统后台集成需求/'
src = open(BASE + '需求评审版源.html', encoding='utf-8').read()


def inline(m):
    p = BASE + m.group(1)
    with open(p, 'rb') as f:
        return 'src="data:image/jpeg;base64,' + base64.b64encode(f.read()).decode() + '"'


out, n = re.subn(r'src="(需求评审版_图/[^"]+\.jpg)"', inline, src)
open(BASE + '3_原型_需求评审版.html', 'w', encoding='utf-8').write(out)
print('内嵌图片', n, '张；成品', round(os.path.getsize(BASE + '3_原型_需求评审版.html') / 1e6, 2), 'MB')
