# 统计一次 Claude Code 会话的 token 用量：主对话按「触发这一轮的消息」分，子任务按各自记录分。
# 用法：python3 _scripts/an_token用量.py <会话 jsonl 路径>   （子任务记录在同名文件夹 subagents/ 下）
# 用量＝每次调用的新输入＋写缓存＋读缓存＋输出；同一次调用的流式分片按 message id 去重取最大值。
import json, sys, os, glob, collections

def calls_of(path, classify=False):
    seen, cls = {}, '开始'
    for l in open(path, encoding='utf-8'):
        try: o = json.loads(l)
        except ValueError: continue
        t = o.get('type')
        if classify and t == 'user':
            c = o.get('message', {}).get('content')
            if isinstance(c, list):
                if any(b.get('type') == 'tool_result' for b in c): continue
                c = ' '.join(b.get('text', '') for b in c if b.get('type') == 'text')
            if not (c or '').strip(): continue
            if 'Stop hook feedback' in c: cls = '自动提交提醒'
            elif any(k in c for k in ('task-notification', 'agent-message', 'Another Claude session', 'SYSTEM NOTIFICATION')): cls = '子任务回报或通知'
            else: cls = '用户消息'
        if t != 'assistant': continue
        m = o.get('message', {}); u = m.get('usage')
        if not u: continue
        ctx = sum((u.get(k) or 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
        out = u.get('output_tokens') or 0
        old = seen.get(m.get('id'), (cls, 0, 0))
        seen[m.get('id')] = (old[0], max(old[1], ctx), max(old[2], out))
    return list(seen.values())

main = sys.argv[1]
mc = calls_of(main, classify=True)
by = collections.Counter(); n = collections.Counter()
for c, ctx, out in mc: by[c] += ctx + out; n[c] += 1
print('主对话', round(sum(by.values()) / 1e6, 1), 'M')
for k, v in by.most_common(): print(f'  {k}：调用 {n[k]}，{v/1e6:.1f}M')
for p in sorted(glob.glob(os.path.splitext(main)[0] + '/subagents/*.jsonl')):
    cs = calls_of(p)
    tot = sum(ctx + out for _, ctx, out in cs)
    excess = sum(max(0, ctx - 150_000) for _, ctx, _ in cs)
    print(f'{os.path.basename(p)[:24]}  调用 {len(cs)}，{tot/1e6:.1f}M，末次上下文 {cs[-1][1]/1e3:.0f}k，超出 15 万的部分 {excess/1e6:.1f}M')
