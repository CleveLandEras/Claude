// 002 横屏灰框：读 timeline.json（时间、字幕、版面）和 data.json（仿真数据），给各个画面用。
// 时间表由 timeline.py 生成，数据由 make_data.py 生成，两份都别手改。
import tl from './timeline.json';
import data from './data.json';

export type Seg = string | [string, string] | [string, string, number];   // 第三项：这一段出现的帧
export type Line = string | Seg[];
export type Beat = {
  id: string; t0: number; t1: number; f0: number; f1: number; dur: number;
  lines: Line[]; text: string; shot: string; scene: string; stop: boolean;
  sub?: {size: number; num: number; lineH: number; y0: number} | null;
  ev: Record<string, number | number[]>;
  as?: string;            // 第五版：接着画另一拍的画面（S18b 接 S18）
};
export type RouteKey = {f: number; t: number; act: 'in' | 'reveal' | 'ask' | 'back' | 'on' | 'out'; i: number};
export const TL = tl as unknown as {
  fps: number; frames: number; dur: number;
  question: {text: string; big: number[]; small: number[]};
  counterFrom: number;
  gen: {f: number; gen: number; mode: 'lin' | 'step' | 'hold'}[];
  layout: any;
  beats: Beat[];
  route: {stages: {code: string; label: string}[]; keys: RouteKey[]};
  // 第七版：S26 接着跑。keys = [(秒, 代), ...] 两点之间线性、最后一点之后停住；soft = 好欺负的人（这一幕画成老实人的黄）
  cycle: {gen0: number; gen1: number; keys: number[][]; soft: string[]};
};
export const D = data as unknown as {
  strategies: {code: string; name: string; color: string}[];
  names: Record<string, string>;
  counts: number[][]; coop: number[];
  grid: {cols: number; rows: number; youCell: number; swindlerCell: number; victims: number[]; s: string[]; starters: number[]; score: Record<string, number[]>};
  links: [number, number, number, number][];
  you: {s: number; sc: number; pct: number; opp: number[]; bet: number[]; look: number | null; lookS: number | null; sw: number}[];
  youAvg: number[];
  starters: {n: number; ever: number; everByGen: number[]; harshThenGtft: number;
    block: {cell: number; main: number; end: number; since: number; you: boolean}[]};
  hist20: {seeds: number[]; counts: number[][][]};
  // 第七版：从第 300 代接着跑（0.5% 新人），s[k] / counts[k] 是第 gen0 + k 代（make_data.py 生成）
  cycle: {gen0: number; gen1: number; mu: number; harshBack30: number; harshPeak: number; harshPeakShare: number; counts: number[][]; s: string[]};
};
export const LAY = TL.layout;
export const FPS = TL.fps;

export const I = {ALLC: 0, ALLD: 1, TFT: 2, GTFT: 3, GRIM: 4, WSLS: 5} as const;
export const CODES = ['ALLC', 'ALLD', 'TFT', 'GTFT', 'GRIM', 'WSLS'];
// 颜色 = 打法（分镜第三节）。不点名（WSLS）画成暗灰，不用数据里的绿
// 第五版：骗子和记仇画成同一个红色家族（片子里都叫“狠”），记仇亮一点（#FF5A3C，相对亮度 0.29）、骗子深一点（#C4282A，0.13），
// 亮度比约 1.9；点阵冷下来（CoopTint 压蓝）时偏冷也还读得成砖红、暗红，不发粉；和老实人的黄、有来有往的蓝、会原谅的绿都隔得开；不点名的灰再压暗一档（#8B9099 → #60656E）
export const COL_OVERRIDE: Record<string, string> = {WSLS: '#60656E', GRIM: '#FF5A3C', ALLD: '#C4282A'};
export const COL = D.strategies.map((s) => COL_OVERRIDE[s.code] ?? s.color);
export const colOf = (code: string) => COL[CODES.indexOf(code)];
// 字幕、连线里用的亮一档：会原谅的绿、记仇（狠）的红
export const COL_HI = {GTFT: '#3CC892', GRIM: '#FF7A5C'};
// 第四版：以牙还牙改叫“有来有往”（数据文件不动）
export const NAME = (i: number) => (CODES[i] === 'TFT' ? '有来有往' : D.names[CODES[i]]);
// 第五版：人身上的标签统一从这里出。片子只分三类讲：老实人、狠（骗子、记仇都是）、会原谅；有来有往是中间那一步
export const TAG_TEXT: Record<string, string> = {ALLC: '老实人', ALLD: '狠·只拿不给', GRIM: '狠·记一辈子', TFT: '有来有往', GTFT: '会原谅', WSLS: '不点名'};
export const tagText = (i: number) => TAG_TEXT[CODES[i]];
export const HARSH = (i: number) => i === I.ALLD || i === I.GRIM;
export const SPARK = '#FFF1D6';       // 光点：暖白
// 抢的那只手：第五版归进红色家族（介于记仇和骗子之间），暗面、亮面由它推
export const GRABHAND = '#E43F3A';
export const ME_WHITE = '#FFFFFF';    // 我：纯白点

export const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';

export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const ease = (t: number) => {
  const x = clamp(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
export const easeOut = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
export const easeIn = (t: number) => Math.pow(clamp(t), 3);
// 进度：f 在 [a, b] 里走了多少（0..1）
export const prog = (f: number, ab: number[] | number, len = 9) => {
  const [a, b] = Array.isArray(ab) ? ab : [ab, ab + len];
  return clamp((f - a) / Math.max(1e-6, b - a));
};

export const beatAt = (f: number): Beat => TL.beats.find((b) => f >= b.f0 && f < b.f1) ?? TL.beats[TL.beats.length - 1];
export const beat = (id: string): Beat => TL.beats.find((b) => b.id === id)!;
export const ev = (id: string, k: string) => beat(id).ev[k];
export const evn = (id: string, k: string) => beat(id).ev[k] as number;
export const eva = (id: string, k: string) => beat(id).ev[k] as number[];

// 计数器代数：和 timeline.py 的 gen_at 同一个算法。genF 不取整，给播放头和历史条用
export const genF = (f: number): number => {
  const K = TL.gen;
  if (f <= K[0].f) return K[0].gen;
  for (let i = 1; i < K.length; i++) {
    const k = K[i], p = K[i - 1];
    if (f < k.f || (f === k.f && k.mode !== 'step')) {
      if (k.mode === 'lin') return p.gen + ((k.gen - p.gen) * (f - p.f)) / Math.max(1e-9, k.f - p.f);
      return p.gen;
    }
  }
  return K[K.length - 1].gen;
};
export const genAt = (f: number) => Math.floor(genF(f) + 1e-9);

// 第五版第二轮：还没讲到的打法先压暗（片子“人只分三类讲”：老实人黄、狠红是主角）。返回压暗程度 m（0 全亮，1 压到约 0.25、降饱和）：
//   30.9 秒（S18）以前：有来有往、会原谅、不点名都压暗；S18 起 9 帧里有来有往回到全亮、会原谅回到约 0.5；
//   40.6 秒（S22）起 9 帧里全部全亮。点数、颜色本身不改，只压暗；S24 方块、历史条、四个你都在 S22 以后，不受影响
const MUTE_T = 9;
export const MUTE_O = 0.25;
export const muteAt = (f: number, s: number) => {
  const a = prog(f, [beat('S18').f0, beat('S18').f0 + MUTE_T]);
  const b = prog(f, [beat('S22').f0, beat('S22').f0 + MUTE_T]);
  if (s === I.TFT) return 1 - a;
  if (s === I.GTFT) return lerp(lerp(1, 2 / 3, a), 0, b);    // 2/3 → 不透明度 0.5
  if (s === I.WSLS) return 1 - b;
  return 0;
};
export const muteO = (f: number, s: number) => lerp(1, MUTE_O, muteAt(f, s));

// 有意定住的几段（分镜【停】）：这几段里光点、眨眼都停
const FREEZES: number[][] = [eva('S15', 'freeze'), eva('S19', 'freeze')];
export const animF = (f: number) => {
  let a = f;
  for (const [s, e] of FREEZES) {
    if (f >= e) a -= e - s;
    else if (f > s) a -= f - s;
  }
  return a;
};
export const frozen = (f: number) => FREEZES.some(([s, e]) => f >= s && f < e);

// 远景格子：第 c 列第 r 行，世界坐标（间距 30）
export const GAP = LAY.far.gap as number;
export const cellXY = (cell: number) => ({x: (cell % D.grid.cols) * GAP, y: Math.floor(cell / D.grid.cols) * GAP});
export const stratAt = (gen: number, cell: number) => D.grid.s[clamp(gen, 0, 300)].charCodeAt(cell) - 48;

// 镜头：世界点 (wx, wy) 放在屏幕 (ax, ay)，放大 z 倍
export type Cam = {wx: number; wy: number; ax: number; ay: number; z: number};
export const GRID_C = {x: ((D.grid.cols - 1) * GAP) / 2, y: ((D.grid.rows - 1) * GAP) / 2};
export const FAR: Cam = {wx: GRID_C.x, wy: GRID_C.y, ax: 900, ay: 500, z: 1};
export const YOU_W = cellXY(D.grid.youCell);
export const MID: Cam = {wx: YOU_W.x, wy: YOU_W.y, ax: 900, ay: 510, z: LAY.mid.zoom};
export const camAt = (a: Cam, b: Cam, t: number): Cam => {
  const k = clamp(t);
  const z = Math.exp(lerp(Math.log(a.z), Math.log(b.z), k));
  // 让缩放和平移一起走：先按 z 的进度插值锚点
  const u = Math.abs(Math.log(b.z) - Math.log(a.z)) > 1e-6 ? (Math.log(z) - Math.log(a.z)) / (Math.log(b.z) - Math.log(a.z)) : k;
  return {wx: lerp(a.wx, b.wx, u), wy: lerp(a.wy, b.wy, u), ax: lerp(a.ax, b.ax, u), ay: lerp(a.ay, b.ay, u), z};
};
export const toScreen = (c: Cam, p: {x: number; y: number}) => ({x: c.ax + (p.x - c.wx) * c.z, y: c.ay + (p.y - c.wy) * c.z});
export const zoomOn = (p: {x: number; y: number}, ax: number, ay: number, z: number): Cam => ({wx: p.x, wy: p.y, ax, ay, z});

// 分数条：0–5 分 → 满格 400 px
export const barLen = (score: number, full = LAY.near.barFull as number) => (clamp(score / 5) * full);
