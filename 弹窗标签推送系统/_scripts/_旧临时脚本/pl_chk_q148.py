import re, glob, os
base = '/Users/decheng.huang/claude/弹窗标签推送系统/'
def text(p):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
    return re.sub(r'<[^>]+>', '', s)
f02 = glob.glob(base + '支撑文件/02_*.html')
f02 = [f for f in f02 if 'Cowork' not in f]
files = f02 + [base + '决策汇报.html', base + '环节3_方案.html', base + '环节2_问题诊断.html'] + glob.glob(base + '支撑文件/08_*') + glob.glob(base + '支撑文件/04_*')
terms = ['验证计划', '不能承诺', '不承诺用储值证明', '不能用储值证明', '可代替随机分组', '分了组也', '只能按成本、风险', 'Dk 可改', '判读', '评估重点', '看不出']
for p in files:
    t = text(p) if p.endswith('.html') else open(p, encoding='utf-8', errors='ignore').read()
    print(os.path.basename(p), {k: t.count(k) for k in terms})
# show 02 验证计划 snippets for card 1
t = text(f02[0])
i = t.find('验证计划')
cnt = 0
while i != -1 and cnt < 7:
    print('---', t[i:i+400].replace('\n', ' '))
    i = t.find('验证计划', i + 2000)
    cnt += 1
