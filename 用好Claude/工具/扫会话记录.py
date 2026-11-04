# 用法：python3 扫会话记录.py <输出目录>  —— 扫 ~/.claude/projects 下全部会话记录，输出 sessions.json（每个会话的轮次、工具调用、token）和 user_msgs.jsonl（Dk 的消息语料），每周算三个数用。
import os, json, sys, glob, collections, statistics
base='/Users/decheng.huang/.claude/projects'
dirs=['-Users-decheng-huang-claude','-Users-decheng-huang-claude---------','-Users-decheng-huang-claude--claude-worktrees-image-info-sufficiency-aef28d','-Users-decheng-huang-Documents-dy','-Users-decheng-huang-Documents-----']
out_dir=sys.argv[1]
SKIP=('<command-name>','<local-command','<system-reminder>','<task-notification','<side-sessions','<ci-monitor','<command-message>','<bash-input>','<bash-stdout>','<user-prompt-submit-hook>')
sessions=[]
um=open(os.path.join(out_dir,'user_msgs.jsonl'),'w')
for d in dirs:
    p=os.path.join(base,d)
    if not os.path.isdir(p): continue
    for f in sorted(glob.glob(os.path.join(p,'*.jsonl'))):
        sid=os.path.basename(f)[:-6]
        rec=dict(dir=d,sid=sid,size=os.path.getsize(f),first=None,last=None,user=0,asst=0,tool=0,side=0,interrupts=0,out_tok=0,in_tok=0,cache_read=0,cache_create=0,first_user='',model={},cwd='',slug='')
        models=collections.Counter(); seen=set()
        with open(f,'rb') as fh:
            for line in fh:
                try: o=json.loads(line)
                except Exception: continue
                t=o.get('type'); ts=o.get('timestamp')
                if ts:
                    if rec['first'] is None or ts<rec['first']: rec['first']=ts
                    if rec['last'] is None or ts>rec['last']: rec['last']=ts
                if o.get('isSidechain'): rec['side']+=1
                if not rec['cwd'] and o.get('cwd'): rec['cwd']=o['cwd']
                if not rec['slug'] and o.get('slug'): rec['slug']=o['slug']
                if t=='user':
                    m=o.get('message',{}) or {}; c=m.get('content')
                    text=None
                    if isinstance(c,str): text=c
                    elif isinstance(c,list):
                        parts=[b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text']
                        if parts: text='\n'.join(parts)
                    if text is None or o.get('isMeta'): continue
                    st=text.lstrip()
                    if st.startswith(SKIP): continue
                    if st.startswith('[Request interrupted'): rec['interrupts']+=1; continue
                    rec['user']+=1
                    if not rec['first_user']: rec['first_user']=text[:300]
                    um.write(json.dumps(dict(dir=d,sid=sid,ts=ts,side=bool(o.get('isSidechain')),len=len(text),text=text[:4000]),ensure_ascii=False)+'\n')
                elif t=='assistant':
                    m=o.get('message',{}) or {}
                    mid=m.get('id')
                    if mid and mid in seen: 
                        c=m.get('content')
                        if isinstance(c,list): rec['tool']+=sum(1 for b in c if isinstance(b,dict) and b.get('type')=='tool_use')
                        continue
                    if mid: seen.add(mid)
                    rec['asst']+=1
                    if m.get('model'): models[m['model']]+=1
                    u=m.get('usage') or {}
                    rec['out_tok']+=u.get('output_tokens',0) or 0
                    rec['in_tok']+=u.get('input_tokens',0) or 0
                    rec['cache_read']+=u.get('cache_read_input_tokens',0) or 0
                    rec['cache_create']+=u.get('cache_creation_input_tokens',0) or 0
                    c=m.get('content')
                    if isinstance(c,list): rec['tool']+=sum(1 for b in c if isinstance(b,dict) and b.get('type')=='tool_use')
        rec['model']=dict(models)
        sessions.append(rec)
um.close()
json.dump(sessions,open(os.path.join(out_dir,'sessions.json'),'w'),ensure_ascii=False)
real=[s for s in sessions if s['user']>0]
print('jsonl files',len(sessions),'| with user msgs',len(real),'| pure sidechain/empty',len(sessions)-len(real))
bym=collections.Counter(); umon=collections.Counter(); tokmon=collections.Counter(); intr=collections.Counter()
for s in real:
    mth=(s['first'] or '')[:7]; bym[mth]+=1; umon[mth]+=s['user']; tokmon[mth]+=s['out_tok']; intr[mth]+=s['interrupts']
for k in sorted(bym): print(f"{k}: sessions {bym[k]:5d} | user_turns {umon[k]:6d} | interrupts {intr[k]:4d} | out_tok {tokmon[k]:,}")
print('total user turns',sum(s['user'] for s in real),'| assistant msgs',sum(s['asst'] for s in sessions),'| tool_uses',sum(s['tool'] for s in sessions),'| interrupts',sum(s['interrupts'] for s in sessions))
print('tokens: out',f"{sum(s['out_tok'] for s in sessions):,}",'cache_read',f"{sum(s['cache_read'] for s in sessions):,}",'cache_create',f"{sum(s['cache_create'] for s in sessions):,}",'in',f"{sum(s['in_tok'] for s in sessions):,}")
ut=sorted(s['user'] for s in real)
print('user turns/session: median',statistics.median(ut),'p90',ut[int(len(ut)*0.9)],'max',max(ut))
mc=collections.Counter()
for s in sessions:
    for k,v in s['model'].items(): mc[k]+=v
print('models:',dict(mc))
main=[s for s in real if not s['side']]
print('sessions with no sidechain lines (likely main):',len(main))
big=sorted(real,key=lambda s:-s['user'])[:25]
print('\nTop 25 sessions by user turns:')
for s in big: print(f"{s['user']:4d} turns | {s['interrupts']:3d} intr | {s['asst']:5d} asst | {s['tool']:5d} tools | {s['size']/1048576:6.1f}MB | {(s['first'] or '')[:10]}→{(s['last'] or '')[5:10]} | {s['dir'][-12:]} | {s['first_user'][:70].replace(chr(10),' ')}")
