"""Q82：打印决策汇报第二节卡片顺序（存档框外 / 内分开），并统计每张卡出现次数，查重复或丢失。不带参数运行。"""
import os, re, collections
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
s = open(os.path.join(BASE, '决策汇报.html'), encoding='utf-8').read()
m = re.search(r'<section id="s2">(.*?)</section>', s, re.S)
sec = m.group(1)
arch = ''.join(x.group(0) for x in re.finditer(r'<details[^>]*>\s*<summary>[^<]*存档[^<]*</summary>.*?</details>', sec, re.S))
main = sec
for x in re.finditer(r'<details[^>]*>\s*<summary>[^<]*存档[^<]*</summary>.*?</details>', sec, re.S):
    main = main.replace(x.group(0), '')
print('正文卡片顺序', re.findall(r'<div class="dx"><div class="no">([^<]+)</div>', main))
print('存档框内卡片', re.findall(r'<div class="dx"><div class="no">([^<]+)</div>', arch))
print('正文卡片计数', collections.Counter(re.findall(r'<div class="dx"><div class="no">([^<]+)</div>', main)))
print('第二节 h3 数', len(re.findall(r'<h3', main)))
