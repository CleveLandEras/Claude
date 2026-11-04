// 002 成片：近景的人和道具。人用 FPerson（画风 A 改版），道具照“画成实物”的规矩画：
// 有材料（光点是一颗发暖光的小球，有高光；分数条是一根嵌在槽里的条），有重量（软阴影、稍微歪放），不用细亮边描轮廓。
// 灰框的 people.tsx 不动；姿势在这里重新调过：抱胳膊、转头看、愣住、转身面对镜头。
import React, {useId} from 'react';
import {EXPR, Expr, blink, breath, withBlink} from '../../../components/people/face';
import {Look, ME, OTHER} from '../../../components/people/look';
import {Pose, RPose, mixPose, nudge, resolve, solve} from '../../../components/people/rig';
import {P, mixHex, tube} from '../../../components/people/geom';
import {COL, GRABHAND, SANS, clamp, lerp} from '../lib';
import {FPerson} from './FPerson';

const uidOf = () => useId().replace(/[^a-zA-Z0-9]/g, '');

const STAND: Pose = {yaw: 0.55, pelvis: -2, lean: 1, chest: 1, neck: 2, lN: {hip: 3, knee: 0}, lF: {hip: 10, knee: 10}, ground: true};
const P0 = (o: Pose) => resolve({...STAND, ...o});

export const POSE = {
  idle: P0({aN: {sh: 5, el: 16}, aF: {sh: -4, el: 14}, hN: 'limp', hF: 'limp'}),
  // 双手捧着光点往前递，手心朝上
  give: P0({lean: 5, neck: 4, gaze: {x: 1, y: 0.15}, aN: {to: {x: 64, y: -62}, wr: -22}, aF: {to: {x: 57, y: -57}, wr: -22}, hN: 'open', hF: 'open'}),
  // 一只手往前伸（抢、接），手指张开
  reach: P0({lean: 9, neck: 2, gaze: {x: 1, y: 0.1}, aN: {to: {x: 74, y: -76}, wr: -10}, aF: {sh: -8, el: 20}, hN: 'open', hF: 'limp'}),
  // 攥着拿到的东西收回胸前
  pull: P0({lean: -4, neck: -2, aN: {to: {x: 24, y: -58}, wr: 25}, aF: {sh: -8, el: 18}, hN: 'fist', hF: 'limp'}),
  // 缩起肩，手缩在胸前
  hunch: P0({lean: 7, chest: 6, neck: 10, shrug: 1, pitch: 0.35, gaze: {x: 0.4, y: 0.6}, aN: {to: {x: 30, y: -40}, wr: 30}, aF: {to: {x: 22, y: -44}, wr: 30}, hN: 'fist', hF: 'fist'}),
  // 抱胳膊：两条前臂横在胸前，近侧的在下面压着远侧的；身子往后靠一点、下巴抬起来
  cross: P0({yaw: 0.22, lean: -4, chest: -1, neck: -5, pitch: -0.08, aN: {to: {x: -15, y: -37}, bend: -1}, aF: {to: {x: 18, y: -42}, bend: 1}, hN: 'fist', hF: 'fist'}),
  // 转头看：身子往那边多转一点，抬头，眼睛往右上看分数条
  lookUp: P0({yaw: 0.72, neck: -13, pitch: -0.4, gaze: {x: 0.95, y: -0.85}, aN: {sh: 6, el: 18}, aF: {sh: -4, el: 14}, hN: 'limp', hF: 'limp'}),
  // 愣住：往后一缩，两手抬起半截、手指张开
  startle: P0({lean: -6, chest: -2, neck: -6, shrug: 0.6, gaze: {x: 1, y: 0}, aN: {to: {x: 40, y: -48}, wr: -40}, aF: {to: {x: 33, y: -46}, wr: -40}, hN: 'open', hF: 'open'}),
  // 正面（转身面对镜头）
  front: resolve({yaw: 0.04, pelvis: 0, lean: 0, chest: 0, neck: 0, gaze: {x: 0, y: 0},
    lN: {hip: 2, knee: 0}, lF: {hip: -2, knee: 0}, aN: {sh: 9, el: 12}, aF: {sh: -9, el: 12}, hN: 'limp', hF: 'limp', ground: true}),
  // 转身的半路：四分之一侧
  quarter: resolve({yaw: 0.28, pelvis: -1, lean: 0, chest: 0, neck: 1, gaze: {x: 0.3, y: 0},
    lN: {hip: 2, knee: 0}, lF: {hip: 4, knee: 4}, aN: {sh: 7, el: 14}, aF: {sh: -7, el: 14}, hN: 'limp', hF: 'limp', ground: true}),
  // 第四版结尾：从朝左转到朝右的半路，完全正面、左右对称（在这一帧换朝向，看不出翻转）
  front0: resolve({yaw: 0, pelvis: 0, lean: 0, chest: 0, neck: 0, gaze: {x: 0, y: 0},
    lN: {hip: 0, knee: 0}, lF: {hip: 0, knee: 0}, aN: {sh: 9, el: 12}, aF: {sh: -9, el: 12}, hN: 'limp', hF: 'limp', ground: true}),
  // 第四版结尾：双手托着光点朝右，转头看镜头（身子往镜头这边转一点，手不动）
  endLook: P0({yaw: 0.2, lean: 4, neck: 2, gaze: {x: 0.05, y: 0.05}, aN: {to: {x: 64, y: -62}, wr: -22}, aF: {to: {x: 57, y: -57}, wr: -22}, hN: 'open', hF: 'open'}),
};
export type PoseKey = keyof typeof POSE;
const CROSS: Partial<Record<PoseKey, number>> = {cross: 1};

export const EX: Record<string, Expr> = {
  calm: EXPR.calm, blank: EXPR.blank, worry: EXPR.worry, sad: EXPR.sad, relief: EXPR.relief, surprise: EXPR.surprise,
  // 愣住：眼睛睁圆、眉毛抬起，嘴小小地张开
  stun: {...EXPR.surprise, smile: -0.05, open: 0.35, round: 0.8, mouthW: 0.6, blush: 0.2, brow: 0.9, browIn: 0.15},
  // 一边嘴角翘起来（得意）：近侧嘴角上去、近侧眉挑一点、眼皮半垂
  smirk: {...EXPR.calm, smirk: 1.15, smile: 0.12, lid: 0.34, brow: -0.05, browIn: -0.35, asym: 0.9, blush: 0.35, mouthW: 0.95},
  // 僵着（互相报复时）
  stiff: {...EXPR.calm, brow: -0.1, browIn: -0.8, knit: 0.85, smile: -0.4, mouthW: 0.7, lid: 0.2, blush: 0.15},
  // 冷着脸（记仇的、骗子）：眯眼，眉头压下，嘴角往下
  cold: {...EXPR.suspect, smirk: 0, smile: -0.25, asym: 0.35},
  // 翻脸：眉头狠狠压下，嘴撇着
  angry: {...EXPR.calm, brow: -0.2, browIn: -1.1, knit: 1, lid: 0.22, smile: -0.55, mouthW: 0.75, blush: 0.2, asym: 0.2},
  // 笑
  smile: {...EXPR.calm, smile: 0.8, lid: 0.22, brow: 0.12, blush: 0.85, browArc: 0.45},
  // 淡淡地笑（结尾看镜头）
  soft: {...EXPR.calm, smile: 0.32, brow: 0.12, blush: 0.5, browArc: 0.3},
};

// 衣服颜色 = 打法颜色。你：连帽衫、短发翘毛（ME）；别人：外套、齐肩发（OTHER）
export const lookFor = (strategy: number, who: 'me' | 'other'): Look => {
  const c = COL[strategy];
  const base = who === 'me' ? ME : OTHER;
  return {...base, top: c, topShade: mixHex(c, '#000000', 0.3)};
};

export type TPose = RPose & {cx: number};
// 关键帧：[[帧, 姿势名或 RPose], ...]；返回的姿势带着抱胳膊的程度 cx
export const track = (f: number, keys: [number, PoseKey | RPose][], ease = (t: number) => t * t * (3 - 2 * t)): TPose => {
  const get = (k: PoseKey | RPose) => (typeof k === 'string' ? POSE[k] : k);
  const cx = (k: PoseKey | RPose) => (typeof k === 'string' ? CROSS[k] ?? 0 : 0);
  if (f <= keys[0][0]) return {...get(keys[0][1]), cx: cx(keys[0][1])};
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, a] = keys[i - 1], [f1, b] = keys[i];
      const t = ease(clamp((f - f0) / Math.max(1e-6, f1 - f0)));
      return {...mixPose(get(a), get(b), t), cx: lerp(cx(a), cx(b), clamp((t - 0.35) / 0.5))};
    }
  }
  const last = keys[keys.length - 1][1];
  return {...get(last), cx: cx(last)};
};
export const still = (k: PoseKey): TPose => ({...POSE[k], cx: CROSS[k] ?? 0});

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
  const ang = ((near ? sk.handN : sk.handF) * Math.PI) / 180;
  // 手心（手腕往手的方向走 9 个单位）
  const hx = w.x - Math.sin(ang) * 9, hy = w.y + Math.cos(ang) * 9;
  return {x: x + facing * hx * s, y: G + hy * s};
};
export const handsMid = (r: RPose, x: number, G: number, s: number, facing: 1 | -1) => {
  const a = handAt(r, x, G, s, facing, true), b = handAt(r, x, G, s, facing, false);
  return {x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 4 * s};
};
export const headTop = (r: RPose, x: number, G: number, s: number, facing: 1 | -1) => {
  const sk = solve(r);
  return {x: x + facing * sk.head.x * s, y: G + (sk.head.y - 62) * s};
};
export const headC = (r: RPose, x: number, G: number, s: number, facing: 1 | -1) => {
  const sk = solve(r);
  return {x: x + facing * sk.head.x * s, y: G + sk.head.y * s};
};

export type ManProps = {
  f: number; pose: RPose | TPose; expr: Expr; strategy: number; who: 'me' | 'other';
  x: number; G: number; s: number; facing?: 1 | -1;
  opacity?: number; dim?: number; seed?: string;
  recolor?: {to: number; p: number};        // 衣服从上往下刷成另一个颜色：to = 新打法，p = 0..1
  breathe?: boolean; breathAmp?: number;
  blinks?: number[];                         // 另外指定在这几帧眨眼
  tint?: {color: string; amount: number};    // 灯光颜色
  night?: string;
  ghost?: boolean;                           // 影子你：整体约六成不透明，外面一圈淡黄的光边
  noBlink?: number[][];                      // 这几段里不自动眨眼（愣住、嘴角翘这些表情要睁着眼）
};

// 一个人：带呼吸、眨眼；可以整件衣服从上往下刷色
export const Man: React.FC<ManProps> = (p) => {
  const id = uidOf();
  const facing = p.facing ?? 1;
  const k = p.breathAmp ?? 1;
  const cx = (p.pose as TPose).cx ?? 0;
  const r = p.breathe === false ? p.pose : nudge(p.pose, {shrug: 0.05 * k * breath(p.f), chest: -0.4 * k * breath(p.f), y: -0.8 * (k - 1) * breath(p.f)});
  const BL = [0.45, 1, 1, 0.7, 0.35, 0.1];
  const extra = (p.blinks ?? []).reduce((m, b) => (p.f - b >= 0 && p.f - b < BL.length ? Math.max(m, BL[p.f - b]) : m), 0);
  const held = (p.noBlink ?? []).some(([a, b]) => p.f >= a && p.f <= b);
  const e = withBlink(p.expr, Math.max(held ? 0 : blink(p.f, p.seed ?? p.who), extra));
  const body = (strategy: number) => (
    <FPerson pose={r} expr={e} look={lookFor(strategy, p.who)} x={p.x} y={p.G} s={p.s} facing={facing} cross={cx}
      dim={p.dim ?? 0} night={p.night ?? '#0B0D12'} light={{x: -0.25 * facing, y: -1}} tint={p.tint} />
  );
  const top = p.G - 290 * p.s;
  // 刷色（第四版）：只刷衣服那一段（兜帽上沿到下摆），新颜色从上往下漫下来；
  // 漫到哪里，那里有一条暖色的染色带：用新颜色的这件衣服本身提亮成暖光、再加一圈模糊光晕，上沿最亮、往下柔下去，所以只落在衣服上，不是一根横线
  let dye: React.ReactNode = null;
  let clipH = 0;
  if (p.recolor && p.recolor.p > 0) {
    const sk = solve(r as RPose);
    const yTop = p.G + (Math.min(sk.chest.y, sk.sN.y, sk.sF.y) - 12) * p.s;
    const yBot = p.G + (sk.pelvis.y + 18) * p.s;
    const q = clamp(p.recolor.p);
    const by = lerp(yTop, yBot, q);
    clipH = by - top;
    const bandH = 12 * p.s;                       // 近景约 38 px
    const bo = clamp(q / 0.06) * clamp((1 - q) / 0.12);
    if (bo > 0.001) {
      dye = (
        <g opacity={bo}>
          <defs>
            <linearGradient id={`${id}dg`} x1="0" y1={by - 3 * p.s} x2="0" y2={by + bandH} gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#fff" stopOpacity={0} />
              <stop offset="0.14" stopColor="#fff" stopOpacity={1} />
              <stop offset="0.4" stopColor="#fff" stopOpacity={0.7} />
              <stop offset="1" stopColor="#fff" stopOpacity={0} />
            </linearGradient>
            <mask id={`${id}dm`} maskUnits="userSpaceOnUse" x={p.x - 260 * p.s} y={by - 30 * p.s} width={520 * p.s} height={bandH + 60 * p.s}>
              <rect x={p.x - 260 * p.s} y={by - 3 * p.s} width={520 * p.s} height={bandH + 3 * p.s} fill={`url(#${id}dg)`} />
            </mask>
            <filter id={`${id}df`} x="-30%" y="-30%" width="160%" height="160%" colorInterpolationFilters="sRGB">
              <feColorMatrix type="matrix" values="0.42 0 0 0 0.6  0 0.42 0 0 0.47  0 0 0.42 0 0.26  0 0 0 1 0" result="w" />
              <feGaussianBlur in="w" stdDeviation={3.2 * p.s} result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="b" /><feMergeNode in="w" /></feMerge>
            </filter>
          </defs>
          <g mask={`url(#${id}dm)`} style={{mixBlendMode: 'screen'}}>
            <g filter={`url(#${id}df)`}>{body(p.recolor!.to)}</g>
          </g>
        </g>
      );
    }
  }
  const inner = (
    <>
      {body(p.strategy)}
      {p.recolor && p.recolor.p > 0 && (
        <>
          <clipPath id={`${id}rc`}><rect x={p.x - 200 * p.s} y={top} width={400 * p.s} height={Math.max(0, clipH)} /></clipPath>
          <g clipPath={`url(#${id}rc)`}>{body(p.recolor.to)}</g>
          {dye}
        </>
      )}
    </>
  );
  if (p.ghost) {
    return (
      <g opacity={p.opacity ?? 1}>
        <filter id={`${id}gh`} x="-20%" y="-10%" width="140%" height="120%">
          <feMorphology in="SourceAlpha" operator="dilate" radius={2.2 * p.s} result="d" />
          <feGaussianBlur in="d" stdDeviation={2.4 * p.s} result="b" />
          <feFlood floodColor="#FFE7A6" floodOpacity={0.95} />
          <feComposite in2="b" operator="in" result="edge" />
          <feComponentTransfer in="SourceGraphic" result="sg"><feFuncA type="linear" slope={0.62} /></feComponentTransfer>
          <feMerge><feMergeNode in="edge" /><feMergeNode in="sg" /></feMerge>
        </filter>
        <g filter={`url(#${id}gh)`}>{inner}</g>
      </g>
    );
  }
  return <g opacity={p.opacity ?? 1}>{inner}</g>;
};

// —— 光点：一颗发暖光的小球。外面一圈柔光，球身三层暖色（受光面在左上），一颗高光；落在地上时下面一块软影 ——
export const Spark: React.FC<{x: number; y: number; r?: number; o?: number; warm?: number; ground?: number; glow?: number}> = (
  {x, y, r = 32, o = 1, warm = 0, ground, glow = 1},
) => {
  const body = mixHex('#FFC867', '#FF9F43', warm);
  const lit = mixHex('#FFE6B0', '#FFD08A', warm);
  return (
    <g opacity={o}>
      {ground !== undefined && (() => {
        const hgt = Math.max(0, ground - y);
        const k = clamp(1 - hgt / 420);
        return <ellipse cx={x + 6} cy={ground + r * 0.08} rx={r * (0.7 + 0.5 * k)} ry={r * (0.18 + 0.12 * k)} fill="#000" opacity={0.55 * k}
          filter="url(#fBlur6)" />;
      })()}
      <circle cx={x} cy={y} r={r * (2.3 + 0.5 * warm)} fill="url(#gSparkGlow)" opacity={(0.8 + 0.2 * warm) * glow} />
      <circle cx={x} cy={y} r={r} fill={body} />
      <circle cx={x - r * 0.12} cy={y - r * 0.14} r={r * 0.8} fill={lit} />
      <circle cx={x - r * 0.24} cy={y - r * 0.27} r={r * 0.42} fill="#FFF8EA" />
      <ellipse cx={x - r * 0.4} cy={y - r * 0.44} rx={r * 0.16} ry={r * 0.11} fill="#FFFFFF" transform={`rotate(-35 ${x - r * 0.4} ${y - r * 0.44})`} />
    </g>
  );
};

// —— 抢的那只手：第五版归进红色家族（“抢”就是狠）。张开五指伸过来，抓住以后攥起来；后面拖一截袖子和两道速度线 ——
// 局部坐标：手心在原点，手指朝 +x。r = 手心半径
const GRAB_SHADE = mixHex(GRABHAND, '#000000', 0.3), GRAB_LIT = mixHex(GRABHAND, '#FFFFFF', 0.3);
export const GrabHand: React.FC<{x: number; y: number; r?: number; dir?: number; o?: number; close?: number; trail?: number; sleeve?: number}> = (
  {x, y, r = 30, dir = 0, o = 1, close = 0, trail = 0, sleeve = 1},
) => {
  const c = clamp(close);
  const fingers: P[][] = [];
  const spread = [-0.62, -0.2, 0.2, 0.58];
  const lens = [0.9, 1.05, 1.0, 0.82];
  spread.forEach((a0, i) => {
    const a = a0 * (1 - 0.55 * c);
    const base = {x: Math.cos(a) * r * 0.72, y: Math.sin(a) * r * 0.72};
    const L1 = r * 0.6 * lens[i], L2 = r * 0.5 * lens[i];
    const bend1 = a + c * 1.25 * (a0 < 0 ? 1 : 1);
    const mid = {x: base.x + Math.cos(bend1) * L1 * (1 - 0.15 * c), y: base.y + Math.sin(bend1) * L1};
    const bend2 = bend1 + c * 1.5;
    const tip = {x: mid.x + Math.cos(bend2) * L2, y: mid.y + Math.sin(bend2) * L2};
    fingers.push([base, mid, tip]);
  });
  // 拇指：从手心下方伸出来，抓的时候往里扣
  const ta = 1.35 - 0.5 * c;
  const tb = {x: Math.cos(ta) * r * 0.55, y: Math.sin(ta) * r * 0.75};
  const tm = {x: tb.x + Math.cos(ta - 0.9) * r * 0.55, y: tb.y + Math.sin(ta - 0.9) * r * 0.45};
  const tt = {x: tm.x + Math.cos(ta - 1.6 - c * 0.8) * r * 0.42, y: tm.y + Math.sin(ta - 1.6 - c * 0.8) * r * 0.42};
  const fr = r * 0.2;
  return (
    <g transform={`translate(${x} ${y}) rotate(${dir})`} opacity={o}>
      {trail > 0 && [0.9, 0.45].map((k, i) => (
        <path key={i} d={`M ${-r * (2.2 + i * 0.6)} ${(i ? 1 : -1) * r * 0.45} L ${-r * (1.2 + 1.8 * trail)} ${(i ? 1 : -1) * r * 0.45}`}
          stroke={GRABHAND} strokeWidth={r * 0.16} strokeLinecap="round" opacity={0.35 * k * trail} />
      ))}
      {sleeve > 0 && (
        <path d={tube([{x: -r * 2.3, y: 0}, {x: -r * 0.6, y: 0}], [r * 0.5, r * 0.56])} fill={GRAB_SHADE} opacity={sleeve} />
      )}
      {/* 手心、手指（暗面色先画一遍，往受光那边挪一点再画亮面） */}
      <g>
        <ellipse cx={0} cy={0} rx={r * 0.92} ry={r * 0.86} fill={GRAB_SHADE} />
        {fingers.map((q, i) => <path key={i} d={tube(q, [fr * 1.05, fr * 0.95, fr * 0.85])} fill={GRAB_SHADE} />)}
        <path d={tube([tb, tm, tt], [fr * 1.15, fr, fr * 0.9])} fill={GRAB_SHADE} />
      </g>
      <g transform={`translate(${-r * 0.06} ${-r * 0.09})`}>
        <ellipse cx={0} cy={0} rx={r * 0.86} ry={r * 0.8} fill={GRABHAND} />
        {fingers.map((q, i) => <path key={i} d={tube(q, [fr * 0.92, fr * 0.82, fr * 0.72])} fill={GRABHAND} />)}
        <path d={tube([tb, tm, tt], [fr, fr * 0.88, fr * 0.78])} fill={GRABHAND} />
        <ellipse cx={-r * 0.2} cy={-r * 0.3} rx={r * 0.42} ry={r * 0.22} fill={GRAB_LIT} opacity={0.7} />
      </g>
    </g>
  );
};

// —— 分数条：一根嵌在暗槽里的条。只看长短，没有数字和刻度。粗 h（手机上至少约 10 点：原片 ≥ 54 px）——
export const Bar: React.FC<{x: number; y: number; len: number; full?: number; color?: string; glow?: number; o?: number; align?: 'center' | 'left'; h?: number; shine?: number}> = (
  {x, y, len, full = 400, color = '#EEF1F6', glow = 0, o = 1, align = 'center', h = 56, shine},
) => {
  const id = uidOf();
  const x0 = align === 'center' ? x - full / 2 : x;
  const L = clamp(len, 0, full * 1.05);
  const rr = h / 2;
  const pad = Math.max(4, h * 0.11);
  const fillL = Math.max(0, L - 2 * pad);
  const fh = h - 2 * pad;
  return (
    <g opacity={o}>
      {/* 槽：落一块软影，槽里上半深、下半浅（凹下去的样子） */}
      <rect x={x0 + 4} y={y - h / 2 + h * 0.28} width={full} height={h} rx={rr} fill="#000" opacity={0.45} filter="url(#fBlur6)" />
      <rect x={x0} y={y - h / 2} width={full} height={h} rx={rr} fill="#1B1F28" />
      <rect x={x0 + pad * 0.5} y={y - h / 2 + pad * 0.4} width={full - pad} height={h * 0.42} rx={h * 0.21} fill="#10131A" />
      {glow > 0 && <rect x={x0 - 14} y={y - h / 2 - 14} width={L + 28} height={h + 28} rx={rr + 14} fill={color} opacity={0.42 * glow} filter="url(#fBlur12)" />}
      {fillL > 0 && (
        <g>
          <clipPath id={`${id}c`}><rect x={x0 + pad} y={y - fh / 2} width={Math.max(fh, fillL)} height={fh} rx={fh / 2} /></clipPath>
          <g clipPath={`url(#${id}c)`}>
            <rect x={x0 + pad} y={y - fh / 2} width={Math.max(fh, fillL)} height={fh} fill={mixHex(color, '#000000', 0.22)} />
            <rect x={x0 + pad} y={y - fh / 2 - fh * 0.1} width={Math.max(fh, fillL)} height={fh * 0.86} rx={fh * 0.43} fill={color} />
            <rect x={x0 + pad + fh * 0.35} y={y - fh / 2 + fh * 0.12} width={Math.max(0, Math.max(fh, fillL) - fh * 0.7)} height={fh * 0.2} rx={fh * 0.1}
              fill={mixHex(color, '#FFFFFF', 0.5)} opacity={0.7} />
            {shine !== undefined && shine >= 0 && shine <= 1 && (
              <ellipse cx={x0 + pad + fillL * shine} cy={y} rx={fh * 1.1} ry={fh * 0.7} fill="#FFFFFF" opacity={0.55 * Math.sin(shine * Math.PI)} filter="url(#fBlur8)" />
            )}
          </g>
        </g>
      )}
    </g>
  );
};

// —— 标签：一块贴纸似的牌子，下沿一个小尖角指向人；上半略亮、落一块软影、微微歪着 ——
export const tagWidth = (text: string, size: number) =>
  [...text].reduce((s, ch) => s + (/[一-鿿]/.test(ch) ? size : ch === ' ' ? size * 0.3 : ch === '·' ? size * 0.5 : size * 0.58), 0);
// stack：“狠·记一辈子”这种带“·”的标签排成两行，上面“狠”原字号，下面“记一辈子”小一号（0.72），牌子窄一半，挂在人头边上不压脸
export const Tag: React.FC<{x: number; y: number; text: string; bg: string; size?: number; o?: number; fg?: string; tilt?: number; point?: 'down' | 'none'; pop?: number; stack?: boolean}> = (
  {x, y, text, bg, size = 80, o = 1, fg = '#FFFFFF', tilt = -1.5, point = 'down', pop = 1, stack = false},
) => {
  const two = stack && text.includes('·');
  const [main, sub] = two ? text.split('·') : [text, ''];
  const subSize = Math.round(size * 0.72);
  const w = two ? Math.max(tagWidth(main, size), tagWidth(sub, subSize)) : tagWidth(text, size);
  const W = w + size * 0.66, Hh = two ? size * 1.12 + subSize * 1.22 : size * 1.28;
  const s = 0.6 + 0.4 * pop;
  const x0 = x - W / 2, y0 = y - Hh / 2;
  const tri = point === 'down' ? `M ${x - size * 0.2} ${y0 + Hh - 1} L ${x} ${y0 + Hh + size * 0.24} L ${x + size * 0.2} ${y0 + Hh - 1} Z` : '';
  return (
    <g opacity={o} transform={`rotate(${tilt} ${x} ${y}) translate(${x} ${y}) scale(${s}) translate(${-x} ${-y})`}>
      <rect x={x0 + 5} y={y0 + 12} width={W} height={Hh} rx={size * 0.26} fill="#000" opacity={0.45} filter="url(#fBlur8)" />
      {tri && <path d={tri} fill={mixHex(bg, '#000000', 0.12)} />}
      <rect x={x0} y={y0} width={W} height={Hh} rx={size * 0.26} fill={mixHex(bg, '#000000', 0.1)} />
      <rect x={x0} y={y0} width={W} height={Hh - size * 0.128} rx={size * 0.26} fill={bg} />
      <rect x={x0 + size * 0.18} y={y0 + size * 0.1} width={W - size * 0.36} height={size * 0.38} rx={size * 0.14} fill="#FFFFFF" opacity={0.1} />
      {two ? (
        <>
          <text x={x} y={y0 + size * 0.98} fontSize={size} fontFamily={SANS} fontWeight={800} fill={fg} textAnchor="middle">{main}</text>
          <text x={x} y={y0 + size * 1.04 + subSize * 0.98} fontSize={subSize} fontFamily={SANS} fontWeight={700} fill={fg} textAnchor="middle">{sub}</text>
        </>
      ) : (
        <text x={x} y={y + size * 0.3} fontSize={size} fontFamily={SANS} fontWeight={700} fill={fg} textAnchor="middle">{text}</text>
      )}
    </g>
  );
};
export const YOU_BG = '#F2ECE1', YOU_FG = '#1A1C23';

// —— 一颗带眼睛的点（一排 10 个人、比分数条时的小头像、点阵）：本色一块，左上一块亮面，黑点眼带白高光 ——
export const FaceDot: React.FC<{x: number; y: number; r: number; color: string; lid?: number; gx?: number; gy?: number; o?: number; shadow?: boolean}> = (
  {x, y, r, color, lid = 0, gx = 0, gy = 0, o = 1, shadow = true},
) => {
  const er = r * 0.13, ey = y - r * 0.05;
  return (
    <g opacity={o}>
      {shadow && <ellipse cx={x + r * 0.08} cy={y + r * 1.04} rx={r * 0.78} ry={r * 0.16} fill="#000" opacity={0.45} />}
      <circle cx={x} cy={y} r={r} fill={mixHex(color, '#000000', 0.2)} />
      <circle cx={x - r * 0.08} cy={y - r * 0.1} r={r * 0.88} fill={color} />
      <ellipse cx={x - r * 0.34} cy={y - r * 0.44} rx={r * 0.3} ry={r * 0.17} fill="#FFFFFF" opacity={0.18} transform={`rotate(-30 ${x - r * 0.34} ${y - r * 0.44})`} />
      {[-1, 1].map((k) => {
        const ex = x + k * r * 0.3 + gx * r * 0.08, eyy = ey + gy * r * 0.07;
        if (lid > 0.6) return <path key={k} d={`M ${ex - er * 1.1} ${eyy} Q ${ex} ${eyy + er * 0.7} ${ex + er * 1.1} ${eyy}`} stroke="#15171C" strokeWidth={Math.max(1.5, er * 0.5)} fill="none" strokeLinecap="round" />;
        return (
          <g key={k}>
            <ellipse cx={ex} cy={eyy} rx={er} ry={er * 1.25 * (1 - 0.85 * lid)} fill="#15171C" />
            <circle cx={ex + er * 0.35} cy={eyy - er * 0.45} r={er * 0.38} fill="#FFFFFF" />
          </g>
        );
      })}
      <ellipse cx={x - r * 0.5} cy={y + r * 0.25} rx={r * 0.15} ry={r * 0.08} fill="#FF9C8F" opacity={0.35} />
      <ellipse cx={x + r * 0.5} cy={y + r * 0.25} rx={r * 0.15} ry={r * 0.08} fill="#FF9C8F" opacity={0.35} />
    </g>
  );
};

// 共用的滤镜和渐变（每个 svg 层各放一份）
export const FilmDefs: React.FC = () => (
  <defs>
    <radialGradient id="gSparkGlow">
      <stop offset="0" stopColor="#FFD58A" stopOpacity={0.75} />
      <stop offset="0.35" stopColor="#FFB85C" stopOpacity={0.28} />
      <stop offset="1" stopColor="#FFB85C" stopOpacity={0} />
    </radialGradient>
    <radialGradient id="gMeGlow"><stop offset="0" stopColor="#FFFFFF" stopOpacity={0.6} /><stop offset="1" stopColor="#FFFFFF" stopOpacity={0} /></radialGradient>
    <radialGradient id="gWarm"><stop offset="0" stopColor="#FFD9A0" stopOpacity={0.5} /><stop offset="1" stopColor="#FFD9A0" stopOpacity={0} /></radialGradient>
    <filter id="fBlur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={4} /></filter>
    <filter id="fBlur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={6} /></filter>
    <filter id="fBlur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={8} /></filter>
    <filter id="fBlur12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={12} /></filter>
    <filter id="fBlur24" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={24} /></filter>
  </defs>
);
