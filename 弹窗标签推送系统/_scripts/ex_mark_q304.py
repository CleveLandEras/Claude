import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/过程记录/推进计划.md'
lines = open(p, encoding='utf-8').read().split('\n')
out = []
for ln in lines:
    if ln.startswith('- [ ] Q304｜'):
        ln = ln.replace('- [ ] Q304｜', '- [x] Q304｜', 1) + ' → 完成（2026-10-09 19:0x，随 R435–R437 处理一并做）：阶段 8 第四节「可顺手核实」加第 6 项（标签与弹窗内容由运营自写还是数据组代写），待决 11→12 项、核实 5→6 项五处同步，数据收集仍 9 项；阶段 7 该行改指向它；阶段 6 第九节、阶段 8 34 项表的「编写人无记载」说法与之一致；阶段 6、7、8 检索「不依赖研发」「不经研发」「无需研发」「自主率」0 处；A69、A70、A73、A74、A75、A76 头部加更新说明；check_format 阶段 1–8 全部 ✔'
    out.append(ln)
open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
