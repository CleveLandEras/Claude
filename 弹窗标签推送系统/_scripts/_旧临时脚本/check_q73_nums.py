"""Q73 数字核对：在 _versions/ 里找最近的环节2 备份，与现行版比对「完全消失的数字」。不带参数运行。"""
import os, re, glob, collections
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统'
cands = sorted(glob.glob(os.path.join(BASE, '_versions', '**', '*环节2*'), recursive=True), key=os.path.getmtime)
for c in cands[-5:]:
    print('备份', os.path.relpath(c, BASE), os.path.getsize(c))
if not cands:
    print('无备份'); raise SystemExit
b = open(cands[-1], encoding='utf-8').read()
s = open(os.path.join(BASE, '环节2_问题诊断.html'), encoding='utf-8').read()
nums = lambda x: collections.Counter(re.findall(r'\d[\d,]*(?:\.\d+)?', re.sub(r'<[^>]+>', ' ', x)))
nb, ns = nums(b), nums(s)
print('备份中有、现行版完全没有的数字', sorted(k for k in nb if ns[k] == 0))
print('现行版有、备份没有的数字', sorted(k for k in ns if nb[k] == 0))
