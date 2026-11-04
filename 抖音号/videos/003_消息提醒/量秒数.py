"""从时间表量第九版的秒数和字幕：讲为什么、教怎么做、清单屏、结尾各几秒，占比，无字拍，字幕字数和每秒字数。

  /Users/decheng.huang/Documents/dy/.venv/bin/python -I /Users/decheng.huang/Documents/dy/videos/003_消息提醒/量秒数.py

读：studio/src/videos/003/timeline9.ts（BEATS9 每拍的 part：why / teach / list / end）。只读，不改。
口径：字数不算标点和空格，“@所有人”算 1 个字（读的时候是一眼认出来的一个词）；每秒字数的分母不算清单屏那一拍（截图用，不按读速算）。
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TL = os.path.normpath(os.path.join(HERE, '..', '..', 'studio', 'src', 'videos', '003', 'timeline9.ts'))

s = open(TL, encoding='utf-8').read()
dur = float(re.search(r'export const DUR9 = ([\d.]+)', s).group(1))
beats = []
for bid, t0, t1, sub, part in re.findall(r"\{id: '(\w+)', t0: ([\d.]+), t1: ([\d.]+), sub: (\[.*?\]), part: '(\w+)'\}", s):
    text = ''.join(x for x in re.findall(r"'([^']*)'", sub) if x not in ('warm', 'gray'))
    n = len(re.sub(r'[，。：；、“”？！ ]', '', text.replace('@所有人', '@')))
    beats.append(dict(id=bid, t0=float(t0), t1=float(t1), text=text, n=n, part=part))

sec = {p: round(sum(b['t1'] - b['t0'] for b in beats if b['part'] == p), 2) for p in ('why', 'teach', 'list', 'end')}
core = sec['why'] + sec['teach']
silent = [b for b in beats if not b['text']]
list_beat = [b for b in beats if b['part'] == 'list' and b['text']]
chars = sum(b['n'] for b in beats)
chars_nolist = chars - sum(b['n'] for b in list_beat)
secs_nolist = dur - sum(b['t1'] - b['t0'] for b in list_beat)

print(f'全片 {dur} 秒，{len(beats)} 拍')
print(f'讲为什么 {sec["why"]} 秒 = 全片 {sec["why"] / dur:.1%}，不算清单屏和结尾 {sec["why"] / core:.1%}')
print(f'教怎么做 {sec["teach"]} 秒 = 全片 {sec["teach"] / dur:.1%}，不算清单屏和结尾 {sec["teach"] / core:.1%}')
print(f'清单屏（含过场）{sec["list"]} 秒，结尾 {sec["end"]} 秒')
print(f'无字幕 {len(silent)}/{len(beats)} 拍 = {len(silent) / len(beats):.0%}')
print(f'字幕 {chars} 字；不算清单屏 {chars_nolist} 字 / {secs_nolist:.1f} 秒 = {chars_nolist / secs_nolist:.2f} 字/秒')
fast = max((b for b in beats if b['n']), key=lambda b: b['n'] / (b['t1'] - b['t0']))
print(f'最快的一拍 {fast["id"]}「{fast["text"]}」{fast["n"]} 字 / {fast["t1"] - fast["t0"]:.1f} 秒 = {fast["n"] / (fast["t1"] - fast["t0"]):.1f} 字/秒')
