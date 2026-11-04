#!/bin/bash
# 改 ~/.claude/skills/验收考试/SKILL.md 第 26 行一处：评审用什么模型不在技能里另写，改成照 做法.md「谁来派、用什么」表。
# 任务：~/claude/_底座/任务/用好Claude/2026-11-03_结构角色按金字塔原理_改用opus.md（思考页第 7 节 M1-4）
# 用法：bash 改技能一行.sh                  预览（只读，不改文件）
#       bash 改技能一行.sh --执行           核对通过才改：先备份到 ~/.claude/backups/结构角色改opus_<时间>/，再改，改完核
#       bash 改技能一行.sh --撤回 <备份夹>   现文件还是本脚本改后那份时，拷回备份
# 只供测试：环境变量 TARGET_SKILL、BACKUP_ROOT 可把目标文件和备份根换到别处。
exec /usr/bin/python3 -I - "$@" <<'PY'
import datetime, hashlib, os, shutil, sys
T = os.environ.get('TARGET_SKILL') or os.path.expanduser('~/.claude/skills/验收考试/SKILL.md')
BR = os.environ.get('BACKUP_ROOT') or os.path.expanduser('~/.claude/backups')
SHA_PRE = '7e601d2dccff61f87394aa37c37717f3a46899aeda45e0f8897ae96e9e0adba5'
OLD = '先派总验收人第一步（`subagent_type: 总验收人`，opus，思考强度 xhigh，不用 max），再同时派五个角色（`subagent_type: Explore`，sonnet）；'
NEW = '先派总验收人第一步，再同时派五个角色（各用什么派法、模型、思考强度，照 `做法.md`「谁来派、用什么」表，派的时候显式传参，这里不另写）；'
BK = '验收考试_SKILL.md'
def sha(b): return hashlib.sha256(b).hexdigest()
def die(m): print(m); sys.exit(1)
def rd(p): return open(p, 'rb').read()
def after(b):
    t = b.decode('utf-8')
    if t.count(OLD) != 1: die('改前那句在文件里出现 %d 次（应为 1 次），不改' % t.count(OLD))
    return t.replace(OLD, NEW).encode('utf-8')
a = sys.argv[1:]
cur = rd(T)
if a[:1] == ['--撤回']:
    if len(a) < 2: die('--撤回 后面要跟备份夹')
    old = rd(os.path.join(a[1], BK))
    if sha(old) != SHA_PRE: die('备份不是改前那份（%s），不撤回' % sha(old))
    if sha(cur) != sha(after(old)): die('现文件已不是本脚本改后的那份（之后又被改过），不撤回，请人工看')
    shutil.copy2(os.path.join(a[1], BK), T)
    if sha(rd(T)) != SHA_PRE: die('撤回后核对不一致')
    print('已撤回：%s 恢复成改前那份' % T); sys.exit(0)
if sha(cur) != SHA_PRE: die('目标文件和写脚本时不一样（现在是 %s），不改' % sha(cur))
new = after(cur)
print('目标：%s\n改前：%s\n改后：%s\n改后 sha256：%s' % (T, OLD, NEW, sha(new)))
if a[:1] != ['--执行']: print('预览完，没改任何文件；要改加 --执行'); sys.exit(0)
bk = os.path.join(BR, '结构角色改opus_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
os.makedirs(bk)
shutil.copy2(T, os.path.join(bk, BK))
if sha(rd(os.path.join(bk, BK))) != SHA_PRE: die('备份核对不一致，没改')
open(T, 'wb').write(new)
if sha(rd(T)) != sha(new): die('写入后核对不一致；撤回：bash 改技能一行.sh --撤回 %s' % bk)
print('已改。备份在 %s；撤回：bash 改技能一行.sh --撤回 %s' % (bk, bk))
PY
