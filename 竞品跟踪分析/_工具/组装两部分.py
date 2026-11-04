# 用法：python3 -I 组装两部分.py 报告.html 第一部分片段.html
# 把报告改成两部分：第一部分常规跟踪（新插入），第二部分对我方项目的参照（原有各章顺延编号）
import re
import sys

rp, pp = sys.argv[1], sys.argv[2]
h = open(rp, encoding="utf-8").read()
CAL, MX, PROF = open(pp, encoding="utf-8").read().split("\n<!--SPLIT-->\n")

# 1. 原第二部分各章顺延：一→五 … 七→十一（只改原有内容，第一部分稍后插入）
NUM = {"一": "五", "二": "六", "三": "七", "四": "八", "五": "九", "六": "十", "七": "十一"}
body_start = h.index('<div class="keys">')
head, body = h[:body_start], h[body_start:]
body = re.sub(r'<div class="lab">([一二三四五六七]) · ', lambda m: f'<div class="lab">{NUM[m.group(1)]} · ', body)
body = re.sub(r"第([一二三四五六七])章", lambda m: f"第{NUM[m.group(1)]}章", body)
h = head + body

# 2. 首屏结论
v0 = h.index('<div class="verdict">')
v1 = h.index('<div class="bound">')
VERDICT = '''<div class="verdict">
  <div class="vk">核心结论</div>
  <div class="vt">本期三款竞品都在推实物大奖活动和新游戏，活动节奏和主题各不相同；对我方项目，最直接的参照在弹窗收纳、游戏外触达和银行规则三处。</div>
  <div class="blk">
    <div class="bk2">本期竞品在做什么（第一部分）</div>
    <ul>
      <li><b>活动节奏各不相同：</b>豪神把「2026 豪神嘉年華」的 10 项活动排成 9/22–11/2 的日程；星城写了日期的 4 项都是储值渠道或异业合作；金好运写了日期的只有登入月曆和万圣组装活动。</li>
      <li><b>实物大奖与新游戏三款都有：</b>iPhone 18（金好运、豪神）、LG 触控屏（星城）；三款都有标「新機」「NEW」或「新品」的游戏。</li>
      <li><b>主题各不相同：</b>金好运万圣，星城中秋，豪神大甲妈公益。</li>
      <li><b>运营动态：</b>金好运公告「嘎哩迺夜市」10/22 停止营运；星城 7/1 品牌更名、10/7 版本更新；豪神把 SLOT 尊荣厅最大押分开放到 300,000（9/25–10/11）。</li>
    </ul>
  </div>
  <div class="blk">
    <div class="bk2">对我方项目（第二部分）</div>
    <div class="vl" style="margin-top:0;padding-top:0;border-top:none">
'''
# 保留原来的三行（短期候选、提案、对照）
vl0 = h.index('<div class="vl">', v0)
vl_inner_start = vl0 + len('<div class="vl">')
vl_end = h.index("</div>\n</div>", vl_inner_start)
three = h[vl_inner_start:vl_end]
VERDICT += three + "</div>\n  </div>\n</div>\n\n"
h = h[:v0] + VERDICT + h[v1:]

# 3. 第一部分
GAMES = '''<div class="gcard">
  <div class="card c1"><h3>金好运</h3><p>活动窗口 15 项，以新机宣传、爭霸榜和储值渠道活动为主；商城只加载出两档万元官网包；看得到赠礼、合成、背包，保险箱录屏中未出现。</p>
    <dl><dt>录屏</dt><dd>175 秒，账号 1 级</dd><dt>大厅入口</dt><dd>25 个（含底栏展开后 4 个）</dd><dt>活动</dt><dd>窗口里 15 项</dd><dt>商城</dt><dd>2 个分页</dd><dt>版本号</dt><dd>录屏中未出现</dd></dl></div>
  <div class="card c2"><h3>星城</h3><p>「活動快訊」15 项，写了日期的 4 项都是渠道或异业合作；商城 4 个分页、11 档 NT$1–3,000；三种币，保险箱里的星币可赠礼或到官网移转。</p>
    <dl><dt>录屏</dt><dd>66 秒，账号 1 级</dd><dt>大厅入口</dt><dd>顶栏 6、右侧分类 7、底栏 8</dd><dt>活动</dt><dd>活動 5、推薦 10</dd><dt>商城</dt><dd>4 个分页</dd><dt>版本号</dt><dd>录屏中未出现（公告 10/7 版本更新）</dd></dl></div>
  <div class="card c3"><h3>豪神娱乐城</h3><p>「最新活動」18 项，主线是「2026 豪神嘉年華」；商城 7 个分页，蓝新 10 档 NT$30–20,000 没有加送，加送集中在新手限时包；两种币，保险箱 50 级以上可用。</p>
    <dl><dt>录屏</dt><dd>105 秒，账号 1 级、普卡</dd><dt>大厅入口</dt><dd>顶栏 12、底栏 10、展开后 12</dd><dt>活动</dt><dd>窗口里 18 项，另嘉年華横幅 10 项日程</dd><dt>商城</dt><dd>7 个分页</dd><dt>版本号</dt><dd>v5.72</dd></dl></div>
</div>'''

PART1 = f'''
<div class="part" id="p1"><div class="pn">第一部分</div><h2>常规跟踪：本期竞品在做什么</h2>
<p>按固定的十二个维度，记下每款竞品本期能看到的全部内容，不论与我方项目是否相关；下期照同一维度记，对比变了什么。维度：样本、大厅与游戏、运营活动、商城与付费、福利与留存、社交与排行、经济系统、账号与安全、公告动态、品牌营销、功能入口、界面与体验。</p></div>

<section class="ch" id="r1">
  <div class="lab">一 · 本期动向</div>
  <h2>三款都在推实物大奖和新游戏；活动节奏、主题、运营动态各不相同</h2>
  <div class="trend">
    <div class="card wide"><h3>活动节奏：三款各不相同</h3>
      <div class="gl">
        <div class="gn2 g1">金好运</div><div>写了日期的只有「登入月曆」（10/1–10/31）和「限時組裝萬聖趴」（至 11/3）；活动窗口其余 13 项都没写日期</div>
        <div class="gn2 g2">星城</div><div>写了日期的 4 项都是储值渠道或异业合作，各跨约 1 至 3 个月；「行星大獎賽」写「即日起」</div>
        <div class="gn2 g3">豪神</div><div>「2026 豪神嘉年華」把 10 项活动排成 9/22–11/2 的日程；录屏日之后还有 3 项依次开始（10/12、10/23、10/24）</div>
      </div></div>
    <div class="card"><h3>实物大奖 <span class="cnt">3/3 款</span></h3>
      <div class="gl">
        <div class="gn2 g1">金好运</div><div>「限時組裝萬聖趴」写「iPhone 18送到家」；MyCard 储值「加碼抽iPhone18」</div>
        <div class="gn2 g2">星城</div><div>伏特加合作「再抽LG觸控智慧螢幕」</div>
        <div class="gn2 g3">豪神</div><div>「狂送100支iPhone18」，另有金禮盒卡、點數卡</div>
      </div></div>
    <div class="card"><h3>新游戏或新品 <span class="cnt">3/3 款</span></h3>
      <div class="gl">
        <div class="gn2 g1">金好运</div><div>金幣館 3 款标「新機」：火焰之鎖、華燈盛宴2、威鯨傳奇7 破日之神羿；活动窗口第 1 项宣传電子館新机「神來運轉」</div>
        <div class="gn2 g2">星城</div><div>推荐分页第 1 项「NEW 爆金龍」；「星幣兌換券」只在 5 款指定游戏里掉落，含爆金龍</div>
        <div class="gn2 g3">豪神</div><div>熱門里「月兔」标「NEW」；刮刮乐「射門奪金」标「新品推出」</div>
      </div></div>
    <div class="card"><h3>主题内容各不相同</h3>
      <div class="gl">
        <div class="gn2 g1">金好运</div><div>万圣：「限時組裝萬聖趴」</div>
        <div class="gn2 g2">星城</div><div>中秋：「月滿中秋夜」「月兔中秋來串場」</div>
        <div class="gn2 g3">豪神</div><div>大甲媽：「大甲媽祈福平安禮包」「鎮瀾宮大甲媽公益累積」（10/5–10/14）</div>
      </div></div>
    <div class="card"><h3>运营动态</h3>
      <div class="gl">
        <div class="gn2 g1">金好运</div><div>公告「嘎哩迺夜市」10/22 停止营运（原文写因代言人合约即将到期）；「南國育」关闭说明；「LINE登入異常」；「金卡以上贈禮服務金 0%」优惠已于 6/18 结束</div>
        <div class="gn2 g2">星城</div><div>公告「遊戲品牌更名《星城》」（7/1）；「版本更新內容－調整優化」（10/7）</div>
        <div class="gn2 g3">豪神</div><div>「所有SLOT遊戲尊榮廳最大押分開放至300000」（9/25–10/11）；大厅版本号 v5.72</div>
      </div></div>
  </div>
  <p class="note">三款都是一个像新号的账号、一段录屏所见；「录屏中未出现」不等于没有。</p>
</section>

<section class="ch" id="r2">
  <div class="lab">二 · 运营活动日历</div>
  <h2>豪神写了日期的 13 项排到 11/2，星城 4 项最长到 12/31，金好运只有 2 项写了日期</h2>
  <p class="lead">只收画面上写了起止日期的活动；没写日期的活动见第三章与各款档案。悬停横条可看日期与出处。</p>
  <div class="card">{CAL}</div>
</section>

<section class="ch" id="r3">
  <div class="lab">三 · 功能总览</div>
  <h2>三款都有汇总活动窗口、排行赛活动、实物大奖；保险箱、兑换、新手礼包等只在一到两款看到</h2>
  <p class="lead">「看过」＝录屏里看到了内容；「只见入口」＝只看到入口、没点开；「录屏中未出现」不等于没有。</p>
  <div class="card">{MX}</div>
</section>

<section class="ch" id="r4">
  <div class="lab">四 · 三款档案</div>
  <h2>每款按十二个维度记全，下期照同一维度对比</h2>
  {GAMES}
  {PROF}
</section>

<div class="part" id="p2"><div class="pn">第二部分</div><h2>对我方项目的参照</h2>
<p>从第一部分里挑出与我方弹窗、推送、标签和中期项目相关的做法，逐条对照我方现状并给出建议。</p></div>
'''
k = h.index('<div class="keys">')
h = h[:k] + PART1 + h[k:]

# 4. 目录
t0 = h.index('<nav class="toc">')
t1 = h.index("</nav>", t0) + len("</nav>")
TOC = '''<nav class="toc">
  <div class="tt">目录</div>
  <a href="#top">结论</a>
  <div class="sep"></div>
  <a href="#p1">第一部分　常规跟踪</a>
  <a class="sub" href="#r1">一　本期动向</a>
  <a class="sub" href="#r2">二　运营活动日历</a>
  <a class="sub" href="#r3">三　功能总览</a>
  <a class="sub" href="#r4">四　三款档案</a>
  <div class="sep"></div>
  <a href="#p2">第二部分　对我方项目</a>
  <a class="sub" href="#c1">五　弹窗</a>
  <a class="sub" href="#c2">六　游戏外触达</a>
  <a class="sub" href="#c3">七　每天回来的理由</a>
  <a class="sub" href="#c4">八　银行类功能</a>
  <a class="sub" href="#c5">九　商城</a>
  <a class="sub" href="#c6">十　其他发现</a>
  <a class="sub" href="#c7">十一　建议汇总</a>
  <div class="sep"></div>
  <a href="#apx">附录</a>
  <a class="sub" href="#apxA">A　样本与局限</a>
  <a class="sub" href="#apxB">B　三款画面清单</a>
  <a class="sub" href="#apxC">C　下次跟踪怎么录</a>
  <a class="sub" href="#apxD">D　做法与依据</a>
</nav>'''
h = h[:t0] + TOC + h[t1:]

# 5. 悬停提示
h = h.replace('<div id="lb">', '<div id="tip"></div>\n<div id="lb">', 1)
TIPJS = '''
  var tip=document.getElementById('tip');
  document.addEventListener('mousemove',function(e){var t=e.target.closest('[data-tip]');
    if(t){tip.textContent=t.getAttribute('data-tip');tip.style.display='block';
      var x=Math.min(e.clientX+14,window.innerWidth-380);tip.style.left=x+'px';tip.style.top=(e.clientY+16)+'px';}
    else{tip.style.display='none';}});
'''
h = h.replace("  var g=document.getElementById('gallery')", TIPJS + "  var g=document.getElementById('gallery')", 1)

# 6. 附录 D 补常规跟踪一行
h = h.replace('<tr><td class="k">对比与结论</td>',
              '<tr><td class="k">常规档案</td><td>按固定十二个维度（模板见 <code>过程/常规档案模板.md</code>）从核对过的观察记录整理三款档案，每条带帧号；再做本期动向、活动日历与功能总览</td></tr>\n      <tr><td class="k">对比与结论</td>', 1)
open(rp, "w", encoding="utf-8").write(h)
print("ok", len(h))
