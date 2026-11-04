import re
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self, words):
        super().__init__()
        self.stack = []  # (tag, info)
        self.words = words
        self.hits = []
        self.cur_summary = None
        self.in_summary = False
        self.sec = ''
        self.in_h = False
        self.htext = ''
    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'img', 'meta', 'link', 'input', 'hr', 'col'):
            return
        info = ''
        if tag == 'details':
            info = 'DETAILS'
        self.stack.append([tag, info])
        if tag == 'summary':
            self.in_summary = True
            self.stext = ''
        if tag in ('h1', 'h2', 'h3'):
            self.in_h = True; self.htext = ''
    def handle_endtag(self, tag):
        if tag == 'summary':
            self.in_summary = False
            for s in reversed(self.stack):
                if s[0] == 'details':
                    s[1] = 'DETAILS:' + self.stext[:40]
                    break
        if tag in ('h1', 'h2', 'h3') and self.in_h:
            self.in_h = False; self.sec = self.htext[:40]
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, d):
        if self.in_summary: self.stext += d
        if self.in_h: self.htext += d
        for w in self.words:
            for m in re.finditer(re.escape(w), d):
                dets = [s[1] for s in self.stack if s[0] == 'details']
                self.hits.append((w, self.sec, dets, d[max(0, m.start()-40):m.end()+30].replace('\n', ' ')))

for f in ['决策汇报.html', '环节3_方案.html']:
    t = open(base + f, encoding='utf-8').read()
    p = P(['只有 2 项', '推送条', '按 A29 重核'])
    p.feed(t)
    print('=====', f)
    for h in p.hits:
        print(h[0], '| sec:', h[1], '| details:', h[2])
        print('      ', h[3])
