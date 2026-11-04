// 画风 A 的牌、筹码、牌桌。
// 牌：米白卡纸，圆角，左上和右下角有点数和小花色（右下角倒过来），中间是花色点；人头牌画成一个框加大字母。
//     放在桌上时：按桌面压扁、转一个角度，下面露出纸的厚度，再投一个软阴影。可以掀起一角（看底牌），可以翻面。
// 筹码：顶面一个椭圆、侧面一圈，边上有一段段白色的边纹；不写面额。
// 牌桌：绿色绒布（有一点绒的颗粒）、灯下一圈亮、印着一条下注线；边上一圈黑皮包边。
import React, {useId} from 'react';
import {random} from 'remotion';
import {P, mixHex, polyPath} from './geom';
import {CH, CR, CW, CardId, RANK_FONT, Suit, SUIT_PATH, isRed, peekGeom, pipSpots} from './cards';
import {SoftShadow} from './FlatProps';

const useUid = () => useId().replace(/[^a-zA-Z0-9]/g, '');
export const RED = '#C23A2E';
export const BLACK = '#1D1A1E';
export const CARD_PAPER = '#FBF7EE';

const Pip: React.FC<{s: Suit; x: number; y: number; size: number; flip?: boolean; color: string}> = ({s, x, y, size, flip, color}) => (
  <path d={SUIT_PATH[s]} fill={color} transform={`translate(${x} ${y}) scale(${size}) ${flip ? 'rotate(180)' : ''}`} />
);

// —— 牌面（牌的局部坐标：中心为原点，宽 100 高 140）——
export const CardFace: React.FC<{c: CardId; paper?: string}> = ({c, paper = CARD_PAPER}) => {
  const col = isRed(c.s) ? RED : BLACK;
  const ten = c.r === '10';
  const idx = (rot: number, k: string) => (
    <g key={k} transform={`rotate(${rot})`}>
      <text x={-CW / 2 + 11.5} y={-CH / 2 + 24} textAnchor="middle" fontFamily={RANK_FONT} fontWeight={700} fontSize={ten ? 19 : 23}
        letterSpacing={ten ? -2.5 : 0} fill={col}>{c.r}</text>
      <Pip s={c.s} x={-CW / 2 + 11.5} y={-CH / 2 + 36} size={12.5} color={col} />
    </g>
  );
  const court = c.r === 'J' || c.r === 'Q' || c.r === 'K';
  return (
    <g>
      <rect x={-CW / 2} y={-CH / 2} width={CW} height={CH} rx={CR} fill={paper} />
      {idx(0, 'a')}
      {idx(180, 'b')}
      {c.r === 'A' && <Pip s={c.s} x={0} y={0} size={c.s === 'S' ? 50 : 40} color={col} />}
      {c.r === 'A' && c.s === 'S' && <circle cx={0} cy={-2} r={34} fill="none" stroke={col} strokeWidth={1.2} opacity={0.5} />}
      {!court && c.r !== 'A' && pipSpots(c.r).map((q, i) => (
        <Pip key={i} s={c.s} x={q.p.x * 0.84} y={q.p.y * 0.86} size={ten || c.r === '9' ? 15.5 : 18} flip={q.flip} color={col} />
      ))}
      {court && (
        <g>
          <rect x={-CW / 2 + 22} y={-CH / 2 + 16} width={CW - 44} height={CH - 32} rx={3} fill={mixHex(paper, isRed(c.s) ? '#E9B9A6' : '#B9B4C4', 0.35)}
            stroke={col} strokeWidth={1.4} />
          <text x={0} y={18} textAnchor="middle" fontFamily={RANK_FONT} fontWeight={700} fontSize={58} fill={col}>{c.r}</text>
          <Pip s={c.s} x={-CW / 2 + 31} y={-CH / 2 + 27} size={11} color={col} />
          <Pip s={c.s} x={CW / 2 - 31} y={CH / 2 - 27} size={11} flip color={col} />
          {/* 王冠：三个尖 */}
          <path d="M -15 -28 L -15 -40 L -8 -33 L 0 -44 L 8 -33 L 15 -40 L 15 -28 Z" fill={col} opacity={c.r === 'J' ? 0 : 0.9} />
          {c.r === 'J' && <path d="M -14 -30 Q 0 -46 14 -30 Z" fill={col} opacity={0.9} />}
        </g>
      )}
    </g>
  );
};

// —— 牌背：深蓝底、白边、斜格纹 ——
export const CardBack: React.FC<{color?: string}> = ({color = '#2E4470'}) => {
  const id = useUid();
  return (
    <g>
      <defs>
        <pattern id={`${id}p`} width={10} height={10} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width={10} height={10} fill={color} />
          <rect width={10} height={2.2} fill={mixHex(color, '#FFFFFF', 0.28)} />
          <rect width={2.2} height={10} fill={mixHex(color, '#FFFFFF', 0.28)} />
        </pattern>
      </defs>
      <rect x={-CW / 2} y={-CH / 2} width={CW} height={CH} rx={CR} fill={CARD_PAPER} />
      <rect x={-CW / 2 + 7} y={-CH / 2 + 7} width={CW - 14} height={CH - 14} rx={4} fill={`url(#${id}p)`} />
      <rect x={-CW / 2 + 7} y={-CH / 2 + 7} width={CW - 14} height={CH - 14} rx={4} fill="none" stroke={mixHex(color, '#000000', 0.3)} strokeWidth={1.4} />
      <ellipse cx={0} cy={0} rx={18} ry={26} fill={color} stroke={mixHex(color, '#FFFFFF', 0.45)} strokeWidth={2} />
    </g>
  );
};

const cardRect = `M ${-CW / 2 + CR} ${-CH / 2} H ${CW / 2 - CR} Q ${CW / 2} ${-CH / 2} ${CW / 2} ${-CH / 2 + CR} V ${CH / 2 - CR} Q ${CW / 2} ${CH / 2} ${CW / 2 - CR} ${CH / 2} H ${-CW / 2 + CR} Q ${-CW / 2} ${CH / 2} ${-CW / 2} ${CH / 2 - CR} V ${-CH / 2 + CR} Q ${-CW / 2} ${-CH / 2} ${-CW / 2 + CR} ${-CH / 2} Z`;

// —— 桌上的一张牌 ——
// x, y：牌心在画面上的位置；s：大小；rot：在桌面上转的角度；sq：桌面压扁（1 = 正上方往下看）
// face：翻开的牌；不给就是扣着；peek：掀起右下角 0..1；flip：从扣着翻到正面 0..1；light：受光 0..1
export const TableCard: React.FC<{
  x: number; y: number; s: number; rot?: number; sq?: number; face?: CardId; down?: boolean; peek?: number; flip?: number;
  dim?: number; back?: string; shadow?: number; lift?: number;
}> = ({x, y, s, rot = 0, sq = 0.55, face, down, peek = 0, flip, dim = 0, back, shadow = 0.55, lift = 0}) => {
  const id = useUid();
  const T = `translate(${x} ${y}) scale(${s} ${s * sq}) rotate(${rot})`;
  const thick = 2.6 * s;
  const fl = flip ?? (down || !face ? 0 : 1);
  const showFace = face && fl >= 0.5;
  const sx = Math.abs(Math.cos(Math.PI * fl));
  const up = Math.sin(Math.PI * Math.min(1, fl)) * (flip !== undefined ? 1 : 0) * 40 * s + lift * s;
  const pg = peekGeom(peek);
  const {A, B: Bp, C2, faceMat} = pg;
  const bodyClip = polyPath(pg.clip);
  const C = (c: string) => mixHex(c, '#0C0A0A', dim);
  return (
    <g opacity={1 - dim * 0.15}>
      <SoftShadow x={x + 5 * s + up * 0.15} y={y + 8 * s * sq + up * 0.35} rx={CW * 0.55 * s * (0.6 + 0.4 * sx) + up * 0.2} ry={CH * 0.5 * s * sq} o={shadow * (1 - up / (200 * s))} />
      <g transform={`translate(0 ${-up})`}>
        {/* 纸的厚度：在画面上往下挪一点，画一层暗一点的边 */}
        <g transform={`translate(0 ${thick})`}>
          <g transform={T}>
            <clipPath id={`${id}e`}><path d={bodyClip} /></clipPath>
            <g transform={`scale(${sx} 1)`} clipPath={peek > 0.01 ? `url(#${id}e)` : undefined}><path d={cardRect} fill={C('#C9BFAC')} /></g>
          </g>
        </g>
        <g transform={T}>
          <clipPath id={`${id}b`}><path d={bodyClip} /></clipPath>
          <g transform={`scale(${sx} 1)`} clipPath={peek > 0.01 ? `url(#${id}b)` : undefined}>
            <g style={{filter: dim > 0 ? `brightness(${1 - dim * 0.75})` : undefined}}>
              {showFace ? <CardFace c={face!} /> : <CardBack color={back} />}
            </g>
          </g>
          {peek > 0.01 && face && (
            <g>
              <path d={polyPath([A, Bp, pg.C])} fill="#000" opacity={0.22} transform="translate(3 -2)" />
              <clipPath id={`${id}f`}><path d={polyPath([A, Bp, C2])} /></clipPath>
              <g clipPath={`url(#${id}f)`} style={{filter: dim > 0 ? `brightness(${1 - dim * 0.75})` : undefined}}>
                <g transform={faceMat}><CardFace c={face} /></g>
                <path d={polyPath([A, Bp, C2])} fill="#8A7A66" opacity={0.12} />
              </g>
              <path d={`M ${A.x} ${A.y} L ${Bp.x} ${Bp.y}`} stroke="#B9AE9A" strokeWidth={1.4} />
            </g>
          )}
        </g>
      </g>
    </g>
  );
};

// —— 竖着立起来的牌（比喻镜头）：不压扁；glow：发亮 ——
export const StandingCard: React.FC<{x: number; y: number; s: number; face?: CardId; glow?: number; dim?: number; back?: string; tilt?: number}> = (
  {x, y, s, face, glow = 0, dim = 0, back, tilt = 0},
) => {
  const id = useUid();
  return (
    <g transform={`translate(${x} ${y}) rotate(${tilt})`}>
      {glow > 0 && (
        <g style={{mixBlendMode: 'screen'}}>
          <filter id={`${id}g`} x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation={26 * s} /></filter>
          <rect x={-CW * 0.62 * s} y={-CH * 1.1 * s} width={CW * 1.24 * s} height={CH * 1.2 * s} rx={10 * s} fill="#FFC861" opacity={0.95 * glow} filter={`url(#${id}g)`} />
        </g>
      )}
      <g transform={`scale(${s}) translate(0 ${-CH / 2})`}>
        <path d={cardRect} fill="#CFC6B4" transform="translate(3 1)" />
        <g style={{filter: dim > 0 ? `brightness(${1 - dim * 0.8})` : undefined}}>
          {face ? <CardFace c={face} /> : <CardBack color={back} />}
        </g>
        {glow > 0 && <path d={cardRect} fill="#FFC861" opacity={0.42 * glow} style={{mixBlendMode: 'screen'}} />}
      </g>
    </g>
  );
};

// —— 筹码 ——
export type ChipColor = {base: string; edge: string; inlay: string};
export const CHIP: Record<string, ChipColor> = {
  navy: {base: '#2F4D7C', edge: '#F1EBDD', inlay: '#3E5F92'},
  cream: {base: '#E8DFCC', edge: '#2F4D7C', inlay: '#F3EDE1'},
  black: {base: '#2A272D', edge: '#D7B357', inlay: '#38343B'},
  amber: {base: '#C88E30', edge: '#F6F0E2', inlay: '#D9A247'},
  plum: {base: '#6A3F5E', edge: '#F1E6EC', inlay: '#7B4E6E'},
};

// 一枚筹码，(x, y) 是顶面中心，R 是半径（屏幕像素），sq 是压扁，t 是厚度（屏幕像素），a0 是边纹转到哪
const ChipShape: React.FC<{x: number; y: number; R: number; sq: number; t: number; c: ChipColor; a0: number; top: boolean; dim: number}> = (
  {x, y, R, sq, t, c, a0, top, dim},
) => {
  const C = (k: string) => mixHex(k, '#0B0A0A', dim);
  const ry = R * sq;
  const side = `M ${x - R} ${y} A ${R} ${ry} 0 0 0 ${x + R} ${y} L ${x + R} ${y + t} A ${R} ${ry} 0 0 1 ${x - R} ${y + t} Z`;
  const stripes: React.ReactNode[] = [];
  for (let i = 0; i < 8; i++) {
    const th = a0 + (i / 8) * Math.PI * 2;
    const w = 0.2;
    if (Math.sin(th) > 0.05) {
      const xa = x + R * Math.cos(th - w / 2), xb = x + R * Math.cos(th + w / 2);
      const ya = y + ry * Math.sin(th - w / 2), yb = y + ry * Math.sin(th + w / 2);
      stripes.push(<path key={`s${i}`} d={polyPath([{x: xa, y: ya}, {x: xb, y: yb}, {x: xb, y: yb + t}, {x: xa, y: ya + t}])} fill={C(mixHex(c.edge, '#000000', 0.12))} />);
    }
  }
  const rim: React.ReactNode[] = [];
  if (top) {
    for (let i = 0; i < 8; i++) {
      const th = a0 + (i / 8) * Math.PI * 2;
      const w = 0.24;
      const pts = [[th - w / 2, 0.97], [th + w / 2, 0.97], [th + w / 2, 0.76], [th - w / 2, 0.76]].map(([a, r]) => ({x: x + R * r * Math.cos(a), y: y + ry * r * Math.sin(a)}));
      rim.push(<path key={`r${i}`} d={polyPath(pts)} fill={C(c.edge)} />);
    }
  }
  return (
    <g>
      <path d={side} fill={C(mixHex(c.base, '#000000', 0.28))} />
      {stripes}
      <ellipse cx={x} cy={y} rx={R} ry={ry} fill={C(c.base)} />
      {top && rim}
      {top && <ellipse cx={x} cy={y} rx={R * 0.6} ry={ry * 0.6} fill={C(c.inlay)} />}
      {top && <ellipse cx={x} cy={y} rx={R * 0.6} ry={ry * 0.6} fill="none" stroke={C(c.edge)} strokeWidth={Math.max(0.8, R * 0.035)} opacity={0.7} />}
      {top && <path d={`M ${x - R * 0.82} ${y - ry * 0.2} A ${R * 0.85} ${ry * 0.85} 0 0 1 ${x - R * 0.1} ${y - ry * 0.84}`} fill="none" stroke="#FFFFFF" strokeWidth={Math.max(1, R * 0.06)} opacity={0.18} strokeLinecap="round" />}
    </g>
  );
};

// 一摞筹码：n 枚，从下往上，每枚歪一点点
export const ChipStack: React.FC<{x: number; y: number; R: number; n: number; c: ChipColor; sq?: number; t?: number; seed?: string; dim?: number; shadow?: number}> = (
  {x, y, R, n, c, sq = 0.5, t, seed = 'cs', dim = 0, shadow = 0.5},
) => {
  const th = t ?? R * 0.2;
  return (
    <g>
      <SoftShadow x={x + R * 0.18} y={y + R * sq * 0.35} rx={R * 1.18} ry={R * sq * 1.05} o={shadow} blur={R * 0.16} />
      {Array.from({length: n}, (_, i) => {
        const jx = (random(`${seed}x${i}`) - 0.5) * R * 0.1;
        const jy = (random(`${seed}y${i}`) - 0.5) * R * 0.03;
        return <ChipShape key={i} x={x + jx} y={y - i * th + jy - th} R={R} sq={sq} t={th} c={c} a0={random(`${seed}a${i}`) * 6.28} top={i === n - 1} dim={dim} />;
      })}
    </g>
  );
};

// 一枚平放的散落筹码
export const LooseChip: React.FC<{x: number; y: number; R: number; c: ChipColor; sq?: number; seed?: string; dim?: number}> = ({x, y, R, c, sq = 0.5, seed = 'lc', dim = 0}) => (
  <ChipStack x={x} y={y} R={R} n={1} c={c} sq={sq} seed={seed} dim={dim} shadow={0.45} />
);

// —— 绿色绒布桌面：给一个多边形（画面坐标），灯光在 (lx, ly) ——
export const Felt: React.FC<{pts: P[]; lx: number; ly: number; lr: number; sq?: number; line?: {cx: number; cy: number; rx: number; ry: number}; dim?: number}> = (
  {pts, lx, ly, lr, sq = 0.5, line, dim = 0},
) => {
  const id = useUid();
  const C = (c: string) => mixHex(c, '#070A08', dim);
  return (
    <g>
      <defs>
        <radialGradient id={`${id}l`} cx={lx} cy={ly} r={lr} gradientUnits="userSpaceOnUse" gradientTransform={`translate(0 ${ly * (1 - sq)}) scale(1 ${sq})`}>
          <stop offset="0" stopColor={C('#4C9A6E')} />
          <stop offset="0.55" stopColor={C('#357A55')} />
          <stop offset="1" stopColor={C('#1C4A33')} />
        </radialGradient>
        <filter id={`${id}n`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={3} />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0.08  0 0 0 0 0.03  0 0 0 0.55 0" />
          <feComposite in2="SourceGraphic" operator="in" />
        </filter>
        <clipPath id={`${id}c`}><path d={polyPath(pts)} /></clipPath>
      </defs>
      <path d={polyPath(pts)} fill={`url(#${id}l)`} />
      <g clipPath={`url(#${id}c)`}>
        <path d={polyPath(pts)} fill="#000" filter={`url(#${id}n)`} opacity={0.6} />
        {line && <ellipse cx={line.cx} cy={line.cy} rx={line.rx} ry={line.ry} fill="none" stroke={C('#8CC7A2')} strokeWidth={3} opacity={0.35} />}
      </g>
    </g>
  );
};

// —— 黑皮包边：沿一条曲线的一段鼓起来的皮条，上沿一道受光 ——
export const Rail: React.FC<{d: string; w: number; dim?: number}> = ({d, w, dim = 0}) => {
  const C = (c: string) => mixHex(c, '#050404', dim);
  return (
    <g>
      <path d={d} fill="none" stroke={C('#1E1714')} strokeWidth={w} strokeLinecap="round" />
      <path d={d} fill="none" stroke={C('#2E2420')} strokeWidth={w * 0.62} strokeLinecap="round" transform={`translate(0 ${-w * 0.14})`} />
      <path d={d} fill="none" stroke={C('#5A4A40')} strokeWidth={Math.max(1.5, w * 0.08)} strokeLinecap="round" transform={`translate(0 ${-w * 0.33})`} opacity={0.8} />
    </g>
  );
};
