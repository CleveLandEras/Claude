p = '/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/审查记录.md'
t = open(p, encoding='utf-8').read()
i = t.find('### R95')
j = t.find('\n复核', i)
k = t.find('\n通过的改动', i)
end = min(x for x in [j, k, len(t)] if x > 0)
print(t[i:end])
