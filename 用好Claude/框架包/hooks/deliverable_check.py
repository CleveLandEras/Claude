#!/usr/bin/env python3
"""PostToolUse hook：Claude 用 Write/Edit 改完一个交付物文件后自动做程序判。

只对路径里含 DELIVERABLE_DIRS 任一词、且是 .md/.html 的文件生效；
有问题 → 在 stdout 输出 JSON {decision: block, reason: 清单}（PostToolUse 下会自动把原因提示给 Claude，它会当场修）；没问题或不适用 → 不输出，exit 0。
名单按项目改：DELIVERABLE_DIRS、SKIP_IF、FORBIDDEN。
"""
import sys, json, re, os

DELIVERABLE_DIRS = ['交付', '简报', '评审版', '需求评审', '原型', '呈交', '汇报', '方案']
SKIP_IF = ['README', '目标卡', '_旧版', '归档', '过程记录', '/分析/', '规则与交接', '研发评审待确认', '样本']
FORBIDDEN = ['待确认', '待核实', '资料没写', '主管要求', '请主管', '请评审定', '评审判断', '到此结束',
             '之后没有其他内容', 'TODO', 'TBD', '待补', '【待', '核心五件', '必需档', '尽量档', '合并版', '不合并版']

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    fp = (data.get('tool_input') or {}).get('file_path') or ''
    if not fp or not fp.endswith(('.md', '.html', '.htm')):
        return 0
    if not any(d in fp for d in DELIVERABLE_DIRS) or any(s in fp for s in SKIP_IF):
        return 0
    if not os.path.isfile(fp):
        return 0
    try:
        text = open(fp, encoding='utf-8', errors='ignore').read()
    except Exception:
        return 0
    issues = []
    for i, line in enumerate(text.splitlines(), 1):
        for w in FORBIDDEN:
            if w in line:
                issues.append(f'第 {i} 行出现「{w}」：{line.strip()[:60]}')
    base = os.path.dirname(fp)
    links = re.findall(r'\]\(([^)#\s]+)', text) + re.findall(r'(?:href|src)=["\']([^"\'#]+)["\']', text)
    seen = set()
    for l in links:
        if l in seen or re.match(r'^(https?:|mailto:|data:|javascript:|//|#|tel:)', l):
            continue
        seen.add(l)
        p = os.path.normpath(os.path.join(base, l.split('?')[0]))
        if not os.path.exists(p):
            issues.append(f'链接目标不存在：{l}')
    if issues:
        lines = [f'[交付物程序判] {os.path.basename(fp)} 有 {len(issues)} 处要处理（禁用词或断链），改完再交：']
        lines += [' - ' + s for s in issues[:30]]
        if len(issues) > 30:
            lines.append(f' - …还有 {len(issues) - 30} 处')
        # PostToolUse：用 JSON 的 decision=block 把原因直接送到 Claude 面前（文档：会自动提示 Claude）；exit 0。
        print(json.dumps({'decision': 'block', 'reason': '\n'.join(lines)}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    sys.exit(main())
