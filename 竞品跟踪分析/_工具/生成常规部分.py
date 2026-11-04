# 用法：python3 -I 生成常规部分.py 输出片段.html
# 生成报告第一部分「常规跟踪」：本期动向、运营活动日历、功能总览、三款档案（档案原文嵌入折叠区）
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md转html import md2html  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D0 = dt.date(2026, 9, 1)
D1 = dt.date(2026, 12, 31)
SPAN = (D1 - D0).days + 1
GAME = {"金好运": "g1", "星城": "g2", "豪神": "g3"}


def pos(d):
    return (d - D0).days / SPAN * 100


def day(m, d):
    return dt.date(2026, m, d)


# 名称、起、止、备注、帧号；起为 None 表示开始日期未写
CAL = [
    ("金好运", "「登入月曆」", day(10, 1), day(10, 31), "每日 00:00 重置", "录屏1 t0002.0"),
    ("金好运", "「限時組裝萬聖趴」", None, day(11, 3), "开始日期未写；结束日见「組裝行動」页（推断为同一活动）", "录屏1 t0119.5"),
    ("星城", "「夠烈才夠強運」", day(9, 1), day(11, 30), "异业合作", "录屏2 t0028.0"),
    ("星城", "「萊爾富儲值」", day(9, 16), day(10, 13), "储值渠道活动", "录屏2 原视频 t26.5"),
    ("星城", "「全家儲值」", day(9, 30), day(10, 27), "储值渠道活动", "录屏2 原视频 t22.5"),
    ("星城", "「悠遊付儲值」", day(10, 1), day(12, 31), "储值渠道活动", "录屏2 t0024.0"),
    ("豪神", "「無限禮包」", day(9, 22), day(10, 1), "嘉年華（只见横幅）", "录屏3 t0024.5"),
    ("豪神", "「捕魚外贈禮」", day(9, 22), day(10, 1), "嘉年華（只见横幅）", "录屏3 t0024.5"),
    ("豪神", "「登入集字」", day(9, 22), day(10, 12), "嘉年華（只见横幅）", "录屏3 t0024.5"),
    ("豪神", "「蛋蛋向前衝」", day(9, 22), day(10, 11), "嘉年華", "录屏3 t0036.0"),
    ("豪神", "「支援金升級加領」", day(9, 22), day(10, 31), "嘉年華", "录屏3 t0029.0"),
    ("豪神", "「豪運歡樂券」", day(9, 22), day(10, 31), "嘉年華", "录屏3 t0099.5"),
    ("豪神", "「生肖奪寶」", day(9, 25), day(10, 9), "嘉年華；横幅写到 10/1，录屏日仍在活动列表、底栏标「6天」，结束日判不了", "录屏3 t0024.5、t0032.5、t0101.5"),
    ("豪神", "「最大押分提升」", day(9, 25), day(10, 11), "规则调整", "录屏3 t0038.0"),
    ("豪神", "「平安禮包」", day(10, 5), day(10, 14), "大甲媽公益", "录屏3 t0040.5"),
    ("豪神", "「積分爭霸」", day(10, 8), day(10, 11), "", "录屏3 t0033.0"),
    ("豪神", "「衝等娃娃機」", day(10, 12), day(10, 22), "嘉年華（只见横幅）", "录屏3 t0024.5"),
    ("豪神", "「幸運時刻」", day(10, 23), day(11, 2), "嘉年華（只见横幅）", "录屏3 t0024.5"),
    ("豪神", "「明日驚喜禮包」", day(10, 24), day(11, 2), "嘉年華（只见横幅）", "录屏3 t0024.5"),
]
REC = day(10, 9)
EVENTS = [("金好运", "「嘎哩迺夜市」停止营运", day(10, 22), "公告：因代言人合约即将到期", "录屏1 t0031.5")]


def md(d):
    return f"{d.month}/{d.day}"


def calendar():
    o = ['<div class="cal">']
    o.append('<div class="cal-legend"><span><i class="sw g1"></i>金好运</span><span><i class="sw g2"></i>星城</span>'
             '<span><i class="sw g3"></i>豪神</span><span><i class="ev"></i>停运公告</span>'
             '<span class="mut">竖线＝录屏日 10/9；横条一端渐淡＝那一端的日期没写或判不了</span></div>')
    # 月份刻度
    o.append('<div class="cal-row cal-axis"><div class="cal-lab"></div><div class="cal-track">')
    for m, label in [(9, "9 月"), (10, "10 月"), (11, "11 月"), (12, "12 月")]:
        o.append(f'<span class="tick" style="left:{pos(day(m, 1)):.2f}%">{label}</span>')
    o.append(f'<span class="recline" style="left:{pos(REC):.2f}%"><em>录屏日</em></span></div></div>')
    for gg in ["金好运", "星城", "豪神"]:
        o.append(f'<div class="cal-group">{gg}</div>')
        for g, name, s, e, note, fr in CAL:
            if g != gg:
                continue
            s2 = s or REC
            left, width = pos(s2), (e - s2).days / SPAN * 100 + 100 / SPAN
            dates = (f"开始未写–{md(e)}" if s is None else f"{md(s)}–录屏日仍在" if "判不了" in note else f"{md(s)}–{md(e)}")
            tip = f"{g} {name}｜{dates}" + (f"｜{note}" if note else "") + f"｜{fr}"
            cls = GAME[g] + (" open" if s is None else "") + (" openend" if "判不了" in note else "")
            o.append(f'<div class="cal-row"><div class="cal-lab">{name}<span>{dates}{("　" + note) if note else ""}</span></div>'
                     f'<div class="cal-track"><span class="grid"></span><span class="recline" style="left:{pos(REC):.2f}%"></span>'
                     f'<b class="bar {cls}" style="left:{left:.2f}%;width:{width:.2f}%" data-tip="{tip}"></b></div></div>')
        for g, name, d, note, fr in EVENTS:
            if g != gg:
                continue
            tip = f"{g} {name}｜{md(d)}｜{note}｜{fr}"
            o.append(f'<div class="cal-row"><div class="cal-lab">{name}<span>{md(d)}　{note}</span></div>'
                     f'<div class="cal-track"><span class="grid"></span><span class="recline" style="left:{pos(REC):.2f}%"></span>'
                     f'<b class="evt" style="left:{pos(d):.2f}%" data-tip="{tip}"></b></div></div>')
    o.append("</div>")
    # 表格视图
    o.append('<details class="tv"><summary>表格视图</summary><table><tr><th>竞品</th><th>名称</th><th>起止</th><th>备注</th><th>帧号</th></tr>')
    for g, name, s, e, note, fr in CAL:
        dates = (f"开始未写–{md(e)}" if s is None else f"{md(s)}–录屏日仍在" if "判不了" in note else f"{md(s)}–{md(e)}")
        o.append(f"<tr><td>{g}</td><td>{name}</td><td>{dates}</td><td>{note or ''}</td><td>{fr}</td></tr>")
    for g, name, d, note, fr in EVENTS:
        o.append(f"<tr><td>{g}</td><td>{name}</td><td>{md(d)}</td><td>{note}</td><td>{fr}</td></tr>")
    o.append("</table></details>")
    return "\n".join(o)


# 功能总览：类别、功能、三款（看过／入口／—）
S, E, N = "看过", "入口", "—"
MATRIX = [
    ("大厅", "场馆或分类", "看过：金幣館、電子館、籌碼館", "看过：SLOT、特殊、魚機等 7 类", "看过：熱門、SLOT、經典、銀幣、最愛"),
    ("大厅", "彩金显示", "看过：游戏格上的 JP 金额", "入口：「彩金」分类", "看过：顶部「彩金巨獎」"),
    ("大厅", "中奖播报", "看过：跑马灯等", "看过：播报卡", "看过：红框、系统提示等"),
    ("运营活动", "汇总活动的窗口", "看过：火焰分页 15 项活动", "看过：活動 5、推薦 10", "看过：看到 18 项"),
    ("运营活动", "排行赛活动", "看过：海神、賭神、虎神爭霸榜", "看过：「行星大獎賽」每日前 100 名", "看过：「積分爭霸」横幅，只写累积分，排名规则没看到"),
    ("运营活动", "收集与合成", "看过：「組裝行動」", N, "看过：「神龍獻豪禮」集字"),
    ("运营活动", "任务或通行证", N, "看过：「任務通行證」横幅", "看过：「徽章任務」横幅"),
    ("运营活动", "刮刮乐", "入口", "入口：「Lv.50開放」", "看过"),
    ("运营活动", "乐透、宾果或摸彩", "入口：「LUCKY BINGO」", "入口：公告标题「摸彩－每日摸千萬」；另有宾果游戏「賓果行星」", "看过：「天天大樂透」"),
    ("运营活动", "储值渠道活动", "看过：4 项", "看过：4 项", N),
    ("运营活动", "异业合作或公益", N, "看过：伏特加合作", "看过：大甲媽公益"),
    ("运营活动", "实物大奖", "看过：iPhone 18", "看过：LG 触控屏", "看过：iPhone 18；另有金禮盒卡等奖品卡，是否实物画面没写"),
    ("商城", "商城分页", "看过：2 个", "看过：4 个", "看过：7 个"),
    ("商城", "新手专属礼包", N, N, "看过：「新手助力包」"),
    ("商城", "每日或每周限购包", N, "看过", N),
    ("商城", "官网专属包", "看过：2 档", N, N),
    ("商城", "卡别或 VIP 显示", "看过：赠礼页「當前VIP X」", N, "看过：「再儲值1vip值」"),
    ("福利与留存", "签到或登录领取", "看过：「登入月曆」", N, "看过：登录送彩券、周五至周日登录领钥匙"),
    ("福利与留存", "在线时长奖励", N, "看过：「每日挖寶」", N),
    ("福利与留存", "定时领取或配发", "入口：「發財金」（没点开，按名称归类）", "看过：铜币配发倒数", "看过：支援金 0 点、12 点重置"),
    ("福利与留存", "付费后每天领", N, "看过：「星城回饋卡」", "看过：「7日優惠禮」"),
    ("社交", "排行榜", "看过：「富豪榜」", "入口：「排行」", "看过：「大獎名人榜」"),
    ("社交", "公会", "入口", "入口", N),
    ("社交", "聊天", "看过：大厅聊天栏（聊天窗口没点开）", "看过：大厅「[全頻]」栏（聊天窗口没点开）", "看过：大厅聊天播报（聊天窗口没点开）"),
    ("社交", "赠礼", "看过：赠礼页", "看过：金庫页说明写保险箱星币可赠礼（没看到赠礼界面）", "入口；储值转盘写「中獎豪幣在7日內不可贈送」"),
    ("社交", "邀请或应援", N, "看过：「應援團」横幅", N),
    ("社交", "官方社群引导", N, N, "看过：「好康資訊」"),
    ("经济", "币种", "看过：金币，另有橙色币与「P」", "看过：星币、银币、铜币", "看过：豪币、银币"),
    ("经济", "保险箱", N, "看过", "看过"),
    ("经济", "货币兑换", N, "看过", "看过"),
    ("经济", "序号或兑换码", "入口：商城分页没加载出来", "看过", "看过"),
    ("经济", "背包", "看过", N, "入口"),
    ("经济", "交易记录", "入口：「贈禮紀錄」「凍結明細」按钮", N, "看过：「存摺」"),
    ("账号", "绑定提示", N, "看过：手机", "看过：手机、LINE"),
    ("账号", "防诈或安全提醒", "看过：「防詐安全提醒」公告", "入口：公告标题「反詐騙宣導」", "看过：「帳號安全提醒」弹窗，以安全为由引导绑 LINE"),
    ("公告与品牌", "公告列表", "看过：7 篇，含 2 款游戏关闭", "看过：「官網公告」6 条，只有标题", "入口：顶栏信封（没点开）"),
    ("公告与品牌", "代言人", "看过：只在停运公告里出现「代言人合約」字样", N, "看过：刮刮乐 logo「憲哥 頂刮刮」，多个活动画面用真人照片"),
    ("界面", "关闭方式", "看过：多数右上「X」；「恭喜獲得!」只有「確定」", "看过：多数右上「X」；绑定提示只有「確定」", "看过：多数右上「X」；「恭喜您」只有「領取」"),
    ("界面", "「今日不再顯示」", N, "看过", N),
    ("界面", "红点或角标", "看过：底栏、活动分页红点，看过后消失", "看过：顶栏、「推薦」红色「N」", "看过：活动分页与列表红点，看过后消失"),
    ("界面", "气泡提醒", N, "看过：「立即前往一鍵下載」", "看过：刮刮乐「獲得了新的彩券」"),
    ("界面", "加载等待", "看过：商城约 53 秒才出礼包", "看过：进功能页先「Loading」约 2–3 秒", "看过：存摺、转盘等打开时转圈"),
]


def cell(v):
    if v == N:
        return '<td class="na">录屏中未出现</td>'
    k = "s" if v.startswith("看过") else "e"
    txt = v.split("：", 1)[1] if "：" in v else ""
    head = "看过" if k == "s" else ("只见入口" if v.startswith("入口") else v)
    if k == "e" and not v.startswith("入口"):
        return f"<td>{v}</td>"
    return f'<td><span class="fm {k}">{head}</span>{(" " + txt) if txt else ""}</td>'


def matrix():
    o = ['<table class="mx"><thead><tr><th style="width:10%">类别</th><th style="width:15%">功能</th><th class="gh g1" style="width:25%">金好运</th><th class="gh g2" style="width:25%">星城</th><th class="gh g3" style="width:25%">豪神</th></tr></thead><tbody>']
    last = None
    for cat, f, a, b, c in MATRIX:
        c0 = f'<td class="k">{cat}</td>' if cat != last else '<td></td>'
        last = cat
        o.append(f"<tr>{c0}<td>{f}</td>{cell(a)}{cell(b)}{cell(c)}</tr>")
    o.append("</tbody></table>")
    return "\n".join(o)


def profiles():
    o = []
    for g, f in [("金好运", "常规档案_金好运.md"), ("星城", "常规档案_星城.md"), ("豪神娱乐城", "常规档案_豪神.md")]:
        t = open(os.path.join(ROOT, "过程", f), encoding="utf-8").read()
        # 只取十二个维度与补充：去掉文件头的建档说明、末尾的判卷处理记录
        t = t[t.index("\n## ") + 1:]
        if "\n## 判卷意见的处理" in t:
            t = t[:t.index("\n## 判卷意见的处理")]
        t = t.replace("## 补充（观察记录未记）", "## 补充")
        # 裁剪图是内部文件路径，帧号已足够定位，嵌入时去掉
        t = re.sub(r"（裁剪图?[：:]?\s*(?:`[^`]+`[、，和\s]*)+）", "", t)
        t = re.sub(r"[；，、]?\s*裁剪图?[：:]?\s*(?:`[^`]+`[、，和\s]*)+", "", t)
        lines = t.split("\n")
        o.append(f'<details class="apx prof"><summary>{g}　完整档案<span>十二个维度，每条带帧号</span></summary><div class="in md">{md2html(chr(10).join(lines))}</div></details>')
    return "\n".join(o)


if __name__ == "__main__":
    out = sys.argv[1]
    parts = {"CAL": calendar(), "MX": matrix(), "PROF": profiles()}
    open(out, "w", encoding="utf-8").write("\n<!--SPLIT-->\n".join(parts[k] for k in ["CAL", "MX", "PROF"]))
    print("ok", {k: len(v) for k, v in parts.items()})
