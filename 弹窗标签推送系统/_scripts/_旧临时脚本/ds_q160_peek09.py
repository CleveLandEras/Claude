"""设计卡 Q160 只读：打印 09 取数需求中表 6、表 7、表 16 所在工作表的文本（不读 数据/）。"""
import os, glob, re
from _textify import BASE, textify
for p in sorted(glob.glob(os.path.join(BASE, '支撑文件', '09*'))):
    s = textify(p)
    parts = re.split(r'(?=## 工作表 )', s)
    for part in parts:
        head = part.split('\n', 1)[0]
        if any(k in head for k in ('表6', '表7', '表16', '表 6', '表 7', '表 16', '说明', '通用')):
            print(part[:4000])
            print('-' * 40)
