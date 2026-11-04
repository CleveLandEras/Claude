# Q181：只读，独立重数 A37 的计数（不依赖生成脚本的变量），并检索「→有」等写法
import re, os, time
B = '/Users/decheng.huang/claude/弹窗标签推送系统/'
txt = open(B + '分析/A37_能力线现有能力.md', encoding='utf-8').read()
lines = txt.split('\n')
# 动作行：以 | D\d+ | 开头；能力项行：以 | K\d+ | 开头
D = [l for l in lines if re.match(r'\| D\d+ \|', l)]
K = [l for l in lines if re.match(r'\| K\d+ \|', l)]
# 能力项清单里的行（排除末尾「为什么是一件事」表也以 | K 开头）
sec2 = txt.split('## 第二部分')[1].split('**名字里仍带并列词')[0]
K2 = [l for l in sec2.split('\n') if re.match(r'\| K\d+ \|', l)]
sec1 = txt.split('## 第一部分')[1].split('### 28 格网格')[0]
D1 = [l for l in sec1.split('\n') if re.match(r'\| D\d+ \|', l)]
print('动作行', len(D1), '唯一编号', len({l.split('|')[1].strip() for l in D1}))
blk = {}
cur = None
for l in sec1.split('\n'):
    if l.startswith('### '):
        cur = l[4:].strip()
    if re.match(r'\| D\d+ \|', l):
        blk[cur] = blk.get(cur, 0) + 1
print('动作分块', blk)
cols = [[c.strip() for c in l.strip().strip('|').split('|')] for l in D1]
print('列数', {len(c) for c in cols})
print('未覆盖(以「未覆盖」开头)', sum(1 for c in cols if c[-1].startswith('未覆盖')), '其中明确排除', sum(1 for c in cols if c[-1].startswith('未覆盖') and '明确排除' in c[-1]))
print('类型=推断', sum(1 for c in cols if c[8] == '推断'), [c[0] for c in cols if c[8] == '推断'])
print('步', {s: sum(1 for c in cols if c[9] == str(s)) for s in (1, 2, 3)})
print('能力项行', len(K2), '唯一编号', len({l.split('|')[1].strip() for l in K2}))
kb = {}
cur = None
for l in sec2.split('\n'):
    if l.startswith('### '):
        cur = l[4:].strip()
    if re.match(r'\| K\d+ \|', l):
        kb[cur] = kb.get(cur, 0) + 1
print('能力项分块', kb)
nums = sorted(int(l.split('|')[1].strip()[1:]) for l in K2)
print('K 编号连续', nums == list(range(1, len(nums) + 1)), nums[0], nums[-1])
head = txt.split('## 第三部分')[0]
print('「→有」', head.count('→有'), '「→没有」', head.count('→没有'))
print('「，且」「，也能」「以及」(只数第二部分能力项文本列)', sum(1 for l in K2 if re.search(r'，且|，也能|以及', l.split('|')[2])))
print('已列全', '已列全' in txt.split('## 方法')[0], '扫描未完成' in txt.split('## 方法')[0])
print('第三部分仍为空', txt.split('## 第三部分')[1].strip().endswith('（待 Q175）'))
st = os.stat(B + '_versions/A37_step1_draft.md')
print('step1 存档 mtime', time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime)))
print('草稿并列出处的动作', len([c for c in cols if '盘点附录四' in c[7]]))
