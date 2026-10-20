import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import re
base=_ROOT + '/'
for f in ['阶段8_结论汇总.html','弹窗标签推送方案_V1.html']:
    t=open(base+f,encoding='utf-8').read()
    txt=re.sub(r'<[^>]+>','',t)
    print('#####',f,len(txt))
    for k in ['待决','34 ?项','34 个','快速提升','25 个','数据项','数据收集','待 Dk','主对话','内部','未定时','规划者','执行者','审查者']:
        ms=[txt[max(0,m.start()-20):m.end()+28].replace('\n',' ') for m in re.finditer(k,txt)]
        print('--',k,len(ms))
        for x in ms[:14]: print('    ',x)
    print('编号命中',re.findall(r'(?<![A-Za-z0-9])[QRKA]\d{1,3}(?![0-9A-Za-z])',txt)[:20])
