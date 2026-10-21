// 需求评审版截图的后台外框：每张截图都带出它在触达系统里的层级。
// 用法：截图源里 <div class="shot bk" data-page="弹窗" data-crumb="新增弹窗规则" data-tabs="*弹窗列表|操作纪录">页面内容</div>，
//       页面末尾 <script src="_后台框.js"></script>，<head> 里 <link rel="stylesheet" href="_后台框.css">。
//   data-page   菜单里当前高亮的页面（须是下面 PUSH 或 OLD 里的名字），面包屑自动写「分组 / 页面」
//   data-crumb  页面以下的层级，如编辑页「新增弹窗规则」；多级用 / 分
//   data-tabs   页面内的页签，用 | 分，当前页签前加 *；不写则不显示页签行
//   data-subnav 页面内的子导航（照实有的才写），用 | 分，当前项前加 *
//   data-open   写 all 时展开全部分组（开屏后台结构用）；不写只展开当前分组，其余分组收起
//   data-app    不写为触达系统的页面，侧栏只显示触达系统自己的菜单；写「管理后台」为现有管理后台的页面（会员标签设定），侧栏只显示它所在的一组
//   内容里 class="bk-pop" 的元素是从本页打开的弹层、确认框：移到遮罩之上，横向在内容区居中，纵向用 style="--pop-top:Npx" 调
(function () {
  // 触达系统的菜单：两级，第一级为分组，第二级为页面
  const PUSH = [
    ['游戏外推送', ['推播', '短信']],   // 推播、短信的每人每天上限与勿扰在各自列表顶部设置，不单开一页
    ['游戏内推送', ['弹窗', '快显']],   // 大厅自动弹窗与快显的每人每天上限在弹窗页顶部设置，不单开一页
    ['数据', ['数据概览', '弹窗与快显位置数据', '每人每天推送量']],
    ['查询', ['玩家查询']],             // 操作纪录在各页的「操作纪录」页签，不单开总表
  ];
  // 现有管理后台里用到的页面（会员标签设定在会员管理下为推断）
  const OLD = [['会员管理', ['会员标签设定']]];
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  for (const shot of document.querySelectorAll('.shot.bk')) {
    const inOld = shot.dataset.app === '管理后台';
    const page = shot.dataset.page, all = shot.dataset.open === 'all';
    const menu = inOld ? OLD : PUSH;
    const grp = menu.find(g => g[1].includes(page));
    if (!grp) { shot.textContent = '✘ 菜单里没有页面：' + page; continue; }
    const side = menu.map(([g, list]) => {
      const open = all || g === grp[0];
      return `<div class="g${open ? ' open' : ''}">${esc(g)}</div>` +
        (open ? list.map(it => `<div class="i${it === page ? ' on' : ''}">${esc(it)}</div>`).join('') : '');
    }).join('');
    const crumbs = [grp[0], page].concat((shot.dataset.crumb || '').split('/').map(s => s.trim()).filter(Boolean));
    const head = crumbs.map((c, i) => `<span class="${i === crumbs.length - 1 ? 'cur' : ''}">${esc(c)}</span>`).join('<span class="sep">/</span>') +
      '<span class="acct"><i>运</i>运营01</span>';
    const bar = (v, cls) => v ? `<div class="${cls}">` + v.split('|').map(t =>
      t.startsWith('*') ? `<span class="on">${esc(t.slice(1))}</span>` : `<span>${esc(t)}</span>`).join('') + '</div>' : '';
    const tabs = bar(shot.dataset.tabs, 'bk-tabs') + bar(shot.dataset.subnav, 'bk-subnav');
    const pops = [...shot.querySelectorAll('.bk-pop')];
    pops.forEach(p => p.remove());
    const body = shot.innerHTML;
    shot.innerHTML = `<div class="bk-app"><div class="bk-brand">${inOld ? '管理后台' : '触达系统'}</div><div class="bk-head">${head}</div>` +
      `<div class="bk-side">${side}</div><div class="bk-main">${tabs}<div class="bk-body">${body}</div></div></div>`;
    if (pops.length) {
      const ov = document.createElement('div');
      ov.className = 'bk-ov';
      pops.forEach(p => ov.appendChild(p));
      shot.appendChild(ov);
    }
  }
})();
