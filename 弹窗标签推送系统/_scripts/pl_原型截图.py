# 原型分页截图（设计概要配图用）
# 用法：python3 pl_原型截图.py <输出目录> [页 id …]      页 id 如 p3、p15、overview；不给则截全部页
# 做法：3_原型.html 每页另存一份到输出目录，只显示该页的原型窗口（隐藏目录、页眉、其他页、右侧说明栏），
#   去掉说明标注（紫色编号 .co、紫框 .hl、「新增／改」标记 .mk、蓝色虚线框 .nc）、取消淡化；
#   用 pl_网页截图测量.swift 以 1280 宽排版、2 倍像素截整页，存为 <输出目录>/<页>.jpg；
#   同时量出各「块」的位置（CSS 像素），存为 <输出目录>/<页>.json，供设计概要按块裁图（坐标×2＝截图像素）。
# 块：.win（整个窗口）、.sec（表单分块）、.top、.steps、.mini、table、.card、.f（表单行）以及带 id 的元素，
#   每个记 文字前 40 字，方便按文字找。
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, re, json, subprocess
BASE = _ROOT + '/'
SRC = BASE + '推送系统后台集成需求/3_原型.html'
TOOL = BASE + '_scripts/pl_网页截图测量.swift'
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
html = open(SRC, encoding='utf-8').read()
# 10/19 起原型样式另存为同目录 原型样式.css；页面另存到别处截图时，把样式内联回页面，否则另存的页面没有样式
if '<link rel="stylesheet" href="原型样式.css">' in html:
    html = html.replace('<link rel="stylesheet" href="原型样式.css">', '<style>' + open(os.path.join(os.path.dirname(SRC), '原型样式.css'), encoding='utf-8').read() + '</style>', 1)
ids = sys.argv[2:] or re.findall(r'<section id="(p\d+)">', html)

CSS = '''
.page > *:not(section#%s) { display:none !important }
section#%s > .crumb, section#%s > h2, section#%s .notes, section#%s details, section#%s > .more { display:none !important }
section#%s .row { display:block !important }
.co, .mk, .mkc { display:none !important }
.ref-link { display:none !important }
.hl { outline:none !important }
td.nc, th.nc { border-left-color:transparent !important; border-right-color:transparent !important }
div.nc, span.nc { outline:none !important }
.focus * { opacity:1 !important }
body { background:#fff !important }
'''

MEASURE = r'''
(function(){
  var sec=document.querySelector('section#%s'); var o=[];
  var sels=['.win','.win-in','.fig','.side','.menu','.main','.top','.steps','.sec','.mini','table','.card','.f','.bar','.dlg','.pop','.dd','.ddf','[id]'];
  sels.forEach(function(sel){
    sec.querySelectorAll(sel).forEach(function(e,i){
      var r=e.getBoundingClientRect(); if(r.width<4||r.height<4) return;
      o.push({sel:sel,i:i,x:Math.round(r.left),y:Math.round(r.top+scrollY),w:Math.round(r.width),h:Math.round(r.height),
              t:(e.innerText||'').replace(/\s+/g,' ').slice(0,40)});
    });
  });
  return JSON.stringify(o);
})()
'''

procs = []
for pid in ids:
    css = CSS % ((pid,) * 7)
    page = html.replace('</head>', '<style>%s</style></head>' % css, 1)
    hp = os.path.join(out, pid + '.html')
    open(hp, 'w', encoding='utf-8').write(page)
    jp = os.path.join(out, pid + '.measure.js')
    open(jp, 'w', encoding='utf-8').write(MEASURE % pid)
    procs.append((pid, subprocess.Popen(['swift', TOOL, hp, os.path.join(out, pid + '.jpg'), '1280', jp], stdout=subprocess.PIPE, text=True)))
    if len(procs) >= 6:
        for p_, p in procs:
            res = p.communicate()[0].strip().splitlines()
            open(os.path.join(out, p_ + '.json'), 'w', encoding='utf-8').write(res[0] if res else 'null')
        procs = []
for p_, p in procs:
    res = p.communicate()[0].strip().splitlines()
    open(os.path.join(out, p_ + '.json'), 'w', encoding='utf-8').write(res[0] if res else 'null')
# 截图工具分段输出 <页>_0.jpg、<页>_1.jpg……，拼成整页（需要 pillow）
try:
    from PIL import Image
    for pid in ids:
        tiles = []; i = 0
        while os.path.exists(os.path.join(out, '%s_%d.jpg' % (pid, i))):
            tiles.append(Image.open(os.path.join(out, '%s_%d.jpg' % (pid, i))).convert('RGB')); i += 1
        if tiles:
            full = Image.new('RGB', (tiles[0].width, sum(t.height for t in tiles)), (255, 255, 255)); y = 0
            for t in tiles:
                full.paste(t, (0, y)); y += t.height
            full.save(os.path.join(out, pid + '.jpg'), quality=92)
            for j in range(i):
                os.remove(os.path.join(out, '%s_%d.jpg' % (pid, j)))
except ImportError:
    print('未装 pillow：分段截图未拼接')
print('shot', len(ids), 'pages →', out)
