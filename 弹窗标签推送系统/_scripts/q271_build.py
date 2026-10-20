import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import io
base = _ROOT + '/'
src = io.open(base + '阶段7_方案验证.html', encoding='utf-8').read()
head = src.split('<div class="wrap">')[0]
head = head.replace('<title>方案验证</title>', '<title>结论汇总</title>')
body = io.open(base + '_versions/stage8_body.html', encoding='utf-8').read()
out = head + '<div class="wrap">\n' + body + '\n</div></body></html>\n'
io.open(base + '阶段8_结论汇总.html', 'w', encoding='utf-8').write(out)
print('ok', len(out))
