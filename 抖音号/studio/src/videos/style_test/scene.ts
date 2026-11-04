// 画风测试：两种画风画同样的内容。牌、姿势、表情、时间点都写在这里，画风文件只管怎么画。
// 牌局（前后一致）：底牌 9♥ 8♥；公共牌 K♥ 7♥ 2♣ 4♠，河牌 6♥ 凑成同花。
// 转牌后差一张红桃：没见过的牌 52 - 6 = 46 张，里面红桃还剩 13 - 4 = 9 张（比喻镜头里 46 张扣着的牌、9 张发亮）。
import {easeInOut, easeOut, track} from '../../components/people/geom';
import {Expr, EXPR, blink, breath, exprTrack, mixExpr, withBlink} from '../../components/people/face';
import {RPose, nudge, pose, poseTrack, resolve, poseDef} from '../../components/people/rig';
import {CardId, card} from '../../components/people/cards';

export const W = 1080, H = 1920, FPS = 30;
export const HOLE: CardId[] = [card('9h'), card('8h')];
export const BOARD: CardId[] = [card('Kh'), card('7h'), card('2c'), card('4s'), card('6h')];
export const OUTS = [2, 6, 11, 15, 21, 26, 31, 37, 42];   // 46 张里第几张是红桃（发亮）
export const UNSEEN = 46;

// 静帧取第几帧（避开眨眼）
export const STILL_FRAME = 20;

// 坐在桌后、手放在桌面上：2D 骨骼里“往观众这边伸”就是往画面下方伸，手的目标点往下挪
const onTable = (name: string, dy: number, dxN = 0, dxF = 0): RPose => {
  const d = poseDef(name);
  return resolve({
    ...d,
    aN: {...d.aN, to: {x: (d.aN?.to?.x ?? 60) + dxN, y: (d.aN?.to?.y ?? -36) + dy}},
    aF: {...d.aF, to: {x: (d.aF?.to?.x ?? 50) + dxF, y: (d.aF?.to?.y ?? -36) + dy}},
  });
};

// 镜头 1、小动作片：桌后看底牌
export const PEEK = onTable('peek', 26, 4, 0);
export const PEEK_SIGH = onTable('peekSigh', 26, 2, 0);
export const BOARD_LOOK = onTable('board', 26, 2, 0);

// 镜头 4：两个人
export const ALLIN = pose('allIn');
export const THINK = pose('think');
export const PUSHER_FACE: Expr = {...EXPR.calm, browIn: -0.45, knit: 0.3, smile: -0.15, mouthW: 0.75, brow: -0.1, blush: 0.3};

// 小动作片：5 秒 150 帧
export const MINI_FRAMES = 150;
export const miniPose = (f: number): RPose => {
  const base = poseTrack(f, [
    [0, PEEK], [34, PEEK], [48, nudge(PEEK, {shrug: 0.35, chest: -3, neck: -4})], [70, PEEK_SIGH], [80, PEEK_SIGH],
    [92, BOARD_LOOK], [104, nudge(BOARD_LOOK, {neck: -6, pitch: -0.1, shrug: 0.3, gy: -0.2})],
    [128, nudge(BOARD_LOOK, {neck: -12, lean: -2, shrug: -0.6, pitch: -0.1})], [150, nudge(BOARD_LOOK, {neck: -10, lean: -2, shrug: -0.45, pitch: -0.08})],
  ], easeInOut);
  const b = breath(f);
  return nudge(base, {shrug: 0.06 * b, chest: -0.6 * b});
};
export const miniExpr = (f: number): Expr => {
  const e = exprTrack(f, [
    [0, 'worry'], [30, 'worry'], [44, mixExpr(EXPR.worry, EXPR.sad, 0.5)], [58, 'sighing'], [76, 'sighing'],
    [90, mixExpr(EXPR.worry, EXPR.calm, 0.3)], [100, 'surprise'], [108, 'surprise'], [122, 'relief'], [150, 'relief'],
  ], easeInOut);
  // 眨眼：只在眼睛睁着的那几段
  const can = (f > 4 && f < 40) || (f > 82 && f < 98);
  return can ? withBlink(e, blink(f, 'mini')) : e;
};
// 掀牌角、河牌翻开、叹气的那口气
export const miniPeek = (f: number) => track(f, [[0, 0.15], [8, 0.95], [32, 0.95], [40, 0]], easeOut);
export const miniFlip = (f: number) => track(f, [[84, 0], [98, 1]], easeInOut);
export const miniPuff = (f: number) => track(f, [[54, 0], [60, 1], [74, 0]]) ;
export const miniPuff2 = (f: number) => track(f, [[116, 0], [122, 1], [138, 0]]);

// 静帧不眨眼（片子里才眨）；seed 留着给片子用
export const stillExpr = (e: Expr, _f: number, _seed: string) => e;

// —— 各镜头的布局（两种画风共用同一组数字）——
// 镜头 1：桌后看底牌的特写。G = 人脚下的地面（在画面外），桌面远沿（包边）在 railY
export const L1 = {
  s: 4.6, x: 300, railY: 1230,
  get G() { return this.railY + 88 * this.s; },
  lamp: {x: 700, y: 250, w: 300},
  pool: {x: 640, y: 1360},
  hole: [{dx: -118, dy: 60, rot: -112}, {dx: -96, dy: 22, rot: -96}],   // 相对近侧手腕（画面像素）；掀的是左下角，转过来朝右下，正好在手指底下
  holeS: 2.2,
  chips: [{x: 150, y: 1420, n: 9, c: 'black'}, {x: 255, y: 1470, n: 6, c: 'navy'}, {x: 120, y: 1560, n: 4, c: 'cream'}],
};
// 镜头 2：输了一手，瘫在椅背上
export const L2 = {s: 3.2, x: 610, G: 1520, lamp: {x: 560, y: 470, w: 230}, table: {x0: 850, x1: 1140}};
// 镜头 3：桌面俯视
export const L3 = {
  sq: 0.62, railY: 250,
  board: [{x: 165, y: 880, rot: -4}, {x: 352, y: 868, rot: 2}, {x: 540, y: 884, rot: -1}, {x: 728, y: 870, rot: 3}, {x: 914, y: 882, rot: -2}],
  cardS: 1.72,
  pool: {x: 540, y: 980},
  stacks: [
    {x: 430, y: 1330, n: 9, c: 'black'}, {x: 545, y: 1300, n: 12, c: 'navy'}, {x: 655, y: 1340, n: 7, c: 'cream'},
    {x: 500, y: 1430, n: 6, c: 'amber'}, {x: 615, y: 1450, n: 10, c: 'navy'}, {x: 380, y: 1440, n: 4, c: 'plum'},
  ],
  loose: [{x: 300, y: 1360, c: 'cream'}, {x: 760, y: 1250, c: 'black'}, {x: 330, y: 1530, c: 'navy'}],
  hand: {x: 830, y: 1520, r: 32, s: 2.7},
};
// 镜头 4：两个人隔着牌桌
export const L4 = {
  s: 3.0, G: 1560, left: 60, right: 1020,
  table: {x0: 170, x1: 910, far: 1140, near: 1312},
  lamp: {x: 540, y: 380, w: 260},
  push: [
    {x: 395, y: 1220, n: 9, c: 'black'}, {x: 455, y: 1262, n: 11, c: 'navy'}, {x: 510, y: 1205, n: 8, c: 'cream'},
    {x: 385, y: 1285, n: 6, c: 'amber'}, {x: 560, y: 1250, n: 10, c: 'navy'}, {x: 450, y: 1185, n: 5, c: 'plum'},
  ],
  sliding: [{x: 615, y: 1215, c: 'navy'}, {x: 628, y: 1262, c: 'black'}, {x: 600, y: 1292, c: 'cream'}],
  theirs: [{x: 790, y: 1185, n: 6, c: 'navy'}, {x: 835, y: 1225, n: 4, c: 'cream'}, {x: 800, y: 1262, n: 7, c: 'black'}],
  board: [{x: 590, y: 1162}, {x: 645, y: 1160}, {x: 700, y: 1163}, {x: 755, y: 1159}],
  chipR: 31, cardS: 0.52,
};
// 镜头 5 的透视：相机高 1、牌高 0.55、宽 0.39；第 i 张在深度 z = z0 + i·dz；x 方向有一点左右摆，像一张张随手立起来的
export const L5 = {
  s: 2.75, person: {x: 245, G: 1730},
  horizon: 470, F: 2500, z0: 2.25, dz: 0.52, cx: 540, X: 0.3,
};
export const rowCard = (i: number) => {
  const z = L5.z0 + i * L5.dz;
  const X = L5.X + 0.05 * Math.sin(i * 1.7) - 0.06 * Math.min(1, i / 12);
  const base = L5.horizon + L5.F / z;
  const h = (L5.F * 0.55) / z;
  return {x: L5.cx + (L5.F * X) / z, y: base, s: h / 140, k: L5.z0 / z, tilt: Math.sin(i * 2.3) * 3};
};
// 小动作片：和镜头 1 一样的桌，镜头往后拉，前景是公共牌
export const L6 = {
  s: 4.3, x: 270, railY: 1110,
  get G() { return this.railY + 88 * this.s; },
  lamp: {x: 640, y: 210, w: 260},
  hole: [{dx: -110, dy: 56, rot: -112}, {dx: -88, dy: 20, rot: -96}],
  holeS: 2.0,
  board: [{x: 150, y: 1560, rot: -3}, {x: 345, y: 1552, rot: 2}, {x: 540, y: 1564, rot: -1}, {x: 735, y: 1554, rot: 3}, {x: 930, y: 1562, rot: -2}],
  cardS: 1.7,
  chips: [{x: 110, y: 1290, n: 8, c: 'black'}, {x: 205, y: 1330, n: 5, c: 'navy'}],
};
