// 表情：每种表情是一组数字（眉、眼、嘴），两种表情之间直接插值，所以换表情是连续变过去的。
// 两种画风共用这一套数字：扁平小人把它画成色块，墨线小人把它画成两三笔。
import {random} from 'remotion';
import {clamp, lerp} from './geom';

export type Expr = {
  brow: number;     // 眉毛整体高低：+ 抬起
  browIn: number;   // 眉头（靠鼻梁那端）：+ 往上拧（担心、委屈），- 往下压（皱眉、生气）
  browArc: number;  // 眉毛弯度：+ 拱起
  knit: number;     // 两眉往中间靠
  lid: number;      // 上眼皮盖下来：0 睁开，1 闭上（不算眨眼）
  closed: number;   // 闭眼时那条线的弯：+ 笑眼（∩），- 放松（∪）
  eye: number;      // 眼睛大小倍数
  shine: number;    // 高光大小倍数
  tear: number;     // 含泪：0..1
  mouthW: number;   // 嘴宽倍数
  smile: number;    // 嘴角：+ 上扬，- 下撇
  open: number;     // 张嘴：0..1
  wobble: number;   // 委屈的波浪嘴：0..1
  round: number;    // 圆嘴（呼气、惊讶）：0..1
  blush: number;    // 腮红：0..1
  asym: number;     // 一边眉高一边眉低：+ 近侧（右）那条挑起来
  smirk: number;    // 嘴一边翘：+ 右嘴角上去
};

const E = (o: Partial<Expr>): Expr => ({
  brow: 0, browIn: 0, browArc: 0.3, knit: 0, lid: 0, closed: 0, eye: 1, shine: 1, tear: 0,
  mouthW: 1, smile: 0.1, open: 0, wobble: 0, round: 0, blush: 0.5, asym: 0, smirk: 0, ...o,
});

export const EXPR = {
  // 平静：眉自然，嘴角微微上扬
  calm: E({brow: 0, browIn: 0, browArc: 0.35, smile: 0.2, mouthW: 0.9}),
  // 担心：眉头往上拧、往中间靠，嘴抿成一小条、嘴角往下
  worry: E({brow: 0.15, browIn: 0.85, browArc: 0.05, knit: 0.6, smile: -0.35, mouthW: 0.7, lid: 0.08, blush: 0.35}),
  // 委屈含泪：眉头拧得更高，眼里汪着泪，波浪嘴
  teary: E({brow: 0.25, browIn: 1.25, browArc: -0.1, knit: 0.55, smile: -0.55, mouthW: 0.85, wobble: 1, tear: 1, shine: 1.8, eye: 1.1, blush: 0.9}),
  // 松一口气：眼睛放松闭上，眉舒开往上，嘴圆圆地呼气、嘴角带笑
  relief: E({brow: 0.35, browIn: 0.35, browArc: 0.25, lid: 1, closed: -0.9, smile: 0.4, open: 0.25, round: 0.55, mouthW: 0.7, blush: 0.8}),
  // 发呆：上眼皮耷拉一半，眉平，嘴一条小直线、微张
  blank: E({brow: -0.05, browIn: 0.1, browArc: 0.05, lid: 0.45, smile: -0.05, mouthW: 0.6, open: 0.12, round: 0.2, blush: 0.25, shine: 0.8}),
  // 惊喜：眉高高抬起，眼睛睁大，嘴张开、嘴角往上
  surprise: E({brow: 1, browIn: 0.3, browArc: 0.7, eye: 1.18, shine: 1.35, smile: 0.55, open: 0.75, round: 0.35, mouthW: 0.95, blush: 0.9}),
  // 叹气：眼皮垂下，眉头微拧，嘴圆着往外呼气
  sighing: E({brow: -0.1, browIn: 0.55, browArc: 0, knit: 0.3, lid: 0.7, smile: -0.25, open: 0.2, round: 0.7, mouthW: 0.6, blush: 0.3}),
  // 怀疑（他是不是在诈）：眯眼，一边眉压下一边眉挑起，嘴抿着往一边歪
  suspect: E({brow: -0.1, browIn: -0.55, browArc: 0.1, knit: 0.5, lid: 0.42, asym: 1, smile: -0.1, smirk: 0.6, mouthW: 0.75, blush: 0.2, shine: 0.9}),
  // 难过（不含泪）
  sad: E({brow: 0, browIn: 1, browArc: -0.05, knit: 0.4, lid: 0.25, smile: -0.6, mouthW: 0.8, blush: 0.4}),
};
export type ExprName = keyof typeof EXPR;
export const EXPR_NAMES = Object.keys(EXPR) as ExprName[];

export const mixExpr = (a: Expr, b: Expr, t: number): Expr => {
  const o = {} as Expr;
  (Object.keys(a) as (keyof Expr)[]).forEach((k) => {
    o[k] = lerp(a[k], b[k], t);
  });
  return o;
};
export const expr = (e: Expr | ExprName): Expr => (typeof e === 'string' ? EXPR[e] : e);

// 关键帧表情
export const exprTrack = (f: number, keys: [number, Expr | ExprName][], ease: (t: number) => number): Expr => {
  if (f <= keys[0][0]) return expr(keys[0][1]);
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, a] = keys[i - 1], [f1, b] = keys[i];
      return mixExpr(expr(a), expr(b), ease((f - f0) / Math.max(1e-6, f1 - f0)));
    }
  }
  return expr(keys[keys.length - 1][1]);
};

// 眨眼：每 2–5 秒一次，间隔按帧确定性随机（同一个 seed，渲染几次都一样）。返回上眼皮盖下来的程度 0..1
const BLINK = [0.45, 1, 1, 0.7, 0.35, 0.1];
export const blink = (f: number, seed = 'p', fps = 30): number => {
  let t = Math.floor(fps * (0.6 + random(`${seed}-b0`) * 2));
  for (let i = 1; t <= f + 1; i++) {
    const k = f - t;
    if (k >= 0 && k < BLINK.length) return BLINK[k];
    t += Math.floor(fps * (2 + random(`${seed}-b${i}`) * 3));
    if (i > 2000) break;
  }
  return 0;
};

// 呼吸：一呼一吸约 3.8 秒。返回 -1..1（+ 吸气，胸口抬起）
export const breath = (f: number, fps = 30, period = 3.8) => Math.sin((f / (fps * period)) * Math.PI * 2);

export const withBlink = (e: Expr, b: number): Expr => ({...e, lid: clamp(e.lid + (1 - e.lid) * b)});
