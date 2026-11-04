// 002 成片：远景、中景的点阵。1000 个点个个是真人（data.json 的 grid.s），颜色 = 这一代的打法。
// 远：一片有微光的点（每颗点外面一圈很淡的本色光，慢慢地明暗）；中：点变成带眼睛的小圆脸，黑点眼带白高光，会眨眼，脚下一块软影。
// 光：头顶一盏灯，在点阵下面打出一圈暖光；合作率低的时候这圈光变暗、整片偏冷（冷暖仪表），合作率回来以后回暖。
// 拉远时点按镜头远近淡入：点还大得出画（直径 > 约 150 px）的时候不画，所以不会出现几颗被放大裁切的大点。
import React from 'react';
import {random} from 'remotion';
import {blink} from '../../../components/people/face';
import {mixHex} from '../../../components/people/geom';
import {COL, Cam, D, HARSH, I, LAY, YOU_W, animF, cellXY, clamp, lerp, muteAt, muteO, stratAt, toScreen} from '../lib';

const N = D.grid.cols * D.grid.rows;
const R0 = LAY.far.dot / 2;
const STAGE = LAY.stage;

const PAIRS = Array.from({length: 220}, (_, i) => {
  const a = Math.floor(random(`pa${i}`) * N);
  const right = (a % D.grid.cols) < D.grid.cols - 1 && random(`pd${i}`) < 0.6;
  const b = right ? a + 1 : Math.min(N - 1, a + D.grid.cols);
  return {a, b, rank: random(`pr${i}`), ph: random(`pp${i}`), per: 28 + random(`pq${i}`) * 20};
});
const PH = Array.from({length: N}, (_, i) => random(`tw${i}`) * Math.PI * 2);
const SHADE = COL.map((c) => mixHex(c, '#000000', 0.24));
const LIT = COL.map((c) => mixHex(c, '#FFFFFF', 0.12));
// 第五版第二轮：还没讲到的打法压暗时往暗灰里降饱和（不透明度在 lib 的 muteO）
export const MUTE_GRAY = '#4C5059';
export const mutedCol = (f: number, s: number, c = COL[s]) => {
  const m = muteAt(f, s);
  return m > 0 ? mixHex(c, MUTE_GRAY, 0.7 * m) : c;
};

// 冷暖：0 冷 1 暖（按这一代的合作率：第 0 代 69%，第 65 代 9.6%，第 300 代 86%）
export const warmthAt = (gen: number) => {
  const c = D.coop[clamp(Math.round(gen), 0, 300)];
  return clamp((c - 0.08) / (0.8 - 0.08));
};

export type CrowdProps = {
  f: number; gen: number; cam: Cam;
  opacity?: number;
  dim?: (cell: number, s: number) => number;
  eyes?: boolean;
  bars?: boolean;
  sweep?: {from: number; p: number} | null;
  lookAt?: boolean;
  links?: number;
  sparks?: boolean;
  ring?: {color?: string; scale?: number; o?: number};
  skip?: Set<number>;
  tint?: number;                 // 冷暖按哪一代（不给就不加滤色）
  fadeBig?: boolean;             // 拉远：点太大时不画
  light?: number;                // 头顶那圈光的强度倍数
  topFade?: [number, number];    // 第五版第二轮：点的中心在这两个 y 之间从 0 渐到 1（S11 让出顶上的路线图）
  // 第七版（S26 接着跑）：不按 D.grid.s 取打法、上色，改由外面给
  strat?: (cell: number) => number;
  paint?: (cell: number) => {col: string; sh: string; lt: string; o: number; glow?: number};
  coop?: number;                 // 光点飞的多少（不给就按 D.coop[gen]）
  tintW?: number;                // 冷暖直接给 0..1（不给就按 tint 那一代的合作率）
};

export const Crowd: React.FC<CrowdProps> = (p) => {
  const {cam, gen} = p;
  const z = cam.z;
  const r = R0 * z;
  const x0 = -r * 2, x1 = 1920 + r * 2, y0 = STAGE.y0 - 40 - r * 2, y1 = STAGE.y1 + 40 + r * 2;
  const af = animF(p.f);
  const g = clamp(Math.round(gen), 0, 300);
  const big = p.fadeBig ? clamp((150 - 2 * r) / 50) : 1;     // 直径 150 px 以上不画，100 px 以下全画
  const faceK = clamp((z - 2.2) / 1.2);                        // 眼睛：z 2.2 起慢慢出来
  const glowK = clamp((2.4 - z) / 1.2);                         // 远景的微光
  // 这一帧每种打法的显示色和压暗（第五版第二轮）
  const PC = COL.map((_, s) => mutedCol(p.f, s)), PS = SHADE.map((c, s) => mutedCol(p.f, s, c)), PL = LIT.map((c, s) => mutedCol(p.f, s, c));
  const PO = COL.map((_, s) => muteO(p.f, s));
  const items: React.ReactNode[] = [];
  const halos: React.ReactNode[] = [];
  const shadows: React.ReactNode[] = [];
  if (big > 0.001) {
    for (let cell = 0; cell < N; cell++) {
      if (p.skip?.has(cell)) continue;
      const w = cellXY(cell);
      const s = toScreen(cam, w);
      if (s.x < x0 || s.x > x1 || s.y < y0 || s.y > y1) continue;
      const st = p.strat ? p.strat(cell) : stratAt(g, cell);
      const tf = p.topFade ? clamp((s.y - p.topFade[0]) / (p.topFade[1] - p.topFade[0])) : 1;
      const pc = p.paint ? p.paint(cell) : null;
      const b = (p.dim ? p.dim(cell, st) : 1) * big * (pc ? pc.o : PO[st]) * tf;
      if (b < 0.01) continue;
      let col = pc ? pc.col : PC[st], sh = pc ? pc.sh : PS[st], lt = pc ? pc.lt : PL[st];
      let sweepNode: React.ReactNode = null;
      if (p.sweep && p.sweep.p < 1) {
        const old = stratAt(p.sweep.from, cell);
        if (old !== st) {
          const h = 2 * r * p.sweep.p;
          sweepNode = (
            <g>
              <clipPath id={`fsw${cell}`}><rect x={s.x - r} y={s.y - r} width={2 * r} height={h} /></clipPath>
              <circle cx={s.x} cy={s.y} r={r * 1.001} fill={PC[old]} />
              <circle cx={s.x} cy={s.y} r={r * 1.001} fill={PC[st]} clipPath={`url(#fsw${cell})`} />
              <rect x={s.x - r * 0.9} y={s.y - r + h - 2} width={r * 1.8} height={4} fill="#FFF4DC" opacity={0.8} />
            </g>
          );
          col = PC[old]; sh = PS[old]; lt = PL[old];
        }
      }
      // 远景的微光：每颗点外面一圈本色的光，各自慢慢明暗
      if (glowK > 0) {
        const tw = 0.55 + 0.45 * Math.sin(af / 19 + PH[cell]);
        halos.push(<circle key={cell} cx={s.x} cy={s.y} r={r * 1.9} fill={col} opacity={clamp(b * glowK * (0.16 + 0.22 * tw) * (1 + (pc?.glow ?? 0)))} />);
      }
      if (faceK > 0) shadows.push(<ellipse key={cell} cx={s.x + r * 0.08} cy={s.y + r * 1.02} rx={r * 0.8} ry={r * 0.16} fill="#000" opacity={0.5 * faceK * b} />);
      let eyes: React.ReactNode = null;
      if (p.eyes !== false && faceK > 0) {
        let gx = 0, gy = 0;
        if (p.lookAt && g < 300) {
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
        const er = r * 0.13, ey = s.y - r * 0.04;
        eyes = (
          <g opacity={faceK}>
            {[-1, 1].map((k) => {
              const ex = s.x + k * r * 0.3 + gx * r * 0.1, eyy = ey + gy * r * 0.08;
              if (lid > 0.6) return <path key={k} d={`M ${ex - er * 1.1} ${eyy} Q ${ex} ${eyy + er * 0.7} ${ex + er * 1.1} ${eyy}`} stroke="#15171C" strokeWidth={Math.max(1.5, er * 0.5)} fill="none" strokeLinecap="round" />;
              return (
                <g key={k}>
                  <ellipse cx={ex} cy={eyy} rx={er} ry={er * 1.25 * (1 - 0.85 * lid)} fill="#15171C" />
                  <circle cx={ex + er * 0.35} cy={eyy - er * 0.45} r={er * 0.38} fill="#FFFFFF" />
                </g>
              );
            })}
            <ellipse cx={s.x - r * 0.52} cy={s.y + r * 0.26} rx={r * 0.15} ry={r * 0.08} fill="#FF9C8F" opacity={0.3} />
            <ellipse cx={s.x + r * 0.52} cy={s.y + r * 0.26} rx={r * 0.15} ry={r * 0.08} fill="#FF9C8F" opacity={0.3} />
          </g>
        );
      }
      let bar: React.ReactNode = null;
      if (p.bars && z > 2) {
        const sc = D.grid.score[String(cell)];
        if (sc && g < sc.length) {
          const full = r * 1.9, bh = Math.max(16, r * 0.3);
          const by = s.y - r - bh - 10;
          bar = (
            <g>
              <rect x={s.x - full / 2} y={by} width={full} height={bh} rx={bh / 2} fill="#0E1016" opacity={0.8} />
              <rect x={s.x - full / 2 + 3} y={by + 3} width={Math.max(bh - 6, (full - 6) * clamp(sc[g] / 5))} height={bh - 6} rx={(bh - 6) / 2} fill="#F1EBDD" />
            </g>
          );
        }
      }
      items.push(
        <g key={cell} opacity={b}>
          <circle cx={s.x} cy={s.y} r={r} fill={sh} />
          <circle cx={s.x - r * 0.08} cy={s.y - r * 0.1} r={r * 0.88} fill={col} />
          {r > 6 && <ellipse cx={s.x - r * 0.34} cy={s.y - r * 0.44} rx={r * 0.3} ry={r * 0.17} fill={lt} opacity={0.9} transform={`rotate(-30 ${s.x - r * 0.34} ${s.y - r * 0.44})`} />}
          {sweepNode}
          {eyes}{bar}
        </g>,
      );
    }
  }

  const links: React.ReactNode[] = [];
  if (p.links !== undefined) {
    for (const [lg, a, b2, st] of D.links) {
      const age = p.links - lg;
      if (age < -0.0001 || age > 3) continue;
      const A = toScreen(cam, cellXY(a)), B = toScreen(cam, cellXY(b2));
      const u = clamp(age / 0.8);
      links.push(<line key={`${lg}-${a}`} x1={B.x} y1={B.y} x2={lerp(B.x, A.x, u)} y2={lerp(B.y, A.y, u)} stroke={PC[st]} strokeWidth={5} opacity={clamp(1 - age / 3) * PO[st]} strokeLinecap="round" />);
    }
  }

  // 冷暖：光点在互相好的人之间来回飞（骗子从不递）
  const sparks: React.ReactNode[] = [];
  if (p.sparks && big > 0.2) {
    const c = p.coop ?? D.coop[g];
    PAIRS.forEach((q, i) => {
      if (q.rank > c) return;
      const sa = p.strat ? p.strat(q.a) : stratAt(g, q.a), sb = p.strat ? p.strat(q.b) : stratAt(g, q.b);
      if (sa === I.ALLD || sb === I.ALLD) return;
      if (p.skip?.has(q.a) || p.skip?.has(q.b)) return;
      const A = toScreen(cam, cellXY(q.a)), B = toScreen(cam, cellXY(q.b));
      if (A.x < -50 || A.x > 1970 || A.y < y0 || A.y > y1) return;
      const t = ((af / q.per + q.ph) % 1);
      const k = t < 0.5 ? t * 2 : 2 - t * 2;
      const x = lerp(A.x, B.x, k), y = lerp(A.y, B.y, k) - Math.sin(k * Math.PI) * 9 * z;
      const sr = Math.max(3.2, 4.2 * z);
      sparks.push(
        <g key={i} opacity={big}>
          <circle cx={x} cy={y} r={sr * 3} fill="url(#gSparkGlow)" />
          <circle cx={x} cy={y} r={sr} fill="#FFE2A8" />
          <circle cx={x - sr * 0.3} cy={y - sr * 0.3} r={sr * 0.45} fill="#FFFBF0" />
        </g>,
      );
    });
  }

  const ys = toScreen(cam, YOU_W);
  const ringR = Math.max(LAY.far.ring / 2, r + 16) * (p.ring?.scale ?? 1);
  const ringO = (p.ring?.o ?? 1) * (p.fadeBig ? clamp((260 - 2 * r) / 80) : 1);
  return (
    <g opacity={p.opacity ?? 1}>
      <mask id="fStageMask" maskUnits="userSpaceOnUse" x={0} y={0} width={1920} height={1080}>
        <rect x={0} y={0} width={1920} height={1080} fill="url(#gStageFade)" />
      </mask>
      <g mask="url(#fStageMask)">
        {shadows.length > 0 && <g>{shadows}</g>}
        {halos.length > 0 && <g filter="url(#fBlur6)">{halos}</g>}
        {items}
        {links}
        {sparks}
      </g>
      {p.tint !== undefined && <CoopTint gen={p.tint} w={p.tintW} />}
      {ringO > 0.01 && (
        <g opacity={ringO}>
          <circle cx={ys.x} cy={ys.y} r={ringR} fill="none" stroke="#000" strokeWidth={LAY.far.ringStroke + 6} opacity={0.35} />
          <circle cx={ys.x} cy={ys.y} r={ringR} fill="none" stroke={p.ring?.color ?? '#FFFFFF'} strokeWidth={LAY.far.ringStroke} />
        </g>
      )}
    </g>
  );
};

// 地面和头顶那盏灯打下来的一圈光（画在点阵下面）。warm 0..1
export const CrowdFloor: React.FC<{gen: number; o?: number; cx?: number; cy?: number; w?: number}> = ({gen, o = 1, cx = 900, cy = 500, w: w0}) => {
  const w = w0 ?? warmthAt(gen);
  return (
    <g opacity={o}>
      <rect width={1920} height={1080} fill="#0C0F15" />
      <ellipse cx={cx} cy={cy + 40} rx={1050} ry={520} fill="url(#gFloorWarm)" opacity={0.25 + 0.75 * w} />
      <ellipse cx={cx} cy={cy + 40} rx={1050} ry={520} fill="url(#gFloorCold)" opacity={0.85 * (1 - w)} />
    </g>
  );
};

// 合作率低时整片压暗、偏冷蓝（画在点上面，白圈不被压暗）
// 第四版：“世界冷了”那段（22.9–28.4 秒）原来平均亮度只有 21–28/255，压暗从 0.5 减到 0.1，冷蓝的滤色留着，再在暗部抬一层冷蓝，冷但看得清
export const CoopTint: React.FC<{gen: number; o?: number; w?: number}> = ({gen, o = 1, w: w0}) => {
  const w = w0 ?? warmthAt(gen);
  return (
    <g opacity={o} pointerEvents="none">
      <rect x={0} y={0} width={1920} height={1080} fill="#03050A" opacity={0.1 * (1 - w)} />
      <rect x={0} y={0} width={1920} height={1080} fill="#3E6FBF" opacity={0.34 * (1 - w)} style={{mixBlendMode: 'multiply'}} />
      <rect x={0} y={0} width={1920} height={1080} fill="#1E3A6A" opacity={0.24 * (1 - w)} style={{mixBlendMode: 'screen'}} />
      <rect x={0} y={0} width={1920} height={1080} fill="#FFB96B" opacity={0.07 * w} style={{mixBlendMode: 'soft-light'}} />
    </g>
  );
};

// 四角压暗（灯只照中间）；右下角再压一层，那里留给平台的按钮
export const Vignette: React.FC<{o?: number}> = ({o = 1}) => (
  <g opacity={o} pointerEvents="none">
    <rect width={1920} height={1080} fill="url(#gVignette)" />
    <rect width={1920} height={1080} fill="url(#gCorner)" />
  </g>
);

export const CrowdDefs: React.FC = () => (
  <defs>
    <linearGradient id="gStageFade" x1="0" y1="0" x2="0" y2="1080" gradientUnits="userSpaceOnUse">
      <stop offset={170 / 1080} stopColor="#fff" stopOpacity={0} />
      <stop offset={212 / 1080} stopColor="#fff" stopOpacity={1} />
      <stop offset={800 / 1080} stopColor="#fff" stopOpacity={1} />
      <stop offset={850 / 1080} stopColor="#fff" stopOpacity={0} />
    </linearGradient>
    <radialGradient id="gFloorWarm">
      <stop offset="0" stopColor="#5A4630" stopOpacity={0.95} />
      <stop offset="0.45" stopColor="#3A2F25" stopOpacity={0.55} />
      <stop offset="1" stopColor="#0C0F15" stopOpacity={0} />
    </radialGradient>
    <radialGradient id="gFloorCold">
      <stop offset="0" stopColor="#2A3E62" stopOpacity={0.95} />
      <stop offset="0.5" stopColor="#1A2740" stopOpacity={0.6} />
      <stop offset="1" stopColor="#0C0F15" stopOpacity={0} />
    </radialGradient>
    <radialGradient id="gVignette" cx="0.47" cy="0.42" r="0.75">
      <stop offset="0.55" stopColor="#000" stopOpacity={0} />
      <stop offset="1" stopColor="#000" stopOpacity={0.6} />
    </radialGradient>
    <radialGradient id="gCorner" cx="1" cy="1" r="0.32">
      <stop offset="0" stopColor="#05060A" stopOpacity={0.7} />
      <stop offset="1" stopColor="#05060A" stopOpacity={0} />
    </radialGradient>
  </defs>
);

export const isHarsh = HARSH;
