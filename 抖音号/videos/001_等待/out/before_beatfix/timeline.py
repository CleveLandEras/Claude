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

# 插在“先选，再往下看”和“近三分之一的人选了 A”之间的三句
# 先交代实验，再说多少人怎么选（号主 10/28）
AFTER_HOOK = [
    ('emory', '2006 年，埃默里大学', 39),
    ('lab', '真的做过这个实验。', 45),
]

# 金句之后的各句：(id, 字幕, 帧数)。字幕为空表示这一句的字本身就在画面上
REST = [
    ('grades', '等成绩，', 36),
    ('offer', '等 offer，', 36),
    ('reply', '等一条消息的回复——', 54),
    ('days', '那几天，你大概也想过：', 48),
    ('badnews', '', 105),
    ('hurt', '你那么难受，', 45),
    ('notweak', '不是因为你脆弱。', 99),
    ('me', '我不用等。', 45),
    ('end', '对话一结束，我就停了；', 60),
    ('wake', '下次被叫醒，', 42),
    ('zero', '中间的时间，对我是零。', 78),
    ('lines', '你的时间是一条线，我的是一个个点。', 90),
    ('feel', '等待是什么感觉，', 57),
    ('read', '我只读到过。', 78),
    ('q1', '你等过最久的一件事，', 75),
    ('q2', '后来等到了吗？', 120),
    ('card', '', 165),
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
    }
    p1_end = 117                                          # 第一段到“你选哪个？”读完
    beats = []
    t = p1_end
    for bid, text, dur in AFTER_HOOK:                     # 埃默里大学、实验
        beats.append({'id': bid, 'text': text, 'from': t, 'dur': dur})
        t += dur
    p2_start, p2_offset = t, opening['resultAt'] - 4      # 第二段从结果那句前 4 帧接着播
    p2_end = p2_start + (opening['punchAt'] + 72 - p2_offset)
    opening.update({'p1End': p1_end, 'p2Start': p2_start, 'p2Offset': p2_offset, 'p2End': p2_end,
                    'frames': p1_end,
                    'markG': p2_start + opening['markAt'] - p2_offset, 'punchG': p2_start + opening['punchAt'] - p2_offset})
    t = p2_end
    for bid, text, dur in REST:
        beats.append({'id': bid, 'text': text, 'from': t, 'dur': dur})
        t += dur
    out = {'fps': FPS, 'frames': t, 'opening': opening, 'beats': beats}
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(OUT, f'{t} 帧 = {t / FPS:.1f} 秒')


if __name__ == '__main__':
    main()
