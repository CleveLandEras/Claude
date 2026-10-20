"""把目录下所有交付物 xlsx 转成文本输出，供读取。不带参数运行。"""
from _textify import deliverables, textify
for p in deliverables():
    if p.endswith('.xlsx'):
        print('=' * 60 + '\n' + p)
        print(textify(p))
