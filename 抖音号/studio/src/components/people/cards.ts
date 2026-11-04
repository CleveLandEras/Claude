// 扑克牌的几何：四种花色的形状、2–10 的花色点位置、牌面尺寸。两种画风共用。
// 颜色规矩：红桃、方块是红色；黑桃、梅花是黑色。
import {P} from './geom';

export type Suit = 'S' | 'H' | 'D' | 'C';   // 黑桃 红桃 方块 梅花
export type Rank = 'A' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K';
export type CardId = {r: Rank; s: Suit};
export const card = (code: string): CardId => {
  // 'As' 'Td' '10h' 'Kc'
  const s = code.slice(-1).toUpperCase() as Suit;
  let r = code.slice(0, -1).toUpperCase();
  if (r === 'T') r = '10';
  return {r: r as Rank, s};
};
export const isRed = (s: Suit) => s === 'H' || s === 'D';
export const SUIT_NAME: Record<Suit, string> = {S: '黑桃', H: '红桃', D: '方块', C: '梅花'};

// 牌面尺寸（扑克牌 63×88 毫米）：宽 100、高 140，圆角 7
export const CW = 100, CH = 140, CR = 7;

// 花色形状：以 (0,0) 为中心，高约 1（-0.5..0.5）
export const SUIT_PATH: Record<Suit, string> = {
  H: 'M 0 0.46 C -0.08 0.36 -0.5 0.08 -0.5 -0.17 C -0.5 -0.37 -0.36 -0.47 -0.22 -0.47 C -0.11 -0.47 -0.03 -0.4 0 -0.3 '
    + 'C 0.03 -0.4 0.11 -0.47 0.22 -0.47 C 0.36 -0.47 0.5 -0.37 0.5 -0.17 C 0.5 0.08 0.08 0.36 0 0.46 Z',
  D: 'M 0 -0.5 C 0.1 -0.32 0.24 -0.15 0.38 0 C 0.24 0.15 0.1 0.32 0 0.5 C -0.1 0.32 -0.24 0.15 -0.38 0 C -0.24 -0.15 -0.1 -0.32 0 -0.5 Z',
  S: 'M 0 -0.5 C 0.08 -0.38 0.5 -0.16 0.5 0.1 C 0.5 0.28 0.37 0.37 0.23 0.37 C 0.13 0.37 0.06 0.31 0.03 0.24 '
    + 'C 0.04 0.36 0.1 0.44 0.19 0.5 L -0.19 0.5 C -0.1 0.44 -0.04 0.36 -0.03 0.24 C -0.06 0.31 -0.13 0.37 -0.23 0.37 '
    + 'C -0.37 0.37 -0.5 0.28 -0.5 0.1 C -0.5 -0.16 -0.08 -0.38 0 -0.5 Z',
  C: 'M 0.03 0.18 C 0.06 0.28 0.12 0.4 0.2 0.5 L -0.2 0.5 C -0.12 0.4 -0.06 0.28 -0.03 0.18 '
    + 'C -0.08 0.27 -0.15 0.31 -0.24 0.31 C -0.37 0.31 -0.47 0.21 -0.47 0.08 C -0.47 -0.05 -0.37 -0.15 -0.24 -0.15 '
    + 'C -0.2 -0.15 -0.16 -0.14 -0.13 -0.12 C -0.2 -0.17 -0.23 -0.24 -0.23 -0.3 C -0.23 -0.42 -0.13 -0.52 0 -0.52 '
    + 'C 0.13 -0.52 0.23 -0.42 0.23 -0.3 C 0.23 -0.24 0.2 -0.17 0.13 -0.12 C 0.16 -0.14 0.2 -0.15 0.24 -0.15 '
    + 'C 0.37 -0.15 0.47 -0.05 0.47 0.08 C 0.47 0.21 0.37 0.31 0.24 0.31 C 0.15 0.31 0.08 0.27 0.03 0.18 Z',
};
// 墨线版的花色：同样的形状（墨线画风把它当成一块墨填满，再沿边描一笔）

// 2–10 的花色点：x 是三列（左、中、右），y 是从上到下的比例；下半边的点倒过来画
const XL = 0.29, XM = 0.5, XR = 0.71;
const Y = [0.2, 0.35, 0.5, 0.65, 0.8];
const Y4 = [0.2, 0.4, 0.6, 0.8];
export const PIPS: Record<string, [number, number][]> = {
  '2': [[XM, Y[0]], [XM, Y[4]]],
  '3': [[XM, Y[0]], [XM, Y[2]], [XM, Y[4]]],
  '4': [[XL, Y[0]], [XR, Y[0]], [XL, Y[4]], [XR, Y[4]]],
  '5': [[XL, Y[0]], [XR, Y[0]], [XM, Y[2]], [XL, Y[4]], [XR, Y[4]]],
  '6': [[XL, Y[0]], [XR, Y[0]], [XL, Y[2]], [XR, Y[2]], [XL, Y[4]], [XR, Y[4]]],
  '7': [[XL, Y[0]], [XR, Y[0]], [XM, 0.35], [XL, Y[2]], [XR, Y[2]], [XL, Y[4]], [XR, Y[4]]],
  '8': [[XL, Y[0]], [XR, Y[0]], [XM, 0.35], [XL, Y[2]], [XR, Y[2]], [XM, 0.65], [XL, Y[4]], [XR, Y[4]]],
  '9': [[XL, Y4[0]], [XR, Y4[0]], [XL, Y4[1]], [XR, Y4[1]], [XM, 0.5], [XL, Y4[2]], [XR, Y4[2]], [XL, Y4[3]], [XR, Y4[3]]],
  '10': [[XL, Y4[0]], [XR, Y4[0]], [XM, 0.3], [XL, Y4[1]], [XR, Y4[1]], [XL, Y4[2]], [XR, Y4[2]], [XM, 0.7], [XL, Y4[3]], [XR, Y4[3]]],
};
// 牌面坐标：中心为原点，宽 CW 高 CH。返回每个花色点的位置、是否倒置
export const pipSpots = (r: Rank): {p: P; flip: boolean}[] => {
  const list = PIPS[r] ?? [];
  return list.map(([u, v]) => ({p: {x: (u - 0.5) * CW, y: (v - 0.5) * CH}, flip: v > 0.5}));
};

export const RANK_FONT = '"Georgia", "Times New Roman", serif';

// 掀牌角：扣着的牌，左下角对着的是牌面右下角的点数（牌沿长边翻过来，左右对调）。
// 折线 AB 把左下角切下来，角往回折（fold：0 平放，1 折平）。返回：牌身的裁剪多边形、折起来那块三角、
// 把“牌面坐标”画到折角上的矩阵（先左右镜像，再沿 AB 折）。
export const peekGeom = (peek: number, fold = 0.62) => {
  const a = 46 * peek, b = 62 * peek;
  const C = {x: -CW / 2, y: CH / 2};
  const A = {x: -CW / 2 + a, y: CH / 2}, B = {x: -CW / 2, y: CH / 2 - b};
  const ux = B.x - A.x, uy = B.y - A.y, ul = Math.hypot(ux, uy) || 1;
  let n = {x: uy / ul, y: -ux / ul};
  if ((C.x - A.x) * n.x + (C.y - A.y) * n.y < 0) n = {x: -n.x, y: -n.y};
  const k = 1 + fold;
  const An = A.x * n.x + A.y * n.y;
  const F = (q: P) => {
    const d = q.x * n.x + q.y * n.y - An;
    return {x: q.x - k * d * n.x, y: q.y - k * d * n.y};
  };
  const C2 = F(C);
  const m = [1 - k * n.x * n.x, -k * n.x * n.y, -k * n.x * n.y, 1 - k * n.y * n.y, k * An * n.x, k * An * n.y];
  const faceMat = `matrix(${-m[0]} ${-m[1]} ${m[2]} ${m[3]} ${m[4]} ${m[5]})`;
  // 一个大方块，只留 AB 线里面那一侧
  const box: P[] = [{x: -80, y: -100}, {x: 80, y: -100}, {x: 80, y: 100}, {x: -80, y: 100}];
  const side = (q: P) => q.x * n.x + q.y * n.y - An;
  const clip: P[] = [];
  for (let i = 0; i < box.length; i++) {
    const p = box[i], q = box[(i + 1) % box.length];
    const sp = side(p), sq = side(q);
    if (sp <= 0) clip.push(p);
    if ((sp < 0 && sq > 0) || (sp > 0 && sq < 0)) {
      const t = sp / (sp - sq);
      clip.push({x: p.x + (q.x - p.x) * t, y: p.y + (q.y - p.y) * t});
    }
  }
  return {A, B, C, C2, faceMat, clip, inside: (q: P) => side(q) < 0};
};
