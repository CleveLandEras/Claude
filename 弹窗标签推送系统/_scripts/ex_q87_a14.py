import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
p = _ROOT + '/分析/A14_问题清单与影响规模.md'
s = open(p, encoding='utf-8').read()
i = s.find('重排（按业绩）')
i = s.rfind('\n## ', 0, i) if s.rfind('\n## ', 0, i) != -1 else i
print(s[i:i + 9000])
