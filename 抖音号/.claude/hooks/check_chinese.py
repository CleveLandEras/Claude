"""Stop hook：最后一条回复如果主要是英文，就拦下来，让 Claude 用中文重写。

读 hook 输入里的 transcript_path，找最后一条助手文字消息，按“汉字 / (汉字 + 英文字母)”算占比。
已经是被这个 hook 拦回来的那一轮（stop_hook_active）就放行，免得来回打转。
"""
import json
import re
import sys

data = json.load(sys.stdin)
if data.get('stop_hook_active'):
    sys.exit(0)

text = ''
try:
    with open(data['transcript_path'], encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get('type') != 'assistant':
                continue
            parts = [c.get('text', '') for c in (d.get('message') or {}).get('content') or []
                     if isinstance(c, dict) and c.get('type') == 'text']
            if any(p.strip() for p in parts):
                text = '\n'.join(parts)
except (KeyError, OSError):
    sys.exit(0)

# 去掉代码块、行内代码和链接地址，路径和命令里的英文不算
body = re.sub(r'```.*?```', '', text, flags=re.S)
body = re.sub(r'`[^`]*`', '', body)
body = re.sub(r'\]\([^)]*\)', ']', body)
cjk = len(re.findall(r'[一-鿿]', body))
latin = len(re.findall(r'[A-Za-z]', body))
if cjk + latin >= 40 and cjk / (cjk + latin) < 0.3:
    print(json.dumps({'decision': 'block',
                      'reason': '你刚才最后一条回复主要是英文。这个项目里对用户说的话一律用中文：请用中文把最后一条回复完整重写一遍。'},
                     ensure_ascii=False))
