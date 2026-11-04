#!/usr/bin/env python3
"""抽弹窗段落点名单，并可比对 PPT 文字。
用法：
  python3 抽节点.py list            列出功能框架弹窗段二级节点、一次进入七步、保存与上架检查 12 条
  python3 抽节点.py check <pptx>    比对 PPT 全部文字（含备注），列出没落点的项；没落点为 0 时退出码 0
不放进 PPT 的项写在 不放 字典里，附理由；check 时不算缺。
"""
import re, sys, html, pathlib
根 = pathlib.Path.home()/'claude/弹窗标签推送系统/评审版_定稿改_1027/推送系统后台集成需求'
框架 = 根/'功能框架_脑图.md'
源 = 根/'需求评审版源.html'

# 名字太泛、PPT 里要用的写法
别名 = {'每行': '列表每行', '每条展开': '展开', '入口': '打开入口',
        '对应的活动或礼包': '对应的活动或礼包', '操作纪录页签': '操作纪录'}
检查短名 = {'规则里一个活动或礼包都没有': '一个活动或礼包都没有',
          '规则里有已结束或被活动后台关闭的活动或礼包': '有已结束或被活动后台关闭的',
          '发送对象的群组已被删除或停用': '群组已被删除或停用',
          '群组当前符合人数为 0': '符合人数为 0',
          '复制已结束的规则': '复制已结束的规则',
          '「不受弹出间隔限制」名单里的项被移出本场景所有规则或已结束': '名单里的项被移出或已结束',
          '发送对象选了「群组」却没选任何群组': '没选任何群组'}
不放 = {}  # 例：{'某节点': '理由'}；整份做完时由执行按思考页第 7 节填

def 规范(s):
    s = re.sub(r'（[^）]*）', '', s)          # 去掉（必填）（只读）等
    s = s.split('：')[0].strip()
    return 别名.get(s, s)

def 框架节点():
    行 = 框架.read_text(encoding='utf-8').split('\n')
    起 = next(i for i, l in enumerate(行) if l.startswith('- 游戏内推送'))
    止 = next(i for i, l in enumerate(行) if l.startswith('  - 新建快显'))
    结果, 页 = [], None
    for i in range(起 + 1, 止):
        l = 行[i]
        if re.match(r'^  - ', l):
            页 = l[4:].strip()
        elif re.match(r'^    - ', l):
            原 = l[6:].strip()
            结果.append((i + 1, 页, 原, 规范(原)))
    return 结果

def 源行(n):
    l = 源.read_text(encoding='utf-8').split('\n')[n - 1]
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', l))).strip()

def 规则条目():
    文 = 源.read_text(encoding='utf-8').split('\n')
    def 找(词):  # 只认整行就是这个小标题的那一行
        return next(i + 1 for i, l in enumerate(文) if re.sub(r'<[^>]+>', '', l).strip() == 词)
    七步起 = 找('一次进入怎么判（先后）'); 检查起 = 找('保存与上架检查')
    步 = []
    for n in range(七步起 + 1, 检查起):
        t = 源行(n); m = re.match(r'^([①②③④⑤⑥⑦])([^：:]+)[：:]', t)
        if m: 步.append((n, m.group(1) + m.group(2), m.group(1) + re.sub(r'（[^）]*）', '', m.group(2))))
    查 = []
    for n in range(检查起 + 1, 检查起 + 20):
        t = 源行(n); m = re.match(r'^(\d{1,2}) ([^｜]+)', t)
        if m and not t.startswith('情形'):
            名 = re.split(r'[：；（]', m.group(2))[0].strip()
            名 = 检查短名.get(名, 名)
            查.append((n, m.group(1) + ' ' + 名, 名))
    return 步, 查

def 全部():
    项 = [(f'框架:{n}', f'{页} › {原}', 键) for n, 页, 原, 键 in 框架节点()]
    步, 查 = 规则条目()
    项 += [(f'源:{n}', f'一次进入怎么判 {全}', 键) for n, 全, 键 in 步]
    项 += [(f'源:{n}', f'保存与上架检查 {全}', 键) for n, 全, 键 in 查]
    return 项

def ppt文字(p):
    from pptx import Presentation
    out = []
    for s in Presentation(p).slides:
        for sh in s.shapes:
            if sh.has_text_frame: out.append(sh.text_frame.text)
            if getattr(sh, 'has_table', False) and sh.has_table:
                out += [c.text for r in sh.table.rows for c in r.cells]
            if sh.shape_type == 6:  # 组合
                out += [x.text_frame.text for x in sh.shapes if x.has_text_frame]
        if s.has_notes_slide: out.append(s.notes_slide.notes_text_frame.text)
    return re.sub(r'\s+', '', '\n'.join(out))

if __name__ == '__main__':
    项 = 全部()
    if sys.argv[1:2] == ['list']:
        for 处, 名, 键 in 项: print(f'{处}\t{名}\t查找词：{键}')
        print(f'合计 {len(项)} 项')
    elif sys.argv[1:2] == ['check']:
        文 = ppt文字(sys.argv[2]); 缺 = []
        for 处, 名, 键 in 项:
            if 键 in 不放: continue
            if re.sub(r'\s+', '', 键) not in 文: 缺.append((处, 名, 键))
        for x in 缺: print('没落点', *x, sep='\t')
        print(f'合计 {len(项)} 项，不放 {len(不放)} 项，没落点 {len(缺)} 项')
        sys.exit(1 if 缺 else 0)
