// 002 近景的人：用现成的 FlatPerson（画风 A），只在这里补分镜要的新姿势和表情，不改 components/people 里的文件。
// 补上的：递（双手往前伸）、伸手抢、缩肩、抱胳膊、抬头看、转身面对镜头；表情：一边嘴角翘、僵着、笑、冷着脸。
// 半透明的“影子你”= 同一个人整体压透明度。
import React, {useId} from 'react';
import {FlatPerson} from '../../components/people/FlatPerson';
import {EXPR, Expr, blink, breath, withBlink} from '../../components/people/face';
import {Look, ME, OTHER} from '../../components/people/look';
import {Pose, RPose, mixPose, nudge, resolve, solve} from '../../components/people/rig';
import {mixHex} from '../../components/people/geom';
import {COL, GRABHAND, SANS, clamp} from './lib';

const STAND: Pose = {yaw: 0.55, pelvis: -2, lean: 1, chest: 1, neck: 2, lN: {hip: 3, knee: 0}, lF: {hip: 10, knee: 10}, ground: true};
const P = (o: Pose) => resolve({...STAND, ...o});

export const POSE = {
  idle: P({aN: {sh: 4, el: 14}, aF: {sh: -4, el: 14}, hN: 'limp', hF: 'limp'}),
  // 双手把光点往前递
  give: P({lean: 5, neck: 4, gaze: {x: 1, y: 0.15}, aN: {to: {x: 64, y: -62}, wr: -15}, aF: {to: {x: 56, y: -58}, wr: -15}, hN: 'open', hF: 'open'}),
  // 一只手往前伸（抢、接）
  reach: P({lean: 8, gaze: {x: 1, y: 0.1}, aN: {to: {x: 70, y: -58}, wr: -25}, aF: {sh: -6, el: 16}, hN: 'open', hF: 'limp'}),
  // 手收回胸前（抢到手）
  pull: P({lean: -3, aN: {to: {x: 26, y: -60}, wr: 20}, aF: {sh: -6, el: 16}, hN: 'fist', hF: 'limp'}),
  // 缩起肩
  hunch: P({lean: 7, chest: 6, neck: 10, shrug: 1, pitch: 0.35, gaze: {x: 0.4, y: 0.6}, aN: {sh: 12, el: 40}, aF: {sh: 8, el: 40}, hN: 'fist', hF: 'fist'}),
  // 抱起胳膊（两只前臂横在胸前）
  cross: P({lean: -3, neck: -4, front: true, aN: {to: {x: -12, y: -36}, bend: 1}, aF: {to: {x: 18, y: -40}, bend: -1}, hN: 'fist', hF: 'fist'}),
  // 抬头看（转头看分高的人）
  lookUp: P({neck: -12, pitch: -0.35, gaze: {x: 0.9, y: -0.8}, aN: {sh: 4, el: 14}, aF: {sh: -4, el: 14}, hN: 'limp', hF: 'limp'}),
  // 正面（转身面对镜头）
  front: resolve({yaw: 0.04, pelvis: 0, lean: 0, chest: 0, neck: 0, gaze: {x: 0, y: 0},
    lN: {hip: 2, knee: 0}, lF: {hip: -2, knee: 0}, aN: {sh: 8, el: 10}, aF: {sh: -8, el: 10}, hN: 'limp', hF: 'limp', ground: true}),
};
export type PoseKey = keyof typeof POSE;

export const EX: Record<string, Expr> = {
  calm: EXPR.calm, blank: EXPR.blank, worry: EXPR.worry, sad: EXPR.sad, relief: EXPR.relief, surprise: EXPR.surprise,
  // 一边嘴角翘起来（得意）
  smirk: {...EXPR.calm, smirk: 1, smile: 0.1, lid: 0.32, brow: -0.05, browIn: -0.3, asym: 0.8, blush: 0.3},
  // 僵着（互相报复时）
  stiff: {...EXPR.calm, brow: -0.1, browIn: -0.75, knit: 0.8, smile: -0.35, mouthW: 0.7, lid: 0.18, blush: 0.2},
  // 冷着脸（记仇的）
  cold: {...EXPR.suspect, smirk: 0, smile: -0.2},
  // 笑
  smile: {...EXPR.calm, smile: 0.75, lid: 0.25, brow: 0.1, blush: 0.8},
};

// 衣服颜色 = 打法颜色。你：连帽衫、短发翘毛（ME）；别人：外套、齐肩发（OTHER）
export const lookFor = (strategy: number, who: 'me' | 'other'): Look => {
  const c = COL[strategy];
  const base = who === 'me' ? ME : OTHER;
  return {...base, top: c, topShade: mixHex(c, '#000000', 0.28)};
};

// 关键帧：[[帧, 姿势名或 RPose], ...]
export const track = (f: number, keys: [number, PoseKey | RPose][], ease = (t: number) => t * t * (3 - 2 * t)): RPose => {
  const get = (k: PoseKey | RPose) => (typeof k === 'string' ? POSE[k] : k);
  if (f <= keys[0][0]) return get(keys[0][1]);
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, a] = keys[i - 1], [f1, b] = keys[i];
      return mixPose(get(a), get(b), ease((f - f0) / Math.max(1e-6, f1 - f0)));
    }
  }
  return get(keys[keys.length - 1][1]);
};
export const exTrack = (f: number, keys: [number, string][]): Expr => {
  const mix = (a: Expr, b: Expr, t: number) => {
    const o = {} as Expr;
    (Object.keys(a) as (keyof Expr)[]).forEach((k) => (o[k] = a[k] + (b[k] - a[k]) * t));
    return o;
  };
  if (f <= keys[0][0]) return EX[keys[0][1]];
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, a] = keys[i - 1], [f1, b] = keys[i];
      const t = clamp((f - f0) / Math.max(1e-6, f1 - f0));
      return mix(EX[a], EX[b], t * t * (3 - 2 * t));
    }
  }
  return EX[keys[keys.length - 1][1]];
};

// 屏幕上的手、头顶
export const handAt = (r: RPose, x: number, G: number, s: number, facing: 1 | -1, near = true) => {
  const sk = solve(r);
  const w = near ? sk.wN : sk.wF;
  return {x: x + facing * w.x * s, y: G + w.y * s};
};
export const handsMid = (r: RPose, x: number, G: number, s: number, facing: 1 | -1) => {
  const a = handAt(r, x, G, s, facing, true), b = handAt(r, x, G, s, facing, false);
  return {x: (a.x + b.x) / 2, y: (a.y + b.y) / 2};
};
export const headTop = (r: RPose, x: number, G: number, s: number, facing: 1 | -1) => {
  const sk = solve(r);
  return {x: x + facing * sk.head.x * s, y: G + (sk.head.y - 62) * s};
};

export type ManProps = {
  f: number; pose: RPose; expr: Expr; strategy: number; who: 'me' | 'other';
  x: number; G: number; s: number; facing?: 1 | -1;
  opacity?: number; dim?: number; seed?: string;
  // 衣服从上往下刷成另一个颜色：to = 新打法，p = 0..1
  recolor?: {to: number; p: number};
  breathe?: boolean;
  breathAmp?: number;      // 呼吸幅度倍数（结尾要看得出在呼吸）
  blinks?: number[];       // 另外指定在这几帧眨眼
};
// 一个人：带呼吸、眨眼；可以整件衣服从上往下刷色
export const Man: React.FC<ManProps> = (p) => {
  const id = useId().replace(/[^a-zA-Z0-9]/g, '');
  const facing = p.facing ?? 1;
  const k = p.breathAmp ?? 1;
  const r = p.breathe === false ? p.pose : nudge(p.pose, {shrug: 0.05 * k * breath(p.f), chest: -0.4 * k * breath(p.f), y: -0.8 * (k - 1) * breath(p.f)});
  const BL = [0.45, 1, 1, 0.7, 0.35, 0.1];
  const extra = (p.blinks ?? []).reduce((m, b) => (p.f - b >= 0 && p.f - b < BL.length ? Math.max(m, BL[p.f - b]) : m), 0);
  const e = withBlink(p.expr, Math.max(blink(p.f, p.seed ?? p.who), extra));
  const body = (strategy: number) => (
    <FlatPerson pose={r} expr={e} look={lookFor(strategy, p.who)} x={p.x} y={p.G} s={p.s} facing={facing}
      dim={p.dim ?? 0} night="#0B0D12" light={{x: -0.35 * facing, y: -1}} />
  );
  const top = p.G - 280 * p.s;
  const h = 300 * p.s;
  return (
    <g opacity={p.opacity ?? 1}>
      {body(p.strategy)}
      {p.recolor && p.recolor.p > 0 && (
        <>
          <clipPath id={`${id}rc`}><rect x={p.x - 200 * p.s} y={top} width={400 * p.s} height={h * clamp(p.recolor.p)} /></clipPath>
          <g clipPath={`url(#${id}rc)`}>{body(p.recolor.to)}</g>
        </>
      )}
    </g>
  );
};

// 抢的那只橙红的手（灰框：一个橙红圆加三根短指头）
export const GrabHand: React.FC<{x: number; y: number; r?: number; dir?: number; o?: number}> = ({x, y, r = 30, dir = 0, o = 1}) => (
  <g transform={`translate(${x} ${y}) rotate(${dir})`} opacity={o}>
    {[-0.55, 0, 0.55].map((a, i) => (
      <rect key={i} x={r * 0.55} y={a * r - r * 0.16} width={r * 0.75} height={r * 0.32} rx={r * 0.16} fill={GRABHAND} />
    ))}
    <circle r={r} fill={GRABHAND} />
  </g>
);

// 光点：芯 64 px、光晕 128 px（分镜第七节）
export const Spark: React.FC<{x: number; y: number; r?: number; o?: number; warm?: number}> = ({x, y, r = 32, o = 1, warm = 0}) => (
  <g opacity={o}>
    <circle cx={x} cy={y} r={r * 2} fill="url(#sparkGlow)" />
    <circle cx={x} cy={y} r={r} fill={warm > 0 ? '#FFD38A' : '#FFF1D6'} />
    <circle cx={x - r * 0.25} cy={y - r * 0.25} r={r * 0.35} fill="#FFFFFF" opacity={0.8} />
  </g>
);

// 头顶的分数条：只看长短，没有数字和刻度
export const Bar: React.FC<{x: number; y: number; len: number; full?: number; color?: string; glow?: number; o?: number; align?: 'center' | 'left'; h?: number}> = (
  {x, y, len, full = 400, color = '#EEF1F6', glow = 0, o = 1, align = 'center', h = 32},
) => {
  const x0 = align === 'center' ? x - full / 2 : x;
  return (
    <g opacity={o}>
      <rect x={x0} y={y - h / 2} width={full} height={h} rx={h / 2} fill="#FFFFFF" opacity={0.1} />
      {glow > 0 && <rect x={x0 - 10} y={y - h / 2 - 10} width={Math.max(0, len) + 20} height={h + 20} rx={h / 2 + 10} fill={color} opacity={0.35 * glow} />}
      <rect x={x0} y={y - h / 2} width={Math.max(0, len)} height={h} rx={h / 2} fill={color} />
    </g>
  );
};

// 标签：白字压在本色圆角底上（打法 80 px；“你”88 px）
export const Tag: React.FC<{x: number; y: number; text: string; bg: string; size?: number; o?: number; fg?: string}> = (
  {x, y, text, bg, size = 80, o = 1, fg = '#FFFFFF'},
) => {
  const w = [...text].reduce((s, ch) => s + (/[一-鿿]/.test(ch) ? size : ch === ' ' ? size * 0.3 : size * 0.55), 0);
  return (
    <g opacity={o}>
      <rect x={x - w / 2 - size * 0.3} y={y - size * 0.62} width={w + size * 0.6} height={size * 1.24} rx={size * 0.3} fill={bg} />
      <text x={x} y={y + size * 0.36} fontSize={size} fontFamily={SANS} fontWeight={600} fill={fg} textAnchor="middle">{text}</text>
    </g>
  );
};

// 占位块：分镜要、但这版灰框没画出来的东西
export const Placeholder: React.FC<{x: number; y: number; w: number; h: number; text: string; o?: number}> = ({x, y, w, h, text, o = 1}) => (
  <g opacity={o}>
    <rect x={x} y={y} width={w} height={h} fill="#5A5F6B" stroke="#9AA0AC" strokeWidth={3} strokeDasharray="12 8" rx={10} />
    <text x={x + w / 2} y={y + h / 2 + 14} fontSize={40} fontFamily={SANS} fill="#E6E8EE" textAnchor="middle">{text}</text>
  </g>
);
