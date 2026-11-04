# 只读：列出项目各目录文件与大小（规划者用）
import os
BASE = '/Users/decheng.huang/claude/弹窗标签推送系统/'
for d in ['', '支撑文件', '分析', '数据', '来源资料', '规则与交接', '过程记录']:
    p = os.path.join(BASE, d)
    print('==', d or '根目录')
    for f in sorted(os.listdir(p)):
        fp = os.path.join(p, f)
        if os.path.isfile(fp):
            print('  ', f, os.path.getsize(fp))
        else:
            print('  [目录]', f)
