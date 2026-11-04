// 远景、中景的点阵：1000 个点个个是真人（data.json 的 grid.s = crowd 导出），颜色 = 这一代的打法。
// 远：直径 22 px、间距 30；中：放大到直径 100 px，看得见眼睛在眨。你（第 72 号）套白圈。
// 冷暖仪表：每对正在互相好的人之间有光点来回飞，数目和屏幕亮度跟着这一代的合作率走。
import React from 'react';
import {random} from 'remotion';
import {blink} from '../../components/people/face';
import {COL, Cam, D, GAP, HARSH, I, LAY, YOU_W, animF, cellXY, clamp, lerp, stratAt, toScreen} from './lib';

const N = D.grid.cols * D.grid.rows;
const R0 = LAY.far.dot / 2;   // 世界坐标里点的半径
const STAGE = LAY.stage;

// 光点来回飞的 200 对邻居（固定随机）
const PAIRS = Array.from({length: 200}, (_, i) => {
  const a = Math.floor(random(`pa${i}`) * N);
  const right = (a % D.grid.cols) < D.grid.cols - 1 && random(`pd${i}`) < 0.6;
  const b = right ? a + 1 : Math.min(N - 1, a + D.grid.cols);
  return {a, b, rank: random(`pr${i}`), ph: random(`pp${i}`), per: 28 + random(`pq${i}`) * 20};
});

export type CrowdProps = {
  f: number; gen: number; cam: Cam;
  opacity?: number;
  dim?: (cell: number, s: number) => number;     // 每个点的亮度 0..1
  eyes?: boolean;                                  // 中景：画眼睛
  bars?: boolean;                                  // 中景：头顶分数条（只有跟踪点有分数）
  sweep?: {from: number; p: number} | null;        // 中景：变色从上往下刷（from = 上一代）
  lookAt?: boolean;                                // 中景：要变色的点先把眼睛转向旁边那个颜色的点
  links?: number;                                  // 远景：变狠时从旁边连过来的线（当前代，带小数）
  sparks?: boolean;                                // 冷暖：光点来回飞
  ring?: {color?: string; scale?: number; o?: number};
  clip?: boolean;
  skip?: Set<number>;                              // 不画的格子（方块飞走以后）
  tint?: number;                                   // 冷暖滤色按这一代的合作率；画在点和白圈之间，白圈不被压暗
};

export const coopShade = (gen: number) => {
  const c = D.coop[clamp(Math.round(gen), 0, 300)];
  return {c, dark: (1 - c) * 0.55, cold: clamp((0.7 - c) / 0.6) * 0.18};
};

export const Crowd: React.FC<CrowdProps> = (p) => {
  const {cam, gen} = p;
  const z = cam.z;
  const r = R0 * z;
  const x0 = STAGE.x0 - r * 2, x1 = STAGE.x1 + r * 2, y0 = STAGE.y0 - r * 2, y1 = STAGE.y1 + r * 2;
  const af = animF(p.f);
  const items: React.ReactNode[] = [];
  const g = clamp(Math.round(gen), 0, 300);
  for (let cell = 0; cell < N; cell++) {
    if (p.skip?.has(cell)) continue;
    const w = cellXY(cell);
    const s = toScreen(cam, w);
    if (s.x < x0 || s.x > x1 || s.y < y0 || s.y > y1) continue;
    const st = stratAt(g, cell);
    const b = p.dim ? p.dim(cell, st) : 1;
    const col = COL[st];
    let body: React.ReactNode = <circle cx={s.x} cy={s.y} r={r} fill={col} />;
    if (p.sweep && p.sweep.p < 1) {
      const old = stratAt(p.sweep.from, cell);
      if (old !== st) {
        const h = 2 * r * p.sweep.p;
        body = (
          <g>
            <circle cx={s.x} cy={s.y} r={r} fill={COL[old]} />
            <clipPath id={`sw${cell}`}><rect x={s.x - r} y={s.y - r} width={2 * r} height={h} /></clipPath>
            <circle cx={s.x} cy={s.y} r={r} fill={col} clipPath={`url(#sw${cell})`} />
          </g>
        );
      }
    }
    let eyes: React.ReactNode = null;
    if (p.eyes && z > 2) {
      let gx = 0, gy = 0;
      if (p.lookAt && g < 300) {
        // 下一代要变的点：眼睛先转向旁边那个颜色的点
        const nxt = stratAt(g + 1, cell);
        if (nxt !== st) {
          let best = -1, bd = 1e9;
          for (const d of [-1, 1, -D.grid.cols, D.grid.cols, -D.grid.cols - 1, -D.grid.cols + 1, D.grid.cols - 1, D.grid.cols + 1]) {
            const c2 = cell + d;
            if (c2 < 0 || c2 >= N) continue;
            if (stratAt(g, c2) === nxt) {
              const w2 = cellXY(c2);
              const dd = Math.hypot(w2.x - w.x, w2.y - w.y);
              if (dd < bd) { bd = dd; best = c2; }
            }
          }
          if (best >= 0) {
            const w2 = cellXY(best);
            gx = (w2.x - w.x) / bd; gy = (w2.y - w.y) / bd;
          }
        }
      }
      const lid = blink(Math.floor(af), `c${cell}`);
      const er = r * 0.2, ey = s.y - r * 0.1;
      eyes = (
        <g>
          {[-1, 1].map((k) => (
            <g key={k}>
              <ellipse cx={s.x + k * r * 0.34} cy={ey} rx={er} ry={er * (1 - 0.9 * lid)} fill="#FFFFFF" />
              {lid < 0.6 && <circle cx={s.x + k * r * 0.34 + gx * er * 0.45} cy={ey + gy * er * 0.45} r={er * 0.55} fill="#15171C" />}
            </g>
          ))}
        </g>
      );
    }
    let bar: React.ReactNode = null;
    if (p.bars && z > 2) {
      const sc = D.grid.score[String(cell)];
      if (sc && g < sc.length) {
        const full = r * 1.8;
        bar = (
          <g>
            <rect x={s.x - full / 2} y={s.y - r - 26} width={full} height={14} rx={7} fill="#FFFFFF" opacity={0.12} />
            <rect x={s.x - full / 2} y={s.y - r - 26} width={full * clamp(sc[g] / 5)} height={14} rx={7} fill="#EEF1F6" />
          </g>
        );
      }
    }
    items.push(<g key={cell} opacity={b}>{body}{eyes}{bar}</g>);
  }

  // 变狠那一下从旁边连过来的线（示意）
  const links: React.ReactNode[] = [];
  if (p.links !== undefined) {
    for (const [lg, a, b2, st] of D.links) {
      const age = p.links - lg;
      if (age < -0.0001 || age > 3) continue;
      const A = toScreen(cam, cellXY(a)), B = toScreen(cam, cellXY(b2));
      links.push(<line key={`${lg}-${a}`} x1={B.x} y1={B.y} x2={A.x} y2={A.y} stroke={COL[st]} strokeWidth={4} opacity={clamp(1 - age / 3)} strokeLinecap="round" />);
    }
  }

  // 冷暖：光点在互相好的人之间来回飞
  const sparks: React.ReactNode[] = [];
  if (p.sparks) {
    const {c} = coopShade(gen);
    PAIRS.forEach((q, i) => {
      if (q.rank > c) return;
      const sa = stratAt(g, q.a), sb = stratAt(g, q.b);
      if (sa === I.ALLD || sb === I.ALLD) return;    // 骗子从不递
      const A = toScreen(cam, cellXY(q.a)), B = toScreen(cam, cellXY(q.b));
      const t = ((af / q.per + q.ph) % 1);
      const k = t < 0.5 ? t * 2 : 2 - t * 2;
      const x = lerp(A.x, B.x, k), y = lerp(A.y, B.y, k) - Math.sin(k * Math.PI) * 8 * z;
      sparks.push(<circle key={i} cx={x} cy={y} r={Math.max(3, 4.5 * z)} fill="#FFF1D6" opacity={0.9} />);
    });
  }

  const ys = toScreen(cam, YOU_W);
  const ringR = Math.max(LAY.far.ring / 2, r + 16) * (p.ring?.scale ?? 1);
  return (
    <g opacity={p.opacity ?? 1}>
      {p.clip !== false && (
        <clipPath id="stageClip"><rect x={0} y={STAGE.y0 - 10} width={1920} height={STAGE.y1 - STAGE.y0 + 20} /></clipPath>
      )}
      <g clipPath={p.clip !== false ? 'url(#stageClip)' : undefined}>
        {items}
        {links}
        {sparks}
      </g>
      {p.tint !== undefined && <CoopTint gen={p.tint} />}
      <circle cx={ys.x} cy={ys.y} r={ringR} fill="none" stroke={p.ring?.color ?? '#FFFFFF'} strokeWidth={LAY.far.ringStroke} opacity={p.ring?.o ?? 1} />
    </g>
  );
};

// 远景的冷暖滤色：合作率低时整片压暗、偏冷蓝
export const CoopTint: React.FC<{gen: number; o?: number}> = ({gen, o = 1}) => {
  const {dark, cold} = coopShade(gen);
  return (
    <g opacity={o} pointerEvents="none">
      <rect x={0} y={0} width={1920} height={1080} fill="#04060B" opacity={dark} />
      <rect x={0} y={0} width={1920} height={1080} fill="#2B5DA8" opacity={cold} style={{mixBlendMode: 'multiply'}} />
    </g>
  );
};

export const isHarsh = HARSH;
