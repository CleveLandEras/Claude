// 墨线：一串点 → perfect-freehand 出一笔有粗细、两头收尖的笔画轮廓。
// 线条抖动（line boil）：每 3 帧换一次噪声种子，每个点按 @remotion/noise 偏移，幅度按屏幕像素算（0.5–1.5 像素）。
import getStroke from 'perfect-freehand';
import {noise2D} from '@remotion/noise';
import {P, clamp, crSample, polyLen, resample} from './geom';

export const BOIL_EVERY = 3;
export const boilKey = (frame: number) => Math.floor(frame / BOIL_EVERY);

const pathFromOutline = (pts: number[][]) => {
  if (pts.length < 3) return '';
  const r = (v: number) => Math.round(v * 100) / 100;
  let d = `M ${r(pts[0][0])} ${r(pts[0][1])} Q`;
  for (let i = 0; i < pts.length; i++) {
    const [x0, y0] = pts[i];
    const [x1, y1] = pts[(i + 1) % pts.length];
    d += ` ${r(x0)} ${r(y0)} ${r((x0 + x1) / 2)} ${r((y0 + y1) / 2)}`;
  }
  return d + ' Z';
};

export type InkOpt = {
  size: number;              // 笔的直径（和点同一个单位）
  seed: string;
  frame: number;
  px?: number;               // 1 个单位等于几个屏幕像素（算抖动幅度用）
  amp?: number;              // 抖动幅度（屏幕像素），默认 1
  thinning?: number;
  taper?: [number, number];  // 两头收尖的长度（占全长的比例）
  press?: (t: number) => number;   // 沿笔画的压力 0..1
  smooth?: boolean;          // 先用 Catmull-Rom 把控制点连成曲线
  closed?: boolean;
};

const defaultPress = (t: number) => 0.32 + 0.68 * Math.pow(Math.sin(Math.PI * clamp(t)), 0.55);

// 把点抖一下（不画），给填色块之类也用
// freq：沿笔画每个点在噪声里走多远（默认按点算）；抖动的波长大约 80 个屏幕像素，不会抖成锯齿
export const jitter = (pts: P[], seed: string, frame: number, ampUnits: number, freq = 0.11): P[] => {
  const k = boilKey(frame);
  return pts.map((p, i) => ({
    x: p.x + noise2D(`${seed}x${k}`, i * freq, 0.5) * ampUnits,
    y: p.y + noise2D(`${seed}y${k}`, i * freq, 3.5) * ampUnits,
  }));
};

export const ink = (ctrl: P[], o: InkOpt): string => {
  const base = o.smooth === false ? ctrl : crSample(ctrl, 10, o.closed);
  const total = polyLen(base);
  if (total < 0.5) return '';
  const step = Math.max(0.6, Math.min(o.size * 0.35, total / 12));
  const dense = resample(base, step);
  const ampU = (o.amp ?? 1) / (o.px ?? 1);
  const pts = jitter(dense, o.seed, o.frame, ampU, (step * (o.px ?? 1)) / 80);
  const n = pts.length - 1;
  const press = o.press ?? defaultPress;
  const [t0, t1] = o.taper ?? [0.28, 0.32];
  const outline = getStroke(pts.map((p, i) => [p.x, p.y, press(i / Math.max(1, n))]), {
    size: o.size, thinning: o.thinning ?? 0.62, smoothing: 0.62, streamline: 0.18, simulatePressure: false,
    start: {taper: total * t0, cap: true}, end: {taper: total * t1, cap: true}, last: true,
  });
  return pathFromOutline(outline);
};

// 手画的圆：从 a0 起转 sweep 度，半径一点点变，起笔收笔不完全对上
export const inkCircle = (c: P, rx: number, ry: number, o: InkOpt & {a0?: number; sweep?: number; drift?: number}): string => {
  const a0 = o.a0 ?? -70, sweep = o.sweep ?? 348, drift = o.drift ?? 0.05;
  const n = 36;
  const pts: P[] = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const a = ((a0 + sweep * t) * Math.PI) / 180;
    const k = 1 - drift / 2 + drift * t + noise2D(`${o.seed}r`, t * 3, 0) * 0.015;
    pts.push({x: c.x + Math.cos(a) * rx * k, y: c.y + Math.sin(a) * ry * k});
  }
  return ink(pts, {...o, smooth: false, taper: o.taper ?? [0.06, 0.12], press: o.press ?? ((t) => 0.55 + 0.45 * Math.sin(Math.PI * t))});
};

// 排线：在一个多边形范围里画一组平行短线（阴影、木纹、暗面用）
export const hatchLines = (x0: number, y0: number, x1: number, y1: number, gap: number, angle: number): [P, P][] => {
  const out: [P, P][] = [];
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  const R = Math.hypot(x1 - x0, y1 - y0) / 2;
  const a = (angle * Math.PI) / 180;
  const d = {x: Math.cos(a), y: Math.sin(a)}, nn = {x: -Math.sin(a), y: Math.cos(a)};
  for (let s = -R; s <= R; s += gap) {
    const o = {x: cx + nn.x * s, y: cy + nn.y * s};
    out.push([{x: o.x - d.x * R, y: o.y - d.y * R}, {x: o.x + d.x * R, y: o.y + d.y * R}]);
  }
  return out;
};
