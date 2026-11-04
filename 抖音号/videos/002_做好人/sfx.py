"""《被坑多了，你会变狠吗？》（002 横屏，第五版，59.65 秒 = 1790 帧）的音效轨。

只有音效。配乐由号主发布时在抖音曲库里加（纯音乐，钢琴或木琴、拨弦，90–110 BPM，没有重鼓点），
所以这里不放旋律，环境层压得很低，给配乐留地方。唯一的和弦是“你只有一遍”（S27–S27h）那一层暖音，
G 大调（和四盏灯 G5/B5/D6/G6 同一个调），曲子定了以后要是不在 G 调，改 PAD_NOTES 重跑。
第五版：没有“第 N 轮”计数器了，计数“嗒”全删；顶上路线图（老实 → 狠 → 有来有往 → 原谅）每往前走一格一声小铃，
音高和四盏灯是同一组（ROUTE_NOTES），所以 S25 四盏灯是把路线图那几声再放一遍。

  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/videos/002_做好人/sfx.py

读：studio/src/videos/002/timeline.json（每拍起止帧、事件帧；timeline.py 生成，这里只读）
    studio/src/videos/002/data.json（代数、合作率、点阵；make_data.py 生成，这里只读）
写：studio/public/002/sfx.wav（48 kHz、16 bit、双声道；关键音效左右完全一样，放正中）
    studio/public/002/sfx_events.json（每个音效的落点：t 秒、frame 帧、name、beat、key；t 是起音时刻，提前的“嗖”写的是提前后的时刻）
    videos/002_做好人/out/音效/：波形对照图、逐拍对照图、手机频段图、落点核对.json

做法照 001 的 full_audio.py：每个声音用 numpy 合成，按时间表的帧放上去，整条量响度再统一调。和 001 不同的地方：
  - 48 kHz。声音照实物怎么发声来合成：敲击 = 几个按指数衰减的振动模态 + 一下接触噪声；嗖 = 扫频的带通噪声；
    同类声音每次音高、长短都有小随机（固定种子，每个声音的种子由拍号、类别、序号算出来，加删别的声音不影响它）。
  - 手机外放是单声道、250 Hz 以下几乎放不出：关键音效左右一样，都带 1–4 kHz 的成分；
    “来回”靠音高和扫频方向分（他抢你：嗖往下扫；你抢他：嗖往上扫），不靠左右声道。
  - 响度用 ffmpeg 的 ebur128 量：整条 −19 LUFS，真峰值不超过 −1 dBTP（超了过一道前瞻限幅）。
  - 跑完自己从磁盘读回 sfx.wav，逐个找音效的起音，和画面事件对时间差（见 check()）。

定位规则（timeline.json 的事件不够细时，照 Near.tsx / Ending.tsx / Gray002.tsx 里画面怎么用这些事件来定）写在 RULES。
"""
import json
import math
import os
import re
import subprocess
import tempfile
import wave
import zlib

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'studio', 'src', 'videos', '002')
TL = json.load(open(os.path.join(SRC, 'timeline.json')))
D = json.load(open(os.path.join(SRC, 'data.json')))
OUT_WAV = os.path.join(ROOT, 'studio', 'public', '002', 'sfx.wav')
OUT_DIR = os.path.join(HERE, 'out', '音效')
FF = imageio_ffmpeg.get_ffmpeg_exe()
FONT = next((p for p in ('/System/Library/Fonts/Hiragino Sans GB.ttc', '/System/Library/Fonts/STHeiti Medium.ttc')
             if os.path.exists(p)), None)

SR = 48000
FPS = TL['fps']
NF = TL['frames']                 # 第五版 1790 帧
SPF = SR // FPS                   # 每帧 1600 个采样
N = NF * SPF                      # 整条 59.667 秒（第五版）
DUR = N / SR
TARGET = -19.0                    # 整条响度（LUFS）
TP_CEIL = -1.5                    # 真峰值上限（dBTP；第五版从 −1.0 收到 −1.5）
SEED = 2002

BEATS = TL['beats']
B = {b['id']: b for b in BEATS}
CYC = D['cycle']                   # 第七版 S26 接着跑的点阵和人数
ALLC, ALLD, TFT, GTFT, GRIM, WSLS = range(6)
HARSH = {ALLD, GRIM}

def E(bid, k):
    return B[bid]['ev'][k]


def T(s):
    """和 Near.tsx 里的 T() 一样：秒 → 帧，四舍五入（JS 的 Math.round）。"""
    return int(math.floor(s * FPS + 0.5))


# “你只有一遍”的暖音：G 大调和弦（G4 B4 D5 G5，顶上一点 D6），没有 250 Hz 以下的音
PAD_NOTES = (392.00, 493.88, 587.33, 783.99, 1174.66)
PAD_GAINS = (1.0, 0.75, 0.8, 0.6, 0.22)
PAD_RISE = 0.9                    # 暖音慢慢满要多久（秒）；第七版重排：S27 起收薄，淡完在 S28 开头之后 PAD_AFTER 秒，赶在钟表“嘀”（S28 第 2 帧）之前
PAD_AFTER = 0.0
PAD_GAIN = -16.0                   # 第七版重排：垫在带走句和四盏灯底下，只给一点暖（原来是那一刻的主角，−9 dB）

# 路线图四格（老实、狠、有来有往、原谅）的音高 = 四盏灯（S25）的音高：G5、B5（狠，闷）、D6、G6，一格比一格高
ROUTE_NOTES = (783.99, 987.77, 1174.66, 1567.98)
ROUTE = TL['route']['keys']        # [{f, t, act, i}]：in / reveal / ask / back / on / out
# 路线图的铃落在动作开始后第几帧（照 FOverlay.tsx 的 RouteMap）：reveal 是“？”翻成头像（FLIP = 8 帧，+4 头像露出、+5 弹出最大），
# 同时当前标记滑过去（SLIDE = 12 帧，先慢后快再慢）；on 只有滑。第五版预演里只量路线图那一块的逐帧变化：
# reveal、on 都是 +4/+5 帧起大变、+6/+7 帧变化最大，铃放在 +5（离起点 0–1 帧、离最大 2 帧）
ROUTE_LAND = {'reveal': 5, 'on': 5}
OPT_GAIN = -19.0                   # 结尾两个选项的轻叮：同一个音色、同样响（第五版补改）
OPT_TRIM = (0.0, 0.5)              # G6 那声单独合成后 ebur128 瞬时响度低 0.5 LU，补上，两声一样响


def _s(f):
    return f'{f / FPS:.2f}'


# ---------- 代数：和 lib.ts 的 genF / genAt 同一个算法 ----------
GK = TL['gen']


def genF(f):
    if f <= GK[0]['f']:
        return GK[0]['gen']
    for i in range(1, len(GK)):
        k, p = GK[i], GK[i - 1]
        if f < k['f'] or (f == k['f'] and k['mode'] != 'step'):
            if k['mode'] == 'lin':
                return p['gen'] + (k['gen'] - p['gen']) * (f - p['f']) / max(1e-9, k['f'] - p['f'])
            return p['gen']
    return GK[-1]['gen']


GEN = [int(math.floor(genF(f) + 1e-9)) for f in range(NF + 1)]


def beat_at(f):
    for b in BEATS:
        if b['f0'] <= f < b['f1']:
            return b
    return BEATS[-1]


def prog(f, ab):
    a, b = ab
    return min(1.0, max(0.0, (f - a) / max(1e-6, b - a)))


def ease(x):
    x = min(1.0, max(0.0, x))
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def gen_changes(fa, fb):
    """[fa, fb) 里“第 N 代”的显示值变了的帧。"""
    return [f for f in range(max(1, fa), fb) if GEN[f] > GEN[f - 1]]


def pad_start():
    """暖音从哪一帧起（第七版重排：四个你＋带走句那一拍 S25 的开头）。"""
    return B['S25']['f0']


def pad_span():
    """暖音的几个时刻（秒，从 pad_start() 算起）：到最满、开始收薄、淡完。
    第七版重排：“你只有一遍／你没法重来”那句删了，暖音改成垫在 S25 带走句底下，0.9 秒慢慢满；S27（dive）起收薄，
    cos² 一路淡到 S28 开头（之后 PAD_AFTER 秒）淡完，把空间留给 S28 第 2 帧的钟表“嘀”。"""
    t0 = pad_start()
    full = PAD_RISE
    hold = (B['S27']['f0'] - t0) / FPS
    end = (B['S28']['f0'] - t0) / FPS + PAD_AFTER
    return full, hold, end


S08_FALL, S08_FLASH = 7, 9          # 第七版追加：S08 滑掉那颗下落 7 帧，落地闪光 9 帧（FNear.tsx 的 FALL、FLASH）


def s08_slip_at():
    """S08 滑掉那颗出手的帧（FNear.tsx：min(原来均匀排的位置, 拍尾 − 7 − FALL)，让落地闪光在切走前露 7 帧）。"""
    g0, g1 = E('S08', 'gives')
    return min(g0 + (g1 - g0) * E('S08', 'slipIndex') / 19, B['S08']['f1'] - 7 - S08_FALL)


def s08_give_at(i):
    """S08 第 i 颗出手的帧（FNear.tsx 的 giveAt）：滑掉那颗之前的均匀排在 gives 起点到它之间，之后的排在它到 gives 终点之间。"""
    g0, g1 = E('S08', 'gives')
    sl, si = s08_slip_at(), E('S08', 'slipIndex')
    return g0 + (sl - g0) * i / si if i <= si else sl + (g1 - sl) * (i - si) / (19 - si)


def route_at(act, i=None):
    """路线图里某个动作的那一帧（act 和第几格都对上的第一个）。"""
    return next(k['f'] for k in ROUTE if k['act'] == act and (i is None or k['i'] == i))


def _rules():
    """落点规则。帧号全部从 timeline.json 算出来写进去（第四版起不再手写帧号）。"""
    s8 = s08_slip_at()
    q0 = E('S21', 'pong')[0]
    full, hold, end = pad_span()
    f19 = E('S27', 'dive')
    rk = {k['act'] + str(k['i']): k['f'] for k in ROUTE}
    l0, l1 = E('S15', 'lines')
    nv = len(D['grid']['victims'])
    return f"""\
- 时间都从 timeline.json 的帧来；一个事件给的是区间 [a, b] 时，“开始”取 a，“完成”取 b。下面的帧号都是脚本按第五版时间表算出来的。
- 事件表的 beat 写声音实际落在哪一拍；排它的那一拍不同时记在 from_beat（S18 的转头、条、变蓝落在 S18b 里，就是这样）。
- 递光点（FNear.tsx 的 give/back/toRow/fromRow）：t 帧出手，飞 d 帧，t+d 到对方手里。“叮”落在到手那一帧。d：一般 7，S18 是 6。
  S06：第 i 颗在 round(gives0 + (gives1−8−gives0)×i/9) 帧出手，10 颗挤在 {_s(E('S06', 'gives')[0])}–{_s(E('S06', 'gives')[1])} 秒。
  那一排固定是第 4 代碰到的 10 个人（画面 you[4].opp），递给其中骗子的 {sum(1 for s in D['you'][4]['opp'] if s == ALLD)} 颗是闷的“叮”。
- 抢（grab/myGrab/rowGrab）：t 帧伸手，t+0.45d 帧碰到光点（之后连手带光点拿回去）。“嗖”比伸手早 0.1 秒起（分镜：比抢早 0.1 秒），
  “噗”（光点被拿走）落在碰到的那一帧。他抢你：嗖往下扫；你抢他：嗖往上扫。d：S07、S09、S12 是 9，S18 是 7，S22 是 6。
- 开场（S01）：timeline 直接给了 whoosh={E('S01', 'whoosh')} 帧（比 grab 开始的 {E('S01', 'grab')[0]} 帧早 0.1 秒）；“噗”在 {E('S01', 'grab')[0]} 帧，光点开始离开你的手。
  噗里叠一层指节敲木头（1.5 kHz 上下、几十毫秒、晚 6 毫秒，听着是同一下），手机外放靠它听出这一下；噗的低频留着（只低 1 dB 上下）。
- 手滑（slipMe/slipOpp）：t 帧开始滑，下落 1.2×8 = 9.6 帧落地、闪光；“啪”落在落地那一帧。S08 的特写（第七版追加，照 FNear.tsx）：第 14 颗在
  {s8:.0f} 帧出手（拍尾 − 7 − 下落 {S08_FALL} 帧），{s8 + S08_FALL:.0f} 帧落地、闪光 {S08_FLASH} 帧（切走前露 {B['S08']['f1'] - s8 - S08_FALL:.0f} 帧）；
  前 13 颗在 {E('S08', 'gives')[0]} + ({s8:.0f} − {E('S08', 'gives')[0]})×i/13 帧，后 6 颗在 {s8:.0f} + ({E('S08', 'gives')[1]} − {s8:.0f})×(i−13)/6 帧（i = 14…19）。
- 第五版没有“第 N 轮”计数器：计数“嗒”全删。远景、中景里点成片变色的地方（S03、S14、S16、S19）留一层很轻的细碎“嗒”：
  每一代看得见的点里变了几个色（data.json 点阵逐代比，S03 只数开局亮着的 500 个），换成每秒多少颗（最多每秒 55 颗），
  随机撒在这一代显示的那几帧里，不落在帧格上，听着是“一片在翻”，不是在数数。S11 中景照旧：变色的点各一下轻“咔哒”。
  S24 方块翻色：473 格从 {E('S24', 'flip')[0]} 到 {E('S24', 'flip')[1]} 帧一格格翻（FEnding.tsx），配一阵洗牌似的细“嗒”（每秒约 75 颗、随机撒），越翻越高。
- 路线图（timeline.json 的 route.keys）：音高和四盏灯同一组，老实 G5、狠 B5（发闷）、有来有往 D6、原谅 G6。
  in（{rk['in0']} 帧，和字幕同一帧）一声很轻的 G5；reveal 狠（{rk['reveal1']}）、on 狠（{rk['on1']}）、reveal 有来有往（{rk['reveal2']}）、reveal 原谅（{rk['reveal3']}）
  各一声小铃，落在 key 帧 +{ROUTE_LAND['reveal']}（reveal）/ +{ROUTE_LAND['on']}（on）：FOverlay.tsx 里 reveal 是“？”翻成头像、当前标记滑过去，on 只有滑；
  第五版预演里路线图那一块的逐帧变化都是 +4/+5 起大变、+6/+7 最大。后三处的 key 帧正好是换衣 recolor 开始：布料声在 key 帧起，铃在它里面，
  “咔哒”在 recolor 结束（比铃晚 0.23–0.43 秒，铃还在响）；S03 三下错开：字幕“你也是”{_s(B['S03']['lines'][1][0][2])} 秒出（不配声），
  你的点变红 {_s(E('S03', 'youRed'))} 秒（key“咔哒”），路线图亮“狠”{_s(rk['reveal1'])} 秒起翻、闷铃在 {_s(rk['reveal1'] + ROUTE_LAND['reveal'])} 秒，
  两下声音隔 {(rk['reveal1'] + ROUTE_LAND['reveal'] - E('S03', 'youRed')) / FPS:.2f} 秒，不叠成一团；
  ask（{rk['ask2']}）两声轻的往上挑（D6 → G6，就是后面两格的音，隔 3 帧）；back（{rk['back0']}）一下很短的倒吸，和倒带同一帧起；out 不另配（四个你接手，有散开的风声）。
- 你变红（S03 youRed，{E('S03', 'youRed')} 帧，{_s(E('S03', 'youRed'))} 秒）：key，一下按扣似的“咔哒”叠一下指节敲击（1.3 kHz 上下）；路线图狠那一格的闷铃在它后面另起（见上）。
- 倒带（S05）：{E('S05', 'rewind')[0]}–{E('S05', 'rewind')[1]} 帧，第 70 代倒回第 0 代，越倒越尖，停时一下“咔”；{E('S05', 'dive')[0]} 帧扎进你的点。
- 换衣“咔哒”：落在 recolor 结束那一帧（颜色刷完、扣上）；刷的过程中有一层很轻的布料声。
- 一排人换颜色（S18 rowTurn {E('S18', 'rowTurn')[0]}–{E('S18', 'rowTurn')[1]}、S22 rowGreen {E('S22', 'rowGreen')[0]}–{E('S22', 'rowGreen')[1]} 帧）：一层很轻、远一点的布料刷声，跨过这一段。
- 分数条“刷”：落在 bars 那一帧（两根条开始伸出来）。
- 乒乓（S21）：每趟 T(0.4)=12 帧；第 n 趟 {q0}+12n 出发、{q0}+12(n+1) 到。嗖跟着每一趟走，到的那一下一声“啵”（你那边低、他那边高）。
- S23 飞向你的“抢”：第 166 代每 {T(0.15)} 帧一道（{E('S23', 'grabsDense')[0]} 起），第 167 代每 {T(0.34)} 帧一道（{E('S23', 'grabsSparse')[0]} 起），每道 7 帧；小“嗖”从出现那一帧起。
- S15（第五版没有字幕）：{l0} 帧（lines 起点）音效层和环境声全停；第五版补改后画面不再画连向被坑的人的线，那组细“嗞”删了；
  {E('S15', 'freeze')[0]} 帧（定住，你在一片红里、身上的红圈）一声“咚”，里面叠一层 1–3 kHz 的木头敲击（手机外放靠它）；{E('S15', 'freeze')[1]} 帧以后环境声冷着回来。
- 硬切（S18b→S19，{B['S19']['f0']} 帧，{_s(B['S19']['f0'])} 秒，近景切到远景）：一声短“刷”（往下扫），落在切的那一帧。
- 可手滑（S19–S20）：{E('S19', 'freeze')[0]} 帧定住，全停；{E('S20', 'push')[0]}–{E('S20', 'push')[1]} 帧从远景推到近景，一声很轻的往里收的“嗖”
  （单独那一轨，峰值比后面的“啪”低 20 dB），只回一点房间底噪；{E('S20', 'slip') + 9.6:.1f} 帧单独一声“啪”。
- 四个你（S25，带走句也在这一拍）：四声“叮”落在 lamps 的四帧（灯开始亮）。
- 接着跑（第七版三改：S26＋S26b，data.json 的 cycle；代数照 timeline.json 的 cycle.keys {TL['cycle']['keys']}，两点之间线性、最后一点之后停住，
  和 FEnding.tsx 的 cycleGen 同一个算法）：S26 gather {E('S26', 'gather')[0]} 帧一声往外退的轻嗖（从 1.7 kHz 往 480 Hz 落，前重后轻，混响多一点）；
  一层质感从 S26 run（{E('S26', 'run')[0]} 帧）起一直到 S26b run2 结束后 0.25 秒：S26（第 300 → 750 代，好欺负的人从 0 涨到 {(lambda c: (c[ALLC] + c[WSLS]) / sum(c))(CYC['counts'][750 - CYC['gen0']]) * 100:.0f}%）
  紧张度 0.06 → 0.30，安稳里透一点不安、不暗，配点变黄的很轻的“啵”；S26b（第 750 → 860 代）紧张度 = 0.30 + 0.70×狠人比例 ÷ 最高时的比例，
  peak（{E('S26b', 'peak')} 帧，第 {CYC['harshPeak']} 代，{CYC['harshPeakShare'] * 100:.0f}%）那一刻最紧，配点变红的细碎“嗒”；
  back（{E('S26b', 'back')} 帧，第 {CYC['harshBack30']} 代，狠人回到三成）一声发暗的重击，key（72 Hz 闷响＋暗箱板＋1.15 kHz 敲木头，手机外放靠后者）。
  这两拍的环境层按远景算，冷暖跟着狠人比例走。
- 方块聚拢“唰”：{E('S24', 'gather')[0]} 帧起，{E('S24', 'gather')[1]} 帧（聚成方块）收成一声闷响；{E('S24', 'ding')} 帧一声“叮”。
- 结尾（第七版重排：S24 方块 → S26 狠人又回来了 → S25 四个你＋带走句 → S27/S27h 不出字 → S28）：
  暖音（G 大调和弦 G4 B4 D5 G5 D6，泛音压在 1–2 kHz，250 Hz 以下没有音）垫在 S25 带走句底下：{_s(pad_start())} 秒起、{PAD_RISE} 秒慢慢满，
  {PAD_GAIN:g} dB（只给一点暖，不盖四盏灯）；{_s(pad_start() + hold * FPS)} 秒（S27 dive 起）开始收薄，cos² 一路淡到 {_s(pad_start() + end * FPS)} 秒
  （S28 从 {_s(B['S28']['f0'])} 秒开始，钟表“嘀”在 {_s(B['S28']['f0'] + 2)} 秒）。S27 dive {f19[0]}–{f19[1]} 帧从四个你扎回你：一声往里扎的嗖（2.6 kHz 往 650 Hz 落）。
  环境声从 {B['S27']['f0']} 帧起压到三成。
- 结尾（S28）：{B['S28']['f0'] + 2} 帧（“约好七点，朋友没来。”出来）一声很轻的钟表“嘀”，{B['S28']['f0'] + 14} 帧一声“嗒”；
  opt1（{E('S28', 'opt1')} 帧，“再约一次”）、opt2（{E('S28', 'opt2')} 帧，“拉黑”）：两个选项画面上同一个颜色，声音也同一个软槌小铃、同样 {OPT_GAIN:g} dB，
  只差音高（D6、G6，和 ask 那声问句同一个音色），不再一暖一闷。
- 手机外放的清脆层（第四版补改，审片点名的五处）：走下来的脚步（S09、S18，S22 也一样）叠鞋跟踩木地板的“咔”；S20 的“啪”叠 2–3.5 kHz 的玻璃余响；
  S22 抢的“噗”叠指节敲击；方块合拢的闷响叠“咔”地合上的敲击。低频都留着（同样峰值下只低 1–3 dB）。
"""


RULES = _rules()


# ======================================================================
# 声音的零件
# ======================================================================
def ts(n):
    return np.arange(n) / SR


def shape(x, lo=None, hi=None, order=2, tilt=0.0, peaks=()):
    """频域里整形（零相位）：lo/hi 是柔和的高通/低通拐点，tilt<0 往低频倾斜，peaks=(中心, Q, dB) 加共振峰。"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1.0
    g = np.ones_like(f)
    if lo:
        g /= np.sqrt(1 + (lo / f) ** (2 * order))
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    if tilt:
        g *= (f / 1000.0) ** (tilt / 2)
    for fc, q, db in peaks:
        g *= 1 + (10 ** (db / 20) - 1) * np.exp(-0.5 * ((f - fc) / (fc / q)) ** 2)
    g[0] = 0.0
    return np.fft.irfft(X * g, n)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))) + 1e-12)


def noise(n, rng, lo=None, hi=None, order=2, tilt=0.0, peaks=()):
    """整形过的噪声，有效值归一到 1。先整形再乘包络，起音前不会有预回声。"""
    y = shape(rng.standard_normal(max(n, 64)), lo, hi, order, tilt, peaks)[:n]
    return y / rms(y)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-12)


def fades(x, fi=0.0004, fo=0.008):
    a, b = int(fi * SR), int(fo * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b and b < len(x):
        x[-b:] *= np.linspace(1, 0, b)
    return x


def jit(rng, cents):
    return 2 ** (rng.normal(0, cents) / 1200)


def var(rng, p):
    return 1 + rng.uniform(-p, p)


def modal(n, parts, rng, att=0.0006):
    """几个按指数衰减的振动模态（频率, 幅度, 衰减时间）。敲木头、敲金属、敲玻璃都是这样。"""
    t = ts(n)
    y = np.zeros(n)
    for f, a, tau in parts:
        if f <= 20 or f >= 0.45 * SR or a == 0:
            continue
        y += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau)
    return y * (1 - np.exp(-t / att))


def contact(n, rng, lo, hi, tau, att=0.00015):
    """碰上去那一下的接触噪声。"""
    m = min(n, int(max(0.06, 12 * tau) * SR))
    t = ts(m)
    y = np.zeros(n)
    y[:m] = noise(m, rng, lo, hi) * np.exp(-t / tau) * (1 - np.exp(-t / att))
    return y


def tv_noise(n, rng, fc, bw, nfft=1024, hop=128):
    """时变带通噪声：fc（Hz）、bw（倍频程）都可以逐样本变。用短时傅里叶逐帧乘高斯形的通带再叠回去。"""
    fc = np.broadcast_to(np.asarray(fc, float), (n,))
    bw = np.broadcast_to(np.asarray(bw, float), (n,))
    pad = nfft
    x = rng.standard_normal(n + 2 * pad)
    win = np.hanning(nfft + 1)[:-1]
    starts = np.arange(0, n + pad, hop)
    fr = np.lib.stride_tricks.sliding_window_view(x, nfft)[starts] * win
    S = np.fft.rfft(fr, axis=1)
    fq = np.fft.rfftfreq(nfft, 1 / SR)
    fq[0] = 1.0
    ci = np.clip(starts + nfft // 2 - pad, 0, n - 1)
    sig = np.maximum(bw[ci], 0.04) / 2.355
    G = np.exp(-0.5 * (np.log2(fq[None, :] / fc[ci][:, None]) / sig[:, None]) ** 2)
    Y = np.fft.irfft(S * G, nfft, axis=1) * win
    out = np.zeros(len(x) + nfft)
    for i, s in enumerate(starts):
        out[s:s + nfft] += Y[i]
    y = out[pad:pad + n]
    return y / rms(y)


# ======================================================================
# 各种声音（都返回单声道、峰值 1；g_tick 例外，见注释）
# ======================================================================
def g_ding(rng, f0=1568.0, bright=1.0, decay=1.0, dull=False):
    """递光点的“叮”：小金属条（钟琴）的几个模态 2.76、5.40、8.93 倍，第一模态旁边带一个差 1–2 Hz 的伴音（会有一点拍频）。"""
    f0 *= jit(rng, 10)
    dk = decay * var(rng, 0.12)
    n = int(min(1.4, 0.9 * dk + 0.3) * SR)
    if dull:   # 递给骗子的那颗：没有亮的泛音，短，闷
        parts = [(f0 * 0.5, 1.0, 0.05), (f0 * 0.5 * 2.756, 0.15, 0.015)]
        y = norm(modal(n, parts, rng)) + 0.1 * norm(contact(n, rng, 600, 3000, 0.002))
    else:
        parts = [(f0, 1.0, 0.42 * dk), (f0 + rng.uniform(0.7, 2.2), 0.2, 0.38 * dk),
                 (2.756 * f0, 0.34 * bright, 0.10 * dk), (5.404 * f0, 0.14 * bright, 0.032 * dk),
                 (8.933 * f0, 0.05 * bright, 0.011 * dk)]
        y = norm(modal(n, parts, rng)) + 0.22 * bright * norm(contact(n, rng, 2500, 10000, 0.0015))
    return norm(fades(y))


def g_me(rng, f0=1760.0, big=False):
    """白点（我）的“叮”：轻敲玻璃，模态 1、2.32、4.25 倍，衰减长。快进跑到 300、方块翻完时用 big（多一层低八度）。"""
    f0 *= jit(rng, 6)
    dk = 1.3 if big else 1.0
    n = int((2.0 if big else 1.5) * SR)
    parts = [(f0, 1.0, 0.75 * dk), (f0 * 1.0009, 0.3, 0.7 * dk), (2.32 * f0, 0.12, 0.2 * dk), (4.25 * f0, 0.04, 0.07 * dk)]
    if big:
        parts += [(f0 / 2, 0.35, 0.6), (f0 / 2 * 2.32, 0.1, 0.2)]
    y = norm(modal(n, parts, rng, att=0.002)) + 0.1 * norm(contact(n, rng, 4000, 12000, 0.001))
    return norm(fades(y))


def g_warm(rng, f0=880.0):
    """会原谅的人照样递出来的暖光点：低一点、圆一点（近于谐和的泛音，软槌），再叠一层慢起的同音，听着发暖。"""
    n = int(1.8 * SR)
    t = ts(n)
    f0 *= jit(rng, 5)
    parts = [(f0, 1.0, 0.65), (f0 * 1.0015, 0.25, 0.6), (2.0 * f0 * 1.003, 0.3, 0.26), (3.01 * f0, 0.14, 0.12),
             (4.18 * f0, 0.06, 0.05), (f0 / 2, 0.12, 0.5)]
    y = norm(modal(n, parts, rng, att=0.001))
    bloom = modal(n, [(f0, 1, 0.5), (2 * f0, 0.4, 0.3), (3 * f0, 0.15, 0.2)], rng) * (1 - np.exp(-t / 0.06))
    y = y + 0.35 * norm(bloom) + 0.14 * norm(contact(n, rng, 500, 3500, 0.003))
    return norm(fades(y))


def g_glint(rng, f0=4200.0):
    """一颗很小的玻璃亮声（远景里光点飞、点亮起时用）。"""
    n = int(0.09 * SR)
    f0 *= jit(rng, 60)
    y = modal(n, [(f0, 1, 0.022 * var(rng, 0.3)), (1.47 * f0, 0.45, 0.012), (2.09 * f0, 0.2, 0.006)], rng, att=0.0003)
    return norm(fades(y))


def g_rise(rng, f0=1046.5, semis=7.0):
    """上扬的“叮——”：一敲下去音高往上滑一个五度（像敲完再把金属条拧紧），后面冒出三颗小亮光。"""
    n = int(1.5 * SR)
    t = ts(n)
    r = 2 ** (semis / 12 * (1 - np.exp(-t / 0.16)))
    ph = 2 * np.pi * np.cumsum(f0 * jit(rng, 8) * r) / SR
    y = (np.sin(ph) * np.exp(-t / 0.7) + 0.3 * np.sin(2.756 * ph + 1) * np.exp(-t / 0.18)
         + 0.12 * np.sin(5.404 * ph + 2) * np.exp(-t / 0.06) + 0.15 * np.sin(1.0012 * ph + 0.5) * np.exp(-t / 0.6))
    y = norm(y * (1 - np.exp(-t / 0.0008))) + 0.2 * norm(contact(n, rng, 2500, 10000, 0.0015))
    for k, d in enumerate((0.13, 0.24, 0.36)):
        s = g_glint(rng, 3500 * 1.18 ** k)
        i = int(d * SR)
        y[i:i + len(s)] += 0.12 * s[: n - i]
    return norm(fades(y))


def g_lamp(rng, f0, muffled=False):
    """四个你头上的灯：小铜铃（2.70、5.10、8.2 倍）。粉衣那盏像隔着布敲：泛音闷掉、短，带一下 300 Hz 的闷响。"""
    n = int(2.0 * SR)
    f0 *= jit(rng, 4)
    if not muffled:
        parts = [(f0, 1.0, 0.95), (f0 + rng.uniform(1, 2.5), 0.3, 0.9), (2.70 * f0, 0.45, 0.3), (5.10 * f0, 0.2, 0.09),
                 (8.2 * f0, 0.08, 0.03)]
        y = norm(modal(n, parts, rng)) + 0.28 * norm(contact(n, rng, 2500, 11000, 0.0015))
    else:
        parts = [(f0, 1.0, 0.22), (2.70 * f0, 0.12, 0.05), (5.1 * f0, 0.03, 0.015)]
        y = (norm(modal(n, parts, rng)) + 0.35 * norm(modal(n, [(f0 * 0.31, 1, 0.035), (f0 * 0.62, 0.4, 0.02)], rng))
             + 0.15 * norm(contact(n, rng, 500, 2500, 0.004)))
    return norm(fades(y))


def g_tick(rng, f0=2300.0, heavy=0.0, fine=False):
    """计数的“嗒”：小木块，模态 1、1.52、2.31 倍，十几毫秒就没了。heavy>0 时多一层低一点、厚一点的“嗒”。
    这个不归一化：heavy 的大小要留在幅度里（轻的那层峰值约 1）。"""
    n = int(0.07 * SR)
    f0 *= jit(rng, 45)
    k = 0.6 if fine else 1.0
    y = norm(modal(n, [(f0, 1, 0.010 * k), (1.52 * f0, 0.45, 0.007 * k), (2.31 * f0, 0.25, 0.004 * k)], rng, att=0.0003))
    y = y + 0.55 * norm(contact(n, rng, 1500, 8000, 0.0012))
    if not fine:
        y = y + 0.2 * norm(modal(n, [(420 * jit(rng, 50), 1, 0.006)], rng))
    y = norm(y)
    if heavy > 0:
        h = (norm(modal(n, [(1150 * jit(rng, 40), 1, 0.024), (1840 * jit(rng, 40), 0.45, 0.013), (250, 0.5, 0.02)], rng))
             + 0.4 * norm(contact(n, rng, 700, 4000, 0.002)))
        y = y + heavy * 1.3 * norm(h)
    return fades(y)


def g_whoosh(rng, dur=0.24, f0=3200.0, f1=900.0, bw=1.3, tp=0.12, tail=0.05, floor=0.36, flutter=0.12):
    """嗖：带通噪声从 f0 扫到 f1。一起音就到峰值的 −9 dB（floor），tp 秒到峰值，之后按 tail 衰减；带一点气流的抖动。"""
    dur *= var(rng, 0.08)
    tp *= var(rng, 0.08)
    n = int(dur * SR)
    t = ts(n)
    fc = f0 * jit(rng, 60) * (f1 / f0) ** np.clip(t / dur, 0, 1)
    y = tv_noise(n, rng, fc, bw)
    e = np.where(t < tp, floor + (1 - floor) * (t / tp) ** 2, np.exp(-(t - tp) / tail))
    e *= np.clip(t / 0.003, 0, 1)
    am = 1 + flutter * norm(shape(rng.standard_normal(n), 8, 40))
    return norm(fades(y * e * am, 0, 0.01))


def g_pu(rng, size=1.0, low=0.9, knock=0.0, sat=1.5, kf=1500.0, kt=0.065):
    """闷“噗”：光点被一把拿走。一个从 270 Hz 掉到 100 Hz 的闷响 + 一口气（200–1500 Hz）+ 一点 1–2 kHz 的接触声，再轻轻饱和。
    knock>0 时（开场那一下）再叠一层指节敲木头（g_knock，1.5 kHz 上下，晚 6 毫秒），一起饱和：手机外放放不出闷响，
    靠这一层出冲击力；low 压到 0.8、饱和加到 2.0。成品里量：低频峰值只低 1 dB 上下，1–4 kHz 有效值高约 5 dB。
    第四版补改：S22 的抢（41.49 秒那一下）、方块合拢的闷响也用这一层（kf、kt 是敲击层的音高和衰减）。"""
    n = int(0.25 * SR)
    t = ts(n)
    fb = (100 + 170 * np.exp(-t / 0.014)) * jit(rng, 40) / size ** 0.25
    body = np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t / (0.045 * size)) * (1 - np.exp(-t / 0.0012))
    puff = noise(n, rng, 200, 1500, tilt=-0.5) * np.exp(-t / (0.022 * size)) * (1 - np.exp(-t / 0.0015))
    y = low * norm(body) + 0.6 * norm(puff) + 0.3 * norm(contact(n, rng, 900, 2400, 0.003))
    if knock:
        k = g_knock(rng, kf, kt)
        i = int(0.006 * SR)
        y[i:] += knock * k[: n - i]
    y = np.tanh(sat * y) / np.tanh(sat)
    return norm(fades(y))


def g_pa(rng, big=False):
    """清脆的“啪”：一颗硬珠子掉在地上。2–9 kHz 的接触声 + 3–7 kHz 的玻璃响 + 230 Hz 的一下地面，再弹两三下（越弹越轻、越快）。"""
    n = int(0.45 * SR)
    y = np.zeros(n)
    for d, a in ((0.0, 1.0), (0.046, 0.36), (0.079, 0.14), (0.101, 0.05)):
        d *= var(rng, 0.12)
        i = int(d * SR)
        m = n - i
        j = jit(rng, 30)
        hit = (norm(contact(m, rng, 1800, 9500, 0.0022))
               + 0.75 * norm(modal(m, [(3150 * j, 1, 0.045), (4870 * j, 0.6, 0.028), (7200 * j, 0.35, 0.014),
                                      (2300 * j, 0.45, 0.03)], rng, att=0.0002))
               + 0.5 * norm(modal(m, [(235 * jit(rng, 40), 1, 0.02 * (1.5 if big else 1)), (530, 0.4, 0.012)], rng)))
        y[i:] += a * hit
    if big:     # 第四版补改：S20 那一下再叠一层 2–3.5 kHz 的玻璃余响（衰减 70 毫秒），手机外放听得出“当”的一声
        j = jit(rng, 20)
        ring = norm(modal(n, [(2050 * j, 1, 0.07), (3280 * j, 0.6, 0.05), (2620 * j, 0.4, 0.06)], rng, att=0.0004))
        y = y / np.max(np.abs(y)) + 0.45 * ring
    y = np.tanh(1.3 * y / np.max(np.abs(y)))
    return norm(fades(y))


def g_kada(rng, scale=1.0):
    """换衣“咔哒”：按扣扣上。先一下高的“咔”（3.4 kHz），50–68 毫秒后一下低一点、厚一点的“哒”（1.45 kHz + 330 Hz）。"""
    n = int(0.22 * SR)
    j = jit(rng, 35) * scale
    ka = (norm(modal(n, [(3400 * j, 1, 0.006), (5150 * j, 0.6, 0.004), (2200 * j, 0.35, 0.005)], rng, att=0.0002))
          + 0.9 * norm(contact(n, rng, 2000, 9000, 0.0008)))
    j2 = jit(rng, 35) * scale
    da = (norm(modal(n, [(1450 * j2, 1, 0.013), (2320 * j2, 0.5, 0.008), (330 * j2, 0.6, 0.016)], rng, att=0.0003))
          + 0.6 * norm(contact(n, rng, 1000, 5000, 0.0015)))
    gap = int(rng.uniform(0.05, 0.068) * SR)
    y = 0.7 * norm(ka)
    y[gap:] += norm(da)[: n - gap]
    return norm(fades(y))


def g_zip(rng, dur):
    """衣服从上往下刷成新颜色：往上扫的布料声，带细碎的颗粒，越刷越响，接到最后的咔哒上。"""
    n = int(dur * SR)
    t = ts(n)
    y = tv_noise(n, rng, 1300 * (3400 / 1300) ** (t / dur), 1.5)
    imp = (rng.random(n) < 90 / SR) * rng.uniform(0.4, 1, n)
    gr = np.convolve(imp, np.exp(-np.arange(int(0.004 * SR)) / (0.0012 * SR)))[:n]
    e = (0.25 + 0.75 * (t / dur) ** 1.5) * np.clip((dur - t) / 0.02, 0, 1) * np.clip(t / 0.02, 0, 1)
    return norm(y * e * (0.45 + 0.55 * gr / (gr.max() + 1e-9)))


def g_shua(rng, dur=0.2, f0=1100.0, f1=3600.0, ring=None, tp=0.025, tail=0.05):
    """短“刷”：往上扫的带通噪声，起得快。ring 给一个中心频率时，叠一道窄带噪声，听得出音高（20 条历史条一声比一声高）。"""
    n = int(dur * SR)
    t = ts(n)
    y = tv_noise(n, rng, f0 * (f1 / f0) ** (t / dur), 1.4)
    if ring:
        y = y + 0.9 * tv_noise(n, rng, np.full(n, ring), 0.12)
    e = np.where(t < tp, 0.4 + 0.6 * t / tp, np.exp(-(t - tp) / tail)) * np.clip(t / 0.002, 0, 1)
    return norm(fades(y * e, 0, 0.006))


def g_gather(rng, span):
    """方块聚拢“唰”：带通噪声从 5.2 kHz 往 1.1 kHz 收，通带一路变窄、越来越响；聚成方块那一下收成一声闷响。
    第四版补改：闷响里叠一层“咔”地合上的敲击（2 kHz 上下、衰减 80 毫秒），手机外放靠它听见合拢。"""
    n = int((span + 0.35) * SR)
    t = ts(n)
    u = np.clip(t / span, 0, 1)
    y = tv_noise(n, rng, 5200 * (1100 / 5200) ** u, 2.4 + (1.0 - 2.4) * u)
    e = np.where(t < span, 0.12 + 0.88 * u ** 2.2, np.exp(-(t - span) / 0.05))
    e *= 1 - 0.6 * np.clip((t - (span - 0.04)) / 0.03, 0, 1) * (t < span + 0.01)     # 落地前收一下
    y = norm(y * e * np.clip(t / 0.005, 0, 1))
    th = g_pu(rng, 1.3, low=0.8, knock=1.9, sat=2.0, kf=2000, kt=0.08)
    i = int(span * SR)
    y[i:i + len(th)] += 1.2 * th[: n - i]
    return norm(fades(y))


def g_rewind(rng, span=0.3):
    """倒带：磁带倒转的尖声，音高越倒越高（850→2700 Hz），带 38 Hz 的哒哒抖动和带子的嘶声；停下时一下“咔”。"""
    n = int((span + 0.07) * SR)
    t = ts(n)
    u = np.clip(t / span, 0, 1)
    f = 850 * (2700 / 850) ** (u ** 1.3)
    wob = 1 + 0.035 * norm(shape(rng.standard_normal(n), 15, 45))
    ph = 2 * np.pi * np.cumsum(f * wob) / SR
    tone = sum(np.sin(k * ph + rng.uniform(0, 6.28)) / k for k in range(1, 7))
    chatter = 0.55 + 0.45 * np.sin(2 * np.pi * 38 * t) ** 2
    y = (norm(tone) * chatter + 0.25 * noise(n, rng, 2000, 9000)) * np.clip(t / 0.002, 0, 1)
    y *= np.clip((span - 0.02 - t) / 0.005, 0, 1)        # 停带前 20 毫秒先断
    stop = norm(g_tick(rng, 1800, heavy=0.6))
    i = int(span * SR)
    y[i:i + len(stop)] += 1.2 * stop[: n - i]
    return norm(fades(y))


def g_woo(rng, span, gens):
    """快进的“呜”：嗒快到连成一片。音高 = 2 × 每秒代数（从 35 平滑升到约 133，0.12 秒），再随进度升 4 个半音；
    泛音按 1 kHz、2.3 kHz 两个共振峰加重（手机放得出）；里面的棘轮声按每一代跨过的时刻打；到头时音高一沉、收掉。"""
    n = int((span + 0.25) * SR)
    t = ts(n)
    rate1 = len(gens) / span
    rate = rate1 - (rate1 - 35.0) * np.exp(-t / 0.12)
    pr = np.clip(t / span, 0, 1)
    rel = t >= span
    f0 = 2 * rate * 2 ** (4 / 12 * pr)
    f0 = np.where(rel, f0 * (1 - 0.25 * np.clip((t - span) / 0.08, 0, 1)), f0)
    f0 = f0 * (1 + 0.006 * norm(shape(rng.standard_normal(n), 3, 12)))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    tone = np.zeros(n)
    for k in range(1, 30):
        fk = k * f0
        a = (1 / k ** 0.8) * (0.35 + np.exp(-0.5 * (np.log2(fk / 1000) / 0.6) ** 2) + 0.7 * np.exp(-0.5 * (np.log2(fk / 2300) / 0.5) ** 2))
        tone += np.where(fk < 9000, a, 0) * np.sin(k * ph + rng.uniform(0, 6.28))
    wind = tv_noise(n, rng, 900 * (3200 / 900) ** pr, 1.1)
    ratchet = np.zeros(n)
    for gt in gens:
        s = g_tick(rng, 2600, fine=True)
        i = int(gt * SR)
        ratchet[i:i + len(s)] += s[: n - i]
    env = np.clip(t / 0.18, 0, 1) ** 1.5 * (0.85 + 0.15 * pr) * np.where(rel, np.exp(-(t - span) / 0.03), 1)
    rat_env = np.where(rel, np.exp(-(t - span) / 0.01), 1) * (0.6 - 0.35 * np.clip(t / 0.4, 0, 1))
    y = norm(tone) * env + 0.35 * norm(wind) * env + 0.5 * norm(ratchet) * rat_env
    return norm(fades(y))


def g_dong(rng):
    """“和你”那一下的闷“咚”：毡槌敲木箱。104 Hz 的箱体（起音时音高略高、往下沉），饱和一下带出 200–600 Hz 的谐波；
    再叠一下 1–2 kHz 的敲击声（1250、1850 Hz 两个木头模态 + 接触噪声），手机外放靠它听见。
    第四版：再叠一层木头敲击（g_knock，1.55 kHz 上下，晚 12 毫秒，听着还是一下），箱板中频（手机放得出）加重、拖长一点，
    低频尾巴从 0.26 秒收到 0.17 秒，整体再饱和一下压峰值。成品里量：低频峰值比原来低约 2 dB，1–4 kHz 有效值高约 5 dB，
    250 Hz 以下的能量从约 66% 降到约 27%。"""
    n = int(1.4 * SR)
    t = ts(n)
    ph = 2 * np.pi * np.cumsum(104 * (1 + 0.22 * np.exp(-t / 0.03))) / SR
    btau = 0.17
    body = (np.sin(ph) * np.exp(-t / btau) + 0.45 * np.sin(2.13 * ph + 1) * np.exp(-t / (btau * 0.42))
            + 0.2 * np.sin(3.36 * ph + 2) * np.exp(-t / (btau * 0.19))) * (1 - np.exp(-t / 0.002))
    body = np.tanh(2.2 * body) / np.tanh(2.2)
    box = modal(n, [(520, 1, 0.112), (760, 0.6, 0.072), (430, 0.5, 0.128)], rng, att=0.001)    # 箱板的中频（手机放得出）
    knock = (norm(modal(n, [(1250, 1, 0.063), (1850, 0.7, 0.045), (2650, 0.3, 0.02), (980, 0.5, 0.056)], rng, att=0.0004))
             + 0.5 * norm(contact(n, rng, 800, 3200, 0.005)))
    y = 0.6 * norm(body) + 1.5 * norm(box) + 2.0 * norm(knock)
    k2 = g_knock(rng, 1550, 0.06)                     # 叠上去的那一层敲击
    i = int(0.012 * SR)
    y[i:i + len(k2)] += 2.6 * k2[: n - i]
    y = norm(y)
    y = np.tanh(1.8 * y) / np.tanh(1.8)
    return norm(fades(y))


def g_knock(rng, f0=1450.0, tau=0.055):
    """指节敲木头：主模态 f0（1–3 kHz）、1.58 倍、2.31 倍，再加一个 0.55 倍的“木头身子”（800 Hz 上下，手机也放得出）
    和一下 1–4.5 kHz 的接触噪声。几十毫秒就没了。开场的“噗”和“和你”的“咚”上面各叠一下，手机外放靠它出冲击力。"""
    n = int(0.3 * SR)
    f0 *= jit(rng, 25)
    y = norm(modal(n, [(f0, 1, tau), (1.58 * f0, 0.55, 0.6 * tau), (2.31 * f0, 0.3, 0.35 * tau), (0.55 * f0, 0.45, 0.75 * tau)],
                   rng, att=0.00025))
    y = y + 0.7 * norm(contact(n, rng, 1000, 4500, 0.003))
    return norm(fades(y))


def g_converge(rng, span):
    """“收拢”：20 条历史条往中间收成一条。两道带通噪声，一道从 4.8 kHz 往下、一道从 900 Hz 往上，在 1.8 kHz 碰头；
    通带一路变窄、越收越响，碰头那一下 25 毫秒收掉（接上那声“叮”）。"""
    n = int((span + 0.12) * SR)
    t = ts(n)
    u = np.clip(t / span, 0, 1)
    k = u ** 1.4
    bw = 1.3 + (0.35 - 1.3) * u
    hi = tv_noise(n, rng, 4800 * (1800 / 4800) ** k, bw)
    lo = tv_noise(n, rng, 900 * (1800 / 900) ** k, bw)
    e = np.where(t < span, 0.22 + 0.78 * u ** 1.8, np.exp(-(t - span) / 0.025)) * np.clip(t / 0.004, 0, 1)
    return norm(fades((0.8 * hi + lo) * e, 0, 0.01))


def g_pushin(rng, span):
    """从远景推到近景：很轻的往里收的“嗖”。带通噪声从 1.1 kHz 往 3 kHz 走、通带收窄，越推越近、越响，推到那一下 40 毫秒收掉。"""
    n = int((span + 0.15) * SR)
    t = ts(n)
    u = np.clip(t / span, 0, 1)
    y = tv_noise(n, rng, 1100 * (3000 / 1100) ** u, 1.8 + (0.9 - 1.8) * u)
    e = np.where(t < span, 0.12 + 0.88 * u ** 1.6, np.exp(-(t - span) / 0.04)) * np.clip(t / 0.01, 0, 1)
    am = 1 + 0.1 * norm(shape(rng.standard_normal(n), 8, 40))
    return norm(fades(y * e * am, 0, 0.01))


def g_pad(rng, full, hold, end):
    """“你只有一遍”的暖音：G 大调和弦（PAD_NOTES），每个音三条略微走音的声部（±3 音分，听着发暖、会动），
    每个声部 1–8 次谐波，按 1/k 递减，再在 1–2 kHz 加一个宽的共振峰（手机外放靠这一段听见），5 kHz 以上不要。
    包络：0.3 秒慢起到七成，full 秒（dive 结束）到最满；高次谐波起得更慢（像光慢慢亮起来）；挂到 hold 秒，hold→end 淡掉。
    250 Hz 以下没有音（最低是 G4 392 Hz），不要重低音。"""
    n = int((end + 0.05) * SR)
    t = ts(n)
    rise = 0.7 * (1 - np.exp(-t / 0.3 * 2.3)) + 0.3 * np.clip((t - 0.15) / max(0.05, full - 0.15), 0, 1) ** 1.5
    fall = np.where(t < hold, 1.0, np.cos(0.5 * np.pi * np.clip((t - hold) / (end - hold), 0, 1)) ** 2)
    env = np.minimum(rise, 1.0) * fall
    breathe = 1 + 0.06 * norm(shape(rng.standard_normal(n), 0.2, 0.8, order=1))
    y = np.zeros(n)
    for f0, g in zip(PAD_NOTES, PAD_GAINS):
        for cents in (-3.0, 0.0, 3.0):
            fv = f0 * 2 ** ((cents + rng.normal(0, 1.0)) / 1200)
            vib = 1 + 0.0012 * np.sin(2 * np.pi * rng.uniform(4.2, 5.2) * t + rng.uniform(0, 6.28)) * np.clip((t - 0.4) / 0.6, 0, 1)
            ph = 2 * np.pi * np.cumsum(fv * vib) / SR
            lfo = 1 + 0.07 * np.sin(2 * np.pi * rng.uniform(0.25, 0.6) * t + rng.uniform(0, 6.28))
            for k in range(1, 9):
                fk = k * fv
                if fk > 5000:
                    break
                a = (1 / k) * (0.4 + 1.1 * math.exp(-0.5 * (math.log2(fk / 1450) / 0.6) ** 2))
                bloom = env ** (1 + 0.35 * (k - 1))          # 高次谐波起得慢，越亮越满
                y += g * a * bloom * lfo * np.sin(k * ph + rng.uniform(0, 6.28))
    y = shape(y, 300, 5500, order=2) * breathe
    y *= np.clip(t / 0.02, 0, 1)
    return norm(fades(y, 0.002, 0.05))


def g_pok(rng, f0=1300.0):
    """乒乓：手到了那一下的“啵”，短、空心（f0、1.83 倍、0.52 倍三个模态）。"""
    n = int(0.12 * SR)
    j = jit(rng, 20)
    y = (norm(modal(n, [(f0 * j, 1, 0.018), (f0 * j * 1.83, 0.4, 0.009), (f0 * j * 0.52, 0.5, 0.02)], rng, att=0.0003))
         + 0.6 * norm(contact(n, rng, 1200, 6000, 0.0012)))
    return norm(fades(y))


def g_grain(rng):
    """细“噗”：远景里一个点变色。一小口气 + 一下很轻的低响，几十毫秒。"""
    n = int(0.05 * SR)
    t = ts(n)
    y = noise(n, rng, 300, 1600, tilt=-0.5) * np.exp(-t / 0.008) * (1 - np.exp(-t / 0.0008))
    fb = 260 * jit(rng, 80) * (1 + np.exp(-t / 0.005))
    y = norm(y) + 0.5 * norm(np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t / 0.012))
    return norm(fades(y))


def g_bubble(rng, f0=1000.0):
    """“啵”：点在眨眼。小气泡的声音本来就是一个往上滑的短音，几十毫秒。"""
    n = int(0.05 * SR)
    t = ts(n)
    f = f0 * jit(rng, 150) * (1 + 0.6 * t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.011) * (1 - np.exp(-t / 0.0015))
    y = norm(y) + 0.15 * norm(contact(n, rng, 1500, 6000, 0.001))
    return norm(fades(y))


def g_pluck(rng, f0=523.0):
    """白圈跳一下：一下软的拨弦（谐波按 1/k 递减，高的衰减快）。"""
    n = int(0.6 * SR)
    f0 *= jit(rng, 8)
    y = modal(n, [(k * f0 * (1 + 0.0007 * k * k), 1 / k, 0.28 / k ** 0.7) for k in range(1, 9)], rng, att=0.001)
    y = norm(y) + 0.1 * norm(contact(n, rng, 800, 4000, 0.002))
    return norm(fades(y))


def g_rustle(rng, dur=0.35):
    """布料：800–6500 Hz 的噪声乘上细碎的颗粒。抱胳膊、转身用。"""
    n = int(dur * SR)
    t = ts(n)
    base = noise(n, rng, 800, 6500, tilt=-0.3)
    imp = (rng.random(n) < 140 / SR) * rng.uniform(0.2, 1, n)
    gr = np.convolve(imp, np.exp(-np.arange(int(0.006 * SR)) / (0.0015 * SR)))[:n]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return norm(fades(base * (0.35 + gr / (gr.max() + 1e-9)) * e))


def g_sigh(rng, dur=0.7):
    """松一口气：气声，带 650、1150、2500 Hz 三个共振峰。"""
    n = int(dur * SR)
    t = ts(n)
    y = noise(n, rng, 250, 3500, tilt=-0.8, peaks=((650, 3, 9), (1150, 4, 6), (2500, 5, 4)))
    e = np.where(t < 0.12, (t / 0.12) ** 1.5, np.exp(-(t - 0.12) / 0.22))
    return norm(fades(y * e))


def g_walk(rng, span):
    """一个点从那一排走下来变成人：往下扫的轻风声，走到时一下轻脚步（190 Hz + 1.1 kHz）。
    第四版补改：脚步上叠一下鞋跟踩木地板的清脆声（g_click，2 kHz 上下、衰减 45 毫秒），手机外放靠它听见这一步。"""
    n = int((span + 0.2) * SR)
    w = g_whoosh(rng, dur=span + 0.05, f0=2200, f1=700, bw=1.4, tp=span * 0.6, tail=0.08, floor=0.15, flutter=0.1)
    y = np.zeros(n)
    y[:len(w)] += 0.6 * w[:n]
    m = int(0.12 * SR)
    st = norm(modal(m, [(190 * jit(rng, 40), 1, 0.025), (1100 * jit(rng, 40), 0.35, 0.008)], rng)) + 0.3 * norm(contact(m, rng, 600, 3000, 0.003))
    st = norm(st) + 0.7 * g_click(rng, 2000, 0.045)[:m]
    i = int(span * SR)
    y[i:i + m] += norm(st)[: n - i]
    return norm(fades(y))


def g_click(rng, f0=2000.0, tau=0.045, n_s=0.12):
    """清脆的一下“咔”：硬东西碰木头。f0（1.5–4 kHz）、1.47 倍、0.62 倍三个模态 + 1.5–7 kHz 的接触噪声。"""
    n = int(n_s * SR)
    f0 *= jit(rng, 30)
    y = norm(modal(n, [(f0, 1, tau), (1.47 * f0, 0.5, 0.6 * tau), (0.62 * f0, 0.55, 0.8 * tau)], rng, att=0.0002))
    y = y + 0.6 * norm(contact(n, rng, 1500, 7000, 0.0015))
    return norm(fades(y, 0.0002, 0.005))


def g_clock(rng, tock=False):
    """钟表的“嘀”“嗒”：擒纵机构的金属小撞击。嘀高（3.6 kHz 一带）、嗒低一点（2.5 kHz 一带），十几毫秒，带一点壳子的余响。"""
    n = int(0.12 * SR)
    f0 = (2500.0 if tock else 3600.0) * jit(rng, 20)
    y = norm(modal(n, [(f0, 1, 0.012), (1.53 * f0, 0.5, 0.007), (0.71 * f0, 0.4, 0.02)], rng, att=0.0002))
    y = y + 0.5 * norm(contact(n, rng, 2000, 9000, 0.0008))
    return norm(fades(y, 0.0002, 0.005))


def g_ghost(rng, dur=1.6):
    """影子你：两道很窄的带通噪声（E6、B6）加一点空气声，慢起慢落，像一段记忆。"""
    n = int(dur * SR)
    t = ts(n)
    y = (tv_noise(n, rng, 1318.5, 0.06) + 0.6 * tv_noise(n, rng, 1975.5, 0.06) + 0.5 * noise(n, rng, 3000, 9000))
    e = (1 - np.exp(-t / 0.3)) * np.clip((dur - t) / 0.6, 0, 1)
    return norm(fades(y * e))


def tail_fade(y, end_s, fade_s):
    """在 end_s 秒（从声音开头算）之前 fade_s 秒起按 cos² 淡掉，end_s 以后截掉。"""
    n = min(len(y), int(end_s * SR))
    t = ts(n)
    g = np.cos(0.5 * np.pi * np.clip((t - (end_s - fade_s)) / fade_s, 0, 1)) ** 2
    return y[:n] * g


def _mixin(y, s, i=0, g=1.0):
    """把 s 从第 i 个采样起加进 y（超出 y 的部分丢掉）。"""
    m = min(len(s), len(y) - i)
    if m > 0:
        y[i:i + m] += g * s[:m]
    return y


def g_route(rng, f0, muffled=False, soft=False):
    """路线图往前走一格的小铃：和四盏灯（g_lamp）同一个小铜铃（2.70、5.10、8.2 倍），小一号：主音 0.45 秒衰减，接触声亮一点。
    muffled（狠那一格）：没有 5.1 倍以上的亮泛音，0.16 秒就没了，带一下隔着布的“笃”（1.6 kHz 上下的短敲击）和 300 Hz 的闷响——
    听着发闷，手机外放靠那一下“笃”听见。soft（路线图淡入、ask 的两声）：软槌，接触声小、衰减短一半。"""
    n = int(1.0 * SR)
    f0 *= jit(rng, 4)
    if muffled:
        y = norm(modal(n, [(f0, 1.0, 0.16), (2.70 * f0, 0.22, 0.04)], rng))
        y = y + 0.4 * norm(modal(n, [(f0 * 0.31, 1, 0.03), (f0 * 0.62, 0.4, 0.02)], rng))
        y = _mixin(y, g_knock(rng, 1700, 0.04), 0, 1.1)
        return norm(fades(y))
    k = 0.5 if soft else 1.0
    parts = [(f0, 1.0, 0.45 * k), (f0 + rng.uniform(1, 2.5), 0.25, 0.42 * k), (2.70 * f0, 0.5, 0.14 * k),
             (5.10 * f0, 0.22, 0.045 * k), (8.2 * f0, 0.06, 0.015 * k)]
    y = norm(modal(n, parts, rng, att=0.002 if soft else 0.0006))
    y = y + (0.08 if soft else 0.3) * norm(contact(n, rng, 2500, 11000, 0.0012))
    return norm(fades(y))


def g_ask(rng, gap=0.1):
    """ask：路线图后两格的“？”一起跳一下。两声轻的软槌小铃往上挑（D6 → G6，就是后面“有来有往”“原谅”两格的音），像问句的尾音往上走。"""
    a = g_route(rng, ROUTE_NOTES[2], soft=True)
    b = g_route(rng, ROUTE_NOTES[3], soft=True)
    y = np.zeros(int(gap * SR) + len(b))
    _mixin(y, a, 0, 0.8)
    _mixin(y, b, int(gap * SR), 1.0)
    return norm(y)


def g_youred(rng):
    """你那颗点变红（“你也是”）：一下按扣似的“咔哒”（和换衣同一类声音，音高压低一点）＋一下指节敲击（1.3 kHz 上下），
    听着是“嗒”地一下定了。1–4 kHz 都有（手机外放靠它）。"""
    y = norm(g_kada(rng, 0.82))
    y = _mixin(np.concatenate([y, np.zeros(int(0.1 * SR))]), g_knock(rng, 1300, 0.05), int(0.004 * SR), 0.9)
    y = np.tanh(1.4 * norm(y)) / np.tanh(1.4)
    return norm(fades(y))


def g_gasp(rng, dur=0.15):
    """back：很短的倒吸一口气。气声（带 700、1300、2600 Hz 三个共振峰，往上走一点），从起点很快涨起来，最后 15 毫秒收住，
    包络是倒着的（像倒放），和倒带同一帧起。"""
    n = int(dur * SR)
    t = ts(n)
    y = tv_noise(n, rng, 1300 * (1 + 0.35 * t / dur), 1.6)
    y = y + 0.5 * noise(n, rng, 500, 4000, tilt=-0.5, peaks=((700, 3, 6), (2600, 5, 4)))
    e = (0.25 + 0.75 * (t / dur) ** 1.6) * np.clip((dur - t) / 0.015, 0, 1) * np.clip(t / 0.006, 0, 1)
    return norm(fades(y * e, 0, 0.004))


def g_thread(rng, f0=2600.0, dur=0.17):
    """S15 一根粉线连到一个人：很细的一声“嗞”（窄带噪声从 0.8 f0 滑到 f0，像线一下绷紧），连到那一下带一点小接触声。
    起音放在开头（线开始连），尾巴是连到的那一下。"""
    n = int((dur + 0.06) * SR)
    t = ts(n)
    u = np.clip(t / dur, 0, 1)
    y = tv_noise(n, rng, f0 * (0.8 + 0.2 * u), 0.25)
    e = (0.35 + 0.65 * u ** 1.5) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.012)) * np.clip(t / 0.004, 0, 1)
    y = norm(y * e)
    tick = np.zeros(n)
    _mixin(tick, contact(int(0.05 * SR), rng, 2500, 9000, 0.0012), int(dur * SR))
    return norm(fades(y + 0.5 * norm(tick), 0, 0.005))


def g_unease(rng, inten):
    """第七版 S26 run：越来越不安的一层。inten 是逐样本的紧张度（0–1）：带通噪声的中心从 700 Hz 往 1.5 kHz 走、通带收窄，
    上面一层颤动（每秒 7 → 16 下，越紧越快、越深），底下一层 90–320 Hz 的闷响跟着紧张度起来。没有固定的拍子，不像在数数。"""
    n = len(inten)
    fc = 700 * (1500 / 700) ** inten
    bw = 1.6 - 1.0 * inten
    y = tv_noise(n, rng, fc, bw)
    rate = 7 + 9 * inten
    ph = 2 * np.pi * np.cumsum(rate) / SR
    am = 1 - (0.25 + 0.4 * inten) * (0.5 + 0.5 * np.sin(ph))
    low = noise(n, rng, 90, 320, order=2)
    y = norm(y) * am * (0.12 + 0.88 * inten) + 0.45 * norm(low) * inten ** 1.5
    return norm(fades(y, 0.02, 0.05))


def g_dark(rng):
    """第七版 S26 back（狠人回到三成）：发暗的重击。72 Hz 的闷响（起音时高一点、往下沉），饱和一下；310–560 Hz 的暗箱板；
    再叠一下 1.15 kHz 上下的指节敲木头（晚 8 毫秒，听着是一下），手机外放靠它——比 S15 的“咚”暗（那下敲击在 1.25–1.85 kHz）。"""
    n = int(1.2 * SR)
    t = ts(n)
    ph = 2 * np.pi * np.cumsum(72 * (1 + 0.3 * np.exp(-t / 0.025))) / SR
    body = (np.sin(ph) * np.exp(-t / 0.22) + 0.4 * np.sin(2.1 * ph + 1) * np.exp(-t / 0.09)) * (1 - np.exp(-t / 0.002))
    body = np.tanh(2.5 * body) / np.tanh(2.5)
    box = modal(n, [(310, 1, 0.09), (415, 0.6, 0.07), (560, 0.35, 0.05)], rng, att=0.001)
    y = 0.8 * norm(body) + 1.2 * norm(box) + 0.4 * norm(contact(n, rng, 600, 2500, 0.004))
    _mixin(y, g_knock(rng, 1150, 0.05), int(0.008 * SR), 1.6)
    y = np.tanh(1.6 * norm(y)) / np.tanh(1.6)
    return norm(fades(y))


# ======================================================================
# 排事件
# ======================================================================
EVENTS = []
# 自查时每类声音看哪个频段的包络（都在手机外放放得出的 300 Hz 以上）
BAND = {'叮': (700, 9000), '我叮': (700, 9000), '暖叮': (500, 6000), '上扬叮': (700, 9000), '灯叮': (500, 9000),
        '嗖': (500, 7000), '噗': (300, 2500), '啪': (1500, 10000), '咚': (800, 2600), '嗒': (1000, 9000),
        '咔哒': (1000, 9000), '刷': (600, 8000), '倒带': (600, 8000), '扎进去': (500, 7000), '唰收拢': (300, 2500),
        '啵': (700, 5000), '脚步': (600, 3000), '白圈': (400, 5000), '收拢': (900, 5000),
        '推近': (900, 4000), '嘀嗒': (1500, 9000), '闷叮': (500, 6000),
        '路线叮': (600, 9000), '你变红': (1000, 9000), '问': (900, 9000), '倒吸': (900, 4000), '嗞': (1500, 9000),
        '退': (400, 4000), '重击': (800, 2600)}


def put(beat, kind, vis, sound, gain, cat='mid', lead=0.0, anchor=0.0, check=True, label='', send=None, pan=0.0):
    """vis：画面事件的帧（可以带小数）；lead：音效比画面早多少秒（负数）；anchor：声音里“起音”离声音开头多少秒。
    放置位置 = vis/FPS + lead − anchor。cat：key（关键）/ mid / tick（计数）/ tex（细碎的一层）/ solo（全停时单独响的）。"""
    EVENTS.append(dict(beat=beat, kind=kind, vis=float(vis), lead=lead, anchor=anchor, sound=sound, gain=gain, cat=cat,
                       check=check, label=label or kind, send=send, pan=pan))


def grab(beat, t, d, toward_you, gw=-7.0, gp=-10.0, tail=0.04, label='抢', nxt=None, crisp=False):
    """抢：嗖比伸手早 0.1 秒，峰值落在碰到光点前 30 毫秒（手最快的时候）；碰到时一声“噗”，从嗖的尾巴里露出来。
    crisp：噗里叠一层指节敲击（第四版补改，S22 用：最后一下后面没有嗖盖着，手机上要靠它）。"""
    hit = t + 0.45 * d
    tp = max(0.07, min(0.24, hit / FPS - (t / FPS - 0.1) - 0.03))
    dur = tp + 3.5 * tail
    if nxt is not None:            # 连着抢：嗖不长过到下一次抢的间隔，免得糊成一片
        room = (nxt - t) / FPS - 0.01
        tp, dur = min(tp, 0.7 * room), min(dur, room)
    f0, f1 = (3400, 950) if toward_you else (950, 3400)
    put(beat, '嗖', t, lambda r, tp=tp, f0=f0, f1=f1, dur=dur: g_whoosh(r, dur=dur, f0=f0, f1=f1, tp=tp, tail=tail, floor=0.5), gw,
        cat='key', lead=-0.1, label=label + ('（他→你）' if toward_you else '（你→他）'))
    put(beat, '噗', hit, (lambda r: g_pu(r, 0.7, low=0.8, knock=1.3, sat=2.0)) if crisp else (lambda r: g_pu(r, 0.7)), gp,
        cat='mid', label='拿走')


def give(beat, arrive, f0, gain=-13.0, label='递', dull=False):
    put(beat, '叮', arrive, lambda r: g_ding(r, f0, dull=dull), gain, label=label)


def slip(beat, start, land, gain=-1.0, cat='key', big=False, slide=True):
    if slide:
        put(beat, '滑', start, lambda r: g_whoosh(r, dur=0.18, f0=2600, f1=4200, tp=0.06, tail=0.05, floor=0.2), -25,
            cat='tex', check=False)
    put(beat, '啪', land, lambda r: g_pa(r, big), gain, cat=cat, label='手滑落地')


def whoosh_tex(beat, f, gain, dur, f0, f1, tp, tail, label):
    put(beat, '嗖', f, lambda r: g_whoosh(r, dur=dur, f0=f0, f1=f1, tp=tp, tail=tail, floor=0.12), gain, cat='tex',
        check=False, label=label)


def visible_mid_cells():
    """S11 中景里看得见的格子（MID 镜头：对着你，放大 100/22 倍，舞台 y 200–820）。"""
    cols = D['grid']['cols']
    you = D['grid']['youCell']
    wx, wy = (you % cols) * 30, (you // cols) * 30
    z = 100 / 22
    r = 11 * z
    out = []
    for c in range(cols * D['grid']['rows']):
        x = 900 + ((c % cols) * 30 - wx) * z
        y = 510 + ((c // cols) * 30 - wy) * z
        if 120 - 2 * r <= x <= 1680 + 2 * r and 200 - 2 * r <= y <= 820 + 2 * r:
            out.append(c)
    return out


def plan():
    EVENTS.clear()
    rng = np.random.default_rng(SEED)
    you = D['you']
    grid = D['grid']['s']

    # —— S01 0.0–1.6：骗子伸手，0.4 秒一声“嗖”（比抢早 0.1 秒），0.5 秒光点被拿走一声闷“噗”，同一下叠一声指节敲木头
    #    （手机外放放不出噗的低频，靠这一下出冲击力）；转身时一点布料声 ——
    g0 = E('S01', 'grab')[0]
    put('S01', '嗖', g0, lambda r: g_whoosh(r, dur=0.42, f0=3400, f1=800, tp=0.07, tail=0.09, floor=0.5), -4, cat='key', lead=-0.1,
        label='抢（他→你）')
    put('S01', '噗', g0, lambda r: g_pu(r, 1.0, low=0.8, knock=1.3, sat=2.0), -3, cat='key', label='光点被拿走（叠敲击）')
    put('S01', '布料', E('S01', 'turnAway')[0], lambda r: g_rustle(r, 0.33), -27, cat='tex', check=False)

    # —— S02 1.6–3.8：白点“叮”；拉远时铺开一层密的细“啵”（点在眨眼）；白圈跳一下 ——
    put('S02', '我叮', B['S02']['f0'], lambda r: g_me(r), -9, label='白点（我）', send={'hall': 0.25})
    z0, z1 = E('S02', 'zoomOut')
    whoosh_tex('S02', z0, -25, 1.6, 600, 2400, 0.55, 0.5, '拉远')
    for k in range(400):            # 啵：点越来越多、越来越小（音高往上走），眼睛看不见了（z<2，约 2.6 秒）就停
        f = z0 + rng.uniform(0, 1) ** 0.7 * (31)
        u = (f - z0) / 31
        if rng.random() > 0.15 + 0.85 * u or k > 160:
            continue
        put('S02', '啵', f, lambda r, u=u: g_bubble(r, 800 + 900 * u), -27 - 3 * u + rng.uniform(-4, 0), cat='tex',
            check=False, pan=rng.uniform(-0.5, 0.5))
    put('S02', '白圈', E('S02', 'ringPulse'), lambda r: g_pluck(r, 523.25), -17, label='白圈跳一下')

    # —— S03 3.8–6.4：点阵第 0→70 代，开局那 500 个老实人一片黄变成一片红（细碎“嗒”见 flecks()，没有计数器了）；
    #    5.6 秒第二行“你也是”（不配声）→ youRed（5.75 秒）你那颗点变红：key，一下“咔哒”叠敲击 → 路线图“狠”（6.05 秒起翻）的闷铃
    #    在 route_sfx() 里，三下错开（时间表 10/29 晚改的） ——
    put('S03', '你变红', E('S03', 'youRed'), lambda r: g_youred(r), -4, cat='key', label='你变红（你也是）', send={'hall': 0.12})

    # —— S04 6.4–7.8：停在第 70 代（第五版不再快进到 300：“呜”和“跑到 300 的叮”都删了）；ask 见 route_sfx() ——

    # —— S05 7.8–8.4：倒带第 70 代 → 第 0 代（7.8–8.1）；扎进你的点 ——
    put('S05', '倒带', E('S05', 'rewind')[0], lambda r: g_rewind(r, (E('S05', 'rewind')[1] - E('S05', 'rewind')[0]) / FPS), -9,
        label='倒带 70→0')
    put('S05', '扎进去', E('S05', 'dive')[0], lambda r: g_whoosh(r, dur=0.36, f0=2600, f1=650, tp=0.2, tail=0.06, floor=0.45), -12,
        label='扎进你的点')

    # —— S06 8.5–9.3：给那一排 10 个人挨个递光点（到手那一下“叮”，从左到右一个比一个高；递给骗子那颗闷）。
    #    第四版画面把这一排固定成第 4 代碰到的 10 个人（FNear.tsx 的 you[4].opp），谁是骗子按这一排判，不再每代换人 ——
    gg0, gg1 = E('S06', 'gives')
    steps = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21]
    row = you[4]['opp']
    for i in range(10):
        t = int(math.floor(gg0 + (gg1 - 8 - gg0) * i / 9 + 0.5))
        s = row[i]
        give('S06', t + 7, 784 * 2 ** (steps[i] / 12), -14, label='递' + ('（骗子）' if s == ALLD else ''), dull=(s == ALLD))

    # —— S07 9.3–10.5：4 只橙红的手抢光点：“嗖”×4，各比画面早 0.1 秒 ——
    gs = E('S07', 'grabs')
    for k, t in enumerate(gs):
        grab('S07', t, 9, True, gw=-7, nxt=gs[k + 1] if k + 1 < len(gs) else None)

    # —— S08：特写你的手连着递 20 次（一串很轻的小叮），第 14 次那颗滑掉落地：清脆一声“啪”。
    #    第七版追加（10/30，照 FNear.tsx 的 giveAt / SLIP_AT）：拍缩到 0.9 秒后落地闪光露不出来，画面把滑掉那颗提前到 s08_slip_at() 出手、
    #    下落 7 帧，前 13 颗均匀排在 gives 起点到它之间，后 6 颗排在它到 gives 终点之间 ——
    si = E('S08', 'slipIndex')
    for i in range(20):
        t = s08_give_at(i)
        if i == si:
            slip('S08', t, t + S08_FALL)
        else:
            put('S08', '叮', t, lambda r: g_ding(r, 2093 * jit(r, 30), bright=0.6, decay=0.35), -25, cat='tex', check=False)

    # —— S09 12.1–14.8：粉点走下来；你递他递；你手滑“啪”；他抱胳膊；之后连串“嗖” ——
    w0, w1 = E('S09', 'walkDown')
    put('S09', '脚步', w1, lambda r, s=(w1 - w0) / FPS: g_walk(r, s), -19.5, anchor=(w1 - w0) / FPS, label='走下来')
    give('S09', E('S09', 'giveOk') + 7, 1568, -13)
    give('S09', E('S09', 'giveOk') + 6 + 7, 1318.5, -16, label='递回来')
    slip('S09', E('S09', 'slip'), E('S09', 'slip') + 9.6)
    put('S09', '布料', E('S09', 'crossArms')[0], lambda r: g_rustle(r, 0.32), -24, cat='tex', check=False)
    gs = E('S09', 'grabs')
    for k, t in enumerate(gs):
        grab('S09', t, 9, True, nxt=gs[k + 1] if k + 1 < len(gs) else None)

    # —— S10 14.7–16.8：两根条“刷”一声；衣服刷成狠的颜色，“咔哒”（recolor 开始那一帧路线图回到“狠”，见 route_sfx()） ——
    put('S10', '刷', E('S10', 'bars'), lambda r: g_shua(r, 0.22, 1100, 3600), -13, label='两根条')
    rc0, rc1 = E('S10', 'recolor')
    put('S10', '布料', rc0, lambda r, d=(rc1 - rc0) / FPS: g_zip(r, d), -23, cat='tex', check=False)
    put('S10', '咔哒', rc1, lambda r: g_kada(r), -9, label='换衣（狠）')

    # —— S11 16.8–18.9：拉到中景；代数 4→7 每跳一下，看得见的点里变色的那些各一下轻“咔哒”（第四版补改抬 3 dB；第五版计数“嗒”删了） ——
    whoosh_tex('S11', E('S11', 'zoom')[0], -24, 0.45, 2400, 900, 0.15, 0.1, '拉到中景')
    vis = visible_mid_cells()
    for f in gen_changes(B['S11']['f0'], B['S11']['f1']):
        g = GEN[f]
        ch = [c for c in vis if grid[g - 1][c] != grid[g][c]]
        for c in ch[:10]:
            put('S11', '咔哒', f + rng.uniform(0.5, 7.5), lambda r: g_kada(r, 1.25), -20 + rng.uniform(-3, 0), cat='tex',
                check=False, label='点变色')

    # —— S12 19.0–21.3：镜像 S09：他手滑“啪”，你抱胳膊、一直抢（“嗖”往上扫，从你这边出）；光点往你这边堆 ——
    give('S12', E('S12', 'giveOk') + 7, 1568, -13)
    give('S12', E('S12', 'giveOk') + 6 + 7, 1318.5, -16, label='递回来')
    slip('S12', E('S12', 'slip'), E('S12', 'slip') + 9.6)
    put('S12', '布料', E('S12', 'crossArms')[0], lambda r: g_rustle(r, 0.32), -24, cat='tex', check=False)
    gs = E('S12', 'grabs')
    for k, t in enumerate(gs):
        grab('S12', t, 9, False, nxt=gs[k + 1] if k + 1 < len(gs) else None)
        if t + 9 < E('S13', 'grow')[0] - 1:
            put('S12', '叮', t + 9, lambda r, k=k: g_ding(r, 2349 * 2 ** (2 * k / 12), bright=0.8, decay=0.3), -20,
                cat='tex', check=False, label='堆起来')

    # —— S13 21.2–22.8（第五版没有字幕）：你的条一路伸长、发亮：上扬的“叮——” ——
    put('S13', '上扬叮', E('S13', 'grow')[0], lambda r: g_rise(r), -7, cat='key', label='你的条伸长',
        send={'room': 0.2})

    # —— S14 22.9–25.05：远景，7→62 代快“嗒嗒”；黄点变色时细“噗”（每代变了几个按数据，换成每秒多少颗） ——
    whoosh_tex('S14', E('S14', 'zoom')[0], -24, 0.45, 900, 2400, 0.15, 0.12, '拉到远景')
    grains('S14', B['S14']['f0'], B['S14']['f1'], lambda g: sum(1 for c in range(1000) if grid[g - 1][c] == '0' and grid[g][c] != '0'), 32, rng)

    # —— S15 24.95–26.8（第五版没有字幕）：lines 起点全停；定住那一帧（你在一片红里、身上的红圈）一声闷“咚”，
    #    同一帧叠一下木头敲击（1.55 kHz 上下，手机外放靠它）。第五版补改：画面不再画连向被坑的人的线，那组细“嗞”删了 ——
    put('S15', '咚', E('S15', 'freeze')[0], lambda r: g_dong(r), 0, cat='solo', label='和你：咚（叠敲击）', send={'cold': 0.3})

    # —— S17 28.4–31.0：中近景，四周只有零星的“抢”：稀疏、远的“嗖”；影子你 ——
    p0 = E('S17', 'push')[0]
    for k in range(6):
        t = p0 + 8 + k * 15
        if t >= B['S17']['f1']:
            break
        put('S17', '嗖', t, lambda r: g_whoosh(r, dur=0.32, f0=2400, f1=900, tp=0.15, tail=0.07), -19, label='远处的抢',
            send={'cold': 0.35})
    gi0 = E('S17', 'ghostIn')[0]
    put('S17', '影子', gi0, lambda r, d=(E('S17', 'ghostOut')[1] - gi0) / FPS: g_ghost(r, d), -26, cat='tex', check=False)

    # —— S18 30.9–32.9（第五版没有字幕）＋S18b 32.9–34.6：一排变蓝（一层很轻的远处布料刷声）；蓝衣人走下来；你递他递；
    #    你抢他抢；条“刷”；换衣“咔哒”。转头、条、变蓝落在 S18b 里（事件还挂在 S18 名下，事件表 beat 写 S18b） ——
    rt0, rt1 = E('S18', 'rowTurn')
    put('S18', '布料', rt0, lambda r, d=(rt1 - rt0) / FPS: g_zip(r, d), -27, cat='tex', check=False, label='一排变蓝',
        send={'room': 0.3})
    w0, w1 = E('S18', 'walkDown')
    put('S18', '脚步', w1, lambda r, s=(w1 - w0) / FPS: g_walk(r, s), -19.5, anchor=(w1 - w0) / FPS, label='走下来')
    give('S18', E('S18', 'give') + 6, 1568, -13)
    give('S18', E('S18', 'giveBack') + 6, 1318.5, -16, label='递回来')
    grab('S18', E('S18', 'grab'), 7, False, gw=-7, nxt=E('S18', 'grabBack'))
    grab('S18', E('S18', 'grabBack'), 7, True, gw=-7)
    put('S18', '刷', E('S18', 'bars'), lambda r: g_shua(r, 0.22, 1100, 3600), -13, label='两根条')
    rc0, rc1 = E('S18', 'recolor')
    put('S18', '布料', rc0, lambda r, d=(rc1 - rc0) / FPS: g_zip(r, d), -23, cat='tex', check=False)
    put('S18', '咔哒', rc1, lambda r: g_kada(r), -9, label='换衣（有来有往）')

    # —— S19 34.6–37.0：近景硬切到远景，切的那一帧一声短“刷”（往下扫）；蓝色漫开“刷——”；狠的翻色“噗噗”；36.7 定住、全停 ——
    put('S19', '刷', B['S19']['f0'], lambda r: g_shua(r, 0.2, 4600, 1500, tp=0.012, tail=0.05), -12, label='硬切到远景',
        send={'hall': 0.12})
    whoosh_tex('S19', E('S19', 'zoom')[0], -24, 0.45, 900, 2400, 0.15, 0.12, '拉到远景')
    put('S19', '刷', E('S19', 'zoom')[1], lambda r: g_whoosh(r, dur=1.6, f0=700, f1=2600, tp=0.9, tail=0.25, floor=0.1,
                                                              flutter=0.25), -22, cat='tex', check=False, label='蓝色漫开')
    grains('S19', B['S19']['f0'], E('S19', 'freeze')[0], lambda g: sum(1 for c in range(1000) if int(grid[g - 1][c]) in HARSH and int(grid[g][c]) not in HARSH), 32, rng)

    # —— S20 36.2–37.4：远景推到近景（push），一声很轻的往里收的“嗖”（单独那一轨，比“啪”低 20 dB 以上）；先静，再单独一声“啪” ——
    pu0, pu1 = E('S20', 'push')
    put('S20', '推近', pu0, lambda r, s=(pu1 - pu0) / FPS: g_pushin(r, s), -20, cat='solo', check=False, label='推近（往里收）',
        send={'room': 0.15})
    s20 = E('S20', 'slip')
    put('S20', '啪', s20 + 9.6, lambda r: g_pa(r, big=True), 0, cat='solo', label='可手滑：啪', send={'room': 0.3, 'cold': 0.15})

    # —— S21 37.4–39.8：一道“抢”在两人之间来回，像打乒乓（单声道：靠音高和扫频方向分来回）。第四版去掉了那排 10 格，没有配声音 ——
    q0, q1 = E('S21', 'pong')
    per = T(0.4)
    leg = 0
    while q0 + per * leg < q1:
        s = q0 + per * leg
        mine = leg % 2 == 0       # 第 0 趟从你出发（你抢他）
        dur = min(per, q1 - s) / FPS
        put('S21', '嗖', s, lambda r, dur=dur, mine=mine: g_whoosh(r, dur=dur + 0.05, f0=900 if mine else 3000,
                                                                   f1=3000 if mine else 900, tp=dur * 0.55, tail=0.05,
                                                                   floor=0.25), -5, cat='key', check=False,
            label='来回（你→他）' if mine else '来回（他→你）')
        if s + per <= q1:
            put('S21', '啵', s + per, lambda r, mine=mine: g_pok(r, 1350 if mine else 1050), -3, cat='key',
                label='到他那边' if mine else '到你这边')
        leg += 1

    # —— S22 40.6–42.9：一排里会原谅的亮起来（和 S18 一排变蓝同一个轻布料声）；绿衣人走下来；被抢三次：前两次抢回去（嗖、嗖），第三次换成暖“叮” ——
    rg0, rg1 = E('S22', 'rowGreen')
    put('S22', '布料', rg0, lambda r, d=(rg1 - rg0) / FPS: g_zip(r, d), -28, cat='tex', check=False, label='一排变绿',
        send={'room': 0.3})
    w0, w1 = E('S22', 'walkDown')
    put('S22', '脚步', w1, lambda r, s=(w1 - w0) / FPS: g_walk(r, s), -19.5, anchor=(w1 - w0) / FPS, label='走下来')
    gs = sorted([(t, False) for t in E('S22', 'grabs')] + [(t, True) for t in E('S22', 'grabBacks')])
    for k, (t, back) in enumerate(gs):
        grab('S22', t, 6, back, gw=-7, gp=-12, tail=0.035, label='抢回去' if back else '抢',
             nxt=gs[k + 1][0] if k + 1 < len(gs) else E('S22', 'warm'), crisp=True)
    put('S22', '暖叮', E('S22', 'warm'), lambda r: g_warm(r, 880), -6, cat='key', label='照样递出（暖）', send={'room': 0.25})
    give('S22', E('S22', 'giveBack') + 7, 1568, -14, label='你也递回去')

    # —— S23 42.1–44.2：你学会原谅：条“刷”、换衣“咔哒”；飞向你的“抢”从每 0.15 秒一道变成每 0.34 秒一道；松一口气 ——
    put('S23', '刷', E('S23', 'bars'), lambda r: g_shua(r, 0.22, 1100, 3600), -13, label='两根条')
    rc0, rc1 = E('S23', 'recolor')
    put('S23', '布料', rc0, lambda r, d=(rc1 - rc0) / FPS: g_zip(r, d), -23, cat='tex', check=False)
    put('S23', '咔哒', rc1, lambda r: g_kada(r), -9, label='换衣（原谅）')
    d0, d1 = E('S23', 'grabsDense')
    s0, s1 = E('S23', 'grabsSparse')
    for t in list(range(d0, d1, T(0.15))) + list(range(s0, s1, T(0.34))):
        put('S23', '嗖', t, lambda r: g_whoosh(r, dur=0.29, f0=3000, f1=1100, tp=0.22, tail=0.03), -17, label='飞向你的抢')
    put('S23', '叹气', E('S23', 'relief')[0], lambda r: g_sigh(r), -21, cat='tex', check=False)

    # —— S24 44.2–47.9：500 人亮起；473 人聚拢“唰”；翻色细“嗒嗒”；收成一声“叮” ——
    whoosh_tex('S24', E('S24', 'zoom')[0], -24, 0.45, 900, 2400, 0.15, 0.12, '拉到远景')
    st0, st1 = E('S24', 'starters')
    for k in range(26):
        put('S24', '亮起', st0 + (st1 - st0) * k / 26 + rng.uniform(0, 1), lambda r, k=k: g_glint(r, 2600 * 2 ** (k / 20)),
            -25 + rng.uniform(-4, 0), cat='tex', check=False, pan=rng.uniform(-0.4, 0.4))
    ga0, ga1 = E('S24', 'gather')
    put('S24', '唰收拢', ga1, lambda r, s=(ga1 - ga0) / FPS: g_gather(r, s), -8.5, anchor=(ga1 - ga0) / FPS, label='聚成方块')
    # 翻色：473 格从 flip[0] 到 flip[1] 一格格翻（每格翻 5 帧，翻到一半换色）。第五版不再按代数每帧一下“嗒”（像在数数），
    # 换成一阵洗牌似的细“嗒”：每秒约 75 颗，随机撒在翻色的那一段里，越往后越高、略响一点
    fl0, fl1 = E('S24', 'flip')
    a, b = fl0 + 2.5, fl1 + 2.5
    nr = int(round(75 * (b - a) / FPS))
    for k in range(nr):
        f = a + (b - a) * rng.uniform(0, 1)
        u = (f - a) / (b - a)
        put('S24', '嗒', f, lambda r, u=u: g_tick(r, 3000 * 2 ** (0.7 * u) * jit(r, 80), fine=True), -30 + 6 * u + rng.uniform(-4, 0),
            cat='tex', check=False, label='翻色', pan=rng.uniform(-0.35, 0.35))
    put('S24', '我叮', E('S24', 'ding'), lambda r: g_me(r, big=True), -12, cat='key', label='翻完：九成会原谅', send={'hall': 0.3})

    # —— S25 48.9–51.4：方块散开；四个你（就是放大的路线图）的灯一盏盏亮：四声“叮”从低到高，狠那一声闷；带走句也在这一拍 ——
    whoosh_tex('S25', E('S25', 'scatter')[0], -21, 0.35, 800, 4000, 0.06, 0.1, '点阵散开')
    # 第七版重排：带走句底下一点暖（G 大调和弦，和四盏灯同调），S27 起收薄，S28 开头淡完
    put('S25', '暖音', pad_start(), lambda r, sp=pad_span(): g_pad(r, *sp), PAD_GAIN, cat='pad', check=False,
        label='带走句底下的暖音', send={'hall': 0.3})
    for i, (f, f0) in enumerate(zip(E('S25', 'lamps'), ROUTE_NOTES)):
        put('S25', '灯叮', f, lambda r, f0=f0, i=i: g_lamp(r, f0, muffled=(i == 1)), (-7, -10, -7, -8)[i], cat='key',
            label=('老实', '狠（闷）', '有来有往', '原谅')[i] + '的灯', send={'room': 0.2})

    # —— S26（第七版）“可新人一多，狠人又回来了”：gather 四个你散开、退回第 300 代一片绿的点阵：一声往外退的轻声；
    #    run 从第 300 代跑到第 900 代：一层越来越不安的质感（跟着狠人的比例收紧，peak 那一刻最紧），加上点变红时的细碎“嗒”；
    #    back（狠人回到三成）一声发暗的重击，key；原来的 20 声“第 N 遍”刷和 S27 的收拢、白点叮都删了 ——
    cycle_sfx(rng)

    # —— S27 + S27h（第七版重排：不出字，dive 从四个你扎回你）：dive 一声往里扎的嗖；暖音从 S25 挂过来，这里收薄 ——
    dv0, dv1 = E('S27', 'dive')
    put('S27', '扎进去', dv0, lambda r, s=(dv1 - dv0) / FPS: g_whoosh(r, dur=s + 0.05, f0=2600, f1=650, tp=s * 0.6, tail=0.07,
                                                                      floor=0.45), -12, label='扎进你', send={'hall': 0.15})

    # —— S28 55.65–58.65：“约好七点，朋友没来。”出来时两下很轻的钟表“嘀、嗒”；你转过身（很轻的布料声）；
    #    opt1“再约一次”、opt2“拉黑”：第五版补改，画面上两个选项同一个颜色，声音也不替观众选——同一个软槌小铃、同样响，
    #    只差音高（D6、G6，和 6.5 秒“狠下去，会怎样？”那声往上挑的问句同一个音色）。都比 54–55 秒的暖音轻 ——
    s28 = B['S28']['f0']
    put('S28', '嘀嗒', s28 + 2, lambda r: g_clock(r), -24, label='钟表：嘀', send={'room': 0.2})
    put('S28', '嘀嗒', s28 + 14, lambda r: g_clock(r, tock=True), -25, label='钟表：嗒', send={'room': 0.2})
    put('S28', '布料', E('S28', 'turn')[0], lambda r: g_rustle(r, 0.5), -31, cat='tex', check=False)
    for k, (ev, f0, lab) in enumerate((('opt1', ROUTE_NOTES[2], '再约一次'), ('opt2', ROUTE_NOTES[3], '还是拉黑'))):
        put('S28', '问', E('S28', ev), lambda r, f0=f0: g_route(r, f0, soft=True), OPT_GAIN + OPT_TRIM[k], label=f'选项：{lab}',
            send={'room': 0.25})

    route_sfx()
    flecks(rng)
    EVENTS.sort(key=lambda e: e['vis'] / FPS + e['lead'] - e['anchor'])


def route_sfx():
    """路线图（第五版，代替“第 N 轮”计数器、顶上历史条和开场大计数）。按 timeline.json 的 route.keys 排：
    in 一声很轻的 G5（老实）；reveal / on 一声小铃，音高 = 这一格的 ROUTE_NOTES（狠那一格发闷），key，落在 ROUTE_LAND；
    ask 两声轻的往上挑（D6 → G6，隔 3 帧，和画面上两个“？”一个接一个起跳同步）；back 很短的倒吸；out 不另配。"""
    for k in ROUTE:
        f, act, i = k['f'], k['act'], k['i']
        bid = beat_at(f)['id']
        if act == 'in':
            put(bid, '路线叮', f, lambda r: g_route(r, ROUTE_NOTES[0], soft=True), -21, label='路线图：老实（淡入）',
                send={'hall': 0.2})
        elif act in ('reveal', 'on'):
            name = TL['route']['stages'][i]['label']
            fl = f + ROUTE_LAND[act]
            put(beat_at(fl)['id'], '路线叮', fl, lambda r, i=i: g_route(r, ROUTE_NOTES[i], muffled=(i == 1)), (0, -11, -14, -15)[i],
                cat='key', label=f'路线图：{name}（{"亮出" if act == "reveal" else "回到"}）', send={'room': 0.2})
        elif act == 'ask':
            put(bid, '问', f, lambda r: g_ask(r, 3 / FPS), -19, label='路线图：？跳一下', send={'hall': 0.2})
        elif act == 'back':
            put(bid, '倒吸', f, lambda r: g_gasp(r), -15, check=False, label='路线图：倒回老实')


# 细碎“嗒”撒在哪几拍、数哪些点（远景、中景里点成片变色的地方；近景里画面上没东西在跳，不放）
FLECK_BEATS = {'S03': 'starters', 'S14': 'all', 'S16': 'all', 'S19': 'all'}


def color_class(ch):
    """点阵里的打法 → 画面上的颜色类：老实黄、狠红（骗子和记仇同一个红色家族）、有来有往蓝、会原谅绿、其他灰。"""
    return 'YRBGRW'[int(ch)]


def visible_changes(g0, g1, cells):
    s = D['grid']['s']
    return sum(1 for c in cells if color_class(s[g0][c]) != color_class(s[g1][c]))


def flecks(rng):
    """第五版：没有计数器了，计数“嗒”全删。远景里点成片变色的那几拍留一层很轻的细碎“嗒”：每一代看得见的点里变了几个色，
    换成每秒多少颗（最多每秒 55 颗，和细“噗”同一个算法），随机撒在这一代显示的那几帧里（不落在帧格上，听着不像在数数）。"""
    starters = D['grid']['starters']
    for bid, which in FLECK_BEATS.items():
        cells = starters if which == 'starters' else range(1000)
        fa, fb = B[bid]['f0'], B[bid]['f1']
        cold = bid == 'S16'
        f = fa
        while f < fb:
            g = GEN[f]
            f2 = f + 1
            while f2 < fb and GEN[f2] == g:
                f2 += 1
            gp = GEN[f - 1] if f > 0 else g
            c = visible_changes(gp, g, cells) if g > gp else 0
            if c > 0:
                w = min(1.0, c / 30)
                rate = 55 * w ** 0.7
                for _ in range(rng.poisson(rate * (f2 - f) / FPS)):
                    put(bid, '嗒', f + rng.uniform(0, f2 - f), lambda r: g_tick(r, rng_f0(r), fine=True),
                        -29 + 4 * w ** 0.5 + rng.uniform(-4, 0), cat='tex', check=False, label='点变色',
                        pan=rng.uniform(-0.45, 0.45), send={'cold': 0.25} if cold else None)
            f = f2


def rng_f0(r):
    """细碎“嗒”的音高：2.2–4.2 kHz 里随机（每颗不一样，听着不像同一个计数器）。"""
    return 2200 * 2 ** r.uniform(0, 0.93)


# —— 第七版 S26：接着跑（data.json 的 cycle：s[k]、counts[k] 是第 gen0+k 代；run 里从 gen0 线性跑到 gen1；CYC 在文件开头）——


CYC_KEYS = [(int(round(t * FPS)), g) for t, g in TL['cycle']['keys']]      # 第七版三改：(帧, 代)，两点之间线性，最后一点之后停住
SOFT = {PC_ for PC_ in (ALLC, WSLS)}                                         # 好欺负的人（timeline.json 的 cycle.soft：老实人、不点名）


def cycle_gen(f):
    """S26/S26b 第 f 帧画面上是第几代（和 FEnding.tsx 的 cycleGen 同一个算法：timeline.json 的 cycle.keys，两点之间线性，
    第一点之前停在第一点，最后一点之后停住）。"""
    K = CYC_KEYS
    if f <= K[0][0]:
        return K[0][1]
    for i in range(1, len(K)):
        if f <= K[i][0]:
            return K[i - 1][1] + (K[i][1] - K[i - 1][1]) * (f - K[i - 1][0]) / max(1e-6, K[i][0] - K[i - 1][0])
    return K[-1][1]


def harsh_share(g):
    """第 g 代狠人（骗子＋记仇）占多少。"""
    c = CYC['counts'][int(round(g)) - CYC['gen0']]
    return (c[ALLD] + c[GRIM]) / sum(c)


def soft_share(g):
    """第 g 代好欺负的人（老实人＋不点名，这一幕都画成老实人的黄）占多少。"""
    c = CYC['counts'][int(round(g)) - CYC['gen0']]
    return (c[ALLC] + c[WSLS]) / sum(c)


def cycle_sfx(rng):
    """第七版三改：S26“原谅的世界里，好欺负的人多了”＋S26b“狠人又过得好了，大家又学狠”。
    S26 gather 往外退的轻声；run（第 300 → 750 代）一层很轻的质感，安稳里透一点不安（紧张度跟着好欺负的人涨，最多 0.3），
    加上点变黄时很轻的“啵”；S26b run2（第 750 → 860 代）同一层质感跟着狠人比例收紧，peak 那一刻最紧，加上点变红的细碎“嗒”；
    back 发暗的重击（key）；第 860 代停住以后 0.25 秒收掉。"""
    g0, g1 = E('S26', 'gather')
    put('S26', '退', g0, lambda r, s=(g1 - g0) / FPS: g_whoosh(r, dur=s + 0.05, f0=1700, f1=480, bw=1.5, tp=0.04, tail=0.16,
                                                                floor=0.7, flutter=0.08), -20, label='退回点阵', send={'hall': 0.3})
    r0, r1 = E('S26', 'run')
    q0, q1 = E('S26b', 'run2')
    hpk = CYC['harshPeakShare']
    s750 = soft_share(CYC_KEYS[1][1])
    rel = 0.25

    def inten_at(f):
        if f < q0:          # S26：安稳里透一点不安，不暗
            return 0.06 + 0.24 * min(1.0, soft_share(cycle_gen(f)) / s750)
        return min(1.0, 0.30 + 0.70 * harsh_share(cycle_gen(f)) / hpk)
    fr = np.arange(r0, q1 + rel * FPS + 1)
    iv = np.array([inten_at(min(f, q1)) for f in fr])
    iv = np.where(fr > q1, iv[fr <= q1][-1] * np.clip(1 - (fr - q1) / (rel * FPS), 0, 1), iv)
    iv = np.convolve(np.pad(iv, 2, mode='edge'), np.ones(5) / 5, mode='valid')     # 逐帧跳的代数抹平一点
    curve = np.interp(np.arange(int(len(fr) / FPS * SR)) / SR * FPS, np.arange(len(fr)), iv)
    put('S26', '不安', r0, lambda r, c=curve: g_unease(r, c), -17, cat='tex', check=False, label='接着跑：安稳里透出不安，再越来越紧',
        send={'cold': 0.25})
    # S26 点变黄：很轻的“啵”（和 S02 点在眨眼同一个声音）；S26b 点变红：细碎“嗒”。每帧数一数（这一帧和上一帧的代数比），每秒最多 40 / 55 颗，随机撒
    s = CYC['s']
    soft_ch, harsh_ch = '05', '14'
    for f in list(range(r0 + 1, r1 + 1)) + list(range(q0 + 1, q1 + 1)):
        a, b = int(round(cycle_gen(f - 1))) - CYC['gen0'], int(round(cycle_gen(f))) - CYC['gen0']
        if f <= r1:
            c = sum(1 for i in range(1000) if s[a][i] not in soft_ch and s[b][i] in soft_ch)
            w = min(1.0, c / 30)
            for _ in range(rng.poisson(40 * w ** 0.7 / FPS) if c > 0 else 0):
                put('S26', '啵', f - 1 + rng.uniform(0, 1), lambda r: g_bubble(r, 1000 + 600 * r.uniform()), -31 + 3 * w ** 0.5 + rng.uniform(-4, 0),
                    cat='tex', check=False, label='点变黄', pan=rng.uniform(-0.45, 0.45))
        else:
            c = sum(1 for i in range(1000) if s[a][i] not in harsh_ch and s[b][i] in harsh_ch)
            w = min(1.0, c / 30)
            for _ in range(rng.poisson(55 * w ** 0.7 / FPS) if c > 0 else 0):
                put('S26b', '嗒', f - 1 + rng.uniform(0, 1), lambda r: g_tick(r, rng_f0(r), fine=True), -29 + 4 * w ** 0.5 + rng.uniform(-4, 0),
                    cat='tex', check=False, label='点变红', pan=rng.uniform(-0.45, 0.45), send={'cold': 0.25})
    put('S26b', '重击', E('S26b', 'back'), lambda r: g_dark(r), -1, cat='key', label='狠人回到三成：重击', send={'cold': 0.3})


def grains(beat, fa, fb, count, ref, rng):
    """远景里的点变色：每一代变了几个点（data.json 的点阵逐代比），换成每秒多少颗细“噗”（最多每秒 55 颗），撒在这一代显示的那几帧里。"""
    f = fa
    while f < fb:
        g = GEN[f]
        f2 = f + 1
        while f2 < fb and GEN[f2] == g:
            f2 += 1
        c = count(g) if g > 0 else 0
        if c > 0:
            rate = 55 * min(1.0, (c / ref)) ** 0.7
            for _ in range(rng.poisson(rate * (f2 - f) / FPS)):
                put(beat, '噗', f + rng.uniform(0, f2 - f), lambda r: g_grain(r), -27 + rng.uniform(-5, 0), cat='tex',
                    check=False, pan=rng.uniform(-0.4, 0.4))
        f = f2


# ======================================================================
# 环境层：房间底噪 + 远景人群（光点飞的细亮声、暖底子、冷风）。冷暖跟着这一代的合作率走（和画面亮度同一个数）
# ======================================================================
def crowd_weight():
    """每帧“看得见多少人群”：远景 1，中景 0.8，中近景 0.6，近景 0，拉远/扎进去时渐变。"""
    W = np.zeros(NF + 1)
    for f in range(NF + 1):
        b = beat_at(min(f, NF - 1))
        sc, bid = b['scene'], b['id']
        if sc == 'pullback':
            w = ease(prog(f, E('S02', 'zoomOut')))
        elif sc == 'far':
            w = 1.0
        elif sc == 'rewind':
            w = 1 - prog(f, E('S05', 'dive'))
        elif sc == 'mid':
            w = 0.8
        elif sc == 'midYou':
            w = 0.6
        elif sc == 'block':
            st = E('S24', 'starters')[0]
            w = 1.0 if f < st else 1 - 0.65 * prog(f, (st, E('S24', 'gather')[1]))
        elif sc == 'four':             # 第七版重排：四个你从 S26 的点阵散出来（原来是从方块）
            w = 1 - prog(f, E('S25', 'scatter'))
        elif sc == 'cycle':            # 第七版 S26：四个你退回点阵，又是远景
            w = 0.35 + 0.65 * prog(f, E('S26', 'gather'))
        elif bid == 'S20':
            w = 1 - prog(f, E('S20', 'push'))
        else:
            w = 0.0
        W[f] = w
    k = np.ones(5) / 5
    return np.convolve(np.pad(W, 2, mode='edge'), k, mode='valid')


def per_sample(v):
    return np.interp(np.arange(N) / SPF, np.arange(len(v)), v)


AMB_BOOST_DB = 5.0


def ambience(rng):
    W = crowd_weight()
    C = np.array([D['coop'][GEN[min(f, NF)]] for f in range(NF + 1)])
    # 第七版 S26：接着跑的那一段，冷暖跟着狠人的比例走（合作率 ≈ 第 300 代的合作率 × 不狠的比例），狠人回来，世界又冷了
    c300 = D['coop'][CYC['gen0']]
    for f in range(B['S26']['f0'], B['S26b']['f1']):
        C[f] = max(0.08, c300 * (1 - harsh_share(cycle_gen(f))) / (1 - harsh_share(CYC['gen0'])))
    w, c = per_sample(W), per_sample(C)
    slow = lambda lo, hi: norm(shape(rng.standard_normal(N), lo, hi, order=1))
    amb = np.zeros((N, 2))
    db = lambda x: 10 ** (x / 20)
    for ch in range(2):
        room = noise(N, rng, 90, 3000, tilt=-1.0) * db(-47) * (1 + 0.12 * slow(0.05, 0.3))
        warm = noise(N, rng, 150, 1000, tilt=-1.2) * db(-34) * (c / 0.69) ** 1.2 * w * (1 + 0.2 * slow(0.1, 0.6))
        bands = [noise(N, rng, fc / 1.35, fc * 1.35, order=2) for fc in (800, 1400, 2400)]
        mixw = [0.5 + 0.5 * slow(0.03, 0.15) for _ in bands]
        wind = sum(bd * mw for bd, mw in zip(bands, mixw)) / 1.5
        cold = np.clip((0.42 - c) / 0.3, 0, 1)
        wind = wind * db(-35) * cold * w * (1 + 0.5 * slow(0.2, 1.0))
        amb[:, ch] = room + warm + wind
    # 光点飞：每秒 W×(0.8 + 24c²) 颗细亮声（暖的时候约 12–18 颗，冷的时候约 1 颗）
    tw = np.zeros((N, 2))
    t = 0.0
    while t < N / SR:
        f = min(NF, int(t * FPS))
        lam = W[f] * (0.8 + 24 * C[f] ** 2)
        if lam < 0.05:
            t += 0.05
            continue
        t += rng.exponential(1 / lam)
        i = int(t * SR)
        if i >= N:
            break
        s = g_glint(rng, rng.uniform(2800, 5500)) * db(-26 + rng.uniform(-7, 0))
        p = rng.uniform(-0.5, 0.5)
        m = min(len(s), N - i)
        tw[i:i + m, 0] += s[:m] * math.cos((p + 1) * math.pi / 4) * 1.414
        tw[i:i + m, 1] += s[:m] * math.sin((p + 1) * math.pi / 4) * 1.414
    # 10/29 主会话：环境层整体抬高 5 dB，压在曲库配乐下面也能听出“世界冷了”（原来单独量约 −40.5 LUFS）
    boost = 10 ** (AMB_BOOST_DB / 20)
    return (amb + tw) * boost, W, C


# ======================================================================
# 混音
# ======================================================================
def make_ir(rng, rt60, lo, hi, dur=None, pre=0.008):
    n = int((dur or rt60 * 1.1) * SR)
    t = ts(n)
    ir = np.zeros((n, 2))
    for ch in range(2):
        z = rng.standard_normal(n)
        low = shape(z, None, 1500)
        high = z - low
        y = low * np.exp(-6.9 * t / rt60) + high * np.exp(-6.9 * t / (rt60 * 0.45))
        y = shape(y, lo, hi)
        y[: int(pre * SR)] = 0
        ir[:, ch] = y / np.sqrt(np.sum(y ** 2))
    return ir


def conv(x, ir):
    n = len(x) + len(ir) - 1
    m = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, m)
    out = np.zeros((len(x), 2))
    for ch in range(2):
        out[:, ch] = np.fft.irfft(X * np.fft.rfft(ir[:, ch], m), m)[: len(x)]
    return out


def default_send(f):
    sc = beat_at(int(f))['scene']
    if sc in ('far', 'mid', 'pullback', 'rewind', 'block', 'cycle'):
        return {'hall': 0.14}
    if sc == 'midYou':
        return {'cold': 0.2}
    return {'room': 0.1}


def gate_curve():
    """全停：S15 粉线开始连到定住结束（和你）、S19 定住（可手滑前）。停之前那一下计数“嗒”留着（25 毫秒以后才压下去）。"""
    t = np.arange(N) / SR
    g = np.ones(N)

    def cut(fa, fb, back):
        a, b = fa / FPS + 0.025, fb / FPS
        g[(t >= a + 0.025) & (t < b)] = 0
        m = (t >= a) & (t < a + 0.025)
        g[m] = np.minimum(g[m], 1 - (t[m] - a) / 0.025)
        m = (t >= b) & (t < b + back)
        g[m] = np.minimum(g[m], (t[m] - b) / back)
    cut(E('S15', 'lines')[0], E('S15', 'freeze')[1], 0.5)
    cut(E('S19', 'freeze')[0], E('S19', 'freeze')[1], 0.3)
    end = (t - B['S29']['f0'] / FPS) / (N / SR - B['S29']['f0'] / FPS)     # 最后一拍淡到 0
    g *= np.clip(1 - end, 0, 1) ** 1.5
    return g


def duck_curve(x, depth_db=7.0):
    """关键音效响的时候，环境层、计数、细碎层让开：10 毫秒一块取峰值，立即压下、0.25 秒放开。最多压 depth_db。"""
    blk = SR // 100
    nb = len(x) // blk + 1
    pk = np.zeros(nb)
    a = np.abs(x)
    for i in range(nb):
        seg = a[i * blk:(i + 1) * blk]
        if len(seg):
            pk[i] = seg.max()
    ref = np.percentile(pk[pk > 0], 99) if np.any(pk > 0) else 1
    env = np.zeros(nb)
    r = math.exp(-0.01 / 0.25)
    for i in range(nb):
        env[i] = max(pk[i], env[i - 1] * r if i else 0)
    lvl = np.clip(env / (0.5 * ref), 0, 1)
    g = 10 ** (-depth_db * lvl / 20)
    return np.interp(np.arange(len(x)), np.arange(nb) * blk + blk / 2, g)


def render():
    plan()
    rng = np.random.default_rng(SEED)
    bus = {k: np.zeros(N) for k in ('key', 'mid', 'tick', 'tex', 'solo', 'pad')}
    texs = np.zeros((N, 2))
    sends = {k: np.zeros(N) for k in ('room', 'hall', 'cold')}
    solo_sends = {k: np.zeros(N) for k in ('room', 'hall', 'cold')}
    occ = {}
    for e in EVENTS:
        # 第五版补改：种子 = 拍号 + 类别 + 它是这一拍这一类里的第几个（原来用它在全表里的序号，删一个声音，后面所有声音的
        # 小随机都跟着变；峰值归一的声音换种子有效值会差 2–4 dB，整条的平衡就跟着动）。现在加删别的声音不影响它
        key = (e['beat'], e['kind'])
        e['seed'] = [SEED, zlib.crc32((e['beat'] + e['kind']).encode()), occ.get(key, 0)]
        occ[key] = occ.get(key, 0) + 1
        r = np.random.default_rng(e['seed'])
        sig = e['sound'](r) * 10 ** (e['gain'] / 20)
        st = int(round((e['vis'] / FPS + e['lead'] - e['anchor']) * SR))
        e['start'] = st / SR
        if st >= N:
            continue
        if st < 0:
            sig, st = sig[-st:], 0
        sig = sig[: N - st]
        m = len(sig)
        if e['cat'] == 'tex' and e['pan']:
            p = e['pan']
            texs[st:st + m, 0] += sig * math.cos((p + 1) * math.pi / 4) * 1.414
            texs[st:st + m, 1] += sig * math.sin((p + 1) * math.pi / 4) * 1.414
        else:
            bus[e['cat']][st:st + m] += sig
        snd = e['send'] if e['send'] is not None else (default_send(e['vis']) if e['cat'] != 'tex' else {})
        for k, v in snd.items():
            (solo_sends if e['cat'] == 'solo' else sends)[k][st:st + m] += sig * v
    amb, W, C = ambience(rng)
    irs = {'room': make_ir(rng, 0.35, 200, 5000), 'hall': make_ir(rng, 0.9, 300, 7000, pre=0.015),
           'cold': make_ir(rng, 1.6, 250, 4000, pre=0.02)}
    wet = sum(conv(sends[k], irs[k]) for k in irs)
    wet_solo = sum(conv(solo_sends[k], irs[k]) for k in irs)
    gate = gate_curve()
    duck = duck_curve(bus['key'] + bus['mid'] + bus['solo'])
    t = np.arange(N) / SR                                  # 你只有一遍起：环境声压到三成（让给暖音），结尾安静
    a0 = B['S27']['f0'] / FPS
    tail_amb = np.where(t < a0, 1, 1 - 0.7 * np.clip((t - a0) / 0.3, 0, 1))
    mono = lambda x: np.stack([x, x], axis=1)
    stems = {
        'key': mono(bus['key']) * gate[:, None],
        'mid': mono(bus['mid']) * gate[:, None],
        'tick': mono(bus['tick'] * duck) * gate[:, None],
        'tex': (mono(bus['tex']) + texs) * (duck * gate)[:, None],
        'amb': amb * (duck * gate * tail_amb)[:, None],
        'wet': wet * gate[:, None],
        'solo': mono(bus['solo']) + wet_solo,
        'pad': mono(bus['pad']),                           # 暖音：不让开、不全停（它就是那一刻的主角）
    }
    mix = sum(stems.values())
    hp = lambda x: np.stack([shape(x[:, ch], 35, None, order=2) for ch in range(2)], axis=1)
    mix = hp(mix)
    mix[: int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]     # 开头 30 毫秒淡入，第一帧不爆
    stems.update(amb_raw=amb, W=W, C=C)      # 只给自查用，不进混音
    return mix, stems, dict(W=W, C=C)


# ======================================================================
# 响度
# ======================================================================
def write_wav(path, x, dither=False, rng=None):
    x = np.clip(x, -1, 1)
    q = x * 32767
    if dither:
        q = q + (rng.random(q.shape) - rng.random(q.shape))
    data = np.clip(np.round(q), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def read_wav(path):
    with wave.open(path) as w:
        ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
        x = np.frombuffer(w.readframes(n), '<i2').reshape(-1, ch) / 32768.0
    return x, sr


def ebur(path, pre=''):
    """ffmpeg ebur128：整条响度 I、响度范围 LRA、真峰值，和每 0.1 秒的瞬时响度 M（400 毫秒窗）。"""
    af = (pre + ',' if pre else '') + 'ebur128=peak=true:framelog=info'
    err = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af', af, '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    M = [(float(a), -120.0 if 'inf' in b else float(b)) for a, b in re.findall(r't:\s*([\d.]+)\s+TARGET:\S+\s+LUFS\s+M:\s*(\S+)', err)]
    summ = err[err.rfind('Summary:'):]
    I = float(re.search(r'I:\s*(-?[\d.]+) LUFS', summ).group(1))
    LRA = float(re.search(r'LRA:\s*(-?[\d.]+) LU', summ).group(1))
    tp = re.search(r'True peak:\s*Peak:\s*(-?[\d.]+|-inf)', summ)
    TP = float(tp.group(1)) if tp and 'inf' not in tp.group(1) else -120.0
    return dict(I=I, LRA=LRA, TP=TP, M=np.array(M))


def loudnorm_json(path):
    err = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af',
                          f'loudnorm=I={TARGET}:TP={TP_CEIL}:LRA=20:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', err, re.S).group(0))


def true_peak_env(x, os_=4):
    """4 倍过采样后的峰值（每个原始采样取它附近 4 个过采样点的最大值，两个声道取大的）。"""
    n = len(x)
    out = np.zeros(n)
    for ch in range(x.shape[1]):
        X = np.fft.rfft(x[:, ch])
        Y = np.zeros(n * os_ // 2 + 1, complex)
        Y[: len(X)] = X
        y = np.abs(np.fft.irfft(Y, n * os_) * os_)[: n * os_].reshape(n, os_).max(axis=1)
        out = np.maximum(out, y)
    return out


def limit(x, ceil_db):
    """前瞻限幅：按过采样峰值算每 1 毫秒要压多少，往前看 3 毫秒、放开 60 毫秒。只碰超过上限的那几下。"""
    ceil = 10 ** (ceil_db / 20)
    pkv = true_peak_env(x)
    req = np.minimum(1.0, ceil / np.maximum(pkv, 1e-9))
    blk = SR // 1000
    nb = len(x) // blk + 1
    rb = np.array([req[i * blk:(i + 1) * blk].min() if i * blk < len(x) else 1.0 for i in range(nb)])
    la = np.array([rb[i:i + 4].min() for i in range(nb)])
    g = np.ones(nb)
    rel = 1 - math.exp(-1 / 60)
    for i in range(nb):
        prev = g[i - 1] if i else 1.0
        g[i] = min(la[i], prev + (1 - prev) * rel)
    gs = np.interp(np.arange(len(x)), np.arange(nb) * blk, g)
    return x * gs[:, None], float(gs.min())


def master(mix, tmp):
    p = os.path.join(tmp, 'pre.wav')
    s0 = 10 ** (-1 / 20) / np.max(np.abs(mix))
    write_wav(p, mix * s0)
    I0 = ebur(p)['I'] - 20 * math.log10(s0)
    y = mix * 10 ** ((TARGET - I0) / 20)
    gmin = 1.0
    for _ in range(4):
        tp = 20 * math.log10(true_peak_env(y).max())
        if tp <= TP_CEIL - 0.25:
            break
        y, g = limit(y, TP_CEIL - 0.4)
        gmin = min(gmin, g)
        write_wav(p, y)
        y = y * 10 ** ((TARGET - ebur(p)['I']) / 20)
    gain = float(np.max(np.abs(y)) / np.max(np.abs(mix)))
    return y, gain, gmin


# ======================================================================
# 自查：从磁盘读回 sfx.wav，逐个找起音
# ======================================================================
def band_env(x, lo, hi):
    y = shape(x, lo, hi, order=4)
    w = int(0.004 * SR)
    hop = SR // 1000
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    idx = np.arange(0, len(y) - w, hop)
    return 10 * np.log10((c[idx + w] - c[idx]) / w + 1e-14), (idx + w / 2) / SR


def onset(env, tt, te, a, b):
    """起音 = 窗口里 8 毫秒之内电平涨得多的那一刻：取最早的、离最大涨幅不到 6 dB 的那个峰（不受前一个声音的尾巴、混响影响；
    咔哒这种先轻后重的两下，量到的是前一下）。返回（时刻，涨了多少 dB）。"""
    lo, hi = np.searchsorted(tt, te - a), np.searchsorted(tt, te + b)
    rise = env[lo:hi] - env[lo - 8:hi - 8]
    mx = float(rise.max())
    thr = max(6.0, mx - 6.0) if mx >= 6 else mx
    for k in range(len(rise)):
        if rise[k] >= thr and (k + 1 >= len(rise) or rise[k] >= rise[k + 1]):
            return float(tt[lo + k]) - 0.004, float(rise[k])
    k = int(np.argmax(rise))
    return float(tt[lo + k]) - 0.004, float(rise[k])


def detect(x, stems):
    """两步。落点：每个声音在它自己那一轨（关键 / 一般 / 计数 / 单独）上量，窗口只让开同一轨的邻居；混音是逐采样相加、
    高通是零相位，不挪时间，所以这就是成品里的落点。听得出：再在成品 sfx.wav 上量一遍，起音涨幅不到 6 dB 的算被盖住。"""
    mono = x.mean(axis=1)
    envs = {}
    chk = [e for e in EVENTS if e['check']]
    chk.sort(key=lambda e: e['vis'] / FPS + e['lead'])
    texp = {id(e): e['vis'] / FPS + e['lead'] for e in chk}

    def win(lst, i):
        te = texp[id(lst[i])]
        gp = te - texp[id(lst[i - 1])] if i else 1.0
        gn = texp[id(lst[i + 1])] - te if i + 1 < len(lst) else 1.0
        return te, max(0.012, min(0.08, 0.5 * gp)), max(0.012, min(0.12, 0.5 * gn))

    for cat in ('key', 'mid', 'tick', 'solo'):
        lst = [e for e in chk if e['cat'] == cat]
        for i, e in enumerate(lst):
            band = BAND.get(e['kind'], (500, 8000))
            if (cat, band) not in envs:
                envs[(cat, band)] = band_env(stems[cat].mean(axis=1), *band)
            te, a, b = win(lst, i)
            e['meas'], e['snr'] = onset(*envs[(cat, band)], te, a, b)
            e['err_f'] = (e['meas'] - te) * FPS
            e['where'] = cat
    for i, e in enumerate(chk):
        band = BAND.get(e['kind'], (500, 8000))
        if ('mix', band) not in envs:
            envs[('mix', band)] = band_env(mono, *band)
        te, a, b = win(chk, i)
        env, tt = envs[('mix', band)]
        e['meas_mix'], r = onset(env, tt, te, a, b)
        k0 = np.searchsorted(tt, e['meas_mix'])
        k1 = np.searchsorted(tt, e['meas_mix'] + min(0.25, b + 0.12))
        b0, b1 = np.searchsorted(tt, te - 0.25), np.searchsorted(tt, te - 0.02)
        over = float(env[k0:k1].max() - np.median(env[b0:b1])) if b1 > b0 and k1 > k0 else r
        e['rise_mix'] = max(r, over)
    return chk


# ======================================================================
# 画图（没有 matplotlib，用 PIL 画）
# ======================================================================
def font(size):
    return ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()


CAT_COL = {'key': (214, 48, 49), 'solo': (142, 68, 173), 'mid': (230, 126, 34), 'tick': (120, 120, 120), 'tex': (39, 174, 96),
           'pad': (41, 128, 185)}


def rms_db(x, win=0.01):
    w = int(win * SR)
    n = len(x) // w
    y = x[: n * w].reshape(n, w)
    return 10 * np.log10(np.mean(y * y, axis=1) + 1e-14), (np.arange(n) + 0.5) * win


def plot_overview(x, amb, chk, path):
    W, rows, rowH, L = 3200, 4, 430, 90
    seg = 15.0
    img = Image.new('RGB', (W, rows * rowH + 120), 'white')
    d = ImageDraw.Draw(img)
    f16, f20, f28 = font(16), font(20), font(30)
    d.text((L, 20), '002 音效轨：整条波形和每拍对照（上：波形；中：手机频段 300 Hz 以上的有效值 dB，绿 = 环境层单独；下：画面事件（竖线）和量出的起音（▲））',
           fill='black', font=f28)
    mono = x.mean(axis=1)
    phone = shape(mono, 300, None, order=4)
    pdb, pt = rms_db(phone)
    adb, at = rms_db(shape(amb.mean(axis=1), 300, None, order=4))
    pw = W - L - 30
    for r in range(rows):
        y0 = 80 + r * rowH
        ta, tb = r * seg, (r + 1) * seg
        X = lambda t: L + (t - ta) / seg * pw
        for b in BEATS:
            s, e = b['t0'], min(b['t1'], DUR)
            if e <= ta or s >= tb:
                continue
            xa, xb = X(max(s, ta)), X(min(e, tb))
            if BEATS.index(b) % 2:
                d.rectangle([xa, y0, xb, y0 + rowH - 40], fill=(244, 244, 248))
            d.line([X(max(s, ta)), y0, X(max(s, ta)), y0 + rowH - 40], fill=(180, 180, 200), width=1)
            d.text((xa + 4, y0 + 2), b['id'] + (' 停' if b['stop'] else ''), fill=(60, 60, 120), font=f20)
        # 波形
        wy, wh = y0 + 30, 150
        d.line([L, wy + wh / 2, L + pw, wy + wh / 2], fill=(200, 200, 200))
        i0, i1 = int(ta * SR), int(min(tb, DUR) * SR)
        cols = int(pw)
        segm = mono[i0:i1]
        per = max(1, len(segm) // cols)
        mm = segm[: per * (len(segm) // per)].reshape(-1, per)
        mx, mn = mm.max(axis=1), mm.min(axis=1)
        for k in range(len(mx)):
            xx = L + k * (seg * SR / per) ** -1 * pw * 1.0 if False else L + k * per / (seg * SR) * pw
            d.line([xx, wy + wh / 2 - mx[k] * wh / 2, xx, wy + wh / 2 - mn[k] * wh / 2], fill=(70, 70, 80))
        # dB 包络
        ey, eh = wy + wh + 10, 120
        d.rectangle([L, ey, L + pw, ey + eh], outline=(220, 220, 220))
        for lv in (-60, -40, -20):
            yy = ey + (0 - lv) / 70 * eh
            d.line([L, yy, L + pw, yy], fill=(235, 235, 235))
            d.text((L - 60, yy - 10), f'{lv} dB', fill=(150, 150, 150), font=f16)
        for arr, tt, col in ((pdb, pt, (41, 98, 255)), (adb, at, (39, 174, 96))):
            m = (tt >= ta) & (tt < tb)
            pts = [(X(t_), ey + min(eh, max(0, (0 - v) / 70 * eh))) for t_, v in zip(tt[m], arr[m])]
            if len(pts) > 1:
                d.line(pts, fill=col, width=2)
        # 事件
        my = ey + eh + 8
        lab_y = [0] * 6
        for e in EVENTS:
            te = e['vis'] / FPS
            if not (ta <= te < tb) or e['cat'] == 'tex':
                continue
            col = CAT_COL[e['cat']]
            hgt = 26 if e['cat'] in ('key', 'solo') else 16 if e['cat'] == 'mid' else 9
            d.line([X(te), my, X(te), my + hgt], fill=col, width=3 if e['cat'] in ('key', 'solo') else 1)
        for e in chk:
            te = e['meas']
            if not (ta <= te < tb) or e['cat'] == 'tick':
                continue
            xx = X(te)
            d.polygon([(xx, my + 30), (xx - 5, my + 40), (xx + 5, my + 40)], fill=(0, 0, 0))
        last = -1e9
        lane = 0
        for e in EVENTS:
            te = e['vis'] / FPS
            if not (ta <= te < tb) or e['cat'] not in ('key', 'solo'):
                continue
            xx = X(te)
            if xx - last < 70:
                lane = (lane + 1) % 3
            else:
                lane = 0
            last = xx
            d.text((xx + 3, wy - 2 + lane * 18), e['label'][:8], fill=CAT_COL[e['cat']], font=f16)
        for k in range(16):
            t_ = ta + k
            d.text((X(t_) - 8, y0 + rowH - 40), f'{t_:.0f}', fill=(90, 90, 90), font=f16)
    lg = 80 + rows * rowH
    for k, (name, cat) in enumerate((('关键（抢、手滑、咚、四声叮、路线图…）', 'key'), ('全停时单独响的（咚、可手滑的啪）', 'solo'),
                                     ('一般音效（叮、咔哒、刷…）', 'mid'))):
        d.rectangle([L + k * 640, lg, L + k * 640 + 30, lg + 20], fill=CAT_COL[cat])
        d.text((L + k * 640 + 40, lg - 2), name, fill='black', font=f20)
    img.save(path)


def plot_beats(x, chk, path):
    cols, PW, PH = 5, 640, 330
    rows = math.ceil(len(BEATS) / cols)
    img = Image.new('RGB', (cols * PW, rows * PH + 70), 'white')
    d = ImageDraw.Draw(img)
    f15, f18, f22 = font(15), font(18), font(22)
    d.text((20, 18), '逐拍对照：蓝线 = 手机频段（300 Hz 以上）有效值 dB；彩色竖线 = 画面事件；黑三角 = 从 sfx.wav 量出的起音；“差”= 量出的起音减预定的落点（帧）',
           fill='black', font=f22)
    mono = shape(x.mean(axis=1), 300, None, order=4)
    db, tt = rms_db(mono, 0.005)
    for k, b in enumerate(BEATS):
        cx, cy = (k % cols) * PW, 60 + (k // cols) * PH
        ta, tb = b['t0'] - 0.15, min(b['t1'] + 0.15, DUR)
        X = lambda t: cx + 20 + (t - ta) / (tb - ta) * (PW - 40)
        top, h = cy + 52, 200
        d.rectangle([cx + 20, top, cx + PW - 20, top + h], outline=(210, 210, 210))
        d.rectangle([X(b['t0']), top, X(min(b['t1'], DUR)), top + h], fill=(246, 246, 250))
        text = b['text'] or '（无字）'
        d.text((cx + 20, cy + 6), f"{b['id']}  {b['t0']:.2f}–{b['t1']:.2f} 秒  {b['scene']}" + ('  【停】' if b['stop'] else ''),
               fill=(40, 40, 90), font=f18)
        d.text((cx + 20, cy + 28), text[:30], fill=(90, 90, 90), font=f15)
        m = (tt >= ta) & (tt < tb)
        pts = [(X(t_), top + min(h, max(0, -v / 70 * h))) for t_, v in zip(tt[m], db[m])]
        if len(pts) > 1:
            d.line(pts, fill=(41, 98, 255), width=2)
        mine = [e for e in EVENTS if b['f0'] <= e['vis'] < b['f1'] or (e['beat'] == b['id'])]
        lane = 0
        lastx = -1e9
        for e in sorted(mine, key=lambda e: e['vis']):
            te = e['vis'] / FPS
            if not (ta <= te <= tb):
                continue
            col = CAT_COL[e['cat']]
            if e['cat'] == 'tex':
                d.line([X(te), top + h - 8, X(te), top + h], fill=col, width=1)
                continue
            d.line([X(te), top, X(te), top + h], fill=col, width=2 if e['cat'] in ('key', 'solo') else 1)
            if e['lead']:
                d.line([X(te + e['lead']), top + 10, X(te), top + 10], fill=col, width=2)
            if e['cat'] != 'tick':
                xx = X(te)
                lane = lane + 1 if xx - lastx < 60 else 0
                lastx = xx
                d.text((xx + 2, top + 2 + (lane % 6) * 17), e['label'][:7], fill=col, font=f15)
        mc = [e for e in chk if e['beat'] == b['id']]
        for e in mc:
            xx = X(e['meas'])
            d.polygon([(xx, top + h + 2), (xx - 5, top + h + 12), (xx + 5, top + h + 12)], fill=(0, 0, 0))
        if mc:
            worst = max(mc, key=lambda e: abs(e['err_f']))
            ok = all(abs(e['err_f']) <= 2 for e in mc)
            msg = f"核对 {len(mc)} 个落点，最大差 {worst['err_f']:+.2f} 帧（{worst['label'][:6]}）" + ('，都在 2 帧内' if ok else '，有超过 2 帧的')
        else:
            msg = '这一拍没有要核对的落点（只有环境层或很轻的细碎声）'
        d.text((cx + 20, top + h + 18), msg, fill=(0, 120, 0) if (not mc or ok) else (200, 0, 0), font=f15)
        d.text((cx + 20, top + h + 40), '、'.join(sorted({e['kind'] for e in mine if e['cat'] != 'tex'}))[:36], fill=(110, 110, 110), font=f15)
    img.save(path)


def plot_phone(meas, keyrows, path):
    W, H, L = 3200, 1150, 100
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    f16, f20, f28 = font(16), font(20), font(30)
    d.text((L, 16), '手机外放频段（300 Hz 以上）的瞬时响度 M（LUFS，400 毫秒窗，ffmpeg ebur128 量）：灰 = 整条全频，蓝 = 整条 300 Hz 以上，绿 = 环境层单独、300 Hz 以上',
           fill='black', font=f28)
    top, h, pw = 80, 560, W - L - 40
    X = lambda t: L + t / DUR * pw
    Y = lambda v: top + min(h, max(0, (-5 - v) / 55 * h))
    for lv in range(-10, -61, -10):
        d.line([L, Y(lv), L + pw, Y(lv)], fill=(232, 232, 232))
        d.text((L - 80, Y(lv) - 10), f'{lv}', fill=(140, 140, 140), font=f16)
    for b in BEATS:
        d.line([X(b['t0']), top, X(b['t0']), top + h], fill=(225, 225, 240))
        d.text((X(b['t0']) + 2, top + h + 4), b['id'], fill=(120, 120, 160), font=f16)
    for key, col in (('full', (170, 170, 170)), ('phone', (41, 98, 255)), ('amb_phone', (39, 174, 96))):
        M = meas[key]
        pts = [(X(t_), Y(v)) for t_, v in M if t_ <= DUR]
        d.line(pts, fill=col, width=2)
    for row in keyrows:
        xx = X(row['t'])
        d.line([xx, top, xx, top + h], fill=(214, 48, 49), width=1)
        d.text((xx + 3, top + 4 + (keyrows.index(row) % 4) * 18), row['label'][:6], fill=(214, 48, 49), font=f16)
    for s in range(0, 61, 5):
        d.text((X(s) - 8, top + h + 24), f'{s}s', fill=(90, 90, 90), font=f16)
    # 下：每个关键音效在手机频段比环境层高多少、高通掉了多少
    by, bh = top + h + 80, 330
    d.text((L, by - 30), '每个关键音效：红 = 手机频段里比同一时刻的环境层高多少 LU（越高越好）；灰 = 只留 300 Hz 以上后比全频低了多少 dB（越小越好）',
           fill='black', font=f20)
    n = len(keyrows)
    bw = pw / max(1, n)
    for i, row in enumerate(keyrows):
        x0 = L + i * bw
        v = max(0, row['over_amb'])
        d.rectangle([x0 + 4, by + bh - v / 40 * bh, x0 + bw * 0.45, by + bh], fill=(214, 48, 49))
        v2 = max(0, row['drop'])
        d.rectangle([x0 + bw * 0.5, by + bh - v2 / 40 * bh, x0 + bw - 4, by + bh], fill=(160, 160, 160))
        d.text((x0 + 4, by + bh - v / 40 * bh - 18), f"{row['over_amb']:.0f}", fill=(214, 48, 49), font=f16)
        d.text((x0 + bw * 0.5, by + bh - v2 / 40 * bh - 18), f"{row['drop']:.1f}", fill=(110, 110, 110), font=f16)
        d.text((x0 + 2, by + bh + 4), row['label'][:5], fill='black', font=f16)
    img.save(path)


# ======================================================================
def check(stems, gain, tmp):
    x, sr = read_wav(OUT_WAV)
    assert sr == SR and len(x) == N, (sr, len(x))
    fin = ebur(OUT_WAV)
    ln = loudnorm_json(OUT_WAV)
    pa = os.path.join(tmp, 'amb.wav')
    write_wav(pa, stems['amb'] * gain)
    pk = os.path.join(tmp, 'key.wav')
    write_wav(pk, (stems['key'] + stems['solo']) * gain)
    hp = 'highpass=f=300:poles=2,highpass=f=300:poles=2'
    meas = dict(full=fin['M'], phone=ebur(OUT_WAV, hp)['M'], amb_phone=ebur(pa, hp)['M'])
    amb_full = ebur(pa)
    key_full = ebur(pk)
    phone_I = ebur(OUT_WAV, hp)['I']
    chk = detect(x, stems)
    # 关键音效：手机频段里比环境层高多少
    keyrows = []
    for e in EVENTS:
        if e['cat'] not in ('key', 'solo') or e['kind'] in ('嗖',) and e['beat'] == 'S21':
            continue
        if e['kind'] == '噗' and e['beat'] != 'S01' or e['kind'] == '嗞':
            continue
        t = e['vis'] / FPS + e['lead']
        def mx(M, a, b):
            m = (M[:, 0] >= a) & (M[:, 0] <= b)
            return float(M[m, 1].max()) if m.any() else -120.0
        ph = mx(meas['phone'], t + 0.05, t + 0.5)
        am = mx(meas['amb_phone'], t + 0.05, t + 0.5)      # 同一时刻的环境层
        fu = mx(meas['full'], t + 0.05, t + 0.5)
        keyrows.append(dict(label=e['label'], beat=e['beat'], kind=e['kind'], t=t, phone=ph, amb=am, over_amb=ph - am, drop=fu - ph))
    os.makedirs(OUT_DIR, exist_ok=True)
    plot_overview(x, stems['amb'] * gain, chk, os.path.join(OUT_DIR, '波形对照_整条.png'))
    # 环境层冷暖：同一段环境层（没让开、没全停之前的原样），量全频、300 Hz 以上的有效值和频谱重心
    amb_seg = {}
    raw = stems['amb_raw'].mean(axis=1) * gain
    W, C = stems['W'], stems['C']
    def seg_name(tag, bid, a, b):
        ga, gb = GEN[int(a * FPS)], GEN[int(b * FPS)]
        ca = np.mean([D['coop'][GEN[f]] for f in range(int(a * FPS), int(b * FPS))])
        return f'{tag}：{bid}（{a:.2f}–{b:.2f} 秒），第 {ga}–{gb} 代，合作率约 {ca * 100:.0f}%'
    fz19 = E('S19', 'freeze')[0] / FPS
    wins = [('暖', 'S02 尾', B['S03']['t0'] - 0.9, B['S03']['t0']), ('冷', 'S16', B['S16']['t0'] + 0.2, B['S16']['t1']),
            ('回暖', 'S19', fz19 - 0.8, fz19)]
    for tag, bid, a, b in wins:
        name = seg_name(tag, bid, a, b)
        seg = raw[int(a * SR):int(b * SR)]
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        fq = np.fft.rfftfreq(len(seg), 1 / SR)
        fa, fb = int(a * FPS), int(b * FPS)
        lam = float(np.mean([W[f] * (0.8 + 24 * C[f] ** 2) for f in range(fa, fb)]))
        amb_seg[name] = dict(rms_db=round(20 * math.log10(rms(seg)), 1),
                             rms_phone_db=round(20 * math.log10(rms(shape(seg, 300, None, order=4))), 1),
                             centroid_hz=round(float(np.sum(fq * sp) / np.sum(sp))), sparks_per_s=round(lam, 1))
    plot_beats(x, chk, os.path.join(OUT_DIR, '波形对照_逐拍.png'))
    plot_phone(meas, keyrows, os.path.join(OUT_DIR, '手机频段.png'))
    rows = []
    for e in chk:
        land = beat_at(int(math.floor((e['vis'] / FPS + e['lead']) * FPS + 0.5)))['id']    # 第五版：按声音实际落在哪一拍统计
        rows.append(dict(beat=land, from_beat=e['beat'], kind=e['kind'], label=e['label'], cat=e['cat'], visual_frame=round(e['vis'], 2),
                         planned_s=round(e['vis'] / FPS + e['lead'], 4), lead_s=e['lead'], measured_s=round(e['meas'], 4),
                         err_frames=round(e['err_f'], 2), ok=abs(e['err_f']) <= 2, rise_db=round(e['snr'], 1), where=e['where'],
                         mix_err_frames=round((e['meas_mix'] - e['vis'] / FPS - e['lead']) * FPS, 2), mix_rise_db=round(e['rise_mix'], 1)))
    by_beat = {}
    for r in rows:
        bb = by_beat.setdefault(r['beat'], dict(n=0, worst=0.0, fail=0))
        bb['n'] += 1
        bb['worst'] = max(bb['worst'], abs(r['err_frames']))
        bb['fail'] += 0 if r['ok'] else 1
    leads = [r for r in rows if r['lead_s']]
    summary = dict(
        file=OUT_WAV, sr=SR, samples=N, seconds=round(N / SR, 3), channels=2,
        ebur128=dict(I=fin['I'], LRA=fin['LRA'], TP=fin['TP']),
        loudnorm=dict(input_i=float(ln['input_i']), input_tp=float(ln['input_tp']), input_lra=float(ln['input_lra'])),
        phone_I=phone_I, amb_I=amb_full['I'], key_I=key_full['I'],
        amb_M_median=float(np.median(meas['amb_phone'][meas['amb_phone'][:, 1] > -70, 1])),
        checked=len(rows), failed=sum(0 if r['ok'] else 1 for r in rows),
        key_mix=dict(n=sum(r['cat'] in ('key', 'solo') for r in rows),
                     ok=sum(r['cat'] in ('key', 'solo') and r['mix_rise_db'] >= 6 and abs(r['mix_err_frames']) <= 2 for r in rows),
                     bad=[r for r in rows if r['cat'] in ('key', 'solo') and not (r['mix_rise_db'] >= 6 and abs(r['mix_err_frames']) <= 2)]),
        mix_clear=sum(r['mix_rise_db'] >= 6 and abs(r['mix_err_frames']) <= 2 for r in rows),
        worst=max(rows, key=lambda r: abs(r['err_frames'])),
        lead_whoosh=dict(n=len(leads), measured_lead_s=[round(r['measured_s'] - r['visual_frame'] / FPS, 3) for r in leads]),
        by_beat=by_beat, key=keyrows, amb_seg=amb_seg, extra=extra_checks(stems), hits=hit_checks(x, stems, meas),
        key_band=key_band_checks(x, fin['I']), beats_ok=beat_checks(),
    )
    json.dump(dict(summary=summary, rules=RULES, events=rows), open(os.path.join(OUT_DIR, '落点核对.json'), 'w'),
              ensure_ascii=False, indent=1)
    return summary



def low_share(seg):
    """一段声音里 250 Hz 以下、1–4 kHz 各占全频能量的多少（整段直接做一次 FFT，不加窗：加窗会把段首那一下敲击压掉）。"""
    P = np.abs(np.fft.rfft(seg)) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return float(P[f < 250].sum() / P.sum()), float(P[(f >= 1000) & (f < 4000)].sum() / P.sum())


def low_share_check(seg):
    """和 tools/watch/check.py 的 band_levels 同一个算法（2048 点、半重叠、汉宁窗，功率取平均），回 250 Hz 以下占比。"""
    n = 2048
    if len(seg) < n:
        seg = np.pad(seg, (0, n - len(seg)))
    fr = np.lib.stride_tricks.sliding_window_view(seg, n)[::n // 2]
    P = (np.abs(np.fft.rfft(fr * np.hanning(n), axis=1)) ** 2).mean(axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    return float(P[f < 250].sum() / P.sum())


def review_low_share(mono, t, span=0.06):
    """第四版独立审片的口径：10 毫秒一格算有效值，比前 50 毫秒高 9 dB 以上、且高于 −40 dB 的那一格记为起音（在 t 前后 span 秒里找），
    起音后 120 毫秒加汉宁窗做 FFT，回（起音秒数, 250 Hz 以下占比, 1–4 kHz 占比）。"""
    hop = SR // 100
    k0, k1 = int((t - span) * 100), int((t + span) * 100)
    seg = mono[(k0 - 5) * hop:(k1 + 1) * hop]
    nb = len(seg) // hop
    r = np.sqrt(np.mean(seg[:nb * hop].reshape(nb, hop) ** 2, axis=1)) + 1e-12
    on = t
    for k in range(5, nb):
        if 20 * math.log10(r[k]) >= 10 * math.log10(np.mean(r[k - 5:k] ** 2)) + 9 and 20 * math.log10(r[k]) > -40:
            on = (k0 - 5 + k) / 100
            break
    w = mono[int(on * SR):int((on + 0.12) * SR)]
    P = np.abs(np.fft.rfft(w * np.hanning(len(w)))) ** 2
    f = np.fft.rfftfreq(len(w), 1 / SR)
    return on, float(P[f < 250].sum() / P.sum()), float(P[(f >= 1000) & (f < 4000)].sum() / P.sum())


def hit_checks(x, stems, meas):
    """手机外放：开场那一下（嗖＋噗＋敲击）、“和你”的咚，250 Hz 以下能量占比（成品里量）；审片点名的五处打击声按审片口径量；
    “你只有一遍”的暖音有多响、频段在哪。"""
    mono = x.mean(axis=1)
    out = {}
    g22 = E('S22', 'grabs')[-1] + 0.45 * 6
    rev = [('开场的噗', E('S01', 'grab')[0]), ('S09 走下来的脚步', E('S09', 'walkDown')[1]), ('和你：咚', E('S15', 'freeze')[0]),
           ('S18 走下来的脚步', E('S18', 'walkDown')[1]), ('S20 可手滑：啪', E('S20', 'slip') + 9.6), ('S22 最后一下抢的噗', g22),
           ('S24 方块合拢', E('S24', 'gather')[1])]
    out['审片口径（起音后 120 毫秒、汉宁窗）'] = {
        f'{name} {fr / FPS:.2f} 秒': dict(zip(('起音', '250 Hz 以下 %', '1–4 kHz %'),
                                           (lambda v: (round(v[0], 2), round(v[1] * 100, 1), round(v[2] * 100, 1)))(review_low_share(mono, fr / FPS))))
        for name, fr in rev}
    t01 = E('S01', 'grab')[0] / FPS
    t15 = E('S15', 'freeze')[0] / FPS
    for name, a, fr in (('开场（嗖＋噗＋敲）', t01 - 0.1, E('S01', 'grab')[0]), ('和你：咚＋敲', t15, E('S15', 'freeze')[0])):
        row = {}
        for w in (0.3, 0.5):
            lo, mid = low_share(mono[int(a * SR):int((a + w) * SR)])
            row[f'{a:.2f}–{a + w:.2f} 秒 250 Hz 以下'] = round(lo * 100, 1)
            row[f'{a:.2f}–{a + w:.2f} 秒 1–4 kHz'] = round(mid * 100, 1)
        seg = mono[int((fr - 2) / FPS * SR):int((fr + 3) / FPS * SR)]
        row['check.py 口径（第 N±2 帧）250 Hz 以下'] = round(low_share_check(seg) * 100, 1)
        row['峰值 dBFS'] = round(20 * math.log10(np.abs(x[int(a * SR):int((a + 0.5) * SR)]).max() + 1e-12), 1)
        out[name] = row
    # 暖音：成品的瞬时响度 M（400 毫秒窗，t 是窗的末尾）。S27–S27h 整段（含收拢的刷和那声叮）、S27h（只剩暖音）、
    # S27 前一秒各取最大值；再和全片其余地方最响的那一刻比
    M = meas['full']
    tt, vv = M[:, 0], M[:, 1]
    win = lambda a, b: (tt >= a) & (tt <= b)
    # 第七版重排：暖音垫在 S25（带走句、四盏灯）底下，S27 起收薄
    s27 = win(B['S25']['t0'] + 0.1, B['S25']['t1'] + 0.2)
    s27h = win(B['S27h']['t0'] + 0.4, B['S27h']['t1'] + 0.2)
    before = win(B['S25']['t0'] - 1.0, B['S25']['t0'])
    rest = ~win(B['S25']['t0'], B['S28']['t0'] + 0.4)
    k = int(np.argmax(np.where(rest, vv, -200)))
    a, b = pad_start() / FPS + PAD_RISE, B['S27']['t0']
    pad = stems['pad'].mean(axis=1)
    seg = pad[int(a * SR):int(b * SR)]
    lo, mid = low_share(seg)
    P = np.abs(np.fft.rfft(seg)) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    out['暖音'] = dict(M_max_S25_with_lamps=round(float(vv[s27].max()), 1), M_max_S27h_thinning=round(float(vv[s27h].max()), 1),
                       M_max_1s_before_S25=round(float(vv[before].max()), 1),
                       M_max_elsewhere=round(float(vv[k]), 1), M_max_elsewhere_at_s=round(float(tt[k]), 1),
                       louder_frames_elsewhere=int((vv[rest] > vv[s27].max()).sum()),
                       below_250_pct=round(lo * 100, 1), band_1k_2k_pct=round(float(P[(f >= 1000) & (f < 2000)].sum() / P.sum()) * 100, 1),
                       band_1k_4k_pct=round(mid * 100, 1))
    # 第五版：暖音在 S28 开头前后淡完，不盖住钟表“嘀”。暖音那一轨在“嘀”那一刻还剩多少（相对它最满时，dB）；
    # 成品 1–4 kHz 在“嘀”前 40 毫秒和“嘀”起音后 40 毫秒的有效值（dBFS）
    full_, hold_, end_ = pad_span()
    p0 = pad_start() / FPS
    clk = (B['S28']['f0'] + 2) / FPS
    pm = rms_db(pad, 0.02)
    pmax = float(pm[0].max())
    at = lambda tt_: float(pm[0][min(len(pm[0]) - 1, int(tt_ / 0.02))])
    b14 = shape(mono, 1000, 4000, order=4)
    e5, t5 = rms_db(b14, 0.005)
    mx5 = lambda a_, b_: round(float(e5[(t5 >= a_) & (t5 < b_)].max()), 1)
    out['暖音和钟表'] = dict(pad_fade_from_s=round(p0 + hold_, 2), pad_end_s=round(p0 + end_, 2), clock_s=round(clk, 3),
                         pad_at_S28_start_db=round(at(B['S28']['t0']) - pmax, 1), pad_at_clock_db=round(at(clk) - pmax, 1),
                         mix_1k4k_5ms_max_60_10ms_before_clock=mx5(clk - 0.06, clk - 0.01), clock_1k4k_5ms_max=mx5(clk, clk + 0.03))
    return out


def key_band_checks(x, I):
    """和 tools/watch/check.py 同一个口径：事件表里每个 key 点第 N±2 帧（单声道）的 1–4 kHz 电平，
    ≥ 整条响度 − 26 dB 算明显。回最弱的几个和没过的。"""
    mono = x.mean(axis=1)

    def band_levels(seg):
        n = 2048
        if len(seg) < n:
            seg = np.pad(seg, (0, n - len(seg)))
        fr = np.lib.stride_tricks.sliding_window_view(seg, n)[::n // 2]
        w = np.hanning(n)
        P = (np.abs(np.fft.rfft(fr * w, axis=1)) ** 2).mean(axis=0) * 2 / (n * np.sum(w ** 2))
        f = np.fft.rfftfreq(n, 1 / SR)
        return 10 * math.log10(P[(f >= 1000) & (f < 4000)].sum() + 1e-20)
    rows = []
    for r in json.load(open(OUT_EVENTS)):
        if not r['key']:
            continue
        seg = mono[max(0, int((r['frame'] - 2) / FPS * SR)):int((r['frame'] + 3) / FPS * SR)]
        rows.append(dict(t=r['t'], frame=r['frame'], beat=r['beat'], label=r['label'], band_db=round(band_levels(seg), 1)))
    thr = I - 26
    return dict(threshold_dbfs=round(thr, 1), n=len(rows), failed=[r for r in rows if r['band_db'] < thr],
                weakest=sorted(rows, key=lambda r: r['band_db'])[:5])


def beat_checks():
    """事件都落在自己那一拍里：事件表的 beat = 那一帧所在的拍；排它的拍不同（from_beat）的列出来；
    路线图的声音都落在 route.keys 那一帧；音轨长度 = 时间表帧数。"""
    rows = json.load(open(OUT_EVENTS))
    bad = [r for r in rows if not (0 <= r['frame'] < NF) or beat_at(r['frame'])['id'] != r['beat']]
    moved = [(r['t'], r['label'], r['from_beat'], r['beat']) for r in rows if 'from_beat' in r]
    rk = {k['f'] + ROUTE_LAND.get(k['act'], 0) for k in ROUTE if k['act'] != 'out'}
    route_rows = [r for r in rows if r['label'].startswith('路线图')]
    return dict(events=len(rows), outside_or_wrong_beat=bad, from_beat=moved,
                route=[(r['t'], r['frame'], r['label']) for r in route_rows],
                route_on_keys=all(r['frame'] in rk for r in route_rows) and len(route_rows) == len(rk),
                samples=N, frames=NF, samples_eq_frames=N == TL['frames'] * SPF)


def extra_checks(stems):
    """几项单独的自查：四盏灯的亮暗（狠那盏闷不闷）、S26 接着跑（不安的质感什么时候最紧）、细碎嗒的疏密、路线图。"""
    out = {}
    # 灯：把那四个声音用同一个种子原样再合成一遍（和成品里的一模一样），各自量 2 kHz 以上能量占比、频谱重心、衰减
    lamps = []
    for idx, e in enumerate(EVENTS):
        if e['kind'] != '灯叮':
            continue
        r = np.random.default_rng(e['seed'])
        y = e['sound'](r)[: int(0.6 * SR)]
        sp = np.abs(np.fft.rfft(y)) ** 2
        fq = np.fft.rfftfreq(len(y), 1 / SR)
        hi = 10 * math.log10(sp[fq > 2000].sum() / sp.sum())
        y = e['sound'](np.random.default_rng(e['seed']))
        edb, et = rms_db(y, 0.01)
        below = (edb < edb.max() - 20) & (et > et[np.argmax(edb)])
        t30 = round(float(et[np.argmax(below)]), 2) if below.any() else '>2.0'
        y = y[: int(0.6 * SR)]
        lamps.append(dict(label=e['label'], hi_share_db=round(hi, 1), centroid_hz=round(float((fq * sp).sum() / sp.sum())),
                          decay_20db_s=t30))
    out['四盏灯'] = lamps
    # 第七版 S26：不安的质感那一轨（细碎层里只取它）每 50 毫秒的有效值，最响落在哪；back、peak 两刻的狠人比例和紧张度
    ev = next(e for e in EVENTS if e['kind'] == '不安')
    y = ev['sound'](np.random.default_rng(ev['seed']))
    edb, et = rms_db(y, 0.05)
    t0u = E('S26', 'run')[0] / FPS
    out['S26 接着跑'] = dict(
        unease_loudest_s=round(t0u + float(et[np.argmax(edb)]), 2), peak_s=round(E('S26b', 'peak') / FPS, 2), back_s=round(E('S26b', 'back') / FPS, 2),
        unease_db_at=[(round(t0u + float(a), 2), round(float(b) - float(edb.max()), 1)) for a, b in list(zip(et, edb))[::6]],
        harsh_at_back=round(harsh_share(cycle_gen(E('S26b', 'back'))), 3), harsh_at_peak=round(harsh_share(cycle_gen(E('S26b', 'peak'))), 3),
        soft_at_S26_end=round(soft_share(cycle_gen(E('S26', 'run')[1])), 3), yellows=sum(1 for e in EVENTS if e['label'] == '点变黄'),
        reds=sum(1 for e in EVENTS if e['label'] == '点变红'))
    # 第五版：计数“嗒”全删了。还有“嗒”的只剩远景里点变色的细碎声（FLECK_BEATS）和 S24 翻色；
    # 每拍：几颗、每秒几颗、落在帧格上的占多少（不在数数：应远低于 100%）、前中后三段每秒几颗（S03 应先密后稀，跟着变色的点数）
    fl = {}
    for b in list(FLECK_BEATS) + ['S24']:
        tt = np.array(sorted(e['vis'] / FPS for e in EVENTS if e['beat'] == b and e['kind'] == '嗒'))
        if not len(tt):
            fl[b] = dict(n=0)
            continue
        f0, f1 = B[b]['f0'] / FPS, B[b]['f1'] / FPS
        th = np.linspace(f0, f1, 4)
        on_grid = float(np.mean(np.abs(tt * FPS - np.round(tt * FPS)) < 0.05))
        fl[b] = dict(n=int(len(tt)), per_s=round(len(tt) / (f1 - f0), 1), on_frame_grid_pct=round(on_grid * 100),
                     thirds_per_s=[round(float(((tt >= th[k]) & (tt < th[k + 1])).sum()) / (th[k + 1] - th[k]), 1) for k in range(3)])
    s3 = D['grid']['starters']
    ch3 = [visible_changes(GEN[f - 1], GEN[f], s3) for f in range(B['S03']['f0'], B['S03']['f1']) if GEN[f] > GEN[f - 1]]
    k3 = len(ch3) // 3
    fl['S03 每帧变色的点（前中后平均）'] = [round(float(np.mean(ch3[k * k3:(k + 1) * k3])), 1) for k in range(3)]
    out['细碎嗒（点变色）'] = fl
    out['近景里还有没有嗒'] = sorted({e['beat'] for e in EVENTS if e['kind'] == '嗒' and beat_at(int(e['vis']))['scene'] not in ('far', 'mid', 'block', 'cycle')})
    # 路线图小铃：同一个种子原样再合成一遍，量主音（600–2000 Hz 里的谱峰）、2 kHz 以上占比、降 20 dB 要多久
    rt = []
    for idx, e in enumerate(EVENTS):
        if e['kind'] not in ('路线叮', '你变红', '问'):
            continue
        y = e['sound'](np.random.default_rng(e['seed']))
        sp = np.abs(np.fft.rfft(y[: int(0.4 * SR)])) ** 2          # 不加窗：加窗会把开头那一下敲击压掉（同 low_share）
        fq = np.fft.rfftfreq(min(len(y), int(0.4 * SR)), 1 / SR)
        m = (fq > 600) & (fq < 2000)
        edb, et = rms_db(y, 0.01)
        below = (edb < edb.max() - 20) & (et > et[np.argmax(edb)])
        rt.append(dict(t=round(e['vis'] / FPS, 2), label=e['label'], peak_hz=round(float(fq[m][np.argmax(sp[m])])),
                       hi_share_db=round(10 * math.log10(sp[fq > 2000].sum() / sp.sum()), 1),
                       band_1k4k_pct=round(float(sp[(fq >= 1000) & (fq < 4000)].sum() / sp.sum()) * 100),
                       decay_20db_s=round(float(et[np.argmax(below)]), 2) if below.any() else '>1'))
    out['路线图的声音'] = rt
    reveal = [r for r in rt if r['label'].startswith('路线图') and ('亮出' in r['label'] or '淡入' in r['label'])]
    out['路线图四格一格比一格高'] = all(b['peak_hz'] > a['peak_hz'] for a, b in zip(reveal, reveal[1:]))
    return out


OUT_EVENTS = os.path.join(ROOT, 'studio', 'public', '002', 'sfx_events.json')
NAME = {'我叮': '叮', '暖叮': '叮', '上扬叮': '叮', '灯叮': '叮', '嗒': '嗒嗒', '唰收拢': '唰', '扎进去': '嗖', '滑': '嗖',
        '收拢': '刷', '推近': '嗖', '闷叮': '叮', '路线叮': '叮', '问': '叮', '你变红': '咔哒', '倒吸': '嗖', '嗞': '嗖', '退': '嗖', '重击': '咚', '不安': '嗖'}


def is_key(e):
    """事件表里的 key：抢（嗖，开场那一下连“噗”）、手滑（啪）、“和你”的咚、四声叮、S18b→S19 硬切那一声刷；第七版：S26 狠人回到三成的重击（20 声刷删了）；
    第五版加：你变红（5.6 秒“你也是”）、路线图每次亮出 / 回到一格的小铃（cat='key' 的路线叮）。快进收尾那一声叮删了。
    叠在噗、咚上的敲击层不单列 key（和它叠的那一下已经是 key）。"""
    if e['kind'] == '嗖' and e['label'].startswith('抢'):
        return True
    if e['label'] == '硬切到远景':
        return True
    if e['beat'] == 'S01' and e['kind'] == '噗':
        return True
    if e['kind'] in ('啪', '咚', '灯叮', '你变红', '重击'):
        return True
    return e['kind'] == '路线叮' and e['cat'] == 'key'


def write_events():
    """studio/public/002/sfx_events.json：每个音效的落点（t = 起音的秒数；“嗖”是比画面早 0.1 秒的那个点）。"""
    rows = []
    for e in EVENTS:
        t = e['vis'] / FPS + e['lead']
        fr = int(math.floor(t * FPS + 0.5))
        land = beat_at(fr)['id']          # beat 写声音实际落在哪一拍（tools/watch/check.py 按这个核）；排它的那一拍不同时记在 from_beat
        row = dict(t=round(t, 3), frame=fr, name=NAME.get(e['kind'], e['kind']), beat=land, key=is_key(e), label=e['label'],
                   visual_frame=round(e['vis'], 2))
        if land != e['beat']:
            row['from_beat'] = e['beat']
        rows.append(row)
    rows.sort(key=lambda r: r['t'])
    json.dump(rows, open(OUT_EVENTS, 'w'), ensure_ascii=False, indent=1)
    return rows


def main():
    mix, stems, info = render()
    os.makedirs(os.path.dirname(OUT_WAV), exist_ok=True)
    ev_rows = write_events()
    print(f"写出 {OUT_EVENTS}：{len(ev_rows)} 个落点，key {sum(r['key'] for r in ev_rows)} 个")
    with tempfile.TemporaryDirectory() as tmp:
        y, gain, gmin = master(mix, tmp)
        write_wav(OUT_WAV, y, dither=True, rng=np.random.default_rng(SEED + 1))
        s = check(stems, gain, tmp)
    print(f"写出 {OUT_WAV}：{s['seconds']} 秒，{SR} Hz，{len(EVENTS)} 个声音")
    print(f"ebur128：I {s['ebur128']['I']} LUFS，LRA {s['ebur128']['LRA']} LU，真峰值 {s['ebur128']['TP']} dBTP；"
          f"loudnorm 复核 I {s['loudnorm']['input_i']}、TP {s['loudnorm']['input_tp']}；限幅最深 {20 * math.log10(gmin):.2f} dB")
    print(f"300 Hz 以上整条 {s['phone_I']} LUFS；环境层单独 {s['amb_I']} LUFS（手机频段瞬时中位数 {s['amb_M_median']:.1f}）；关键音效单独 {s['key_I']} LUFS")
    print(f"成品里：关键音效 {s['key_mix']['n']} 个，起音听得出且差 ≤2 帧的 {s['key_mix']['ok']} 个；全部 {s['checked']} 个里 {s['mix_clear']} 个", [(r['beat'], r['label'], r['mix_err_frames'], r['mix_rise_db']) for r in s['key_mix']['bad']])
    print(f"落点（单轨上量）核对 {s['checked']} 个，超过 2 帧 {s['failed']} 个；最大差 {s['worst']['err_frames']} 帧（{s['worst']['beat']} {s['worst']['label']}）")
    print('提前的嗖（量出的起音 − 画面事件，秒）：', s['lead_whoosh']['measured_lead_s'])
    for b in BEATS:
        bb = s['by_beat'].get(b['id'])
        print(f"  {b['id']:4s} {b['t0']:5.2f}–{b['t1']:5.2f}  " + (f"{bb['n']:3d} 个落点，最大差 {bb['worst']:.2f} 帧" + (f"，超 {bb['fail']}" if bb['fail'] else '') if bb else '—'))
    for r in s['key']:
        print(f"  关键 {r['beat']} {r['label']:10s} 手机频段 {r['phone']:6.1f}  环境层 {r['amb']:6.1f}  高出 {r['over_amb']:5.1f} LU  高通掉 {r['drop']:4.1f} dB")
    for k, v in s['extra'].items():
        print('  ', k, v)
    for k, v in s['amb_seg'].items():
        print('  环境层', k, v)
    for k, v in s['hits'].items():
        print('  手机外放', k, v)
    kb = s['key_band']
    print(f"  key 点 1–4 kHz（check.py 口径，第 N±2 帧，门槛 {kb['threshold_dbfs']} dBFS）：{kb['n']} 个，没过 {len(kb['failed'])} 个；最弱",
          [(r['t'], r['label'], r['band_db']) for r in kb['weakest']])
    bo = s['beats_ok']
    print(f"  拍：{bo['events']} 个落点，落错拍 {len(bo['outside_or_wrong_beat'])} 个；from_beat {bo['from_beat']}；"
          f"路线图都在 route.keys 上 {bo['route_on_keys']}；采样数 = 帧数×1600 {bo['samples_eq_frames']}")
    for r in bo['route']:
        print('    路线图', r)


if __name__ == '__main__':
    main()
