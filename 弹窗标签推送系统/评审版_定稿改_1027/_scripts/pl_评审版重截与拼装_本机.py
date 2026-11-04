# 本机重截评审版的全部截图并拼装成品：按 需求评审版源.html 里引用的图，逐张用 Chrome 无头截对应原型页的 .shot 元素（2 倍像素），
# 压到质量 80，再调用 an_需求评审版拼装.py 生成单文件成品。用法：python3 _scripts/pl_评审版重截与拼装_本机.py [页名 ...]（不给页名就截全部）
# 只能在装了 Chrome 的 Mac 上跑；本机没有 Noto 字体，截出来是苹方。
import os, re, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, '推送系统后台集成需求')
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OPT = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', '--virtual-time-budget=3000',
       '--blink-settings=preferredColorScheme=1']  # 系统是深色模式时也按浅色截


def shot(src, out):
    html = open(src, encoding='utf-8').read()
    probe = ('<script>window.addEventListener("load",()=>{const r=document.querySelector(".shot").getBoundingClientRect();'
             'document.body.setAttribute("data-bb",[r.left+scrollX,r.top+scrollY,r.width,r.height].map(Math.round).join(","))})</script>')
    tmp = os.path.join(os.path.dirname(src), '_tmp_probe.html')
    open(tmp, 'w', encoding='utf-8').write(html.replace('</body>', probe + '</body>') if '</body>' in html else html + probe)
    try:
        dom = subprocess.run([CH] + OPT + ['--window-size=1280,900', '--dump-dom', 'file://' + tmp], capture_output=True, text=True).stdout
        m = re.search(r'data-bb="(\d+),(\d+),(\d+),(\d+)"', dom)
        if not m:
            sys.exit('没找到 .shot：' + src)
        x, y, w, h = map(int, m.groups())
        png = out[:-4] + '.png'
        # 浏览器可视区比窗口矮约 87px，窗口放高 200 再按 .shot 裁，否则高图底部会被截掉
        subprocess.run([CH] + OPT + [f'--window-size={x + w},{y + h + 200}', '--force-device-scale-factor=2', f'--screenshot={png}', 'file://' + tmp], capture_output=True)
    finally:
        os.remove(tmp)
    # sips 偏移为 0 时会居中裁，所以至少从第 1 像素起
    subprocess.run(['sips', '-c', str(h * 2), str(w * 2), '--cropOffset', str(max(y * 2, 1)), str(max(x * 2, 1)), png, '--out', png], capture_output=True)
    subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', png, '--out', out], capture_output=True)
    os.remove(png)
    print('✔', os.path.basename(out), f'{w}×{h}')


src = open(os.path.join(BASE, '需求评审版源.html'), encoding='utf-8').read()
names = sys.argv[1:] or list(dict.fromkeys(re.findall(r'需求评审版_图/([^"/]+)\.jpg', src)))
for n in names:
    shot(os.path.join(BASE, '需求评审版_原型', n + '.html'), os.path.join(BASE, '需求评审版_图', n + '.jpg'))
subprocess.run([sys.executable, os.path.join(ROOT, '_scripts', 'an_需求评审版拼装.py')])
