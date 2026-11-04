#!/usr/bin/env python3
"""Stop 钩子：回复太长就拦一次。

Dk 10/29：「对话经常回复字长的我根本没法看，而且还夹杂着工作过程」。
最后一条回复超过 LIMIT_CHARS 个汉字或 LIMIT_LINES 行，就 block 一次，让 Claude 压成 ≤ 5 行（结论、成品链接、要 Dk 定的事），过程写进文件。
只拦一次（stop_hook_active 时放行）；回复里写「长回复：Dk 要的」可跳过（Dk 明确要解释时用）；任何异常都放行。
"""
import json, re, sys

LIMIT_CHARS = 300   # 汉字数（不含代码块、链接）
LIMIT_LINES = 8     # 非空行数
SKIP_MARK = '长回复：Dk 要的'

def main():
    data = json.load(sys.stdin)
    if data.get('stop_hook_active'):
        return
    msg = data.get('last_assistant_message') or ''
    if not msg or SKIP_MARK in msg:
        return
    body = re.sub(r'```.*?```', '', msg, flags=re.S)
    body = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)
    cjk = len(re.findall(r'[一-鿿]', body))
    lines = [l for l in body.splitlines() if l.strip()]
    if cjk <= LIMIT_CHARS and len(lines) <= LIMIT_LINES:
        return
    reason = (f'回复过长：{cjk} 个汉字、{len(lines)} 行，超过 Dk 的阅读上限（{LIMIT_CHARS} 字或 {LIMIT_LINES} 行）。'
              '重写成不超过 5 行：一句结论、成品文件链接、要 Dk 定的事；过程、分析、清单写进文件再给链接。'
              f'Dk 明确要长解释时，在回复末尾写「{SKIP_MARK}」。')
    print(json.dumps({'decision': 'block', 'reason': reason}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
