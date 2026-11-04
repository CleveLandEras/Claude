"""只读：输出 03 配置单全文文本。"""
import glob, os
from _textify import BASE, textify
for p in glob.glob(os.path.join(BASE, '支撑文件', '03_*.xlsx')):
    print('=' * 60, p)
    print(textify(p)[:60000])
