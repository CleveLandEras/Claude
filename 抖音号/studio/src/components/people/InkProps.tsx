// 画风 B 的道具和纸面：都是手画的线（perfect-freehand，每 3 帧轻轻抖一次），
// 暗处用一层淡墨（灰色水洗）压，阴影也是一块淡墨；光就是留出来的纸白。
import React, {useId} from 'react';
import {P, add, crSample, rot, smoothClosed} from './geom';
import {ink} from './ink';
import {HAND_CREASES, HAND_NAILS, HAND_OUTLINE} from './FlatProps';
import {INK, PAPER} from './InkPerson';

const useUid = () => useId().replace(/[^a-zA-Z0-9]/g, '');

// 纸：底色 + 很淡的纸纹 + 四角稍微暗一点
export const Paper: React.FC<{w: number; h: number; tone?: string}> = ({w, h, tone = PAPER}) => {
  const id = useUid();
  return (
    <g>
      <rect width={w} height={h} fill={tone} />
      <filter id={`${id}n`} x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed={7} />
        <feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.24  0 0 0 0.09 0" />
      </filter>
      <rect width={w} height={h} filter={`url(#${id}n)`} />
      <filter id={`${id}f`} x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="2" seed={2} />
        <feColorMatrix values="0 0 0 0 0.4  0 0 0 0 0.34  0 0 0 0 0.26  0 0 0 0.12 0" />
      </filter>
      <rect width={w} height={h} filter={`url(#${id}f)`} />
    </g>
  );
};

// 淡墨：一块边缘柔软、不规则的灰（水洗），叠在纸上用 multiply
export const Wash: React.FC<{d: string; color?: string; o?: number; blur?: number; rough?: number}> = ({d, color = '#8F877B', o = 0.35, blur = 10, rough = 18}) => {
  const id = useUid();
  return (
    <g style={{mixBlendMode: 'multiply'}}>
      <filter id={id} x="-20%" y="-20%" width="140%" height="140%">
        <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed={11} result="t" />
        <feDisplacementMap in="SourceGraphic" in2="t" scale={rough} xChannelSelector="R" yChannelSelector="G" result="d" />
        <feGaussianBlur in="d" stdDeviation={blur} />
      </filter>
      <path d={d} fill={color} opacity={o} filter={`url(#${id})`} />
    </g>
  );
};

export const InkShadow: React.FC<{x: number; y: number; rx: number; ry: number; o?: number}> = ({x, y, rx, ry, o = 0.32}) => (
  <Wash d={`M ${x - rx} ${y} A ${rx} ${ry} 0 1 1 ${x + rx} ${y} A ${rx} ${ry} 0 1 1 ${x - rx} ${y} Z`} o={o} blur={Math.max(3, ry * 0.35)} rough={ry * 0.5} color="#7A7266" />
);

type Ctx = {frame: number; seed: string; px: number};
export const stroke = (pts: P[], size: number, c: Ctx, name: string, extra: Record<string, unknown> = {}) =>
  ink(pts, {size, seed: `${c.seed}-${name}`, frame: c.frame, px: c.px, ...extra});

// 排线：给一组平行线的两端，逐条画成短笔
export const Hatch: React.FC<{lines: [P, P][]; size: number; ctx: Ctx; color?: string; o?: number; clip?: string}> = ({lines, size, ctx, color = INK, o = 0.55, clip}) => {
  const id = useUid();
  return (
    <g opacity={o}>
      {clip && <clipPath id={id}><path d={clip} /></clipPath>}
      <g clipPath={clip ? `url(#${id})` : undefined}>
        {lines.map((l, i) => <path key={i} d={stroke(l, size, ctx, `h${i}`, {taper: [0.3, 0.3]})} fill={color} />)}
      </g>
    </g>
  );
};

// —— 吊灯：一根线、一个手画的灯罩，灯下一圈纸白（周围是淡墨），灯泡一点暖黄 ——
export const InkLamp: React.FC<{x: number; y: number; w: number; top?: number; frame: number; seed?: string; glow?: number}> = (
  {x, y, w, top = -40, frame, seed = 'lamp', glow = 1},
) => {
  const c: Ctx = {frame, seed, px: 1};
  const h = w * 0.55;
  const shade = [
    {x: x - w * 0.5, y}, {x: x - w * 0.4, y: y - h * 0.3}, {x: x - w * 0.18, y: y - h * 0.62}, {x: x - w * 0.13, y: y - h},
    {x: x + w * 0.13, y: y - h}, {x: x + w * 0.18, y: y - h * 0.62}, {x: x + w * 0.4, y: y - h * 0.3}, {x: x + w * 0.5, y},
  ];
  return (
    <g>
      <Wash d={`M ${x - w * 0.8} ${y + w * 0.1} A ${w * 0.8} ${w * 0.7} 0 1 0 ${x + w * 0.8} ${y + w * 0.1} A ${w * 0.8} ${w * 0.7} 0 1 0 ${x - w * 0.8} ${y + w * 0.1} Z`}
        color="#F3D57E" o={0.45 * glow} blur={w * 0.18} rough={w * 0.1} />
      <path d={stroke([{x, y: top}, {x: x + 1, y: (top + y - h) / 2}, {x, y: y - h}], 3, c, 'cord')} fill={INK} />
      <path d={smoothClosed(shade)} fill={INK} opacity={0.82} />
      <path d={stroke([...shade, {x: x - w * 0.5, y: y + 1}], 4, c, 'shade', {smooth: true, taper: [0.05, 0.1]})} fill={INK} />
      <path d={stroke([{x: x - w * 0.48, y: y + 2}, {x, y: y + w * 0.08}, {x: x + w * 0.48, y: y + 2}], 3.4, c, 'rim')} fill={INK} />
      <ellipse cx={x} cy={y + w * 0.05} rx={w * 0.17} ry={w * 0.09} fill="#F3C964" opacity={glow} />
      {[-1, -0.5, 0, 0.5, 1].map((k, i) => (
        <path key={i} d={stroke([{x: x + k * w * 0.42, y: y + w * 0.22}, {x: x + k * w * 0.62, y: y + w * 0.38}], 2.4, c, `ray${i}`)} fill={INK} opacity={0.6 * glow} />
      ))}
    </g>
  );
};

// —— 木椅（侧 3/4，椅面朝右；单位、原点和 FlatProps.Chair 一样） ——
export const InkChair: React.FC<{x: number; y: number; s: number; frame: number; seed?: string; light?: boolean}> = ({x, y, s, frame, seed = 'chair', light}) => {
  const c: Ctx = {frame, seed, px: s};
  const off = {x: 12, y: -9};
  const seatY = -40, front = 16, back = -40, postTop = -122;
  const k = light ? 0.7 : 1;   // 背景里的椅子：线细一点、淡一点
  const L = (pts: P[], w: number, n: string, o = 1) => <path key={n} d={stroke(pts, w * k, c, n)} fill={INK} opacity={o * (light ? 0.75 : 1)} />;
  const far = (q: P) => add(q, off);
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <InkShadow x={-10} y={2} rx={70} ry={7} />
      {L([far({x: front - 3, y: 0}), far({x: front - 3, y: seatY})], 3.4, 'fl', 0.75)}
      {L([far({x: back + 3, y: 0}), far({x: back - 8, y: postTop})], 3.4, 'fb', 0.75)}
      {L([{x: back - 2, y: seatY}, {x: front + 2, y: seatY}, far({x: front + 2, y: seatY}), far({x: back - 2, y: seatY})], 3.2, 'seat')}
      {L([{x: back - 2, y: seatY + 6}, {x: front + 2, y: seatY + 6}], 2.8, 'seat2')}
      {L([{x: front - 3, y: seatY + 6}, {x: front - 3, y: 0}], 4, 'nl')}
      {L([{x: back + 3, y: 0}, {x: back - 9, y: postTop}], 4, 'nb')}
      {L([{x: back - 12, y: postTop + 2}, far({x: back - 8, y: postTop})], 3.6, 'rail1')}
      {L([{x: back - 12, y: postTop + 20}, far({x: back - 8, y: postTop + 18})], 3, 'rail2')}
      {L([{x: back - 6, y: -82}, far({x: back - 4, y: -82})], 2.6, 'rail3')}
      {L([{x: back + 3, y: -14}, {x: front - 3, y: -14}], 2.6, 'str')}
      <Hatch lines={[0, 1, 2, 3, 4].map((i) => [{x: back + 4 + i * 11, y: seatY + 1}, {x: back + 9 + i * 11, y: seatY + 5}] as [P, P])} size={1.6} ctx={c} o={0.5} />
    </g>
  );
};

// —— 伸过来的手（右手，手背朝上，往左）：和 FlatProps.ReachHand 同一条轮廓，描成墨线 ——
export const InkReachHand: React.FC<{x: number; y: number; s: number; r?: number; frame: number; seed?: string}> = ({x, y, s, r = 0, frame, seed = 'hand'}) => {
  const c: Ctx = {frame, seed, px: s};
  const outline = crSample(HAND_OUTLINE, 5, true);
  // 分三段描：上沿到小指、四根手指、拇指到手腕下沿
  const n = outline.length;
  const seg = (a: number, b: number) => outline.slice(Math.floor(a * n), Math.floor(b * n) + 1);
  return (
    <g transform={`translate(${x} ${y}) rotate(${r}) scale(${s})`}>
      <InkShadow x={-30} y={46} rx={64} ry={10} />
      <path d={smoothClosed(HAND_OUTLINE, 0.75)} fill={PAPER} />
      <path d={stroke(seg(0, 0.3), 3.2, c, 'o1')} fill={INK} />
      <path d={stroke(seg(0.28, 0.62), 3, c, 'o2')} fill={INK} />
      <path d={stroke(seg(0.6, 1), 3.2, c, 'o3')} fill={INK} />
      {HAND_CREASES.map((q, i) => <path key={i} d={stroke(q, 2, c, `cr${i}`)} fill={INK} opacity={0.8} />)}
      {HAND_NAILS.map(([q, a], i) => (
        <path key={`n${i}`} d={stroke([rot({x: -3, y: -2}, a), rot({x: 2, y: -2.4}, a), rot({x: 3.4, y: 1}, a)].map((v) => add(q, v)), 1.4, c, `n${i}`)} fill={INK} opacity={0.6} />
      ))}
      {/* 袖口、袖子 */}
      <path d={stroke([{x: -1, y: -31}, {x: -5, y: 0}, {x: -1, y: 31}], 3.4, c, 'cuff')} fill={INK} />
      <path d={stroke([{x: 20, y: -36}, {x: 22, y: 0}, {x: 20, y: 36}], 3, c, 'cuff2')} fill={INK} />
      <path d={stroke([{x: 0, y: -31}, {x: 120, y: -40}, {x: 300, y: -50}], 3.4, c, 'sl1')} fill={INK} />
      <path d={stroke([{x: 0, y: 31}, {x: 120, y: 42}, {x: 300, y: 54}], 3.4, c, 'sl2')} fill={INK} />
      {[5, 11].map((k, i) => <path key={k} d={stroke([{x: k, y: -27}, {x: k + 1, y: 27}], 1.6, c, `rib${i}`)} fill={INK} opacity={0.55} />)}
      <Hatch lines={[0, 1, 2, 3, 4, 5, 6, 7].map((i) => [{x: 40 + i * 22, y: 24 + i * 1.2}, {x: 52 + i * 22, y: 44 + i * 1.4}] as [P, P])} size={1.8} ctx={c} o={0.45} />
    </g>
  );
};

