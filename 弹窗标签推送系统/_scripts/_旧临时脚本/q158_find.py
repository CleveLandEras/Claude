import io
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
files = ['决策汇报.html', '环节3_方案.html']
terms = ['挪量', '破产位内', '曝光次数', '误判', '3 个百分点', '95% 区间', '护栏', '含」', '第 12 件', '第 17 件', '路 C', '全量退路']
for fn in files:
    print('=====', fn)
    with io.open(base + fn, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            hit = [t for t in terms if t in line]
            if hit:
                s = line.strip()
                print(i, hit, len(s), s[:160].replace('\n', ' '))
