"""产出状态：按文件内容计算，不手写。供 status.py、record_pass.py 共用。
过审时记录文件内容（转成纯文本后）的 SHA-256；读状态时现算，一致才算「已过审」，否则「待复核」。
用纯文本而不是 HTML 原文计算，只改样式不改文字时状态不变。"""
import os, re, json, glob, hashlib, datetime
from _textify import BASE, textify

STORE = os.path.join(BASE, '_versions', 'pass_hashes.json')
SUBMIT = '弹窗标签推送方案_V1.html'

def tracked():
    """阶段产出加呈交版。"""
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BASE, '阶段[0-9]_*.html')))
    if os.path.exists(os.path.join(BASE, SUBMIT)):
        files.append(SUBMIT)
    return files

def digest(name):
    return hashlib.sha256(textify(os.path.join(BASE, name)).encode('utf-8')).hexdigest()

def load():
    return json.load(open(STORE, encoding='utf-8')) if os.path.exists(STORE) else {}

def save(d):
    json.dump(d, open(STORE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def status(name, store=None):
    store = load() if store is None else store
    rec = store.get(name)
    if not rec:
        return '未过审', ''
    if rec['sha256'] == digest(name):
        return '已过审', rec['at']
    return '待复核', f"上次过审 {rec['at']}，之后有改动"

def files_in(text):
    """从审查记录一节里找出涉及的文件：「阶段 N」「呈交版」。"""
    names = set()
    nums = []
    for grp in re.findall(r'阶段\s*([1-8](?:\s*[、,，和及与]\s*[1-8](?![0-9]))*)', text):  # 含「阶段 1、5、6、7」并列写法
        nums += re.findall(r'[1-8]', grp)
    for n in nums:
        hit = glob.glob(os.path.join(BASE, f'阶段{n}_*.html'))
        if hit:
            names.add(os.path.basename(hit[0]))
    if '呈交版' in text:
        names.add(SUBMIT)
    return sorted(names)

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
