
# 只读：R87–R89 回归检查
import re, os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
rep = open(BASE + '决策汇报.html', encoding='utf-8').read()
h1 = open(BASE + '环节1_现状盘点.html', encoding='utf-8').read()
z0 = open(BASE + '支撑文件/00_推进记录.md', encoding='utf-8').read()

m1 = re.search(r'<pre id="m1">(.*?)</pre>', rep, re.S).group(1).strip()
m0 = re.search(r'\*\*发给运营（3 句）\*\*\s*```\s*(.*?)```', z0, re.S).group(1).strip()
print('运营 3 句 汇报 = 00：', m1 == m0)
print(m1)
print('旧第 2 句残留 汇报/00：', rep.count('保级看什么、看多长时间？') , z0.count('保级看什么、看多长时间？'))
print('环节1「不是账号累计值」剩余：', h1.count('不是账号累计值'))
print('环节1 h3 新写法：', '按盘点（进入、返回大厅不区分），每回到大厅一次就触发一次' in h1)
print('环节1 #u4c 补句：', '也可用会降级或结算延迟解释，见' in h1)
rows = re.findall(r'<tr><td>(\d+)</td>', h1.split('更正记录（')[1])
print('环节1 更正记录行数', len(rows), '最大号', max(map(int, rows)))
rec = rep.split('更正记录（第一节与附录')[1]
rrows = re.findall(r'<tr><td>(\d+)</td>', rec)
print('汇报 更正记录行数', len(rrows))
# 链接存在性
for href in set(re.findall(r'href="([^"#]+)', rec)):
    print('链接', href, os.path.exists(BASE + href))
print('id="m" in 环节1：', 'id="m"' in h1)
