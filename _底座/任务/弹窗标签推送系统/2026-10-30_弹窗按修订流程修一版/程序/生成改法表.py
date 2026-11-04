# -*- coding: utf-8 -*-
import re, glob, subprocess, collections, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; BEN = HERE.parent
ORIG = Path.home()/'claude/_底座/任务/弹窗标签推送系统/2026-10-30_弹窗按六步重排'; DIG = ORIG/'里程碑1_底稿'
PROJ = Path.home()/'claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求'
FRAME = PROJ/'功能框架_脑图.md'; SRC = PROJ/'需求评审版源.html'; PRO = PROJ/'需求评审版_原型'
exec(open(HERE/'改法数据.py', encoding='utf-8').read())
def rd(p): return Path(p).read_text(encoding='utf-8').split('\n')
def txt(l): return re.sub(r'\|+','|',re.sub(r'<[^>]+>','|',l)).strip('| ')
def cardfile(k):
    pat = {'CA':'卡A_*.md','CB1':'卡B1_*.md','CB2':'卡B2_*.md','CB3':'卡B3_*.md','CB4':'卡B4_*.md','CB5':'卡B5_*.md','CC':'卡C_*.md'}[k]
    return Path(glob.glob(str(DIG/pat))[0])
def resolve(key):
    """返回 (路径, 行范围, 显示名, 分组)"""
    if key=='FR': return FRAME,(194,414),'功能框架_脑图.md','F'
    if key=='SH': return SRC,(362,466),'需求评审版源.html','P'
    if key in('CA','CB1','CB2','CB3','CB4','CB5','CC'):
        p=cardfile(key); return p,None,p.name.split('_')[0]+'.md' if False else p.name,'C'
    if key=='QD': return DIG/'功能清单.md',None,'功能清单.md','C'
    if key=='HZ': return ORIG/'控件回指表.md',None,'控件回指表.md','P'
    if key=='MB': return ORIG/'面包板.md',None,'面包板.md','P'
    if key=='PRG': return HERE/'一致性.py',None,'程序/一致性.py','P'
    if key.startswith('P:'):
        n=key[2:]; return PRO/(n+'.html'),None,'需求评审版_原型/'+n+'.html','P'
    raise KeyError(key)
CACHE={}
def lines(p):
    if p not in CACHE: CACHE[p]=rd(p)
    return CACHE[p]
def locate(key,rx,mode,maxn=4):
    if not (key.startswith('P:') or key=='SH'): maxn=1
    p,rng,name,grp=resolve(key)
    if key=='PRG': return name,grp,[1]
    ls=lines(p); out=[]
    for i,l in enumerate(ls,1):
        if rng and not(rng[0]<=i<=rng[1]): continue
        t = l if mode=='raw' and not key.startswith('P:') else txt(l)
        if mode=='raw' and key=='SH': t=l
        if re.search(rx,t): out.append(i)
        if len(out)>=maxn: break
    return name,grp,out
# 1. 改法表 + 位置集合
rows_out=[]; locs=collections.defaultdict(set); miss=[]
for f in FAM:
    short=re.split(r'[（；]',f['layer'])[0].strip()
    for j,(k,rx,mode,new,grp) in enumerate(f['rows'],1):
        name,g,ln=locate(k,rx,mode)
        if not ln: miss.append((f['id'],j,k,rx))
        for x in ln: locs[f['id']].add((name,x,g,'改法位置'))
        pos=name+(':'+'、'.join(map(str,ln)) if ln else '：(未定位)')
        rows_out.append((f'{f["id"]}.{j}',f['name'],f['groups'],short,pos,new,f['touch'],grp))
print('未定位',miss)
# 2. 追链下游
FIELDS={'M01':'A1-F02 A1-F03 A1-F04 B2-F01 B2-F06 B3-F02 B3-F03 B3-F04 C-F05 C-F06 C-F07','M02':'A1-F04 A1-F05 C-F07 B3-F04','M03':'A2-F17 B4-F04 C-F04','M04':'C-F05 C-F06 A1-F03 B1-F09','M05':'B4-F04 B4-F05','M06':'B5-F01 B1-F09 B1-F04 B5-F02','M07':'A2-F02 A2-F11 A2-F18','M08':'C-F08 C-F09','M09':'A2-F11 A2-F02 A1-F02','M10':'A2-F09 A2-F13','M11':'A2-F08 B1-F08 B5-F01','M12':'B4-F01 B4-F02 B4-F03','M13':'B2-F03 C-F07 B2-F06','M14':'B3-F01 B3-F05 A2-F17','M15':'A2-F02 B5-F03 B5-F06 A1-F02','M16':'A2-F05 B4-F04'}
chain=collections.defaultdict(set)
for fid,fl in FIELDS.items():
    for fld in fl.split():
        o=subprocess.run(['python3','-I',str(HERE/'追链.py'),'下游',fld],capture_output=True,text=True).stdout
        for l in o.split('\n'):
            m=re.match(r'\s+([GP]\d*-\d+)\s',l)
            if m: chain[fid].add(('原型控件 '+m.group(1),0,'P','追链下游 '+fld)); continue
            m=re.match(r'\s+板L(\d+)',l)
            if m: chain[fid].add(('面包板.md',int(m.group(1)),'P','追链下游 '+fld)); continue
            m=re.match(r'\s+框L(\d+)',l)
            if m: chain[fid].add(('功能框架_脑图.md',int(m.group(1)),'F','追链下游 '+fld)); continue
            m=re.match(r'\s+源L(\d+)',l)
            if m: chain[fid].add(('需求评审版源.html',int(m.group(1)),'P','追链下游 '+fld))
# 3. 同类筛查
LIM=r'弹出间隔|每人每天几次|每人两次至少隔多久|每人每天最多弹几个|每次最多弹几个|轮换池每次弹几个'
RS=['弹出时机不符','已到每人每天几次','弹出间隔未到','固定的已占满','轮换池没轮到','没有宣传图','在所有规则里暂停','被活动后台关闭','未开始或已结束','已达每次最多弹几个','已达每人每天最多弹几个','两次间隔未到']
def n_lim(t): return len(set(re.findall(LIM,t)))
SCR={
 'M01':(r'一句话：≥3 个限制名（弹出间隔／每人每天几次／每人两次至少隔多久／每人每天最多弹几个／每次最多弹几个／轮换池每次弹几个）同句，且含先后词（先、再、合计、截断、占满、让给、才弹），且不含「规则 7」「一次进入怎么判」', lambda t: n_lim(t)>=3 and re.search('先|再|合计|截断|占满|让给|才弹',t) and not re.search('规则 7|一次进入怎么判',t)),
 'M02':(r'`间隔[^。；，]{0,10}(不弹|没过|未到|内)|不受弹出间隔限制|间隔内`', lambda t: re.search(r'间隔[^。；，]{0,10}(不弹|没过|未到)|间隔内|不受弹出间隔限制',t)),
 'M03':(r'一行里≥3 个没弹原因词，或出现「没弹的原因／下次不会弹的原因」', lambda t: sum(r in t for r in RS)>=3 or re.search('没弹的(各写一个)?原因|下次不会弹的原因|不会弹的原因|没弹原因',t)),
 'M04':(r'`当天|一天|0 点`且`首次登录|第一次进大厅|每人每天几次|每人每天最多弹几个|生效期间`，不含「台湾时间／00:00／0 点」', lambda t: re.search('当天|一天|0 点|零点',t) and re.search('首次登录|第一次进大厅|每人每天几次|每人每天最多弹几个|生效期间',t) and not re.search('台湾时间|00:00',t)),
 'M05':(r'`下次进入|下一次进入`，不含「重新登录／从游戏返回」', lambda t: re.search('下次进入|下一次进入',t) and not re.search('重新登录|从游戏返回',t)),
 'M06':(r'`不能保存|保存不了|不让上架|不让保存|拦下|拦住|不许保存|不能上架|不可点`', lambda t: re.search('不能保存|保存不了|不让上架|不让保存|拦下|拦住|不许保存|不能上架|不可点',t)),
 'M07':(r'`不排号|排号|回原来的号|原来的优先级|恢复后|恢复回|上架中可编辑|草稿可编辑`', lambda t: re.search('不排号|排号|回原来的号|原来的优先级|恢复后|恢复回|上架中可编辑|草稿可编辑',t)),
 'M08':(r'`侧边框`且`保存`，不含「立即／所有规则」', lambda t: '侧边框' in t and '保存' in t and not re.search('立即|所有规则',t)),
 'M09':(r'`确认框`且`暂停|恢复|保存顺序|场景设置|改场景|结束`', lambda t: '确认框' in t and re.search('暂停|恢复|保存顺序|场景设置|改场景|结束',t)),
 'M11':(r'`发送对象和人数|预计人数|可能轮不到本规则的人数|弹不到本规则的人数`，不含「约／每天 00:00」', lambda t: re.search('发送对象和人数|预计人数|可能轮不到本规则的人数|弹不到本规则的人数',t) and not re.search('约|每天 00:00',t)),
 'M12':(r'`发送测试`且`下一次进入|下次进入|进入本场景|进入这条规则`', lambda t: '发送测试' in t and re.search('下一次进入|下次进入|进入本场景|进入这条规则',t)),
 'M13':(r'`固定 N 个|固定的先后|先弹固定的|固定的占满|固定的一个`，不含「不等于／不一定」', lambda t: re.search(r'固定 ?\d+ 个|固定的先后|先弹固定的|固定的占满|固定的一个',t) and not re.search('不等于|不一定',t)),
 'M14':(r'`本规则另设 ▾|没有可弹的|一个都弹不出|全部都弹不了|弹不出`', lambda t: re.search('本规则另设 ▾|没有可弹的|一个都弹不出|全部都弹不了|弹不出',t)),
 'M15':(r'`排在?(本场景)?最后|排最后|垫底`，不含「新加入的排最后／按进池先后」', lambda t: re.search('排在?(本场景)?最后|排最后|垫底',t) and not re.search('新加入的排最后|按进池先后',t)),
 'M16':(r'`按活动或礼包筛选`或独立「预览」按钮出现在哪些原型页', lambda t: '按活动或礼包筛选' in t or re.fullmatch(r'.*\|预览\|.*|预览',t)),
}
def scan_files(all_=False):
    fs=[(cardfile(k),'C',None) for k in('CA','CB1','CB2','CB3','CB4','CB5','CC')]+[(FRAME,'F',(194,414)),(SRC,'P',(362,466))]
    if all_: fs+=[(DIG/'功能清单.md','C',None),(ORIG/'框架随待拍板变的节点.md','C',None),(ORIG/'面包板.md','P',None),(ORIG/'控件回指表.md','P',None)]
    for n in ['10_规则编辑','10a_弹窗列表','10a2_按活动筛选后改弹窗设置','10a3_保存顺序确认','10b_破产时页签','10e_弹窗设置首次配置','10f_弹窗设置带出与在用','10g_弹窗设置改动确认','10h_发送测试确认','10m_按玩家预览','10n_场景设置','11_保存确认','13_游戏内数据','14_单条规则数据','19_玩家查询']:
        fs.append((PRO/(n+'.html'),'P',None))
    return fs
FILES=scan_files()
FILES_ALL=scan_files(True)
def shown(p): 
    s=str(p); 
    for base in(DIG,ORIG,PROJ): 
        if s.startswith(str(base)): return s[len(str(base))+1:]
    return p.name
screen={}
for fid,(cond_txt,fn) in SCR.items():
    hits=[]
    for p,g,rng in (FILES_ALL if fid in('M15','M16') else FILES):
        for i,l in enumerate(lines(p),1):
            if rng and not(rng[0]<=i<=rng[1]): continue
            t=l if p.suffix=='.md' else txt(l)
            if len(t)<4: continue
            if fn(t): hits.append((shown(p),i,g,t[:46]))
    if fid in('M13','M14','M16'): hits=[h for h in hits if h[0].endswith('.html') or h[0].startswith('功能框架')]
    screen[fid]=hits
# M10 程序：同一规则「共 N 个（轮换池 M 个）」跨页一致
RULES='银卡已首储|普卡已首储|新增玩家|回流|潜在流失|其余|节日回归'
seen=collections.defaultdict(dict)
for p,g,rng in FILES:
    if p.suffix!='.html': continue
    for i,l in enumerate(lines(p),1):
        t=txt(l)
        for m in re.finditer(r'('+RULES+r')\|?(?:编号 \d+\|?)?[^共]{0,90}?共 (\d+) 个(?:（(?:轮换池 (\d+) 个|(\d+) 个已结束)）)?',t):
            seen[m.group(1)][(shown(p),i)]=(m.group(2),m.group(3) or '-')
h10=[]
for r,d in seen.items():
    vals=set(d.values())
    if len(vals)>1:
        for (pg,i),v in d.items(): h10.append((pg,i,'P',f'{r} 共{v[0]}个 池{v[1]}（跨页不一致）'))
screen['M10']=(h10); SCR['M10']=('程序：同一规则名在各原型页「共 N 个（轮换池 M 个）」取值不全相同',None)
# 4. 影响项
def key_of(x): return (x[0],x[1])
impact=collections.defaultdict(dict)
for fid in [f['id'] for f in FAM]:
    for (n,ln,g,src) in locs[fid]: impact[fid][(n,ln)]=(g,'改法位置')
    for (n,ln,g,src) in chain[fid]: impact[fid].setdefault((n,ln),(g,src))
    for (n,ln,g,t) in screen.get(fid,[]): impact[fid].setdefault((n,ln),(g,'同类筛查：'+t))
famd={f['id']:f for f in FAM}
# 写文件
GN={'C':'卡和清单','F':'框架','P':'原型'}
L=['# 改法表（T2，10/31）','',
 '任务：`~/claude/_底座/任务/弹窗标签推送系统/2026-10-30_弹窗按修订流程修一版.md`。输入：去向草案摘要「改」38 组＋嫌疑总表；按 12 个修改家族改，另并出 4 个小家族（M13–M16），共 16 个改法家族。**只出改法，不改成品**；位置是 10/31 当前文件的行号（卡用章节，括号里是行号），X1/X2/X3 照此替换。',
 '依据 `思考页.md` 第二级审定第 6 条：①判定规则进源 html 业务规则和分析卡「规则」栏，框架只加缺的字段名或选项，不写说明句；②原型只改控件或文字错、缺的地方，不新开页；③G001 二选一已定（见 M15）；④回指表补 5 行，程序改匹配，不改成品；⑤新增研发待确认、问运营只进修订说明。','',
 '**文件分组**：卡和清单（原夹七张卡、功能清单、框架随待拍板变的节点）＝X1；框架（功能框架脑图弹窗段）＝X2；原型（原型弹窗页、源 html 弹窗段、面包板、控件回指表）＝X3。每行末尾标 C／F／P。','',
 '## 改法数','']
cnt=collections.Counter(r[7] for r in rows_out)
L.append(f'共 **{len(rows_out)} 条**改法（按文件位置计）：卡和清单 {cnt["C"]} 处、框架 {cnt["F"]} 处、原型（含源 html、面包板、回指表）{cnt["P"]} 处；归 {len(FAM)} 个家族。'); L.append('')
L.append('## 附录：新增文字（逐字，卡 A1／B4／B5／C 的规则栏与源 html 业务规则共用同一份）'); L.append('')
for k in sorted(N): 
    L.append(f'### {k}'); L.append('```'); L.append(N[k]); L.append('```'); L.append('')
L.append('## G001 二选一：定「改默认排位」（M15），不定「上架时提示」'); L.append('')
L+=['- **定的**：新上架（含复制出来的草稿上架）的规则默认排在本场景「发送对象为全部玩家」的规则之前、其他规则之后（N9）；没有这类规则时仍排最后。',
 '- **依据 1（运营不配错）**：草稿工作表2 覆盖新用戶、全部用戶、回流用戶三类（`嫌疑_a_真实配置试配.md:10`），每个场景实际都会有一条发送对象为全部玩家的兜底规则；新规则默认垫底，在「只用优先级最高的一条」的场景里一个人也接不到。',
 '- **依据 2（为什么不选「上架时提示」）**：草稿规则不排号（卡 A2 规则 2），列表里拖不了；运营只能先上架（此时位置是错的）再回列表拖、再点「保存顺序」，提示只是让他知道要走这三步，没有消除陷阱。',
 '- **依据 3（对标）**：Braze 同级时新建的优先（`分析/对标顶尖_弹窗与快显_1028.md` 优先级一行，卡 A2 对标已引）；本方案不让新规则排到所有规则之前，只先于兜底规则，所以卡 A2 要守的「新规则不抢具体规则的人」仍成立。',
 '- **不碰已定**：「新上架排最后」不在已定事项第 22、25、26 条，也不在原任务对齐卡「已定、要遵守的」6 条里（`grep 排最后 已定事项.md` 为 0）；它是原任务第二级 10/30 替 Dk 定的（卡 A2 对标「已替你定」），所以以新待拍板 N-01 附推荐交 Dk，上线前按推荐做。','']
L.append('## 改法表'); L.append('')
cur=None
for fid in [f['id'] for f in FAM]:
    f=famd[fid]
    L.append(f'### {fid} {f["name"]}（问题组 {f["groups"]}）'); L.append('')
    L.append(f'- **错层（第一个错处）**：{f["layer"]}'); L.append(f'- **原因**：{f["cause"]}　**证据**：{f["evid"]}'); L.append(f'- **碰不碰已定**：{f["touch"]}'); L.append(f'- **该补的检查点**：{f["check"]}'); L.append('')
    L.append('| 改法# | 家族 | 问题组号 | 错层 | 文件和位置 | 原文→新文 | 碰不碰已定 | 组 |'); L.append('|---|---|---|---|---|---|---|---|')
    for r in [x for x in rows_out if x[0].startswith(fid+'.')]:
        L.append('| '+' | '.join(c.replace('|','／') for c in r)+' |')
    L.append('')
(BEN/'改法表.md').write_text('\n'.join(L),encoding='utf-8')
# 影响项清单
I=['# 影响项清单（T2，10/31）','','由 `程序/生成改法表.py` 生成：①改法位置（改法表每行的定位）②`追链.py 下游`（各家族主字段，列控件、面包板行、框架行、源 html 行）③同类筛查新命中（`同类筛查.md`）。同一（文件，行）在同一家族只记一次。「问题组号」列写该家族涉及的全部组号。行号是 10/31 当前文件的行号；「原型控件 P2-01」类行是控件编号。','']
tot=0; byg=collections.Counter(); byf={}
I.append('| 问题组号 | 文件 | 行号或控件编号 | 改法# | 文件分组 | 来源 |'); I.append('|---|---|---|---|---|---|')
for fid in [f['id'] for f in FAM]:
    k=0
    for (n,ln),(g,src) in sorted(impact[fid].items(), key=lambda x:(x[1][0],x[0][0],x[0][1])):
        loc = ('控件 '+n.split(' ',1)[1]) if n.startswith('原型控件') else (str(ln) if ln else '-')
        fn = '原型控件（回指表）' if n.startswith('原型控件') else n
        I.append(f'| {famd[fid]["groups"]} | {fn} | {loc} | {fid} | {GN[g]} | {src} |'); k+=1; byg[(fid,g)]+=1
    byf[fid]=k; tot+=k
I.insert(2,f'**共 {tot} 处**（按家族计，同一处被两个家族命中算两次；按（文件，行）去重后 {len({(n,ln) for fid in impact for (n,ln) in impact[fid]})} 处）。分组：卡和清单 {sum(v for (a,g),v in byg.items() if g=="C")}、框架 {sum(v for (a,g),v in byg.items() if g=="F")}、原型 {sum(v for (a,g),v in byg.items() if g=="P")}。各家族：'+'、'.join(f'{a} {b} 处' for a,b in byf.items())+'。')
(BEN/'影响项清单.md').write_text('\n'.join(I),encoding='utf-8')
# 同类筛查
S=['# 同类筛查（T2，10/31）','','每个改法家族一条筛查条件，在弹窗全稿（原夹七张卡、功能清单、框架随待拍板变的节点、面包板、回指表、框架弹窗段 194–414、源 html 弹窗段 362–466、15 张原型弹窗页）跑；命中里不在改法位置的并入影响项清单。程序 `程序/生成改法表.py`（条件写在 SCR 字典里，可重跑）。命中是「候选」：命中行要加指针或核对，不是都要改文字。','',
 '| 家族 | 筛查条件 | 命中 | 其中已是改法位置 | **新命中（并入影响项）** |','|---|---|---|---|---|']
newtot=0; det=[]
for fid in [f['id'] for f in FAM]:
    h=screen.get(fid,[]); c=SCR.get(fid,('未设',None))[0]
    inloc={(n,ln) for (n,ln,g,s) in locs[fid]}
    new=[x for x in h if (x[0],x[1]) not in inloc]
    newtot+=len(new)
    S.append(f'| {fid} {famd[fid]["name"]} | {c} | {len(h)} | {len(h)-len(new)} | **{len(new)}** |')
    det.append((fid,new))
S+=['',f'**新命中合计 {newtot} 处**。','','## 新命中明细（每家族最多列 25 条，全部见影响项清单）','']
for fid,new in det:
    S.append(f'### {fid} {famd[fid]["name"]}（{len(new)} 处）')
    for x in new[:25]: S.append(f'- {x[0]}:{x[1]}　{x[3]}')
    S.append('')
(BEN/'同类筛查.md').write_text('\n'.join(S),encoding='utf-8')
import json
json.dump({'byf':byf,'new':{fid:len(n) for fid,n in det},'tot':tot,'newtot':newtot,'rows':len(rows_out),'cnt':dict(cnt),'dedup':len({(n,ln) for fid in impact for (n,ln) in impact[fid]})},open(HERE/'_汇总.json','w'),ensure_ascii=False)
print(len(rows_out),dict(cnt),tot,newtot,byf)

# ---- 修订记录底稿 + 新增待拍板
J=json.load(open(HERE/'_汇总.json'))
PROB={'M01':('G001/G002/G005/G006/G007：判定缺一张完整先后表，限制名散在各卡，研发各自拼顺序（d2-09、c-02、c-03、c-05、c-07、d2-08、d2-10）','浅'),
'M02':('G008/G012：弹出间隔内到底弹不弹两处冲突，例外项是否受自己的两次至少隔多久没写，活动设置里看不到间隔（d2-05、c-06、c-14、d1-07、d2-36）','画错'),
'M03':('G004/G011/G015：没弹原因缺固定不弹账号、多原因取哪个没写、列表预览数据页口径不同、人与次混写（d1-03、d2-23、d2-35、d1-28）','漏'),
'M04':('G003/G018/G028/G031：「当天首次登录」「活动开始后第一次进大厅」口径、一天从几点算、规则晚于活动上架没写（d2-07、d2-37、d1-31、d1-32）','浅'),
'M05':('G006/G018：预览「下次进入」没分重新登录与从游戏返回，草稿排位、事件类场景前提没写（d1-01、d1-17、d2-22）','漏'),
'M06':('G001/G012/G016/G017/G018/G019/G022/G032/G033：保存与上架没有校验表，空规则、群组失效、名单、数值范围、复制带入过期项、草稿改场景都没写（d2-11、d2-25、d2-26、d2-27、d2-28、d2-30、d2-14、d1-36、d1-37）','漏'),
'M07':('G009/G014/G026/G036：已结束不排号与指针按原优先级取下一条矛盾，未开始的操作、暂停与到期交叉、优先级分母没写（d2-06、d2-16、d2-15、d2-41）','画错'),
'M08':('G013/G023/G024/G027：侧边框保存立即写线上、与规则页保存取消的关系、在用的规则范围没写（d1-12、d1-15、d2-20、d2-21）','漏'),
'M09':('G001/G014/G029/G035：暂停恢复没有确认框、保存顺序与场景设置不写影响、还有几个可弹口径没写（d1-14、d1-16、d1-39、d2-38）','漏'),
'M10':('G006/G034/G037：同一规则「共几个（轮换池几个）」跨页不一致，样例日期不一致，玩家查询不标固定或轮换池（d1-40、d2-42、d1-33）','画错'),
'M11':('G004/G017/G030：列表人数、保存确认里交集人数的算法与刷新时机没写（d1-35、d2-29、d2-40）','漏'),
'M12':('G021：发送测试对事件类场景没定义，卡里有一行待研发确认，源 html 与原型仍写「下一次进入」（d2-24、d1-19）','漏'),
'M13':('G010/G019/G022：「固定」字面像一定弹、「两次至少隔多久」与「弹出间隔」读起来相同、右栏不写固定实际能弹几个（d1-22、d1-20、d1-10）','浅'),
'M14':('G006/G020/G025：「本规则另设 ▾」按钮与状态同名、列表不标一个都弹不出、轮流下配置处无就地提示（d1-21、d1-11、d1-06）','画错'),
'M15':('G001：新规则默认垫底，在只用优先级最高的一条的场景接不到人；轮流部分重叠、不顺延没提示（d1-04、d1-05、d1-09）','漏'),
'M16':('G038：回指表页列漏写 5 处，一致性程序按字面匹配造成 98 个误报（g-01）','漏')}
R=['# 修订记录底稿（T2，10/31）','','每个改法家族一行，七栏；第二级审后抄进任务文件「修订记录」表。行数 = 家族数（16）。影响项数来自 `影响项清单.md`（同一家族内按文件、行去重；跨家族重复的不合并）。检查点一律写成「必须交出某样东西，程序或验收官能判」，不直接改模板和规则，交「用好 Claude」统一处理。','',
 '| # | 问题（带组号） | 内容定性 | 错在哪层（L 层＋文件行号） | 原因 | 影响项 | 该补的检查点 |','|---|---|---|---|---|---|---|']
for i,f in enumerate(FAM,1):
    first=[r for r in rows_out if r[0].startswith(f['id']+'.')][0]
    short=re.split(r'[（；]',f['layer'])[0].strip()
    layer=f"{short}；第一个错处在 {first[4]}；{f['evid'].split('；')[0]}"
    chk=f['check'] if '判' in f['check'] else f['check']+'（程序或验收官能判）'
    R.append(f"| {i} {f['id']} | {PROB[f['id']][0]} | {PROB[f['id']][1]} | {layer} | {f['cause']} | 影响项清单家族 {f['id']}，共 {J['byf'][f['id']]} 处（其中同类筛查新命中 {J['new'][f['id']]}） | {chk} |")
(BEN/'修订记录底稿.md').write_text('\n'.join(R),encoding='utf-8')
print('底稿行',len(FAM))
