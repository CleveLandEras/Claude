"""R104 复核：U2 高段按卡别拆分；只算普卡时高段人数与占比；< 60 天层参照组中注册时间缺值人数。只读，不带参数。
复用 an_q66_push.py 的全部定义（runpy 执行后取变量）。"""
import os as _os; _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import runpy
import io
import contextlib

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(_ROOT + '/_scripts/an_q66_push.py')
U2, ref = g['U2'], g['ref']
hi = U2[U2.seg == '高']
print('高段', len(hi), '卡别', hi['卡别'].value_counts().sort_index().to_dict())
pu = U2[U2['卡别'] == 1]
print('U2 普卡', len(pu), '其中高段', int((pu.seg == '高').sum()), f'{(pu.seg == "高").mean() * 100:.2f}%')
yin = U2[U2['卡别'] == 2]
print('U2 银卡', len(yin), '其中高段', int((yin.seg == '高').sum()))
lt = ref[ref.tl == '<60']
print('参照组 <60 层', len(lt), '其中注册时间缺值', int(lt['reg'].isna().sum()))
lt2 = lt[lt['reg'].notna()]
print(f'  去掉缺值后 {len(lt2)} 人，高段 {(lt2.seg == "高").mean() * 100:.2f}%')
x = U2[U2.tl == '<60']
print(f'  U2 <60 层 {len(x)}，高段 {(x.seg == "高").mean() * 100:.2f}%，差 {(x.seg == "高").mean() * 100 - (lt2.seg == "高").mean() * 100:+.2f}')
print('高段仍在近一月名单', int((hi['src'] == '活跃').sum()), '已离开', int((hi['src'] == '离开').sum()))
