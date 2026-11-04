import sys
sys.path.insert(0, '/Users/decheng.huang/claude/弹窗标签推送系统/_scripts')
import pandas as pd
from an_a45_members import load
df, m = load()
new = df[df['is_new']]
print('新增 age>=8 在场率', new[new['age'] >= 8]['present'].mean(), (new['age'] >= 8).sum())
old = df[(df['age'] >= 30) & (df['age'] <= 59)]
print('age30-59', old['present'].mean(), len(old))
for lo, hi in [(60, 119), (120, 364), (365, 99999)]:
    s = df[(df['age'] >= lo) & (df['age'] <= hi)]
    print('age', lo, hi, s['present'].mean(), len(s))
print('在场', df['present'].sum(), '重叠7572/62292', 7572 / 62292, '7572/34363', 7572 / 34363)
bet = m['bet']; act = m['act']
z = new[new[bet] == 0]
g = z[z[act] == 1000]
print('押注0', len(z), '赠点1000', len(g), (g['age'] >= 7).sum(), (g['age'] >= 7).sum() / len(g))
print('押注0 age>=7 占', (z['age'] >= 7).sum() / len(z))
