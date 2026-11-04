"""一次性：呈交版版面重排（Dk 10/9「观感很差……结构性必须要很强」）。
只换样式、重组首屏与「本期范围」的排法，不改内容。原稿备份：_versions/呈交版_版面重排前_1009.html。"""
import os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, '弹窗标签推送方案_V1.html')
s = open(P, encoding='utf-8').read()

CSS = r"""
:root{
  --bg:#f3f2ee;--card:#fff;--ink:#1c1e21;--ink2:#474c53;--mute:#868b92;--line:#e3e0d9;--soft:#f8f7f3;
  --acc:#1f5f8b;--acc-l:#9cc3dc;--acc-w:#e8f1f7;--mut:#868b92;--red:#b4553a;--red-l:#e5b3a3;
  --t1:#2f7d5b;--t1w:#e2f1e9;--t2:#1f5f8b;--t2w:#e3eef6;--t3:#a1660f;--t3w:#f7ebd6;
  --warn:#a1660f;--warnw:#f7ebd6;
  --sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  --serif:"Songti SC","Noto Serif SC",Georgia,serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#141619;--card:#1c1f23;--ink:#ebeae6;--ink2:#b9bdc2;--mute:#858b93;--line:#2d3238;--soft:#181b1f;
  --acc:#78b3da;--acc-l:#35607c;--acc-w:#1a2731;--mut:#858b93;--red:#e08c72;--red-l:#6b3b2e;
  --t1:#7cc3a2;--t1w:#1b2f26;--t2:#78b3da;--t2w:#1a2731;--t3:#e0b45c;--t3w:#33291a;--warn:#e0b45c;--warnw:#33291a;}}
:root[data-theme="dark"]{
  --bg:#141619;--card:#1c1f23;--ink:#ebeae6;--ink2:#b9bdc2;--mute:#858b93;--line:#2d3238;--soft:#181b1f;
  --acc:#78b3da;--acc-l:#35607c;--acc-w:#1a2731;--mut:#858b93;--red:#e08c72;--red-l:#6b3b2e;
  --t1:#7cc3a2;--t1w:#1b2f26;--t2:#78b3da;--t2w:#1a2731;--t3:#e0b45c;--t3w:#33291a;--warn:#e0b45c;--warnw:#33291a;}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:var(--acc);text-decoration:none} a:hover{text-decoration:underline}
s{text-decoration:none}
u{text-decoration:none}

/* 顶栏 */
.top{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--card) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.top .in{max-width:1180px;margin:0 auto;padding:10px 24px;display:flex;align-items:center;gap:16px}
.top .bd{font-weight:700;font-size:15px;letter-spacing:.04em;white-space:nowrap}
.top .bd em{font-style:normal;font-weight:500;color:var(--ink2);margin-left:10px;letter-spacing:0}
.top .sp{flex:1}
.top .meta{font-size:12.5px;color:var(--mute)}
#tog{font:inherit;font-size:13px;padding:5px 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink2);cursor:pointer}
#tog:hover{border-color:var(--acc);color:var(--acc)}

/* 左侧目录 */
.toc{position:fixed;top:72px;left:max(16px,calc(50% - 590px));width:188px;font-size:13.5px;display:none}
.toc .tg0{font-size:12px;color:var(--mute);letter-spacing:.08em;margin:0 0 8px}
.toc .tg0 i{font-style:normal}
.toc a{display:block;color:var(--ink2);padding:5px 10px;border-left:2px solid var(--line);line-height:1.5}
.toc a em{font-style:normal;display:inline-block;min-width:20px;color:var(--mute);font-weight:600}
.toc a.lv1{font-weight:600;margin-top:6px}
.toc a.lv2{padding-left:22px;font-size:13px}
.toc a.on{border-left-color:var(--acc);color:var(--acc);background:var(--acc-w)}
.toc a:hover{text-decoration:none;color:var(--acc)}
@media (min-width:1180px){ .toc{display:block} .home,.doc{margin-left:max(220px,calc(50% - 370px))!important} }

/* 主栏 */
.home,.doc{max-width:860px;margin:0 auto;padding:0 24px;counter-reset:sec}
.home{padding-top:36px}
.hrow{margin:0 0 60px}
.hlab{display:flex;align-items:baseline;gap:12px;padding:0 0 10px;margin:0 0 22px;border-bottom:2px solid var(--ink)}
.hlab b{font-family:var(--serif);font-size:24px;font-weight:700}
.hlab b::before{counter-increment:sec;content:counter(sec,decimal-leading-zero);font-family:var(--sans);font-size:14px;font-weight:700;color:var(--acc);margin-right:10px;vertical-align:3px}
.hlab span{font-size:13px;color:var(--mute)}

/* 首屏 */
.hero-h{font-family:var(--serif);font-size:23px;line-height:1.55;font-weight:700;margin:0 0 18px}
.caps{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:0 0 18px}
.cap{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;color:var(--ink)}
.cap:hover{border-color:var(--acc);text-decoration:none}
.cap i{font-style:normal;font-size:12px;color:var(--acc);font-weight:700}
.cap b{display:block;font-size:14.5px;line-height:1.4;margin:2px 0}
.cap span{display:block;font-size:12.5px;color:var(--mute);line-height:1.45}
.hero-g{display:grid;grid-template-columns:1.25fr 1.25fr .9fr;gap:12px;margin:0 0 14px}
.hb{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.hb-k{font-size:12.5px;color:var(--mute);font-weight:600;letter-spacing:.04em;margin:0 0 8px}
.acc3{margin:0;padding:0;list-style:none;counter-reset:a}
.acc3 li{counter-increment:a;display:flex;gap:8px;font-size:14.5px;font-weight:600;line-height:1.5;margin:0 0 6px}
.acc3 li::before{content:counter(a);flex:none;width:20px;height:20px;border-radius:50%;background:var(--acc);color:#fff;font-size:12px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.tierbar{display:flex;height:34px;border-radius:7px;overflow:hidden;font-size:13px;font-weight:700}
.tierbar span{display:flex;align-items:center;justify-content:center;color:#fff}
.tierbar .t1{background:var(--t1)} .tierbar .t2{background:var(--t2)} .tierbar .t3{background:var(--t3)}
.hb-d{font-size:12.5px;color:var(--ink2);margin:8px 0 0;line-height:1.55}
.big{font-size:34px;font-weight:700;line-height:1.1}
.big small{font-size:16px;color:var(--mute);font-weight:500}
.hero-n{font-size:13px;color:var(--mute);margin:0 0 12px}

/* 总览表 */
.ov2{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:6px 0 0}
.ov2 .oh,.ov2>a{display:grid;grid-template-columns:40px 1.15fr 1.3fr 1fr;gap:14px;padding:12px 16px;border-bottom:1px solid var(--line)}
.ov2 .oh{background:var(--soft);font-size:12.5px;font-weight:650;color:var(--mute);padding:9px 16px}
.ov2>a{color:var(--ink);font-size:14px;line-height:1.55}
.ov2>a:hover{background:var(--acc-w);text-decoration:none}
.ov2 .n{font-family:var(--serif);font-weight:700;font-size:16px;color:var(--acc)}
.ov2 .p{display:flex;flex-direction:column-reverse;font-weight:600}
.ov2 .p s{display:inline-block;align-self:flex-start;font-size:12px!important;font-weight:650;color:var(--acc)!important;background:var(--acc-w);border-radius:999px;padding:0 9px;margin:0 0 4px}
.ov2 .s,.ov2 .l{color:var(--ink2)}
.ov2 .s s,.ov2 .l s{display:block;font-size:12px;font-weight:650;margin-top:4px}
.ov2 .s s{color:var(--t1)} .ov2 .l s{color:var(--t3)}
.ovn{padding:10px 16px;font-size:12.5px;color:var(--mute);background:var(--soft)}
.ltp{margin:0}

/* 问题块 */
.pbk{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px 24px 18px;margin:0 0 22px}
.pbk>header{display:flex;align-items:baseline;gap:12px;margin:0 0 16px}
.qn{flex:none;font-size:12.5px;font-weight:700;color:#fff;background:var(--red);border-radius:6px;padding:2px 10px;letter-spacing:.04em}
.qn.b{background:var(--acc)}
.pbk h3{font-family:var(--serif);font-size:19px;line-height:1.5;margin:0}
.ev{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);gap:22px;margin:0 0 18px}
.evf{background:var(--soft);border-radius:10px;padding:14px 16px}
.cap2{font-size:12.5px;color:var(--mute);margin:0 0 12px;line-height:1.5}
.fx{margin:0;padding:0;list-style:none}
.fx li{position:relative;padding:0 0 0 16px;margin:0 0 9px;font-size:14.5px;color:var(--ink2);line-height:1.65}
.fx li::before{content:"";position:absolute;left:2px;top:.62em;width:6px;height:6px;border-radius:50%;background:var(--red)}

/* 条形与比例 */
.sb2{display:flex;height:14px;border-radius:7px;overflow:hidden;margin:0 0 10px}
.sleg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--ink2)}
.sl{display:flex;align-items:center;gap:6px}
.sl i{width:10px;height:10px;border-radius:3px;display:inline-block}
.sl i.u{background:repeating-linear-gradient(45deg,var(--t3) 0 2px,transparent 2px 5px);border:1px solid var(--t3)}
.cbar{display:grid;grid-template-columns:96px 1fr auto;align-items:center;gap:10px;margin:0 0 10px}
.cbar .cl{font-size:13px;color:var(--ink2);line-height:1.35}
.cbar .cl s{display:block;font-size:11.5px;color:var(--mute)}
.cbar .ct{position:relative;height:12px;background:var(--line);border-radius:6px;overflow:hidden}
.cbar .ct i{position:absolute;left:0;top:0;bottom:0;background:var(--acc);border-radius:6px}
.cbar .ct b{position:absolute;top:0;bottom:0;background:var(--acc-l)}
.cbar .ct b.u{background:repeating-linear-gradient(45deg,var(--t3) 0 2px,transparent 2px 5px)}
.cbar.wv .ct i{background:var(--red)}
.cbar.r .ct i{background:var(--red)}
.cbar .cv{font-size:13.5px;font-weight:700;white-space:nowrap;text-align:right}
.cbar .cv s{display:block;font-size:11.5px;font-weight:500;color:var(--mute)}
.ring{display:flex;align-items:center;gap:16px}
.ring svg{width:92px;height:92px;transform:rotate(-90deg);flex:none}
.ring .tk{fill:none;stroke:var(--line);stroke-width:5}
.ring .vl{fill:none;stroke:var(--red);stroke-width:5;stroke-linecap:round}
.rv{font-size:30px;font-weight:700;line-height:1.1}
.rv u{font-size:16px;margin-left:2px}
.rd{font-size:13px;color:var(--ink2);margin-top:4px}

/* 改动清单 */
.chg{border-top:1px solid var(--line);padding:14px 0 0}
.ck2{font-size:12.5px;font-weight:700;color:var(--mute);letter-spacing:.08em;margin:0 0 8px}
.crs{display:flex;flex-direction:column}
.cr{display:grid;grid-template-columns:48px minmax(150px,210px) 1fr;gap:12px;align-items:baseline;padding:9px 0;border-bottom:1px dashed var(--line);font-size:14px}
.cr:last-child{border-bottom:none}
.cr .ty{font-size:12px;font-weight:700;text-align:center;border-radius:5px;padding:1px 0;color:var(--ink2);background:var(--soft);border:1px solid var(--line)}
.cr.n .ty{color:var(--acc);background:var(--acc-w);border-color:transparent}
.cr.w .ty{color:#fff;background:var(--acc);border-color:transparent}
.cr b{font-weight:650;line-height:1.5}
.cr .ef{color:var(--ink2);line-height:1.6}
.lv{font-style:normal;display:inline-block;font-size:11.5px;font-weight:700;border-radius:999px;padding:0 8px;margin-left:8px;vertical-align:1px;white-space:nowrap;background:var(--soft);color:var(--ink2)}
.lv.t1{background:var(--t1w);color:var(--t1)} .lv.t2{background:var(--t2w);color:var(--t2)} .lv.t3{background:var(--t3w);color:var(--t3)}

/* 展开明细 */
details.pf{margin:14px 0 0;border-top:1px solid var(--line)}
details.pf>summary{list-style:none;cursor:pointer;padding:12px 0 2px;font-size:13.5px;font-weight:600;color:var(--acc)}
details.pf>summary::-webkit-details-marker{display:none}
details.pf>summary::before{content:"＋";display:inline-block;width:20px;font-weight:700}
details.pf[open]>summary::before{content:"－"}
.pfb{display:flex;flex-direction:column;gap:14px;padding:12px 0 4px}
.dt1{border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.dt1 h5{font-size:14.5px;margin:0 0 8px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.dt1 h5 span{font-size:12px;font-weight:500;color:var(--mute)}
.dt1.lt{border-color:var(--t3);background:var(--t3w)}
.dl2{display:grid;grid-template-columns:108px 1fr;gap:6px 14px;margin:0;font-size:14px}
.dl2 dt{color:var(--mute);font-weight:600}
.dl2 dd{margin:0;color:var(--ink2);line-height:1.6}
.dbx{border-radius:10px;padding:12px 16px;background:var(--soft)}
.dbx.sg2{background:var(--t1w)}
.dbx .dbk{font-size:13px;font-weight:700;margin:0 0 6px;color:var(--ink)}
.dbx ul{margin:0;padding-left:1.2em;font-size:14px;color:var(--ink2)}
.dbx li{margin:3px 0}
.dbx p{margin:3px 0;font-size:14px;color:var(--ink2)}
.dbx.pr{display:flex;flex-direction:column;gap:8px;background:transparent;border:1px solid var(--line)}
.prr{display:grid;grid-template-columns:76px 1fr;gap:12px;align-items:baseline}
.prr em{font-style:normal;font-size:12px;font-weight:700;text-align:center;border-radius:5px;padding:1px 0;background:var(--soft);color:var(--ink2)}
.prr em.w{background:var(--warnw);color:var(--warn)}
.prr em.b{background:var(--acc-w);color:var(--acc)}
.prr p{margin:0 0 3px;font-size:14px;color:var(--ink2)}
.src{display:flex;flex-wrap:wrap;gap:6px;font-size:12.5px;color:var(--mute);margin:4px 0 0}
.src a{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:1px 10px;background:var(--card)}
.tn{font-size:12.5px;color:var(--mute);margin:8px 0 0}

/* 本期范围 */
.opts{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 16px}
.opt{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--soft)}
.opt .ok{font-size:14.5px;font-weight:700;display:flex;align-items:center;gap:8px}
.opt .ov{font-size:22px;font-weight:700;margin:4px 0 2px}
.opt .od{font-size:12.5px;color:var(--ink2);line-height:1.5}
.opt.rec{border:2px solid var(--acc);background:var(--acc-w)}
.rtag{font-size:11.5px;color:#fff;background:var(--acc);border-radius:999px;padding:0 8px}
.opt.o1 .ov{color:var(--t1)} .opt.o2 .ov{color:var(--t2)} .opt.o3 .ov{color:var(--t3)}

/* 附录 */
.apxtoc{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.ac{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.ah{font-weight:700;font-size:14px;margin:0 0 6px}
.ah em{font-style:normal;display:inline-block;width:22px;height:22px;border-radius:6px;background:var(--acc);color:#fff;text-align:center;line-height:22px;font-size:12px;margin-right:8px}
.ac a{display:block;font-size:13px;color:var(--ink2);padding:2px 0}
.ac a i{font-style:normal;color:var(--mute);display:inline-block;min-width:34px}
.doc{padding-bottom:80px}
details.apxall{margin:0}
details.apxall>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
details.apxall>summary::-webkit-details-marker{display:none}
.aall{font-family:var(--serif);font-size:18px;font-weight:700}
.aat{flex:1;font-size:13px;color:var(--mute)}
.ax{font-size:12.5px;color:var(--acc);white-space:nowrap}
.apxbody{padding:18px 0 0}
.layer{margin:0 0 26px}
.rail{display:flex;align-items:baseline;gap:10px;margin:0 0 10px;padding:0 0 6px;border-bottom:1px solid var(--line)}
.rail .dot{display:none}
.rail .st{display:flex;align-items:baseline;gap:10px}
.rail .nm{font-family:var(--serif);font-size:17px;font-weight:700}
.rail .sub{font-size:13px;color:var(--mute)}
.layer .body{display:flex;flex-direction:column;gap:8px}
details.apx{background:var(--card);border:1px solid var(--line);border-radius:10px}
details.apx>summary{list-style:none;cursor:pointer;display:flex;align-items:baseline;gap:12px;padding:12px 16px}
details.apx>summary::-webkit-details-marker{display:none}
.ai{flex:none;font-size:12.5px;font-weight:700;color:var(--acc);min-width:34px}
.at2{flex:1;font-weight:650;font-size:14.5px;line-height:1.5}
.at2 s{display:block;font-weight:400;font-size:12.5px;color:var(--mute)}
details.apx[open]>summary .ax{color:var(--mute)}
.abody{padding:2px 16px 16px;border-top:1px solid var(--line)}
.apxnote{font-size:13px;color:var(--ink2);background:var(--soft);border-radius:8px;padding:10px 12px;margin:12px 0}
.pts{display:flex;flex-direction:column;gap:10px;padding:12px 0 0}
.pt1{display:grid;grid-template-columns:24px 1fr;gap:6px;font-size:14px;color:var(--ink2);line-height:1.65}
.pt1 .i{color:var(--acc);font-weight:700}
.foot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:12px;color:var(--mute);border-top:1px solid var(--line);padding:14px 0 0}

/* 表格 */
table.flt{width:100%;border-collapse:collapse;font-size:13.5px;margin:10px 0 6px}
table.flt th{text-align:left;font-weight:650;color:var(--mute);font-size:12.5px;background:var(--soft);padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
table.flt td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink2);line-height:1.6}
table.flt td.k{font-weight:650;color:var(--ink);white-space:nowrap}
table.flt td.n{color:var(--mute);font-weight:600;width:34px}
table.flt td s{display:inline-block;font-size:11px;color:var(--acc);background:var(--acc-w);border-radius:999px;padding:0 6px;margin-left:6px}
table.flt tr.grp td{background:var(--soft);font-weight:700;color:var(--ink);font-size:13px}
.abody table.flt{display:block;overflow-x:auto}

/* 窄屏 */
@media (max-width:860px){
  .caps{grid-template-columns:repeat(2,1fr)}
  .hero-g{grid-template-columns:1fr}
  .ev{grid-template-columns:1fr}
  .opts{grid-template-columns:1fr}
  .apxtoc{grid-template-columns:repeat(2,1fr)}
  .ov2 .oh{display:none}
  .ov2>a{grid-template-columns:28px 1fr;gap:6px 10px}
  .ov2>a .s,.ov2>a .l{grid-column:2}
  .cr{grid-template-columns:44px 1fr}
  .cr .ef{grid-column:2}
  .top .meta{display:none}
}
@media (max-width:560px){
  .home,.doc{padding:0 16px}
  .home{padding-top:24px}
  .hero-h{font-size:20px}
  .caps,.apxtoc{grid-template-columns:1fr}
  .pbk{padding:18px 16px 14px}
  .dl2{grid-template-columns:1fr}
  .dl2 dt{margin-top:6px}
  .prr{grid-template-columns:1fr}
  .prr em{justify-self:start;padding:1px 10px}
}
@media print{
  .top,.toc{display:none}
  .home,.doc{margin:0 auto!important}
  .pbk,details.apx{break-inside:avoid}
}
"""

# 1. 整段替换样式
s = re.sub(r'<style>.*?</style>', '<style>' + CSS + '</style>', s, count=1, flags=re.S)

# 2. 首屏：结论句 + 5 项能力 + 验收 / 分层 / 现状
old_head = re.search(r'<div class="hhead">.*?</div>\s*<p class="ltp"[^>]*>.*?</p>\s*<div class="ltp"[^>]*>(.*?)</div>\n', s, flags=re.S)
assert old_head, '首屏结构没找到'
scope_html = old_head.group(1)
hero = '''<p class="hero-h">运营要具备 5 项能力；推荐推送并入同一后台、按人合计弹窗与推送上限，弹窗自身的控制在弹窗规则里补字段</p>
<div class="caps">
<a class="cap" href="#q1"><i>一</i><b>分人群内容配置</b><span>分人群配置内容</span></a>
<a class="cap" href="#q2"><i>二</i><b>触达量与顺序控制</b><span>控制弹窗数量与先后</span></a>
<a class="cap" href="#q3"><i>三</i><b>人群圈选</b><span>圈得出目标人群</span></a>
<a class="cap" href="#q4"><i>四</i><b>统一推送</b><span>推送统一</span></a>
<a class="cap" href="#q5"><i>五</i><b>效果查看</b><span>事后查得到效果</span></a>
</div>
<div class="hero-g">
<div class="hb"><div class="hb-k">三条验收</div><ol class="acc3"><li>新人群配置不依赖研发</li><li>事前算得出每人触达上限</li><li>事后查得到曝光、点击</li></ol></div>
<div class="hb"><div class="hb-k">34 项，分短期、中期、长期推进</div><div class="tierbar"><span class="t1" style="flex:12">短期 12</span><span class="t2" style="flex:12">中期 12</span><span class="t3" style="flex:10">长期 10</span></div><p class="hb-d">短期＝现有配置 12 项、中期＝小改动 12 项、长期＝较大开发 10 项</p></div>
<div class="hb"><div class="hb-k">现状</div><div class="big">2<small> / 25</small></div><p class="hb-d">现状只确定能做 25 个运营场景中的 2 个</p></div>
</div>
<p class="hero-n">下表为 5 个问题与对应能力；本期做到哪一层，见<a href="#t-scope">本期范围</a>。</p>
'''
s = s[:old_head.start()] + hero + s[old_head.end():]

# 3. 「本期范围」单列一节：三档 + 建议 + 理由（原文逐句保留）
plain = re.sub(r'<[^>]+>', '', scope_html)
need = ['三档按层推进、不互斥', '只做短期（12 项，另含快速提升 8 条）', '做到中期（再加 12 项）', '做到长期（再加 10 项）',
        '推荐方案是三层全做的完整形态', '建议本期先做到中期', '短期 12 项不消除任何根因', '该建议的依据不足']
for k in need:
    assert k in plain, '本期范围原文变了：' + k
m1 = re.search(r'但中期只能消除(.*?)。长期 10 项', plain).group(1)
m2 = re.search(r'(长期 10 项（含统一后台、弹窗与推送合计限量）.*?再决定是否提前)。', plain).group(1)
m3 = re.search(r'该建议的依据不足：(.*?)$', plain).group(1)
scope = f'''<div class="hrow" id="t-scope"><div class="hlab"><b>本期范围</b><span>三档 · 建议</span></div><div class="hmain">
<section class="pbk"><header><span class="qn b">请主管定</span><h3>本期做到哪一层：三档按层推进、不互斥</h3></header>
<div class="opts">
<div class="opt o1"><div class="ok">只做短期</div><div class="ov">12 项</div><div class="od">另含快速提升 8 条</div></div>
<div class="opt o2 rec"><div class="ok">做到中期<span class="rtag">建议</span></div><div class="ov">再加 12 项</div><div class="od">推荐方案是三层全做的完整形态，建议本期先做到中期</div></div>
<div class="opt o3"><div class="ok">做到长期</div><div class="ov">再加 10 项</div><div class="od">含统一后台、弹窗与推送合计限量</div></div>
</div>
<div class="dbx"><div class="dbk">为什么建议本期先做到中期</div><ul>
<li>短期 12 项不消除任何根因，所以至少要做到中期。</li>
<li>但中期只能消除{m1}。</li>
<li>{m2}。</li>
</ul></div>
<p class="tn">该建议的依据不足：{m3}</p>
</section>
</div></div>

'''
anchor = '<!-- ══ 附录目录 ══ -->'
assert s.count(anchor) == 1
s = s.replace(anchor, scope + anchor)
s = s.replace('<a class="lv1 apxlink" href="#L1">附录</a>',
              '<a class="lv1" href="#t-scope"><em>4</em>本期范围</a>\n<a class="lv1 apxlink" href="#L1">附录</a>')

# 4. 层级标签上色；去掉与新样式冲突的内联样式
s = s.replace('<i class="lv">短期</i>', '<i class="lv t1">短期</i>').replace('<i class="lv">中期</i>', '<i class="lv t2">中期</i>').replace('<i class="lv">长期</i>', '<i class="lv t3">长期</i>')
s = s.replace(' style="font-size:.78rem;color:var(--mut)"', '')
s = s.replace('<div style="padding:0 0 0 182px"><div class="foot" style="margin-top:26px">', '<div><div class="foot" style="margin-top:26px">')
s = s.replace('<div style="height:14px"></div>', '')

open(P, 'w', encoding='utf-8').write(s)
print('ok')
