# 生成 商城/2026-10-29_后台怎么做.html：推导 → 原型（按运营操作顺序）→ 现有后台改动 → 功能框架 → 本期做到哪
import sys, os, html, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('fw', os.path.join(here, '功能框架_生成.py')); fw = importlib.util.module_from_spec(spec); spec.loader.exec_module(fw)
E = html.escape
GROUPS = [  # 小标题, [(编号, 图, 标题, 说明, 占满整行)]
  ('配一个周五晚累充：列表新建，填 7 步，审核后到点自动上线', [
    (1, '04_活动列表.jpg', '活动列表', '新的礼包、累充、满减、折扣活动都在这张表建和管：工具、主入口、状态、储值金额、成本进度；可复制、看数据、提前结束、下架', True),
    (2, '05_新建活动_选工具.jpg', '新建活动：选工具', '先选工具；必需四个：礼包、累充、满减、折扣', False),
    (3, '05_新建活动_基本信息.jpg', '基本信息', '名称三种语言；活动编号、点数异动科目由系统生成；说明在填完规则和时间后由系统生成', False),
    (4, '11_累充_后台配置.jpg', '工具规则：累充', '统计方式、储值渠道、档位（门槛→奖励）、领取方式；玩法逻辑只开发一次', False),
    (5, '06_对象与平台.jpg', '对象与平台', '可参与对象从系统的卡别、标签里选；排除、活动分组、平台、参与游戏', False),
    (6, '06_时间.jpg', '时间', '11/06（周五）18:00–23:59；领奖截止默认结束后 3 天', False),
    (7, '06_预算与上限.jpg', '预算与上限', '活动总成本上限，到了自动结束并通知；每人上限', False),
    (8, '07_展示与素材.jpg', '展示与素材', '版式按工具固定，只传主视觉；页签标签、角标、排序权重', False),
    (9, '07_主入口判断.jpg', '主入口判断', '主入口由系统按规则判断，运营不手选；累充进「储值活动」页签（倾向放银行，待和主管定）', False),
    (10, '07_后台预览.jpg', '预览', '竖版、横版各看一次，可切语言', False),
    (11, '08_审核页.jpg', '审核', '另一位有审核权限的人看规则摘要和成本上限，通过后到开始时间自动上架', False),
    (12, '08_进行中的活动.jpg', '进行中的活动', '可改素材、说明、延长、上调上限，改了要重新审核；规则、对象、奖励、开始时间不可改；提前结束、下架立即生效', False),
    (13, '09_活动数据.jpg', '活动数据', '每个活动一张：曝光、打开、参与、储值人数与金额、发奖成本；储值额／成本是台币除以老币，不换算，只用来比较活动', False),
  ]),
  ('礼包：选价格档、填内容，详情页按模板生成，不再每包开发', [
    (14, '10_礼包_后台配置.jpg', '工具规则：礼包', '以老子翻倍包为例：形式选单包，显示位置四处里选「超值礼包」；价格档从储值品项、产包设定选，内容（道具×数量）在这里填；限购、卡别加码', True),
    (15, '10_礼包_超值礼包详情页.jpg', '超值礼包详情页模板', '价格档从储值品项、产包设定选；内容在礼包工具里填；详情页按模板生成：主图、内容清单、价格、购买、倒计时', False),
  ]),
  ('现有页面只加选项：曝光位下拉选得到新活动，限时活动入口加两栏', [
    (16, '18_曝光位下拉选新活动.jpg', '现有大厅 Banner 页：连结位置下拉里选得到新活动', '大厅 Banner、公告「活动」分类（原热门资讯）、游戏内悬浮、推播、大厅自动弹窗首批仍在各自页面配，下拉里直接有活动配置建的活动，不用再找研发补', True),
    (17, '19_限时活动入口_加两栏.jpg', '大厅限时活动入口：加「所在页签」「右侧大图」', '现有条目靠这两栏分进新活动窗口的两个页签、显示右侧大图', True),
    (18, '02_限时活动_游戏活动.jpg', '玩家端活动窗口：游戏活动', '左列表不限个数、可滚动；右侧大图和「立即前往」', False),
    (19, '02_限时活动_平台活动.jpg', '玩家端活动窗口：平台活动', '签到、庆典、人数活动等不限游戏的活动', False),
  ]),
]
COLS = ('主管的话', '现在的实例', '所以要做', '落在后台哪里', '看图')
ROWS = [
  ('碎片化', '储值、商城类活动散在活动管理 21 个子菜单，加上储值活动设定、产包设定、好康设定', '新的礼包、累充、满减、折扣活动都在一张表建和管；21 个子菜单里的现有玩法照常用，接入新入口展示（尽量）', '活动管理下新增「活动配置」；储值活动设定的五类礼包、金流活动设定的累储停止新建', '图 1'),
  ('碎片化', '一个活动要在 3 个一级菜单、约 8 个页面各配一次', '主入口由系统自动挂；曝光位下拉直接选到。本期：活动配置 1 处，加上要用的曝光位各 1 处（最多 5 处），不用再找研发；做成勾选自动生成后（尽量）只剩 1 处', '新建活动 › 展示与素材；各曝光位页面的连结位置下拉', '图 8、9、16'),
  ('按需求独立开发', '每种玩法一套后台、客户端和需求文档', '常见储值玩法做成工具：逻辑开发一次，运营每次只填参数', '新建活动 › 选工具 › 工具规则', '图 2、4'),
  ('按需求独立开发', '超值礼包每包开一张单，研发每次做一张网页', '礼包工具＋超值礼包详情页模板：价格档从储值品项、产包设定选；内容在礼包工具里填；详情页按模板生成', '新建活动 › 礼包；玩家端详情页', '图 14、15'),
  ('复用', '卡别在每个活动里各存一份（推断），加至尊卡拆 12 张单', '用工具配的活动，卡别名单从系统读，加新卡不用开发；各活动的加码比例仍各自填。现有玩法本期仍各改，研发评审时提', '新建活动 › 对象；礼包 › 卡别加码', '图 5、14'),
  ('复用', '大厅换皮每次要客户端发版', '改成后台换素材（大厅主题包），待研发评估；评估前不画', '可行的话在活动管理下加一页「大厅主题」（建议，待研发评估）', '—'),
  ('格式', '入口、Banner、推播、排除对象、点数异动科目，每个活动各做一遍', '一套通用设置：基本信息、对象与排除、时间、预算、展示与素材，所有工具共用', '新建活动的各步', '图 3、5、6、7、8'),
  ('规范', '连结位置下拉写死，新活动要研发补（如至尊回归，限时活动、大厅自动弹窗、好康三处都缺）', '活动配置建的活动自动出现在下拉里；现有玩法（如至尊回归）要等接入新入口展示（尽量）后才自动出现', '各曝光位页面的连结位置', '图 16'),
  ('规范', '限时活动入口最多 20 个图标，同一类只能占一个', '右下改成活动窗口：游戏活动、平台活动两个页签，左列表不限个数；现有条目靠后台加的两栏分页签。「同类只能配一个」本期不改，研发评审时确认能否放开', '活动管理 › 大厅限时活动入口（加两栏）；玩家端活动窗口', '图 17、18、19'),
  ('规范', '点数异动科目每个活动都要开发', '系统按「工具名-活动编号」自动生成', '新建活动 › 基本信息', '图 3'),
  ('规范', '成本只有全局提醒，没有按活动的上限，到了也不会自动停', '每个活动设总成本上限，到了自动结束并通知；上架前另一人审核；每个活动一张数据页', '预算与上限、审核、活动数据', '图 7、11、13'),
]
CHANGES = [  # 菜单, 怎么改
  ('金流储值 › 储值品项管理 › 储值活动设定', '五类礼包（独享、三选一、每日、平台限量、专属）停止新建，已建的到期结束；储优、限时加码等在折扣上线后停建'),
  ('金流储值 › 第三方金流管理 › 金流活动设定', '累储单笔、累储累计停止新建，已建的到期结束；序号活动、礼物卡活动不变'),
  ('活动管理 › 大厅限时活动入口', '每个条目加「所在页签」（游戏活动／平台活动）和「右侧大图」（1 张）'),
  ('活动管理 › 好康设定', '好康的位置让给银行；活动列表里的条目由研发逐项接入银行、限时活动、公告，不做迁移功能；赠礼序号移到银行「序号储值」旁；活动查询（获奖名单）移到活动窗口底部；这个菜单上线后保留还是停用，研发评审时定'),
  ('公告管理 › 公告管理', '分类从「热门资讯、系统公告」改成「官方、活动、其他」：系统公告归官方，热门资讯归活动'),
  ('公告管理 › 前端大厅 Banner、游戏内悬浮活动设定、公告管理 › 活动（原热门资讯）；讯息管理 › 推播通知；活动管理 › 大厅自动弹窗管理', '连结位置下拉里直接选得到活动配置建的活动；页面本身照旧'),
  ('金流储值 › 储值品项设定、产包设定', '不变；礼包工具从这里选价格档'),
  ('系统设定 › 奖励成本预警设定', '不变（全局、只提醒），和每个活动的成本上限并存'),
  ('活动管理下其余子菜单（扭蛋机、红包夺宝、抽奖大厅等）', '照常用，不迁移；接入新入口展示（主入口判断、页签标签、排序）是尽量档'),
]
TIERS = [
  ('必需', [
    '活动配置菜单：活动列表、新建（基本信息、对象、时间、预算与上限、展示与素材、预览）、复制、审核、进行中修改、数据页、权限与操作记录',
    '工具：礼包（含超值礼包详情页模板）、累充、满减、折扣',
    '入口：主入口自动判断；各曝光位连结位置下拉可选新活动；大厅限时活动入口加两栏',
    '玩家端：银行移到左下；「储值活动」页签（累充、满减只在这里显示），倾向放银行，待和主管定；右下改成活动窗口，分游戏活动、平台活动两个页签，入口名称待和主管定；公告分官方、活动、其他',
    '现有后台：储值活动设定、金流活动设定对应类型停建；好康条目由研发逐项接入银行、限时活动、公告；公告管理改分类',
  ]),
  ('尽量', ['抽奖工具；曝光位勾选自动生成；循环时段（如每周五 18:00–23:59 自动开一期）；预估成本；测试账号预览；庆典专题页模板；现有玩法接入新入口展示']),
  ('可选', ['团购、一元夺宝（一元夺宝先确认合规）']),
  ('待研发评估', ['大厅换皮改成后台换素材、活动日历自动列出排期、敲蛋外观后台换；现有玩法改成从系统读卡别（研发评审时提）']),
]
def tree(n, d=0):
    t, k = n
    if not k: return f'<li>{E(t)}</li>'
    inner = ''.join(tree(c, d + 1) for c in k)
    if d == 0: return f'<ul class="fw">{inner}</ul>'
    return f'<li><details open><summary>{E(t)}</summary><ul>{inner}</ul></details></li>'
def table(cols, rows, cls=''):
    head = ''.join(f'<th>{E(c)}</th>' for c in cols)
    body = ''.join('<tr>' + ''.join(f'<td data-l="{E(cols[i])}"{cls_(i, cls)}>{figlinks(v) if cls == "rows" and i == 4 else E(v)}</td>' for i, v in enumerate(r)) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="cards"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
def figlinks(v):  # 「图 8、9、16」→ 每个编号链到对应图
    if not v.startswith('图 '): return E(v)
    return '图 ' + '、'.join(f'<a href="#fig{n}">{n}</a>' for n in v[2:].split('、'))
def cls_(i, cls):
    if cls == 'rows': return ' class="k"' if i == 0 else (' class="f"' if i == 4 else '')
    return ' class="m"' if i == 0 else ''
def page():
    css = """
:root{--bg:#f7f7fb;--card:#fff;--ink:#1b1d21;--ink2:#4b5058;--mute:#80858c;--line:#e1deea;--acc:#2a1d5c;--gold:#b0822a;--green:#2f6b52}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15161a;--card:#1e2026;--ink:#ecedf0;--ink2:#c3c6cc;--mute:#8c9098;--line:#33353d;--acc:#b9a8ff;--gold:#e0b257;--green:#7fc8a3}}
:root[data-theme="dark"]{--bg:#15161a;--card:#1e2026;--ink:#ecedf0;--ink2:#c3c6cc;--mute:#8c9098;--line:#33353d;--acc:#b9a8ff;--gold:#e0b257;--green:#7fc8a3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:1080px;margin:0 auto;padding:32px 16px 80px}
h1{font-size:26px;line-height:1.35;margin:0 0 8px}h2{font-size:20px;line-height:1.4;margin:52px 0 12px}h3{font-size:17px;margin:28px 0 10px;color:var(--acc)}
.sub,.lead{color:var(--ink2);margin:0 0 16px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}.kpi b{display:block;color:var(--acc);font-size:15px;margin-bottom:4px}.kpi span{color:var(--ink2);font-size:14px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;font-size:14px}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--mute);font-weight:600}
td.k{white-space:nowrap;color:var(--gold);font-weight:600}td.f{white-space:nowrap;color:var(--acc)}td.m{font-weight:600;min-width:14em}
@media (max-width:700px){
 table.cards,table.cards tbody,table.cards tr,table.cards td{display:block;width:100%}table.cards thead{display:none}
 table.cards{background:transparent;border:0}
 table.cards tr{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px 4px;margin-bottom:12px}
 table.cards td{border:0;padding:4px 12px;white-space:normal;min-width:0}
 table.cards td::before{content:attr(data-l);display:block;font-size:12px;color:var(--mute);font-weight:400}
}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:16px}
.figs .wide{grid-column:1/-1}
@media (max-width:560px){.figs{grid-template-columns:1fr}}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
figure img{width:100%;border-radius:8px;border:1px solid var(--line);display:block}
figcaption{margin-top:8px;font-size:14px;color:var(--ink2)}figcaption b{display:block;color:var(--ink)}
.fw,.fw ul{list-style:none;padding-left:18px;margin:4px 0}.fw{padding-left:0}
.fw summary{cursor:pointer;font-weight:600}.fw li{margin:3px 0}
@media (min-width:900px){.fw{columns:2;column-gap:32px}.fw>li{break-inside:avoid-column}}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px}
.tier{display:grid;grid-template-columns:7em 1fr;gap:8px 12px;padding:10px 0;border-bottom:1px solid var(--line)}.tier:last-child{border-bottom:0}
.tier ul{margin:0;padding-left:18px}.tier li{margin:2px 0}
@media (max-width:560px){.tier{grid-template-columns:1fr}}
.pend{margin:4px 0 8px}.pend b{color:var(--gold)}.pend ul{margin:6px 0 0;padding-left:20px}.pend li{margin:4px 0;color:var(--ink2)}
.tag{display:inline-block;font-size:13px;font-weight:600;padding:1px 10px;border-radius:999px;border:1px solid var(--line);color:var(--acc);height:fit-content}
a{color:var(--acc)}
"""
    groups = ''
    for title, figs in GROUPS:
        wide = ' class="wide"'
        items = ''.join(f'<figure id="fig{n}"{wide if w else ""}><a href="需求评审材料_图/{E(f)}" target="_blank"><img loading="lazy" src="需求评审材料_图/{E(f)}" alt="{E(t)}"></a><figcaption><b>图 {n}　{E(t)}</b>{E(d)}</figcaption></figure>' for n, f, t, d, w in figs)
        groups += f'<h3>{E(title)}</h3><div class="figs">{items}</div>'
    tiers = ''.join(f'<div class="tier"><span class="tag">{E(t)}</span><ul>' + ''.join(f'<li>{E(x)}</li>' for x in xs) + '</ul></div>' for t, xs in TIERS)
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>活动配置后台怎么做</title><style>{css}</style></head><body><main>
<h1>活动配置怎么做：活动管理下加一个「活动配置」，新的储值活动在这里选工具、填参数、审核后上线</h1>
<p class="sub">起点是主管写的现状：碎片化、按需求独立开发、未统一考量复用／格式／规范。</p>
<div class="kpis">
<div class="kpi"><b>新增一个菜单</b><span>活动管理 › 活动配置：活动列表、新建活动、审核、进行中修改、数据</span></div>
<div class="kpi"><b>现有后台改 6 处，不做迁移功能</b><span>两处停建旧类型；限时活动入口加两栏；各曝光位下拉加新活动；好康、公告重新分类</span></div>
<div class="kpi"><b>本期必需：四个工具＋三处玩家入口</b><span>礼包、累充、满减、折扣；「储值活动」页签、限时活动分两个页签、公告分三类</span></div>
</div>
<div class="box pend"><b>待和主管定两件，哪种结果后台和工具都不变</b><ul>
<li>「储值活动」页签放哪：A 银行（推荐：玩家付款时就看到优惠；与需求原文「好康改为金流／商城」一致）；B 右下活动窗口加第三个页签（三款竞品都这样放）。选 B 只是整个页签换位置。</li>
<li>右下入口叫什么：「活动」（推荐：窗口里也放签到等常驻活动）；「限时活动」（玩家熟悉）。</li>
</ul></div>

<h2>一、主管说的每条现状，都推到后台的一处改动</h2>
{table(COLS, ROWS, 'rows')}

<h2>二、后台长这样：运营配一个周五晚储值活动，不用找研发</h2>
<p class="lead">例：11/06（周五）18:00–23:59，累计储值满 NT$1,000 送老币福袋、满 3,000 送富贵福袋。每周五都做：首批在列表点「复制」改时间再上；每周五自动开一期的循环时段是尽量档。图上数字为示意。</p>
{groups}

<h2>三、现有后台改 6 处，不做迁移功能，其余照旧</h2>
{table(('菜单', '怎么改'), CHANGES)}

<h2>四、功能框架：新菜单、工具规则、现有后台改动</h2>
<p class="lead">脑图代码：<a href="2026-10-29_后台怎么做/功能框架_脑图.md">功能框架_脑图.md</a></p>
<div class="box">{tree(fw.ROOT)}</div>

<h2>五、本期必需：新菜单、四个工具、三处玩家入口</h2>
<div class="box">{tiers}</div>
</main></body></html>"""
if __name__ == '__main__':
    open(sys.argv[1], 'w', encoding='utf-8').write(page()); print('written')
