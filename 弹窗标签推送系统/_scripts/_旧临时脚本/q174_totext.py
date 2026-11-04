# 把盘点、04、05、07、06、08、C1、C2、汇报第五节转成纯文本，便于读（只读来源，写到 _versions/q174_txt/）
import re, os, html
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
OUT = BASE + '_versions/q174_txt/'
os.makedirs(OUT, exist_ok=True)

def h2t(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'</(p|div|h\d|li|tr|section|article|table|ul|ol|details|summary)>', '\n', s)
    s = re.sub(r'</t[dh]>', ' | ', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s

files = {
    'pandian': '来源资料/claude_弹窗标签推送_盘点.html',
    'huibao': '决策汇报.html',
}
for k, f in files.items():
    t = h2t(open(BASE + f, encoding='utf-8').read())
    open(OUT + k + '.txt', 'w', encoding='utf-8').write(t)
    print(k, len(t))
for k in ['支撑文件/04_弹窗功能缺口需求.md', '支撑文件/05_标签需求.md', '支撑文件/07_推送需求.md', '支撑文件/06_推送现状整理.md']:
    p = BASE + k
    print(k, os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else '')
