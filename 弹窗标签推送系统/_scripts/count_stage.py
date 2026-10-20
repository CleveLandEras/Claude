"""数阶段产出正文的汉字数（去掉样式、脚本和标签），对照工作原则第二节的篇幅上限。不带参数运行。"""
import os, re, html, glob
from _textify import BASE
LIMIT = {}   # 10-08 Dk：不设字数上限，结构清楚是第一位的；本脚本只报字数作参考
for p in sorted(glob.glob(os.path.join(BASE, '阶段[0-9]*.html'))):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', '', s))
    n = len(re.findall(r'[一-鿿]', t))
    name = os.path.basename(p)
    lim = next((v for k, v in LIMIT.items() if name.startswith(k)), None)
    flag = '' if lim is None else ('（未超）' if n <= lim else f'（超出上限 {lim}，多 {n - lim}）')
    print(f'{name}：正文汉字 {n}，上限 {lim}{flag}')
