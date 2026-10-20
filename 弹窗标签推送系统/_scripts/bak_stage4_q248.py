import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import shutil, os
B = _ROOT + ''
shutil.copy(os.path.join(B, '阶段4_问题诊断.html'), os.path.join(B, '_versions', '阶段4_问题诊断_Q248前.html'))
print('ok')
