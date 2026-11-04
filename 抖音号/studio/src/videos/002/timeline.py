"""《被坑多了，人会变狠吗？》（002 横屏）时间表。画面只读它生成的 timeline.json。

改字幕、挪时间点：只改这一个文件里的 BEATS / GEN / 各拍的 ev，再跑
  /Users/decheng.huang/Documents/dy/.venv/bin/python /Users/decheng.huang/Documents/dy/studio/src/videos/002/timeline.py
出处：videos/002_做好人/分镜_被坑_横屏.md 第三节（版面）、第四节（分镜表）、第五节（代数）、第七节（字号）。
字幕改过一轮（10/29，主会话按 sim/核对_被坑与改学.md 第五节定的）：
  - 只演不写：7.7、9.0、31.2、34.0、37.6、42.3 秒；
  - 缩短：14.6“坑人的分比你高”，18.7“你也坑起了老实人”，26.0“世界冷了”；
  - 47.8 带走句换成“被坑让人更想变。／变成谁，看身边谁过得比你好”（分镜第三节：句末不加句号），这一拍放长到 3.5 秒，后面顺延 0.4 秒。
  分镜原来的字幕留在 ORIG 里，只拿来比字数。
第二版（10/29 傍晚，主会话看过灰框拼图后定的）：
  - 22.4 缩成“吃掉老实人的，还有记仇的人”；21.0 缩成“你比 99% 的人分高”，这一拍放到 1.6 秒；
  - 5.4 那拍放长到 2.1 秒；“世界冷了”缩到 1.8 秒（省出的 0.8 秒给前两拍），全片 58.7 秒；
  - 24.4–28.4 镜头一直往你那颗点推，接上 28.4 的中近景（你和影子你放大，条加粗）；
  - 47.6 四个你放大，带走句字号 108；结尾慢推，“再给一次机会”“从此拉黑”先后亮起。
  - 再加四处（号主推荐参考片 41–57 的对照）：开头两句改短（473 只让计数器演）；带走句换成“狠是学来的，原谅也是”，
    挪到“你只有一遍”和结尾问题之间，配四个你；47.6 那拍只演四个你、不出字（缩到 2.6 秒）；
    结尾先出场景“朋友借钱，一直没还。”再出问题；“和你”改成从你的点连粉线到第 7 代被你坑的黄点，再定住。全片 59.7 秒。
  时间都已换成第二版的秒数。
第三版（10/29 晚，按独立审片）：
  - 倒带那一下出“你是怎么变的？”，挂到 11.5 秒（7.9–11.5 三拍同一句）；
  - 3.8 改成“老实人里，几乎都变狠过”，计数器写成“473 / 500 个老实人”；
  - 开场被抢放慢、拉远前多停 0.4 秒（0–1.6 秒）；20 条历史条那拍缩 0.25 秒（15 个字至少要 2.31 秒，缩 0.5 就读不完）；
  - 31.9 加回“身边多了以牙还牙的人”，34.7 加回“狠的人互相坑，分最低，都改了”；
  - 绿点第一次成片出现时（6.4 秒、35.5 秒）挂小标签“绿＝会原谅”；
  - 手滑那颗光点放大、落地闪一下，对面的人先愣再翻脸（14.4、20.9、37.9 秒）；
  - 11.5、13.1、17.9 三拍各放长 0.2、0.2、0.1 秒；四个你那拍（48.5，无字）缩 0.4 秒；带走句那拍只淡入一次。全片 59.95 秒。
  - 第三版定稿时删字（主会话定）：15.8“坑人的分比你高”、27.5“世界冷了”、23.9“吃掉老实人的，还有记仇的人”只演不写；
    “和你”那拍改成“吃掉他们的，也有你”（8 字），这一拍从 0.8 放到 1.25 秒（0.3 从四个你那拍挪，0.15 从 23.9 那拍挪）。
  时间都已换成第三版的秒数。

第四版（10/29 晚，解开节奏锁，按成片的独立审片 out/成片/独立审片_成片.md 改；分镜第十九节）：
  - 3.8 那拍不出字，只留计数器“变狠过 N / 500 个老实人”（审片：两层字抢眼睛）；开局 500 个老实人在这一拍亮着，其余压暗；
  - 倒带那句换成“你也狠过”；倒带后 3.6 秒压到 2.6 秒（递光点 1.3→0.8，被骗子抢 1.7→1.2；第一次被抢在 9.6 秒）；
  - 手滑那句换成“谁都会手滑，20 次滑 1 次”（审片：“每一步”看不懂，冒号句像上课）；
  - 规则提前到比分数条那拍（14.8）：“在这里，谁分高，就学谁”；中景那拍（16.9）只演；
  - 网格快进 23.9–29.6 压短：S14 2.65→2.15、S16 1.8→1.5；“吃掉他们的，也有你”换成“坑过他们的，也有你”，1.25→1.85 秒；
  - 互相报复那拍加字“一来一回，没完没了”，去掉那排 10 格；会原谅的那句换成“有人会还手，也会先停手”；
  - 473 方块那拍 +0.3 秒，20 条历史条那拍 +0.1 秒；“你只有一遍”多停 0.8 秒（新加 S27h，同一句接着挂）；
  - 结尾场景换成“约好七点，朋友没来。／再约一次，还是拉黑？”（原来“借钱一直没还”是故意坑人，不是手滑，和“误会多的世界里会原谅的赢”对不上；
    先定的“朋友放了你一次鸽子”按参考片 59 换成具体时刻）；0 秒大题“人会变狠吗”改成“你会变狠吗”（参考片 59：第一句主语是“你”）。
  全片仍是 59.95 秒（1798 帧）。秒数都已换成第四版的。

第四版补改（10/29 晚，按第四版的独立审片 out/成片/独立审片_第四版.md；分镜第十九节末尾）：
  - 结尾两个选项提前到 56.7、57.0 秒亮起（原来 57.25、57.95），整句问题露 2.9 秒；
  - “以牙还牙”在片里改叫“有来有往”（31.0 秒那句和人身上的标签）：“以牙还牙”听着就是“狠”，和“没有一个人还狠着”打架；
  - 计数器“第 N 代”改成“第 N 轮”（画面里改，这里的 GEN 还叫代）。

第五版（10/29 晚，号主看完第四版“没看懂想表达什么”；分镜第二十节，以它为准）：
  主线一句：被坑多了，人会学狠；可狠的人过得最差，后来又都学会了原谅。狠和原谅，都是跟过得好的人学的。
  - 顺着讲、不先公布结局：3.8 秒答“会。老实人里，几乎都变狠过”，5.6 秒第二行亮出“你也是”；6.4 秒问“狠下去，会怎样？”；
    “没有一个人还狠着”整句删掉，点阵只跑到第 70 代（最冷的时候）就停，再倒带回第 0 代讲你。
    第一个数用“几乎都”不用“九成”（473/500 = 94.6%），免得和 45.2 秒“九成后来学会了原谅”两个九成混在一起。
  - 路线图（ROUTE）代替“第 N 轮”计数器、历史条和开场大计数：顶上四格“老实 → 狠 → 有来有往 → 原谅”，没走到的写“？”。
    常驻小问题 3.8 秒淡出，把顶栏让给路线图；48.9 秒四个你接手，路线图退场。
  - 中段三次同一句“他过得比你好，你学了他”（14.7 学记仇、32.9 学有来有往、42.9 学会原谅），变色都压在“你学了他”读到的时候。
  - 字幕只推主线：说规则的换成处境（“谁都有失手的时候”“他就再也不对你好”）；“失手”全片一个词（不再“手滑”）；
    删掉“在这里，谁分高，就学谁”“你比 99% 的人分高”“坑过他们的，也有你”“身边多了有来有往的人”（标签写着）；
    17 秒那句改成“狠下去，／你过得比当老实人时还差”，接 6.4 秒的问题；19 秒那句改成“狠的人过得最差，一个个都改了”。
  - 骗子和记仇画成同一个红色家族，人身上的标签写“狠·只拿不给”“狠·记一辈子”（画面里改）。
  - S18 拆成 S18（有来有往的人出场，只演）和 S18b（比条、变蓝，出第二次“他过得比你好”）；S18b 画面接着画 S18（AS 表），
    事件都还挂在 S18 名下。
  - 带走句挪到四个你那拍（S25），S27b 删掉；顺序是 473 方块 → 四个你＋带走句 → 固定收尾 → 你只有一遍 → 结尾问题。
  全片 59.65 秒（1790 帧）。
第五版补改（10/29 21:00，按只看片的子代理：它说出了“狠的过得最差、原谅的过得最好”，漏了“都是学来的”）：
  - 三次“学”改成递进：14.7“他过得比你好，你学了他”→ 32.9“他过得比你好，你又学了他”→ 42.9“又一次，谁过得好，你就学谁”，
    第三次说出规律，接 48.9 的带走句（审片：一模一样的三句像原地打转）；
  - S15 不再画红线（没字看不懂），“可狠的人越来越多”接着挂；
  - 结尾两个选项同一个颜色（一绿一红等于替观众选了）；473 方块的标签改成“变狠过的老实人”（审片：“几乎都”和“473”对不上，没有分母）。
第六版（10/30，号主：“‘这是我设的世界’观众只能靠猜”；videos/002_做好人/第六版_想清楚.md）：
  - 要说的一句换成“谁都会手滑。被坑一次就记一辈子的人，最后过得最差；会还手、也肯原谅的人，最后过得最好”；
  - 要靠猜的句子改成大白话：1.6“电脑里 1000 个人，你是其中一个”（去掉白点）；“失手”统一成“手滑”，12.0 说出“他就当你坑他”；
    38.2“一次误会，就没完没了”；40.6“有人会还手，也肯先原谅一次”；带走句换成“会还手，也肯原谅的人，／最后过得最好”；
    固定收尾换成“这是电脑模拟，／我试了 20 次，都这样”“可你的人生，只有一次”。秒数没动。
第六版第二稿（10/30，两个新子代理只读字幕逐句测：两人的一句话都对上主线，标出的要猜的句子一次改完）：
  - 1.6“电脑模拟 1000 个人”（“电脑里”被猜成游戏）；8.4“从头看：你对谁都好”（没交代倒回开头）；
  - 三次“学”点名学的是谁：记仇的人／有来有往的人／会原谅的人（“他”是谁两人都卡）；S18/S18b 分界挪到 32.4；
  - 12.0“你手滑一次，／他就记你一辈子”（和主线同一个说法）；18.9“你也开始记仇了”（“坑起了老实人”说不通）；
  - 28.3“狠下去，你反而过得更差了”；34.6“一个个都不狠了”（“都改了”和后面的“九成”打架）；38.2“一次误会，两人就没完没了”；
    40.6“有人会还手，也会主动先原谅”；51.4 只留“我试了 20 次，都这样”（开头已说是电脑模拟）；53.85“你没法试 20 次，只能选一次”
    （“只有一次”被读成“模拟不作数”）。
第六版第三稿（10/30，第二轮文字测试：中年家长、刷得快的年轻人；两人的一句话都对上主线）：
  - 1.6“假如有 1000 个人”（“电脑模拟”两人都猜成打游戏，家长说最可能在这里划走），“电脑”挪到 51.4“在电脑上试了 20 次，都这样”；
  - 10.4/12.0“谁都有不小心的时候”“你只是不小心一次，／他就记你一辈子”（原句像在怪观众，年轻人说最可能在这里划走）；
  - 14.7“记仇的不吃亏，你也学了他”、28.3“人人都狠，你反而过得更差了”（两人都问“凭什么”“为什么”）；
  - 38.2“有来有往的，一次误会就没完没了”（谁跟谁，两轮都有人问）；42.9“这回，你学会了原谅”（第三遍“又学了他”两人都嫌烦）；
  - 34.6“都不狠了”、40.6“也会先原谅”各缩两个字，给每秒 4 字留余地。
第六版第四稿（10/30，第三轮文字测试：收银员、没耐心的大学生；两人的一句话都对上主线）：
  - “不小心”换成“误会”，从他那边看：10.4“可总会有误会”、12.0“一次误会，他就记你一辈子”（“你只是不小心”仍被读成怪观众）；
    38.2 加“可”；全片“误会”一条线，接结尾“朋友没来”；
  - 5.6“你大概也是”（“你也是”太冲，年轻人说最可能在这里划走）；28.3“人人都狠，互相坑，你反而更差了”（给出为什么）；
  - 34.6“后来，狠的人过得最差”（“都不狠了”太突然；后面方块交代变成了什么）；40.6“有人会还手，但时不时先原谅”（先后不清）；
  - 带走句改成结果的口气“过得最好的，／是会还手、也肯原谅的人”（原句被说“最说教”）；
  - 结尾不提电脑：“同样的事重来 20 次，都这样”“可你没法重来，只能选一次”（“假如”开头、结尾才说电脑，被说“有点被耍”；电脑留在标题和简介）。
第六版第五稿（10/30，两个新子代理看着成片逐句测：两人的一句话都对上主线；两人都说最可能在 23 秒前后划走）：
  - 世界变冷那段 22.8–28.3 压到 22.8–26.3（S14 1.6 秒、S15 1.0 秒、S16 0.9 秒，按比例缩事件），后面整体提前 2.0 秒，全片 57.65 秒；
  - 10.4 那拍不出字（“总会有误会”配的是一颗光点掉下去，两人都说对不上），12.0“一次误会，他就记你一辈子”来交代；
  - 18.9“老实人误会一次，你也记一辈子”（和 12.0 对称；原句被说重复，画面又是你在抢）；
  - 26.3“人人都狠，你比当老实人时还差”（点明影子你是当老实人时的你）；38.6“有人会还手，也肯先低头”（收银员自己的说法）；
  - 49.4“把这一切重来 20 次，都这样”（“同样的事”是什么事两人都问）；路线图最左边加“你”牌（画面里改）。
第六版第六稿（10/30，最后一轮成片测试：退休阿姨、大一新生；两人的一句话都对上主线，新生说看懂了路线图）：
  - 8.4“先看你怎么变狠的”（“从头看”被说“问了不答，倒回去重演”，这句交代倒回去看什么）；
  - 10.4 手部特写 1.6 秒压到 0.9 秒（没字的特写被说像在拖），后面整体提前 0.7 秒，全片 56.95 秒；
  - 三处“他”改“她”（画的是女的）；结尾“你没法重来，只能选一次”、方块“九成后来学会原谅”各省一字，守每秒 4 字。
第七版（10/30，照 制作工作流.md 第 0 步回头核对：第六版带走句撞了 19.4 万那条“先善良，敢还击，肯宽恕”）：
  - 带走句换成“你会变成谁，／看身边谁过得好”（和分镜第十六节原定的“狠是学来的，原谅也是”同义，更白）；
    加变异的长模拟显示“原谅赢了”不稳（8 遍 7 遍循环），“看谁过得好就学谁”在所有跑法里都成立。其余不动。
  - 第七版又改（测试两人仍读成“原谅的人赢”，和同类一样）：48.7 秒那拍 20 条彩线换成接着往下跑，
    “可新人一多，狠人又回来了”（从第 300 代接着跑、0.5% 新人，第 773 代狠人回到三成，第 840 代到 88%）；
    结论从“宽容赢”变成“好世界留不住”。S27 的 fade19 去掉，dive 从点阵扎进你。
  - 第七版重排（测试：一人说中“人会跟身边混得好的人学……原谅能赢一阵，但狠人还会回来”，一人问“到底听哪句”）：
    先 S26“可新人一多，狠人又回来了”（46.2），再 S25 带走句“你会变成谁，看身边谁过得好”（48.65）收住；
    S27/S27h 不出字（“你没法重来，只能选一次”和“你变了四次”对不上）。路线图 46.2 退场。
  - 第七版三改（测试：两人都问“新人为什么会带回狠人”；店主仍读成“会还手也肯低头的人最好”）：
    46.2 拆成两句：“原谅的世界里，好欺负的人多了”（黄色长出来）→“狠人又过得好了，大家又学狠”（红色涌回来）；
    方块上的“变狠过的老实人”去掉；扎回你 1.8 秒压到 1.0 秒。全片 58.5 秒。
    再测两人都说中“好欺负的多了、狠人又占便宜、大家又学狠”，但都说路线图退场后黄、红是谁靠猜：
    “好欺负的人”上老实人的黄，“狠人”上记仇的红，字幕自己当图例。
  （上面各版说明里的秒数是当时的，没跟着改。）

约定：
  - 时间都按秒写，脚本换成帧（30 帧/秒，四舍五入）。ev 里的时间是绝对秒数，不是拍内的相对秒数。
  - 字幕 lines：一项一行；两行的拍，第一行在上；一行的拍放在下面那一行（分镜第三节）。
    一行里要上色的字写成 [文字, 打法代码]，比如 ['再给一次机会', 'GTFT']。
  - shot：近 / 中 / 远，和分镜第四节一致；scene 是画面用哪一套组件。
  - stop：分镜里标了【停】的拍。
"""
import json
import math
import os
import re

FPS = 30
DUR = 58.5
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'timeline.json')


def F(t):
    return int(round(t * FPS))


# 结尾问题：两个选项先后出现（第三项 = 出现的秒数），没出场的字也占好位置，行不跳
# 两个选项同一个颜色（只看片的审片：一绿一红等于替观众选好了，没什么可争）
ASK = [['再约一次', 'ASK', 55.25], ['，还是', '', 55.55], ['拉黑', 'ASK', 55.55], ['？', '', 55.55]]
# 字号放大的拍（分镜第七节之外的例外）：带走句 108 px，一行，压在字幕带下沿（第五版挪到四个你那拍 S25）
SUBSTYLE = {'S25': dict(size=108, num=120, lineH=132, y0=1050 - 2 * 132)}

# —— 第五版：31 拍（S18 拆出 S18b；S27b 删掉） ——
# (id, 起, 止, 字幕行, 镜头远近, 画面组件, 【停】, 拍内事件{名字: 秒 或 [秒, 秒]})
BEATS = [
    ('S01', 0.0, 1.6, [], '近', 'open', False,
     dict(reachIn=[0.0, 0.5], whoosh=0.4, grab=[0.5, 0.85], turnAway=[0.85, 1.2], blank=0.9, worry=[1.0, 1.45])),
    ('S02', 1.6, 3.8, ['假如有 1000 个人，', '你是其中一个'], '近→远', 'pullback', False,
     dict(titleShrink=[1.6, 2.2], fadeNear=[1.6, 2.0], zoomOut=[1.6, 3.1], ringPulse=3.3)),
    # 点阵从第 0 代跑到第 70 代（之后再没有新变狠的），开局那 500 个老实人亮着，一片黄变成一片红；
    # 5.6 秒第二行“你也是”亮起，5.75 秒你那颗点的圈变红，6.05 秒路线图“狠”亮出来（错开，一次只变一处）
    ('S03', 3.8, 6.4, ['会。老实人里，几乎都变狠过', [['你大概也是', '', 5.6]]], '远', 'far', False,
     dict(routeIn=[3.8, 4.2], qOut=[3.8, 4.2], dimCrowd=[3.8, 4.2], youRed=5.75)),
    # 停在第 70 代（最冷）：其余的点回到全亮；路线图后两格的“？”跳一下
    ('S04', 6.4, 7.8, ['狠下去，会怎样？'], '远', 'far', False,
     dict(undim=[6.4, 6.9], ask=6.5)),
    ('S05', 7.8, 8.4, [], '远→近', 'rewind', False,
     dict(rewind=[7.8, 8.1], dive=[8.1, 8.4])),
    ('S06', 8.4, 9.2, ['先看你怎么变狠的'], '近', 'near', False,
     dict(gives=[8.46, 9.17])),
    ('S07', 9.2, 10.4, ['先看你怎么变狠的'], '近', 'near', False,
     dict(highlight=9.2, label=9.31, grabs=[9.52, 9.73, 9.94, 10.15], shrink=[9.55, 10.26])),
    ('S08', 10.4, 11.3, [], '近（手特写）', 'near', False,
     dict(zoomIn=[10.4, 10.53], gives=[10.5, 11.2], slipIndex=13, zoomOut=[11.2, 11.3])),
    ('S09', 11.3, 14.0, ['一次误会，她就记你一辈子'], '近', 'near', False,
     dict(pick=11.3, walkDown=[11.35, 11.8], label=11.7, giveOk=11.95, slip=12.3, stun=[12.62, 12.9], crossArms=[12.9, 13.2], grabs=[13.2, 13.45, 13.68])),
    # 第一次“他过得比你好，你学了他”：你学了记仇
    ('S10', 14.0, 16.1, ['记仇的不吃亏，你也学了她'], '近', 'near', False,
     dict(other=[14.0, 14.3], turnHead=[14.1, 14.4], bars=14.4, recolor=[15.3, 15.9])),
    ('S11', 16.1, 18.2, [], '中', 'mid', False,
     dict(zoom=[16.1, 16.41], bars=16.41)),
    ('S12', 18.2, 20.5, ['老实人误会一次，你也记一辈子'], '近', 'near', False,
     dict(giveOk=18.4, slip=18.8, stun=[19.12, 19.4], crossArms=[19.4, 19.7], grabs=[19.7, 19.9, 20.1, 20.2])),
    ('S13', 20.5, 22.1, [], '近', 'near', False,
     dict(grow=[20.5, 21.3], smirk=[20.84, 21.41])),
    ('S14', 22.1, 23.7, ['可狠的人越来越多'], '远（后段往你推）', 'far', False,
     dict(zoom=[22.1, 22.33], pushFrom=22.9)),
    # 只看片的审片：没字的红线看不懂 → 去掉连线，“可狠的人越来越多”接着挂，只留你在一片红里
    ('S15', 23.7, 24.7, ['可狠的人越来越多'], '远（推，定住 0.45 秒）', 'far', True,
     dict(lines=[23.7, 24.02], freeze=[24.02, 24.26])),
    ('S16', 24.7, 25.6, [], '远→中（一直往你推）', 'far', False,
     dict(pushTo=25.6)),
    # 回答 6.4 秒的问题，用同一个开头“狠下去”
    ('S17', 25.6, 28.2, ['人人都狠，你比当老实人时还差'], '中近', 'midYou', False,
     dict(push=[25.6, 28.2], meIn=[25.6, 26.0], ghostIn=[26.5, 26.8], ghostOut=[27.7, 28.1])),
    # S18 只演（一排变蓝、标签“有来有往”、你来我往）；比条和变蓝在 S18b，事件都挂在 S18 名下（AS 表）
    ('S18', 28.2, 29.7, [], '近', 'near', False,
     dict(rowTurn=[28.2, 28.8], label=28.85, walkDown=[28.9, 29.3], give=29.45, giveBack=29.6, grab=29.85, grabBack=30.05,
          turnHead=[30.25, 30.45], bars=30.4, recolor=[31.2, 31.6])),
    # 第二次：你学了有来有往
    ('S18b', 29.7, 31.9, ['有来有往的过得更好，你又学了她'], '近', 'near', False,
     dict()),
    ('S19', 31.9, 34.3, ['后来，狠的过得最差'], '远', 'far', False,
     dict(zoom=[31.9, 32.3], freeze=[34.0, 34.3])),
    ('S20', 34.3, 35.5, [], '远→近', 'near', True,
     dict(push=[34.3, 34.65], slip=34.8, stun=[35.12, 35.5])),
    ('S21', 35.5, 37.9, ['可有来有往的，一误会就没完没了'], '近', 'near', False,
     dict(pong=[35.6, 37.8])),
    ('S22', 37.9, 40.2, ['有人会还手，也肯先低头'], '中→近', 'near', False,
     dict(rowGreen=[37.9, 38.2], label=38.25, walkDown=[38.3, 38.6], grabs=[38.7, 39.1, 39.5], grabBacks=[38.9, 39.3], warm=39.7, pause=[39.8, 39.95], giveBack=40.0)),
    # 第三次：你学了会原谅（变色挪到“你学了他”读到的时候）
    ('S23', 40.2, 42.5, ['这回，你学会了原谅'], '近', 'near', False,
     dict(turnHead=[40.25, 40.5], bars=40.45, recolor=[41.2, 41.6], gen167=41.65, relief=[41.85, 42.25], grabsDense=[40.2, 41.65], grabsSparse=[41.65, 42.5])),
    ('S24', 42.5, 46.2, ['变狠过的人，', '九成后来学会原谅'], '远', 'block', False,
     dict(zoom=[42.5, 42.83], starters=[42.83, 43.15], gather=[43.15, 43.81], flip=[43.81, 45.55], ding=45.55)),
    # 第七版（重排）：先演“好世界留不住”，再用带走句收住（测试：反转放在最后，观众问“到底听哪句”）。
    # 第七版三改（测试：两人都问“新人为什么会带回狠人”）：S26 拆成两句，把原因演出来，不再说“新人”。
    # S26 接着跑：gather 里 473 方块散回人群、退到第 300 代的点阵（一片绿）；run 从第 300 代跑到第 750 代：
    # 好欺负的人（老实人＋不点名，同画成老实人的黄）从 0 涨到 594 人，狠人还少（157 人）。路线图在这一拍开头退场
    ('S26', 46.2, 48.6, [[['原谅的世界里，', ''], ['好欺负的人', 'ALLC'], ['多了', '']]], '远（接着跑）', 'cycle', False,
     dict(routeOut=[46.2, 46.5], gather=[46.2, 46.6], run=[46.6, 48.5])),
    # S26b 接着画 S26：run2 从第 750 代跑到第 860 代，红色涌回来；back 狠人回到三成（第 773 代），peak 最高（第 840 代，88%）；停到拍尾。
    # 第 713–845 代里有 103 代狠人平均分是各类人里最高的（sim/循环_平均分.py）
    ('S26b', 48.6, 51.0, [[['狠人', 'GRIM'], ['又过得好了，大家又学狠', '']]], '远（接着跑）', 'cycle', False,
     dict(run2=[48.6, 49.9], back=48.87, peak=49.66)),
    # 带走句配四个你，收住上一拍的反转：狠、原谅、狠又回来，都是在学过得好的人
    ('S25', 51.0, 53.5, ['你会变成谁，', '看身边谁过得好'], '近（四个你）', 'four', False,
     dict(scatter=[51.0, 51.22], appear=[51.11, 51.33], lamps=[51.36, 51.69, 52.02, 52.36])),
    # 第七版：不出字（“你没法重来，只能选一次”和“你变了四次”对不上），从四个你扎回你，接结尾问题。
    # 第七版三改：S27＋S27h 从 1.8 秒压到 1.0 秒（测试：没字只有人在走，以为片子完了）
    ('S27', 53.5, 54.1, [], '近（四个你→你）', 'endYou', False,
     dict(dive=[53.5, 53.95], pushFrom=53.95)),
    ('S27h', 54.1, 54.5, [], '近（慢推）', 'endYou', False,
     dict()),
    # fourOut：第五版这里已经没有四个你，只剩镜头平移回 0 秒构图
    ('S28', 54.5, 57.5, ['约好七点，朋友没来。', ASK], '近（慢推）', 'endYou', False,
     dict(fourOut=[54.5, 54.8], turn=[54.8, 55.5], opt1=55.25, opt2=55.55)),
    ('S29', 57.5, 58.5, ['约好七点，朋友没来。', ASK], '近（慢推）', 'endYou', True,
     dict()),
]
# 画面接着画另一拍的（第五版）：S18b 接着画 S18，S18 的事件可以落在 S18b 里
AS = {'S18b': 'S18', 'S26b': 'S26'}

# 分镜第四节原来的字幕（第一版改过的那 10 拍），只作记录；第二版又改了 21.0（原“这一代，你比 99% 的人分高”）和 22.4（原“吃掉老实人的，不只是骗子，／还有记仇的人”）
ORIG = {
    'S06': ['你对谁都好'], 'S07': ['可总有人只拿，不给'], 'S10': ['坑人的分比你高。你学了他'],
    'S12': ['后来，老实人一手滑，', '你也一直坑他'], 'S16': ['再没人当老实人了。', '满场多是狠人，世界冷了'],
    'S18': ['身边的人，渐渐成了以牙还牙。', '你又学了'], 'S19': ['狠的人分最低，一个个都改了'],
    'S21': ['你滑一下，他还一下，', '你再还一下……'], 'S23': ['他们的分最高。你也学会了原谅'],
    'S25': ['狠的人，后来过得最冷；', '肯原谅的，过得最好'],
}
ORIG_DUR = 58.5

# —— 代数（第五版不再显示“第 N 轮”，但点阵颜色、近景里谁是什么打法、冷暖都按它走）。(秒, 代, 到这一点为止怎么走) ——
# 'lin'：从上一点线性走到这一点（显示取整）；'step'：到这一秒跳成这一代；'hold'：一直停在上一代，到这一秒为止
GEN = [
    (0.0, 0, 'step'),
    (3.8, 0, 'hold'),
    (5.6, 70, 'lin'),      # S03：跑到第 70 代（第 69 代以后再没有新变狠的）
    (7.8, 70, 'hold'),     # S04：停在最冷的时候，不往后跑（不先公布结局）
    (8.1, 0, 'lin'),       # S05：倒带回第 0 代
    (8.65, 1, 'step'),
    (8.89, 2, 'step'),
    (9.14, 3, 'step'),
    (9.2, 4, 'step'),
    (16.1, 4, 'hold'),
    (16.73, 5, 'step'),
    (17.36, 6, 'step'),
    (17.99, 7, 'step'),
    (22.1, 7, 'hold'),
    (23.7, 62, 'lin'),
    (24.7, 62, 'hold'),
    (28.2, 100, 'lin'),
    (28.8, 108, 'lin'),
    (31.9, 108, 'hold'),
    (34.0, 140, 'lin'),
    (35.5, 140, 'hold'),
    (40.2, 165, 'lin'),
    (40.2, 166, 'step'),
    (41.65, 167, 'step'),
    (43.81, 167, 'hold'),
    (45.55, 300, 'lin'),
    (DUR, 297.3, 'hold'),
]
COUNTER_FROM = 3.8          # 第五版不画计数器了；留着这个字段，旧代码读得到
QUESTION = dict(text='被坑多了，你会变狠吗？', big=[0.0, 1.6], small=[1.6, 3.8])
# 第七版：S26 接着跑的代数范围（data.json 的 cycle.s[k] 是第 gen0+k 代）
CYCLE = dict(gen0=300, gen1=900,
             # 第七版三改：分两段走，(秒, 代)，两点之间线性，最后一点之后停住
             keys=[(46.6, 300), (48.5, 750), (48.6, 750), (49.9, 860)],
             soft=['ALLC', 'WSLS'])   # 这一拍里好欺负的人：都画成老实人的黄   # 第五版：小问题 3.8 秒淡出，顶栏让给路线图

# —— 第五版：路线图（顶上四格：0 老实、1 狠、2 有来有往、3 原谅）。(秒, 动作, 第几格) ——
# in：淡入，老实是当前格，没走到的格子写“？”；reveal：这一格亮出来（名字、颜色），并成为当前格；
# ask：没亮出来的“？”一起跳一下；back：倒带，当前格回到这一格（已亮出来的留着，压暗）；on：当前格换到这一格（已亮出来的）；
# out：整条退场。秒数都和画面上的事对齐（你变色、“你也是”、倒带、四个你接手）。
ROUTE_STAGES = [dict(code='ALLC', label='老实'), dict(code='HARSH', label='狠'), dict(code='TFT', label='有来有往'), dict(code='GTFT', label='原谅')]
ROUTE = [
    (3.8, 'in', 0),
    (6.05, 'reveal', 1),    # “你也是”之后：字幕 5.6 → 你那颗点变红 5.75 → 路线图 6.05，顺着视线从下往上，一次只变一处
    (6.5, 'ask', 2),        # “狠下去，会怎样？”
    (7.8, 'back', 0),       # 倒带
    (15.3, 'on', 1),        # S10 你学了记仇（变色起点）
    (31.2, 'reveal', 2),    # S18b 你学了有来有往
    (41.2, 'reveal', 3),    # S23 你学了会原谅
    (46.2, 'out', -1),      # 第七版：S26“狠人又回来了”那拍开头退场
]

# —— 分镜第三节、第七节：版面和字号（1920×1080 原片像素）——
LAYOUT = dict(
    W=1920, H=1080,
    top=dict(y0=36, y1=128, questionSize=80, questionOpacity=0.8, counterNum=96, counterWord=80, counterRight=1680),
    hist=dict(y0=146, y1=182, x0=120, x1=1680),
    stage=dict(y0=200, y1=820, x0=120, x1=1680),
    sub=dict(y0=830, lineH=110, size=88, numSize=100, cx=900, x0=190, x1=1610, maxChars=15),
    rightSafe=dict(x0=1680, y0=430),
    titleBig=132,
    tagYou=88, tagStrategy=80,
    harshCounter=dict(num=160, word=88),
    blockLabel=dict(text=88, num=100),
    far=dict(cols=50, rows=20, dot=22, gap=30, ring=96, ringStroke=8),
    mid=dict(zoom=100 / 22, dot=100, eye=18),
    near=dict(headToWaist=560, sparkCore=64, sparkGlow=128, barThick=32, barFull=400),
    cells10=90,
    block=dict(cell=26),
    hist20=dict(barH=22),
)
READ_CPS = 6.5   # 分镜：每秒约 6.5 个字


def seg_text(line):
    if isinstance(line, str):
        return line
    return ''.join(s if isinstance(s, str) else s[0] for s in line)


def read_chars(text):
    """读字量：汉字一个算一个；数字按每两位一个字算（“1000”≈2、“5%”≈1）；标点、空格、白点不算。"""
    text = text.replace('●', '')
    nums = re.findall(r'[0-9]+%?', text)
    n_num = sum(math.ceil(len(n) / 2) for n in nums)
    rest = re.sub(r'[0-9]+%?', '', text)
    n_cjk = len(re.findall(r'[一-鿿]', rest))
    return n_cjk + n_num


def doc_chars(text):
    """核对_被坑与改学.md 第五节的口径：汉字一个算 1；一串数字或字母算 1（“1000”“5%”各算 1）；标点、白点不算。"""
    text = text.replace('●', '')
    n_tok = len(re.findall(r'[0-9A-Za-z]+%?', text))
    rest = re.sub(r'[0-9A-Za-z]+%?', '', text)
    return len(re.findall(r'[\u4e00-\u9fff]', rest)) + n_tok


def width_px(line, size=88, num=100):
    """估一行的宽度：汉字和全角标点 1 em；数字 0.6 em（按 100 px）；% 0.9 em；空格 0.3 em；白点 1 em。"""
    w = 0.0
    for ch in seg_text(line):
        if ch.isdigit():
            w += 0.6 * num
        elif ch == '%':
            w += 0.9 * num
        elif ch == ' ':
            w += 0.3 * size
        elif ch == '●':
            w += 0.6 * size
        else:
            w += size
    return round(w)


def gen_keys():
    out = []
    for t, g, mode in GEN:
        out.append(dict(f=F(t), gen=g, mode=mode))
    return out


def gen_at(t):
    """和 TS 里同一个算法：给秒数，回计数器代数（取整）。"""
    keys = GEN
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(1, len(keys)):
        t1, g1, m = keys[i]
        t0, g0, _ = keys[i - 1]
        if t < t1 or (t == t1 and m != 'step'):
            if m == 'lin':
                return int(math.floor(g0 + (g1 - g0) * (t - t0) / max(1e-9, t1 - t0) + 1e-9))
            return g0
    return keys[-1][1]


def conv_line(line):
    """字幕段里的出现秒数换成帧（[文字, 颜色, 秒] → [文字, 颜色, 帧]）"""
    if isinstance(line, str):
        return line
    return [s if isinstance(s, str) else ([s[0], s[1], F(s[2])] if len(s) > 2 else list(s)) for s in line]


def ev_frames(ev):
    o = {}
    for k, v in ev.items():
        if k == 'slipIndex':          # 第几颗滑掉（序号，不是时间）
            o[k] = v
        elif isinstance(v, list):
            o[k] = [F(x) for x in v]
        else:
            o[k] = F(v)
    return o


def main():
    beats = []
    prev_end = 0.0
    problems = []
    for bid, t0, t1, lines, shot, scene, stop, ev in BEATS:
        assert abs(t0 - prev_end) < 1e-9, f'{bid} 和上一拍没接上：{prev_end} → {t0}'
        prev_end = t1
        text = ''.join(seg_text(l) for l in lines)
        chars = read_chars(text)
        need = chars / READ_CPS
        dur = t1 - t0
        cont = bool(beats) and beats[-1]['lines'] == [conv_line(l) for l in lines] and bool(lines)
        if cont:                       # 和上一拍是同一句字幕（S29 接 S28）：从上一拍开始算读字时间
            dur = t1 - beats[-1]['readFrom']
        read_from = beats[-1]['readFrom'] if cont else t0
        st = SUBSTYLE.get(bid, {})
        widths = [width_px(l, st.get('size', 88), st.get('num', 100)) for l in lines]
        for l, w in zip(lines, widths):
            if w > LAYOUT['sub']['x1'] - LAYOUT['sub']['x0']:
                problems.append(f'{bid} 一行太宽：{seg_text(l)}（约 {w} px）')
        # 第五版：AS 表里接着画这一拍的拍（S18b 接 S18），事件可以落到它们的时间里
        t1_ev = max([t1] + [b[2] for b in BEATS if AS.get(b[0]) == bid])
        for k, v in ev.items():
            vs = v if isinstance(v, list) else [v]
            if k == 'slipIndex':
                continue
            for x in vs:
                if not (t0 - 1e-9 <= x <= t1_ev + 1e-9):
                    problems.append(f'{bid} 事件 {k}={x} 不在本拍 {t0}–{t1_ev} 内')
        beats.append(dict(
            id=bid, t0=t0, t1=t1, f0=F(t0), f1=F(t1), dur=round(t1 - t0, 2), readFrom=read_from, cont=cont, **({'as': AS[bid]} if bid in AS else {}),
            lines=[conv_line(l) for l in lines], text=text, shot=shot, scene=scene, stop=stop,
            sub=SUBSTYLE.get(bid),
            ev=ev_frames(ev), ev_s=ev,
            read=dict(chars=chars, need_s=round(need, 2), have_s=round(dur, 2),
                      ok=need <= dur + 1e-9, widths=widths),
            gen=[gen_at(t0), gen_at(max(t0, t1 - 1 / FPS))],
        ))
    assert abs(prev_end - DUR) < 1e-9, f'最后一拍到 {prev_end}，应到 {DUR}'
    # 同一句连着挂好几拍（7.9–11.5 的“你是怎么变的？”）：第一拍的读字时间按整段算
    for i, bt in enumerate(beats):
        if bt['lines'] and not bt['cont']:
            j = i
            while j + 1 < len(beats) and beats[j + 1]['cont']:
                j += 1
            have = beats[j]['t1'] - bt['t0']
            bt['read']['have_s'] = round(have, 2)
            bt['read']['ok'] = bt['read']['need_s'] <= have + 1e-9
    # 字幕密度（核对第五节的口径）：每句字数摊到它露出的时间里；S29 接着 S28 的同一句，不重复算字
    def density(beat_lines, dur, title=True):
        segs = []          # (起, 止, 字数)；title=True 时把 0 秒的大题算进去（核对第五节就是这么算的）
        if title:
            segs.append((QUESTION['big'][0], QUESTION['big'][1], doc_chars(QUESTION['text']), ['__title__']))
        for bid, t0, t1, lines in beat_lines:
            if not lines:
                continue
            if segs and segs[-1][3] == lines:
                a, _, n, l = segs[-1]
                segs[-1] = (a, t1, n, l)
            else:
                segs.append((t0, t1, doc_chars(''.join(seg_text(x) for x in lines)), lines))
        total = sum(n for _, _, n, _ in segs)
        # 最密的 5 秒：0.1 秒一步滑过去
        best, best_t = 0.0, 0.0
        t = 0.0
        while t + 5 <= dur + 1e-9:
            w = sum(n * max(0.0, min(b, t + 5) - max(a, t)) / (b - a) for a, b, n, _ in segs)
            if w > best:
                best, best_t = w, t
            t = round(t + 0.1, 1)
        return dict(chars=total, per_s=round(total / dur, 2), dense5=round(best / 5, 2), dense5_at=[best_t, round(best_t + 5, 1)])

    cur = [(b['id'], b['t0'], b['t1'], b['lines']) for b in beats]
    no_text = [b for b in beats if not b['lines']]
    no_new = [b for b in beats if not b['lines'] or b['cont']]
    stats = dict(
        now=density(cur, DUR), now_no_title=density(cur, DUR, title=False),
        # 对照：分镜原版和灰框第一版（同一口径，第一版的 timeline.py 算的；分镜原版和核对第五节一致）
        orig=dict(chars=329, per_s=5.62, dense5=6.49, dense5_at=[17.4, 22.4], dur=58.5),
        v1=dict(chars=240, per_s=4.07, dense5=6.0, dense5_at=[0.0, 5.0], dur=58.9),
        v2_first8=dict(chars=232, per_s=3.95, dense5=6.0, dense5_at=[0.0, 5.0], dur=58.7),   # 第二版只改前 8 条时
        v2=dict(chars=216, per_s=3.62, dense5=5.73, dense5_at=[11.1, 16.1], dur=59.7),
        v3_before_cut=dict(chars=247, per_s=4.12, dur=59.95),   # 第三版删字之前
        v4=dict(chars=218, per_s=3.64, no_text='10/31', dur=59.95),   # 第四版（定稿，check_第四版）
        no_text_beats=dict(n=len(no_text), of=len(beats), share=round(len(no_text) / len(beats), 3),
                           time_s=round(sum(b['t1'] - b['t0'] for b in no_text), 2),
                           time_share=round(sum(b['t1'] - b['t0'] for b in no_text) / DUR, 3),
                           ids=[b['id'] for b in no_text]),
        no_new_text_beats=dict(n=len(no_new), share=round(len(no_new) / len(beats), 3),
                               time_share=round(sum(b['t1'] - b['t0'] for b in no_new) / DUR, 3),
                               ids=[b['id'] for b in no_new]),
        unreadable=[b['id'] for b in beats if not b['read']['ok']],
        reading_time_share=round(sum(b['read']['need_s'] for b in beats if not b['cont']) / DUR, 3),
    )
    # 锁节奏的验收单（现状.md）：0 秒大题算字幕；这一拍没有新出现的字幕就算无字拍；结尾【停】算无字拍
    def checklist(rows, dur):
        no_new = [r for r in rows if r['id'] != 'S01' and (not r['lines'] or r['cont'])]
        d = density([(r['id'], r['t0'], r['t1'], r['lines']) for r in rows], dur)
        return dict(dur=dur, chars=d['chars'], per_s=d['per_s'], dense5=d['dense5'], dense5_at=d['dense5_at'],
                    no_text=len(no_new), of=len(rows), share=round(len(no_new) / len(rows), 3),
                    no_text_time_share=round(sum(r['t1'] - r['t0'] for r in no_new) / dur, 3),
                    no_text_ids=[r['id'] for r in no_new],
                    ok_len=dur <= 60 + 1e-9, ok_cps=d['per_s'] <= 4 + 1e-9, ok_no_text=len(no_new) / len(rows) >= 0.3 - 1e-9,
                    ok_read=all(r['read']['ok'] for r in rows if r['lines'] and not r['cont']))
    def drop(ids):
        rows = []
        for r in beats:
            r2 = dict(r)
            if r['id'] in ids:
                r2['lines'] = []
                r2['cont'] = False
            rows.append(r2)
        return checklist(rows, DUR)
    stats['checklist'] = checklist(beats, DUR)
    tl = dict(
        stats=stats,
        title='被坑多了，你会变狠吗？（002 横屏，第五版）',
        source='videos/002_做好人/分镜_被坑_横屏.md',
        fps=FPS, frames=F(DUR), dur=DUR, readCps=READ_CPS,
        question=dict(text=QUESTION['text'], big=[F(x) for x in QUESTION['big']], small=[F(x) for x in QUESTION['small']]),
        counterFrom=F(COUNTER_FROM),
        gen=gen_keys(),
        route=dict(stages=ROUTE_STAGES, keys=[dict(f=F(t), t=t, act=a, i=i) for t, a, i in ROUTE]),
        cycle=CYCLE,
        layout=LAYOUT,
        beats=beats,
    )
    with open(OUT, 'w') as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    print(f'写出 {OUT}：{len(beats)} 拍，{tl["frames"]} 帧')
    print('拍    起–止       字数  要读  有   一行最宽')
    for b in beats:
        r = b['read']
        flag = '' if r['ok'] else '  ← 读不完'
        print(f"{b['id']}  {b['t0']:5.1f}–{b['t1']:<5.1f} {r['chars']:3d}  {r['need_s']:4.2f} {r['have_s']:4.2f}  "
              f"{max(r['widths']) if r['widths'] else 0:5d}  代 {b['gen'][0]}→{b['gen'][1]}  {b['text']}{flag}")
    for p in problems:
        print('问题：', p)
    print('验收单', json.dumps(stats['checklist'], ensure_ascii=False))


if __name__ == '__main__':
    main()
