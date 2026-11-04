BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
OLD = '改完以后的完整规则见 02 开头（结构、按玩家看、规则全表）；03 新增「最终规则全表」工作表。'
NEW = '改完以后的完整规则见 02 开头（结构、按玩家看、规则全表）和 03 的「最终规则全表」工作表。'

def rw(path, pairs):
    t = open(path, encoding='utf-8').read()
    for o, n, c in pairs:
        assert t.count(o) == c, (path, o[:50], t.count(o))
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)

rw(BASE + '决策汇报.html', [
    # 首屏
    ('由主管定（第五节第 1 件）。</b>' + OLD, '由主管定（第五节第 1 件）。</b>' + NEW, 1),
    # ⓪ 里的重复句
    ('；改完以后的完整规则见 02 开头（结构、按玩家看、规则全表）。各卡验证计划已集中到附录七', '；各卡验证计划已集中到附录七', 1),
    # 更正第 95 条里的引文
    ('首屏加一句「' + OLD + '」', '首屏加一句『' + NEW + '』', 1),
])
rw(BASE + '环节3_方案.html', [
    ('（' + OLD + '），', '（' + NEW.rstrip('。') + '），', 1),
    ('首屏加一句「' + OLD + '」', '首屏加一句『' + NEW + '』', 1),
])
print('ok')
