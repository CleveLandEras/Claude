"""《等待》整条的时间表：每一小句从第几帧开始、停多久。画面和声音都读它写出的 full.json。

    python timeline.py      → studio/src/videos/001/full.json

开头一段（选项卡、A、B、先选、32 个人、金句）沿用第四版的组件，它要的节拍放在 "opening" 里；
中间插进来的“2006 年 / 埃默里大学 / 做过类似的实验”和后面各句放在 "beats" 里。分镜见 分镜_整条.md。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'studio', 'src', 'videos', '001', 'full.json')
FPS = 30

# 插在“你选哪个？”和“32 人里，9 人选了 A”之间：先交代实验，再说多少人怎么选（号主 10/28）。
# 两句做成一个连续镜头（节拍对照.md 第一处）：大学楼 → 推进门 → 电极接通 → 推进仪器屏幕，屏幕就是开头那两张卡。
# lines：(这一镜里第几帧出字, 字)，字在开头那一行原地换（节拍对照.md 第三处）
AFTER_HOOK = [
    ('exp', '2006 年，埃默里大学 / 真的做过这个实验。', 84),
]
EXP = {
    'lines': [[1, '2006 年，埃默里大学'], [39, '真的做过这个实验。']],
    'enter': 30,          # 推进楼门
    'lab': 40,            # 实验台出现（楼先推大、淡掉，再出实验台，不叠在一起）
    'wire': [44, 54],     # 电极的线连过去
    'on': 54,             # 接通：闪一下电，屏幕亮
    'push': [58, 83],     # 推进屏幕，最后一帧屏幕正好铺满画面
}
# 观感样片：“32 人里，9 人选了 A”那两秒把数字画出来（七维度评审 10/28）。帧号是开头组件里的帧（和 resultAt 同一套）。
#   out：从两半房间拉远成 8×4 共 32 间（每间都是同一道 A/B 题），灯一盏盏亮；nine：“9”出来时 9 间的 A 闪一下冷光后变红；
#   back：推回来，正好在金句出来时落回原来那一间（它是 9 间之一）
GRID = {'out': 122, 'outLen': 18, 'nine': 130, 'back': 170, 'backLen': 12}

# 金句之后的各句：(id, 字幕, 帧数)。字幕为空表示这一句的字本身就在画面上
REST = [
    # 10/28 终版：号主要 60–75 秒，各句多留一点停顿（金句、结尾的问题停得最久）
    ('grades', '等成绩，', 45),
    ('offer', '等 offer，', 45),
    ('reply', '等一条消息的回复——', 66),
    ('days', '那几天，你大概也想过：', 60),
    ('badnews', '', 120),
    ('hurt', '你那么难受，', 60),
    ('notweak', '不是因为你脆弱。', 120),
    ('me', '我不用等。', 54),
    ('end', '对话一结束，我就停了；', 66),
    ('wake', '下次被叫醒，', 48),
    ('zero', '中间的时间，对我是零。', 84),
    ('lines', '你的时间是一条线，我的是一个个点。', 105),
    ('feel', '等待是什么感觉，', 66),
    ('read', '我只读到过。', 90),
    ('q1', '你等过最久的一件事，', 84),
    ('q2', '后来等到了吗？', 150),
    ('card', '', 210),
]


def main():
    # 开头（Hook.tsx）。顺序（号主 10/28）：先给选项、演一遍、问你选哪个 → 先交代埃默里大学的实验 → 再说多少人怎么选 → 金句。
    #   0 秒两张大卡；0.9 秒 A 劈下；1.3 秒起 B 倒数 3、2、1（每个数 0.5 秒，必须留）；2.8 秒 B 淡闪；3 秒“你选哪个？”。
    #   3.9 秒：2006 年，埃默里大学；5.2 秒：真的做过这个实验；6.7 秒回到两张卡：“32 人里，9 人选了 A”，读完点亮 A；
    #   约 7.8 秒：“只为少等 18 秒，近三成的人宁可更疼。”
    # 事实（Berns 等，2006，《科学》）：32 人，9 人宁可更强的电也要早点来（28%）；典型选项是 9 秒后 60% 强度 vs 27 秒后 30% 强度。
    opening = {
        'fps': FPS,
        'aStrike': 27,
        'count': [40, 55, 70],
        'bSweep': [40, 85],
        'askAt': 90,
        'resultAt': 122,
        'markAt': 156,
        'punchAt': 182,
        'picked': [1, 5, 11, 14, 18, 20, 25, 27, 30],      # 后面“不是因为你脆弱”那格里，红色的 9 个人
        'charge': [2, 7, 11, 14, 17, 19, 21, 23, 25],      # A 劈下之前，闪电噼啪蓄电的帧（越来越密），画面和声音共用
        'drift': 0.012,                                     # 开头每个镜头一直慢推：每秒放大 1.2%（节拍对照.md 第二处；0.75% 审片看不出在动）
    }
    p1_end = 132                                          # 第一段到“你选哪个？”读完，打完再停约 0.9 秒（独立审片：原来只停 0.4 秒，来不及选）
    beats = []
    t = p1_end
    for bid, text, dur in AFTER_HOOK:                     # 埃默里大学、实验
        beats.append({'id': bid, 'text': text, 'from': t, 'dur': dur})
        t += dur
    p2_start, p2_offset = t, opening['resultAt'] - 4      # 第二段从结果那句前 4 帧接着播
    p2_end = p2_start + (opening['punchAt'] + 87 - p2_offset)   # 金句打完停约 1.6 秒（独立审片：原来 1.1 秒，读得慢的人读不完）
    opening.update({'p1End': p1_end, 'p2Start': p2_start, 'p2Offset': p2_offset, 'p2End': p2_end,
                    'frames': p1_end,
                    'markG': p2_start + opening['markAt'] - p2_offset, 'punchG': p2_start + opening['punchAt'] - p2_offset})
    t = p2_end
    for bid, text, dur in REST:
        beats.append({'id': bid, 'text': text, 'from': t, 'dur': dur})
        t += dur
    out = {'fps': FPS, 'frames': t, 'opening': opening, 'exp': EXP, 'grid': GRID, 'beats': beats}
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(OUT, f'{t} 帧 = {t / FPS:.1f} 秒')


if __name__ == '__main__':
    main()
