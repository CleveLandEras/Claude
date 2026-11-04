// 画风 B 的牌、筹码、桌布：线是手画的（每 3 帧抖一次），花色用红墨、黑墨填满。
// 桌上的牌按桌面压扁：先在 JS 里把牌的轮廓点算到画面上再描线，线的粗细不会被压扁。
import React, {useId} from 'react';
import {random} from 'remotion';
import {P, add, polyPath, rot} from './geom';
import {CH, CR, CW, CardId, Suit, SUIT_PATH, isRed, peekGeom, pipSpots} from './cards';
import {INK} from './InkPerson';
import {Hatch, InkShadow, Wash, stroke} from './InkProps';

const useUid = () => useId().replace(/[^a-zA-Z0-9]/g, '');
export const INK_RED = '#B8352A';
export const CARD_WHITE = '#FCFAF4';
export const HAND_FONT = '"Noteworthy", "Chalkboard SE", "Marker Felt", sans-serif';

type Ctx = {frame: number; seed: string; px: number};

// 圆角长方形的一圈点（牌的局部坐标）
const roundRect = (w: number, h: number, r: number, n = 3): P[] => {
  const pts: P[] = [];
  const corners = [{x: w / 2 - r, y: -h / 2 + r, a: -90}, {x: w / 2 - r, y: h / 2 - r, a: 0}, {x: -w / 2 + r, y: h / 2 - r, a: 90}, {x: -w / 2 + r, y: -h / 2 + r, a: 180}];
  corners.forEach((c) => {
    for (let i = 0; i <= n; i++) {
      const a = ((c.a + (90 * i) / n) * Math.PI) / 180;
      pts.push({x: c.x + Math.cos(a) * r, y: c.y + Math.sin(a) * r});
    }
  });
  return pts;
};

const InkPip: React.FC<{s: Suit; x: number; y: number; size: number; flip?: boolean}> = ({s, x, y, size, flip}) => (
  <path d={SUIT_PATH[s]} fill={isRed(s) ? INK_RED : INK} transform={`translate(${x} ${y}) scale(${size}) ${flip ? 'rotate(180)' : ''}`} />
);

// 一圈点里有一段被去掉了（掀角）：从缺口后面那一点开始排，描出来是一笔不闭合的线
const rotateToGap = (pts: P[]): P[] => {
  let best = 0, gap = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length];
    const d = Math.hypot(b.x - a.x, b.y - a.y);
    if (d > gap) {
      gap = d;
      best = (i + 1) % pts.length;
    }
  }
  return [...pts.slice(best), ...pts.slice(0, best)];
};

// —— 牌面：纸白底、手画的一圈边、手写的点数、墨填的花色 ——
export const InkCardFace: React.FC<{c: CardId; frame: number; seed: string; px?: number; outline?: boolean}> = ({c, frame, seed, px = 1, outline = true}) => {
  const ctx: Ctx = {frame, seed, px};
  const col = isRed(c.s) ? INK_RED : INK;
  const ten = c.r === '10';
  const court = c.r === 'J' || c.r === 'Q' || c.r === 'K';
  const idx = (rr: number, k: string) => (
    <g key={k} transform={`rotate(${rr})`}>
      <text x={-CW / 2 + 12} y={-CH / 2 + 25} textAnchor="middle" fontFamily={HAND_FONT} fontWeight={700} fontSize={ten ? 19 : 24}
        letterSpacing={ten ? -2 : 0} fill={col}>{c.r}</text>
      <InkPip s={c.s} x={-CW / 2 + 12} y={-CH / 2 + 37} size={12} />
    </g>
  );
  return (
    <g>
      <path d={polyPath(roundRect(CW, CH, CR))} fill={CARD_WHITE} />
      {outline && <path d={stroke([...roundRect(CW, CH, CR), {x: CW / 2 - CR + 2, y: -CH / 2}], 2.6, ctx, 'edge', {smooth: true, taper: [0.03, 0.05], press: () => 0.6})} fill={INK} />}
      {idx(0, 'a')}
      {idx(180, 'b')}
      {c.r === 'A' && <InkPip s={c.s} x={0} y={0} size={c.s === 'S' ? 48 : 40} />}
      {!court && c.r !== 'A' && pipSpots(c.r).map((q, i) => (
        <InkPip key={i} s={c.s} x={q.p.x * 0.84} y={q.p.y * 0.86} size={ten || c.r === '9' ? 15.5 : 18} flip={q.flip} />
      ))}
      {court && (
        <g>
          <path d={stroke([...roundRect(CW - 44, CH - 32, 3, 1), {x: (CW - 44) / 2 - 3, y: -(CH - 32) / 2}], 1.8, ctx, 'frame', {smooth: false, taper: [0.02, 0.04], press: () => 0.6})} fill={col} />
          <text x={0} y={20} textAnchor="middle" fontFamily={HAND_FONT} fontWeight={700} fontSize={60} fill={col}>{c.r}</text>
          <InkPip s={c.s} x={-CW / 2 + 31} y={-CH / 2 + 27} size={11} />
          <InkPip s={c.s} x={CW / 2 - 31} y={CH / 2 - 27} size={11} flip />
          {c.r !== 'J'
            ? <path d={stroke([{x: -15, y: -29}, {x: -15, y: -41}, {x: -8, y: -33}, {x: 0, y: -45}, {x: 8, y: -33}, {x: 15, y: -41}, {x: 15, y: -29}, {x: -15, y: -29}], 2, ctx, 'crown', {smooth: false, taper: [0.02, 0.02], press: () => 0.6})} fill={col} />
            : <path d={stroke([{x: -14, y: -30}, {x: 0, y: -44}, {x: 14, y: -30}], 2.2, ctx, 'hat')} fill={col} />}
        </g>
      )}
    </g>
  );
};

// —— 牌背：一圈边，里面一个框，框里交叉排线 ——
export const InkCardBack: React.FC<{frame: number; seed: string; px?: number}> = ({frame, seed, px = 1}) => {
  const ctx: Ctx = {frame, seed, px};
  const id = useUid();
  const iw = CW - 18, ih = CH - 18;
  const lines: [P, P][] = [];
  for (let k = -ih; k < iw + ih; k += 11) {
    lines.push([{x: -iw / 2 + k - ih, y: ih / 2}, {x: -iw / 2 + k, y: -ih / 2}]);
    lines.push([{x: -iw / 2 + k - ih, y: -ih / 2}, {x: -iw / 2 + k, y: ih / 2}]);
  }
  return (
    <g>
      <path d={polyPath(roundRect(CW, CH, CR))} fill={CARD_WHITE} />
      <clipPath id={id}><rect x={-iw / 2} y={-ih / 2} width={iw} height={ih} rx={3} /></clipPath>
      <g clipPath={`url(#${id})`}>
        <rect x={-iw / 2} y={-ih / 2} width={iw} height={ih} fill="#D9D2C2" />
        {lines.map((l, i) => <path key={i} d={stroke(l, 1.5, ctx, `x${i}`, {taper: [0.05, 0.05], press: () => 0.6})} fill={INK} opacity={0.75} />)}
      </g>
      <path d={stroke([...roundRect(iw, ih, 3, 1), {x: iw / 2 - 3, y: -ih / 2}], 1.8, ctx, 'in', {smooth: false, taper: [0.02, 0.04], press: () => 0.6})} fill={INK} />
      <ellipse cx={0} cy={0} rx={17} ry={25} fill={CARD_WHITE} />
      <path d={stroke(Array.from({length: 13}, (_, i) => ({x: Math.cos((i / 12) * Math.PI * 2) * 17, y: Math.sin((i / 12) * Math.PI * 2) * 25})), 1.8, ctx, 'oval', {taper: [0.05, 0.1]})} fill={INK} />
      <path d={stroke([...roundRect(CW, CH, CR), {x: CW / 2 - CR + 2, y: -CH / 2}], 2.6, ctx, 'edge', {smooth: true, taper: [0.03, 0.05], press: () => 0.6})} fill={INK} />
    </g>
  );
};

// —— 桌上的一张牌（参数和 FlatCards.TableCard 一样） ——
export const InkTableCard: React.FC<{
  x: number; y: number; s: number; rot?: number; sq?: number; face?: CardId; down?: boolean; peek?: number; flip?: number;
  frame: number; seed: string; lift?: number; shadow?: number;
}> = ({x, y, s, rot: r = 0, sq = 0.55, face, down, peek = 0, flip, frame, seed, lift = 0, shadow = 0.3}) => {
  const id = useUid();
  const ctx: Ctx = {frame, seed, px: 1};
  const fl = flip ?? (down || !face ? 0 : 1);
  const showFace = face && fl >= 0.5;
  const sx = Math.abs(Math.cos(Math.PI * fl));
  const up = Math.sin(Math.PI * Math.min(1, fl)) * (flip !== undefined ? 1 : 0) * 40 * s + lift * s;
  const proj = (q: P): P => {
    const v = rot({x: q.x * sx, y: q.y}, r);
    return {x: x + v.x * s, y: y + v.y * s * sq - up};
  };
  const T = `translate(${x} ${y - up}) scale(${s} ${s * sq}) rotate(${r}) scale(${sx} 1)`;
  // 掀角（和画风 A 同一套折线算法，见 cards.ts 的 peekGeom）
  const pg = peekGeom(peek);
  const {A, B: Bp, C2, faceMat} = pg;
  const bodyClip = polyPath(pg.clip);
  const rim = roundRect(CW, CH, CR);
  const peeking = peek > 0.01;
  // 轮廓：掀角时只描没掀起来的那部分
  const outlinePts = (peeking ? rotateToGap(rim.filter((q) => pg.inside(q))) : [...rim, rim[1]]).map(proj);
  return (
    <g>
      <InkShadow x={x + 6 * s} y={y + 8 * s * sq} rx={CW * 0.52 * s * (0.6 + 0.4 * sx) + up * 0.15} ry={CH * 0.48 * s * sq} o={shadow} />
      <g>
        <g transform={T}>
          <clipPath id={`${id}b`}><path d={bodyClip} /></clipPath>
          <g clipPath={peeking ? `url(#${id}b)` : undefined}>
            {showFace ? <InkCardFace c={face!} frame={frame} seed={seed} outline={false} px={s} /> : <InkCardBack frame={frame} seed={seed} px={s} />}
          </g>
        </g>
        {/* 纸的厚度：近边多描一道 */}
        <path d={stroke([proj({x: -CW / 2 + 4 + (peeking ? A.x + CW / 2 : 0), y: CH / 2}), proj({x: CW / 2 - 4, y: CH / 2})].map((q) => add(q, {x: 0, y: 3.2 * s})), 1.6 * s, ctx, 'thick')} fill={INK} opacity={0.6} />
        <path d={stroke(outlinePts, 2.6 * s, ctx, 'edge', {smooth: false, taper: [0.03, 0.05], press: () => 0.6})} fill={INK} />
        {peeking && face && (
          <g>
            <g transform={T}>
              <clipPath id={`${id}f`}><path d={polyPath([A, Bp, C2])} /></clipPath>
              <g clipPath={`url(#${id}f)`}><g transform={faceMat}><InkCardFace c={face} frame={frame} seed={seed} outline={false} px={s} /></g></g>
            </g>
            <path d={stroke([A, C2, Bp].map(proj), 2.4 * s, ctx, 'flap', {smooth: false, taper: [0.05, 0.05], press: () => 0.6})} fill={INK} />
            <path d={stroke([A, Bp].map(proj), 1.6 * s, ctx, 'fold')} fill={INK} opacity={0.7} />
          </g>
        )}
      </g>
    </g>
  );
};

// —— 立起来的牌（比喻镜头）：glow 发亮 = 周围一圈暖黄的淡彩 + 几道光线 ——
export const InkStandingCard: React.FC<{x: number; y: number; s: number; glow?: number; frame: number; seed: string; face?: CardId; fade?: number}> = (
  {x, y, s, glow = 0, frame, seed, face, fade = 0},
) => {
  const ctx: Ctx = {frame, seed, px: s};
  return (
    <g transform={`translate(${x} ${y})`} opacity={1 - fade}>
      {glow > 0 && <Wash d={`M ${-CW * 0.75 * s} ${-CH * 0.5 * s} A ${CW * 0.75 * s} ${CH * 0.68 * s} 0 1 0 ${CW * 0.75 * s} ${-CH * 0.5 * s} A ${CW * 0.75 * s} ${CH * 0.68 * s} 0 1 0 ${-CW * 0.75 * s} ${-CH * 0.5 * s} Z`}
        color="#EDBF4A" o={0.55 * glow} blur={14 * s} rough={8 * s} />}
      <g transform={`scale(${s}) translate(0 ${-CH / 2})`}>
        {face ? <InkCardFace c={face} frame={frame} seed={seed} px={s} /> : <InkCardBack frame={frame} seed={seed} px={s} />}
        {glow > 0 && <path d={polyPath(roundRect(CW, CH, CR))} fill="#F2C75C" opacity={0.45 * glow} style={{mixBlendMode: 'multiply'}} />}
        {glow > 0 && [-1, -0.4, 0.4, 1].map((k, i) => (
          <path key={i} d={stroke([{x: k * 62, y: -CH / 2 - 8 - Math.abs(k) * 2}, {x: k * 80, y: -CH / 2 - 26}], 2.2, ctx, `gl${i}`)} fill={INK} opacity={0.8 * glow} />
        ))}
      </g>
    </g>
  );
};

// —— 筹码：tone 0 白（留纸）、1 灰（淡墨）、2 黑（墨填，边纹留白） ——
const TONE = [{fill: CARD_WHITE, stripe: INK}, {fill: '#BDB5A6', stripe: CARD_WHITE}, {fill: '#2B2622', stripe: CARD_WHITE}];
export const InkChipStack: React.FC<{x: number; y: number; R: number; n: number; tone: number; frame: number; seed: string; sq?: number}> = (
  {x, y, R, n, tone, frame, seed, sq = 0.5},
) => {
  const ctx: Ctx = {frame, seed, px: 1};
  const t = R * 0.2;
  const ry = R * sq;
  const T = TONE[tone % 3];
  const ell = (cx: number, cy: number, from: number, to: number, nn = 16): P[] =>
    Array.from({length: nn + 1}, (_, i) => {
      const a = from + ((to - from) * i) / nn;
      return {x: cx + R * Math.cos(a), y: cy + ry * Math.sin(a)};
    });
  const items: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const jx = (random(`${seed}x${i}`) - 0.5) * R * 0.1;
    const cy = y - i * t - t, cx = x + jx;
    const a0 = random(`${seed}a${i}`) * 6.28;
    items.push(
      <g key={i}>
        <path d={`M ${cx - R} ${cy} A ${R} ${ry} 0 0 0 ${cx + R} ${cy} L ${cx + R} ${cy + t} A ${R} ${ry} 0 0 1 ${cx - R} ${cy + t} Z`} fill={T.fill} />
        {Array.from({length: 8}, (_, j) => {
          const th = a0 + (j / 8) * Math.PI * 2;
          if (Math.sin(th) < 0.15) return null;
          const xx = cx + R * Math.cos(th), yy = cy + ry * Math.sin(th);
          return <path key={j} d={stroke([{x: xx, y: yy + t * 0.12}, {x: xx + 0.5, y: yy + t * 0.88}], Math.max(1.6, R * 0.09) * Math.sin(th), ctx, `st${i}${j}`, {taper: [0.1, 0.1], press: () => 0.8})} fill={T.stripe} />;
        })}
        <path d={stroke(ell(cx, cy + t, 0, Math.PI), Math.max(1.4, R * 0.045), ctx, `b${i}`, {taper: [0.1, 0.1], press: () => 0.6})} fill={INK} />
        <path d={stroke([{x: cx - R, y: cy}, {x: cx - R, y: cy + t}], Math.max(1.4, R * 0.045), ctx, `l${i}`, {press: () => 0.6})} fill={INK} />
        <path d={stroke([{x: cx + R, y: cy}, {x: cx + R, y: cy + t}], Math.max(1.4, R * 0.045), ctx, `r${i}`, {press: () => 0.6})} fill={INK} />
        {i === n - 1 && (
          <g>
            <ellipse cx={cx} cy={cy} rx={R} ry={ry} fill={T.fill} />
            <path d={stroke(ell(cx, cy, -0.3, Math.PI * 2 - 0.1, 24), Math.max(1.6, R * 0.05), ctx, `top${i}`, {taper: [0.05, 0.1], press: () => 0.6})} fill={INK} />
            <path d={stroke(ell(cx, cy, 0, Math.PI * 2, 20).map((q) => ({x: cx + (q.x - cx) * 0.6, y: cy + (q.y - cy) * 0.6})), Math.max(1.2, R * 0.035), ctx, `in${i}`, {taper: [0.05, 0.1], press: () => 0.5})} fill={INK} opacity={0.7} />
            {Array.from({length: 8}, (_, j) => {
              const th = a0 + (j / 8) * Math.PI * 2;
              const p1 = {x: cx + R * 0.95 * Math.cos(th), y: cy + ry * 0.95 * Math.sin(th)};
              const p2 = {x: cx + R * 0.74 * Math.cos(th), y: cy + ry * 0.74 * Math.sin(th)};
              return <path key={j} d={stroke([p1, p2], Math.max(2, R * 0.12), ctx, `rt${i}${j}`, {taper: [0.05, 0.05], press: () => 0.8})} fill={tone === 0 ? INK : CARD_WHITE} opacity={tone === 0 ? 0.75 : 1} />;
            })}
          </g>
        )}
      </g>,
    );
  }
  return (
    <g>
      <InkShadow x={x + R * 0.2} y={y + ry * 0.3} rx={R * 1.15} ry={ry * 1.05} o={0.3} />
      {items}
    </g>
  );
};

// —— 桌布：一层淡绿的水彩，几道顺着桌面的淡排线 ——
export const InkFelt: React.FC<{pts: P[]; frame: number; seed?: string; o?: number; hatch?: boolean}> = ({pts, frame, seed = 'felt', o = 0.5, hatch = true}) => {
  const ctx: Ctx = {frame, seed, px: 1};
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const lines: [P, P][] = [];
  for (let i = 0; i < 18; i++) {
    const yy = y0 + ((i + 0.5) / 18) * (y1 - y0);
    const xx = x0 + random(`${seed}${i}`) * (x1 - x0) * 0.8;
    lines.push([{x: xx, y: yy}, {x: xx + 80 + random(`${seed}l${i}`) * 140, y: yy + 6}]);
  }
  return (
    <g>
      <Wash d={polyPath(pts)} color="#7FAE88" o={o} blur={6} rough={14} />
      {hatch && <Hatch lines={lines} size={1.6} ctx={ctx} color="#476B50" o={0.4} clip={polyPath(pts)} />}
    </g>
  );
};

export const InkRail: React.FC<{pts: P[]; w: number; frame: number; seed?: string}> = ({pts, w, frame, seed = 'rail'}) => {
  const ctx: Ctx = {frame, seed, px: 1};
  const up = pts.map((q) => add(q, {x: 0, y: -w / 2}));
  const dn = pts.map((q) => add(q, {x: 0, y: w / 2}));
  return (
    <g>
      <Wash d={polyPath([...up, ...dn.slice().reverse()])} color="#3A332D" o={0.55} blur={2} rough={6} />
      <path d={stroke(up, 3.4, ctx, 'up', {taper: [0.02, 0.02]})} fill={INK} />
      <path d={stroke(dn, 3.8, ctx, 'dn', {taper: [0.02, 0.02]})} fill={INK} />
    </g>
  );
};

