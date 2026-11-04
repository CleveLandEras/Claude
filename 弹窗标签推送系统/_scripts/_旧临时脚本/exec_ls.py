"""执行者用：列出分析/、支撑文件/、_scripts/、数据/ 下的文件名。不带参数。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ('分析', '支撑文件', '_scripts', '数据'):
    print('==', d)
    for f in sorted(os.listdir(os.path.join(BASE, d))):
        print('  ', f)
