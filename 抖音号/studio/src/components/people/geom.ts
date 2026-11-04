// 画人用的几何小工具：点、旋转、平滑曲线、锥形管。
// 角度一律用 SVG 的习惯：正 = 屏幕上顺时针。
export type P = {x: number; y: number};

export const pt = (x: number, y: number): P => ({x, y});
export const add = (a: P, b: P): P => ({x: a.x + b.x, y: a.y + b.y});
export const sub = (a: P, b: P): P => ({x: a.x - b.x, y: a.y - b.y});
export const scl = (a: P, k: number): P => ({x: a.x * k, y: a.y * k});
export const len = (a: P) => Math.hypot(a.x, a.y);
export const dist = (a: P, b: P) => len(sub(a, b));
export const nrm = (a: P): P => {
  const l = len(a) || 1;
  return {x: a.x / l, y: a.y / l};
};
export const rad = (d: number) => (d * Math.PI) / 180;
export const deg = (r: number) => (r * 180) / Math.PI;
export const rot = (a: P, d: number): P => {
  const r = rad(d);
  const c = Math.cos(r), s = Math.sin(r);
  return {x: a.x * c - a.y * s, y: a.x * s + a.y * c};
};
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const lerpP = (a: P, b: P, t: number): P => ({x: lerp(a.x, b.x, t), y: lerp(a.y, b.y, t)});
export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const smooth = (t: number) => {
  const k = clamp(t);
  return k * k * (3 - 2 * k);
};
export const easeInOut = (t: number) => {
  const k = clamp(t);
  return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
};
export const easeOut = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
export const easeIn = (t: number) => Math.pow(clamp(t), 3);
// 把角度规整到 (-180, 180]
export const wrap = (d: number) => {
  let a = d % 360;
  if (a > 180) a -= 360;
  if (a <= -180) a += 360;
  return a;
};
export const lerpAng = (a: number, b: number, t: number) => a + wrap(b - a) * t;
// 一根“往下指”的骨头的世界角：0 = 竖直向下，正 = 顺时针（脚朝右的人，往后摆）
export const angDown = (d: P) => deg(Math.atan2(-d.x, d.y));
export const dirDown = (d: number): P => rot({x: 0, y: 1}, d);
export const dirUp = (d: number): P => rot({x: 0, y: -1}, d);

const cr = (p0: P, p1: P, p2: P, p3: P, t: number): P => {
  const t2 = t * t, t3 = t2 * t;
  const f = (a: number, b: number, c: number, d: number) =>
    0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
  return {x: f(p0.x, p1.x, p2.x, p3.x), y: f(p0.y, p1.y, p2.y, p3.y)};
};

// 穿过所有点的平滑曲线（Catmull-Rom），每段取 per 个点
export const crSample = (pts: P[], per = 8, closed = false): P[] => {
  const n = pts.length;
  if (n < 2) return pts.slice();
  const at = (i: number): P => {
    if (closed) return pts[((i % n) + n) % n];
    if (i < 0) return sub(scl(pts[0], 2), pts[1]);
    if (i >= n) return sub(scl(pts[n - 1], 2), pts[n - 2]);
    return pts[i];
  };
  const out: P[] = [];
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    for (let j = 0; j < per; j++) out.push(cr(at(i - 1), at(i), at(i + 1), at(i + 2), j / per));
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
};

// 按弧长重新取点（每 step 一个）
export const resample = (pts: P[], step: number): P[] => {
  if (pts.length < 2) return pts.slice();
  const out: P[] = [pts[0]];
  let carry = 0;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    const d = dist(a, b);
    let t = step - carry;
    while (t <= d) {
      out.push(lerpP(a, b, t / d));
      t += step;
    }
    carry = d - (t - step);
  }
  const last = pts[pts.length - 1];
  if (dist(out[out.length - 1], last) > step * 0.3) out.push(last);
  else out[out.length - 1] = last;
  return out;
};

export const polyLen = (pts: P[]) => pts.reduce((s, p, i) => (i ? s + dist(pts[i - 1], p) : 0), 0);

const f2 = (v: number) => (Math.round(v * 100) / 100).toString();

// 平滑闭合路径：穿过每个点的三次贝塞尔（tension 1 = 标准 Catmull-Rom）
export const smoothClosed = (pts: P[], tension = 1): string => {
  const n = pts.length;
  if (n < 3) return '';
  const k = tension / 6;
  let d = `M ${f2(pts[0].x)} ${f2(pts[0].y)}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = {x: p1.x + (p2.x - p0.x) * k, y: p1.y + (p2.y - p0.y) * k};
    const c2 = {x: p2.x - (p3.x - p1.x) * k, y: p2.y - (p3.y - p1.y) * k};
    d += ` C ${f2(c1.x)} ${f2(c1.y)} ${f2(c2.x)} ${f2(c2.y)} ${f2(p2.x)} ${f2(p2.y)}`;
  }
  return d + ' Z';
};

export const smoothOpen = (pts: P[], tension = 1): string => {
  const n = pts.length;
  if (n < 2) return '';
  const k = tension / 6;
  const at = (i: number) => (i < 0 ? sub(scl(pts[0], 2), pts[1]) : i >= n ? sub(scl(pts[n - 1], 2), pts[n - 2]) : pts[i]);
  let d = `M ${f2(pts[0].x)} ${f2(pts[0].y)}`;
  for (let i = 0; i < n - 1; i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    const c1 = {x: p1.x + (p2.x - p0.x) * k, y: p1.y + (p2.y - p0.y) * k};
    const c2 = {x: p2.x - (p3.x - p1.x) * k, y: p2.y - (p3.y - p1.y) * k};
    d += ` C ${f2(c1.x)} ${f2(c1.y)} ${f2(c2.x)} ${f2(c2.y)} ${f2(p2.x)} ${f2(p2.y)}`;
  }
  return d;
};

export const polyPath = (pts: P[], closed = true) =>
  pts.map((p, i) => `${i ? 'L' : 'M'} ${f2(p.x)} ${f2(p.y)}`).join(' ') + (closed ? ' Z' : '');

const circleSub = (c: P, r: number) =>
  `M ${f2(c.x + r)} ${f2(c.y)} A ${f2(r)} ${f2(r)} 0 1 1 ${f2(c.x - r)} ${f2(c.y)} A ${f2(r)} ${f2(r)} 0 1 1 ${f2(c.x + r)} ${f2(c.y)} Z`;
const area = (q: P[]) => q.reduce((s, p, i) => {
  const b = q[(i + 1) % q.length];
  return s + p.x * b.y - b.x * p.y;
}, 0);

// 锥形管：沿一串点，每个点一个半径，拼成一整块（圆和公切梯形的并集，同一绕向，不会自交出洞）
export const tube = (pts: P[], radii: number[]): string => {
  const parts: string[] = [];
  for (let i = 0; i < pts.length; i++) parts.push(circleSub(pts[i], radii[i]));
  for (let i = 0; i < pts.length - 1; i++) {
    const c1 = pts[i], c2 = pts[i + 1], r1 = radii[i], r2 = radii[i + 1];
    const d = dist(c1, c2);
    if (d <= Math.abs(r1 - r2) + 1e-6) continue;
    const u = nrm(sub(c2, c1));
    const b = deg(Math.acos(clamp((r1 - r2) / d, -1, 1)));
    let q = [
      add(c1, scl(rot(u, b), r1)), add(c2, scl(rot(u, b), r2)),
      add(c2, scl(rot(u, -b), r2)), add(c1, scl(rot(u, -b), r1)),
    ];
    if (area(q) < 0) q = q.reverse();
    parts.push(polyPath(q));
  }
  return parts.join(' ');
};

// 一条中线、两头不同宽度，算出两侧偏移的封闭轮廓（用在不会急弯的地方：躯干、袖子的平滑段）
export const ribbon = (center: P[], widths: number[]): P[] => {
  const n = center.length;
  const left: P[] = [], right: P[] = [];
  for (let i = 0; i < n; i++) {
    const a = center[Math.max(0, i - 1)], b = center[Math.min(n - 1, i + 1)];
    const t = nrm(sub(b, a));
    const nn = {x: -t.y, y: t.x};
    left.push(add(center[i], scl(nn, widths[i])));
    right.push(add(center[i], scl(nn, -widths[i])));
  }
  return [...left, ...right.reverse()];
};

export const mixHex = (a: string, b: string, t: number) => {
  const h = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
  const A = h(a), B = h(b);
  const k = clamp(t);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * k).toString(16).padStart(2, '0')).join('');
};

// 关键帧取值：keys = [[帧, 值], ...]，两帧之间用缓动
export const track = (f: number, keys: [number, number][], ease: (t: number) => number = easeInOut) => {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, v0] = keys[i - 1], [f1, v1] = keys[i];
      return lerp(v0, v1, ease((f - f0) / Math.max(1e-6, f1 - f0)));
    }
  }
  return keys[keys.length - 1][1];
};
