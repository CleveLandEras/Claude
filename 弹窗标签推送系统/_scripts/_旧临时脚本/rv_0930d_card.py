# 只读：打印设计卡 Q122 一节
from pathlib import Path
t = Path('/Users/decheng.huang/claude/弹窗标签推送系统/过程记录/设计卡.md').read_text(encoding='utf-8')
i = t.find('## Q122｜')
j = t.find('\n## ', i + 5)
print(t[i:j if j > 0 else None])
