// 《等待》观感样片的基本画面：一盏吊灯下，坐在实验椅上、手腕绑着电极的人（videos/001_等待/观感对照.md）。
// 颜色只有三种意思：房间是暖的灯光；电是冷的白蓝光（冷光闯进暖房间，就是“被电”）；红色只给疼和结果，疼之前画面上没有红。
// 第三版（七维度评审 10/28，平均 5.4 分）：
//   轮廓光按灯的方向打、离灯越远越暗（座位下、椅腿不再亮）；人有侧脸、脖子、拇指；发光不再被裁成方框；
//   电是从手腕炸开的冷光，在人身后（剪影始终不透明，动作看得见），锥形分叉的电弧每 2 帧重画；灯先变冷、跳闸一帧、再闪三下；
//   电击盒的指针平时停在低处，电下去的那一下甩到满格、红区亮起；电极待机时冷白呼吸；B 的钟是挂在墙上的真钟。
import {random} from 'remotion';

export const L = {
  wall: '#26190F',
  dark: '#050403',
  lamp: '#FFE2B0',
  amber: '#F2B266',
  rim: '#F4C98A',
  cold: '#BFD8FF',
  sil: '#0A0705',
  elec: '#DDF0FF',
  elecGlow: '#6FA8FF',
  red: '#FC5A4D',
  ink: '#F3EBDD',
  soft: 'rgba(243,235,221,0.74)',
  mute: '#9A958C',
  idle: '#8C7A62',
  serif: '"Songti SC", "STSong", "Noto Serif SC", serif',
};

type P = {x: number; y: number};
export const rot = (p: P, c: P, deg: number): P => {
  const a = (deg * Math.PI) / 180;
  const dx = p.x - c.x, dy = p.y - c.y;
  return {x: c.x + dx * Math.cos(a) - dy * Math.sin(a), y: c.y + dx * Math.sin(a) + dy * Math.cos(a)};
};
const hex = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
export const mix = (a: string, b: string, t: number) => {
  const A = hex(a), B = hex(b);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * Math.max(0, Math.min(1, t)))).join(',')})`;
};
const bez = (p0: P, p1: P, p2: P, p3: P, t: number): P => {
  const u = 1 - t;
  return {
    x: u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x,
    y: u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y,
  };
};

// 坐着的人，面朝右。坐面上沿 y=0，地面 y=150，手腕搁在扶手上。lean：上身往后仰（度）；tense：绷紧、往前探
export const WRIST: P = {x: 74, y: -76};
// 电极在左脚脚背上（Berns 等 2006 原文：shocks were delivered to the dorsum of the left foot）
export const ELEC: P = {x: 86, y: 134};
export const Figure: React.FC<{lean?: number; tense?: number; breath?: number; jit?: P; hop?: number; look?: number}> = (
  {lean = 0, tense = 0, breath = 0, jit = {x: 0, y: 0}, hop = 0, look = 0},
) => {
  const H = {x: -30, y: -14};
  const up = (p: P) => rot({x: p.x + 10 * tense, y: p.y + 6 * tense + breath}, H, -lean);
  const S = up({x: -36, y: -150});
  const N = up({x: -22 + 6 * tense, y: -182});
  const c = up({x: -18 + 10 * tense, y: -210});
  const S2 = up({x: -30, y: -140});
  const E = up({x: -18, y: -76});
  const K = {x: 64, y: -22};
  const F = {x: 74, y: 140};
  const line = (a: P, b: P, w: number) => (
    <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={L.sil} strokeWidth={w} strokeLinecap="round" />
  );
  // 侧脸：后脑、头顶、额头、眉骨、鼻尖、嘴、下巴、下颌、后颈（以头的中心为原点，面朝右）
  const head = 'M -27 -2 C -29 -20 -16 -32 -2 -32 C 12 -32 21 -24 23 -12 L 25 -6 C 26 -2 30 3 31 6 C 30 8 27 8 25 9 '
    + 'C 26 11 27 13 25 15 C 26 17 26 21 24 25 C 18 30 9 31 2 30 C -6 29 -14 26 -20 20 C -25 14 -27 7 -27 -2 Z';
  return (
    <g>
      {/* 实验椅：钉在地上，有头枕、扶手上有束带 */}
      <rect x={-92} y={-236} width={34} height={46} rx={10} fill={L.sil} transform="rotate(-6 -74 0)" />
      <rect x={-84} y={-196} width={20} height={200} rx={9} fill={L.sil} transform="rotate(-6 -74 0)" />
      <rect x={-86} y={-2} width={160} height={18} rx={7} fill={L.sil} />
      <rect x={-80} y={14} width={11} height={136} rx={4} fill={L.sil} />
      <rect x={58} y={14} width={11} height={136} rx={4} fill={L.sil} />
      <rect x={-74} y={92} width={140} height={7} rx={3} fill={L.sil} />
      <rect x={-66} y={-66} width={140} height={11} rx={5} fill={L.sil} />
      <rect x={54} y={-58} width={9} height={60} rx={3} fill={L.sil} />
      {/* 人（被电时自己抖、往上弹，椅子不动） */}
      <g transform={`translate(${jit.x} ${jit.y - hop})`}>
      {line(H, K, 46)}
      {line(K, F, 30)}
      {line(F, {x: 104, y: 146}, 15)}
      {line(H, S, 70)}
      {line(S, N, 26)}
      <path d={head} fill={L.sil} transform={`translate(${c.x} ${c.y}) rotate(${-lean * 0.8 + look})`} />
      {line(S2, E, 25)}
      {line(E, WRIST, 21)}
      {/* 手：握着的拳，指节和拇指 */}
      <path d="M 80 -86 C 88 -90 100 -89 106 -84 C 110 -80 110 -72 106 -68 C 100 -64 88 -64 80 -66 Z" fill={L.sil} />
      {line({x: 86, y: -84}, {x: 99, y: -92}, 7)}
      {/* 扶手上的束带 */}
      <rect x={40} y={-90} width={12} height={30} rx={3} fill={L.sil} />
      </g>
    </g>
  );
};

// 电弧：锥形（主干从粗到细），每条带两三个分叉，每 2 帧重画一次；外面两层辉光
type Seg = {pts: P[]; w: number};
const bolt = (o: P, ang: number, len: number, w: number, seed: string, depth: number, out: Seg[]) => {
  const n = 7;
  const pts: P[] = [o];
  for (let j = 1; j <= n; j++) {
    const t = j / n;
    const off = (random(`${seed}o${j}`) - 0.5) * len * 0.22;
    pts.push({x: o.x + Math.cos(ang) * len * t - Math.sin(ang) * off, y: o.y + Math.sin(ang) * len * t + Math.cos(ang) * off});
  }
  out.push({pts, w});
  if (depth > 0) {
    [2, 4].forEach((j, b) => {
      if (random(`${seed}b${b}`) < 0.75) {
        const a2 = ang + (random(`${seed}ba${b}`) - 0.5) * 1.6;
        bolt(pts[j], a2, len * (0.35 + random(`${seed}bl${b}`) * 0.25), w * 0.5, `${seed}${b}`, depth - 1, out);
      }
    });
  }
};
export const Bolts: React.FC<{o: P; reach: number; n: number; w: number; seed: string; k: number; also?: Seg[]}> = (
  {o, reach, n, w, seed, k, also = []},
) => {
  const segs: Seg[] = [...also];
  for (let i = 0; i < n; i++) {
    const s = `${seed}${Math.floor(k / 2)}_${i}`;
    bolt(o, (i / n) * Math.PI * 2 + random(`${s}a`) * 1.2, reach * (0.6 + 0.4 * random(`${s}l`)), w, s, 1, segs);
  }
  // 锥形：每一小段的线宽从段首到段尾递减
  const draw = (stroke: string, mul: number, add: number, op: number) => segs.map((sg, i) => sg.pts.slice(1).map((p, j) => {
    const a = sg.pts[j];
    const t = j / (sg.pts.length - 1);
    const width = Math.max(0.5, sg.w * (1 - t * 0.85)) * mul + add;
    return <line key={`${i}-${j}`} x1={a.x} y1={a.y} x2={p.x} y2={p.y} stroke={stroke} strokeWidth={width} strokeLinecap="round" opacity={op} />;
  }));
  return (
    <g style={{mixBlendMode: 'screen'}}>
      {draw(L.elecGlow, 1, 22, 0.16)}
      {draw(L.elecGlow, 1, 6, 0.4)}
      {draw('#EAF2FF', 1, 0, 1)}
    </g>
  );
};

const DUST = Array.from({length: 54}, (_, i) => ({
  u: random(`du${i}`), v: random(`dv${i}`), r: 0.8 + random(`dr${i}`) * 1.8, sp: 0.15 + random(`ds${i}`) * 0.35,
  ph: random(`dp${i}`) * 6.28,
}));

export type Clock = {x: number; y: number; r: number; digit: string; hand: number; flash: number; dark: number; flip?: number};

export type RoomProps = {
  id: string;
  w: number;
  h: number;
  f: number;                       // 画面里一直在动的东西（灰尘、灯的呼吸、电极的呼吸）用的帧
  fig: {x: number; y: number; s: number};   // 坐面上沿的位置和大小
  lampX?: number;
  lamp?: number;                   // 灯的亮度（0 = 跳闸）
  cold?: number;                   // 灯光变冷：0 暖，1 冷白
  swing?: number;                  // 吊灯晃的角度（度）
  lean?: number;
  hop?: number;
  jit?: P;
  look?: number;
  lampDrop?: number;               // 灯往下挪（给标题让位置）
  tense?: number;
  breath?: number;
  strike?: {k: number; power: number};   // 电下去之后第几帧（<0 表示还没电）；power：1 重电，约 0.33 轻电
  charge?: number;                 // 蓄电：0–1，电极越来越亮
  pulses?: number[];               // 正在沿线跑向手腕的电流，0 = 在盒子那头，1 = 到手腕
  zap?: boolean;                   // 电流到手腕时噼啪一下
  dial?: number;                   // 电击盒指针：0 最低，1 满格
  dialHot?: number;                // 红区和指针亮成红色（只在疼的那一下）
  dialWarm?: boolean;              // 指针用琥珀色（B 的轻电，不用红）
  clock?: Clock;
  wireTo?: P;
  box?: boolean;
  children?: React.ReactNode;
};

export const Room: React.FC<RoomProps> = (p) => {
  const {id, w, h, f, fig} = p;
  const s = fig.s;
  const lampX = p.lampX ?? fig.x - 30 * s;
  const lamp = p.lamp ?? 1;
  const cold = p.cold ?? 0;
  const swing = (p.swing ?? 0) + Math.sin((f / 66) * Math.PI * 2);   // 没被碰的时候，灯也在很轻地晃：±1°，2.2 秒一个来回
  const floorY = fig.y + 150 * s;
  const shadeY = fig.y - 300 * s + (p.lampDrop ?? 0);
  const sh = 52 * s;
  const k = p.strike?.k ?? -1;
  const power = p.strike?.power ?? 0;
  const hop = p.hop ?? 0;
  // 电极：脚背（人往上弹时脚也跟着离地一点）
  const wrist = {x: fig.x + (ELEC.x + (p.jit?.x ?? 0) * 0.3) * s, y: fig.y + (ELEC.y - hop * 0.3) * s};
  const box = p.wireTo ?? {x: fig.x + 150 * s, y: floorY - 52 * s};   // 电击盒放在一个小架子上（不贴地，免得被字幕压住）
  const glow = lamp * (0.94 + 0.06 * Math.sin(f / 20));
  const lampC = mix(L.lamp, L.cold, cold);
  const ambC = mix(L.amber, L.cold, cold);
  const rimC = mix(L.rim, L.cold, cold);
  const charge = p.charge ?? 0;
  const idleBreath = 0.8 + 0.2 * Math.sin((f / 25) * Math.PI * 2);   // 1.2 Hz
  const elecOn = Math.max(charge, k >= 0 ? Math.exp(-k / (4 + 6 * power)) : 0);
  const burst = k >= 0 ? ([1, 0.85, 0.6, 0.35, 0.18, 0.08, 0.03][k] ?? 0) * (0.4 + 0.6 * power) : 0;
  const w0 = {x: wrist.x + 10 * s, y: wrist.y + 2 * s};
  const c1 = {x: wrist.x + 40 * s, y: wrist.y + 14 * s};
  const c2 = {x: box.x - 30 * s, y: box.y + 30 * s};
  const pulsePts = (p.pulses ?? []).map((t) => bez(box, c2, c1, w0, t));
  const swingDx = Math.tan((swing * Math.PI) / 180) * floorY;
  const lampY = shadeY + sh * 0.5;
  const figT = `translate(${fig.x} ${fig.y}) scale(${s})`;
  const figure = <Figure lean={p.lean} tense={p.tense} breath={p.breath} jit={p.jit} hop={hop} look={p.look} />;
  const big = {x: '-60%', y: '-60%', width: '220%', height: '220%'};
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      <defs>
        <radialGradient id={`${id}wall`} cx={lampX + swingDx * 0.4} cy={floorY - 140 * s} r={Math.max(w, h) * 0.8} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor={mix(L.wall, '#1A2230', cold)} />
          <stop offset="0.5" stopColor="#120C08" />
          <stop offset="1" stopColor={L.dark} />
        </radialGradient>
        <linearGradient id={`${id}cone`} x1="0" y1={shadeY} x2="0" y2={floorY} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor={lampC} stopOpacity={0.55} />
          <stop offset="1" stopColor={ambC} stopOpacity={0.08} />
        </linearGradient>
        <radialGradient id={`${id}pool`}>
          <stop offset="0" stopColor={ambC} stopOpacity={0.5} />
          <stop offset="1" stopColor={ambC} stopOpacity={0} />
        </radialGradient>
        <radialGradient id={`${id}bulb`}>
          <stop offset="0" stopColor="#FFF8EA" stopOpacity={1} />
          <stop offset="0.22" stopColor={lampC} stopOpacity={0.75} />
          <stop offset="1" stopColor={ambC} stopOpacity={0} />
        </radialGradient>
        <radialGradient id={`${id}burst`}>
          <stop offset="0" stopColor="#FFFFFF" stopOpacity={1} />
          <stop offset="0.15" stopColor={L.elec} stopOpacity={0.9} />
          <stop offset="0.5" stopColor={L.elecGlow} stopOpacity={0.35} />
          <stop offset="1" stopColor={L.elecGlow} stopOpacity={0} />
        </radialGradient>
        <radialGradient id={`${id}vig`} cx="50%" cy="46%" r="78%">
          <stop offset="0.5" stopColor="#000" stopOpacity={0} />
          <stop offset="1" stopColor="#000" stopOpacity={0.78} />
        </radialGradient>
        {/* 轮廓光：剪影往背光方向挪 6 像素再和原剪影相减，剩下的就是朝灯的那条边；再按离灯的远近衰减 */}
        <radialGradient id={`${id}fall`} cx={lampX} cy={lampY} r={360 * s} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#fff" stopOpacity={1} />
          <stop offset="0.55" stopColor="#fff" stopOpacity={0.75} />
          <stop offset="1" stopColor="#fff" stopOpacity={0} />
        </radialGradient>
        <mask id={`${id}rimMask`} maskUnits="userSpaceOnUse" x={0} y={0} width={w} height={h}>
          <rect x={0} y={0} width={w} height={h} fill={`url(#${id}fall)`} />
        </mask>
        <filter id={`${id}rim`} {...big}>
          <feOffset in="SourceAlpha" dx={0} dy={4 * s} result="off" />
          <feComposite in="SourceAlpha" in2="off" operator="out" result="edge" />
          <feFlood floodColor={rimC} floodOpacity={Math.min(1, 0.35 + 0.65 * glow)} />
          <feComposite in2="edge" operator="in" result="rimc" />
          <feGaussianBlur in="rimc" stdDeviation={0.7 * s} />
        </filter>
        <filter id={`${id}halo`} {...big}>
          <feOffset in="SourceAlpha" dx={0} dy={4 * s} result="off" />
          <feComposite in="SourceAlpha" in2="off" operator="out" result="edge" />
          <feFlood floodColor={rimC} floodOpacity={0.8 * glow} />
          <feComposite in2="edge" operator="in" result="rimc" />
          <feGaussianBlur in="rimc" stdDeviation={7 * s} />
        </filter>
        <filter id={`${id}soft`} {...big}><feGaussianBlur stdDeviation={10 * s} /></filter>
        <filter id={`${id}smoke`} {...big}><feGaussianBlur stdDeviation={6 * s} /></filter>
        <filter id={`${id}shadow`} {...big}><feGaussianBlur stdDeviation={6} /></filter>
      </defs>

      {/* 墙和地 */}
      <rect x={0} y={0} width={w} height={h} fill={`url(#${id}wall)`} />
      <rect x={0} y={floorY} width={w} height={h - floorY} fill="#000" opacity={0.3} />
      <line x1={0} y1={floorY} x2={w} y2={floorY} stroke={L.amber} strokeOpacity={0.09} strokeWidth={1.5} />

      {/* 墙上的钟（B：等） */}
      {p.clock && (() => {
        const c = p.clock;
        const o = 1 - 0.55 * c.dark;
        const tip = rot({x: c.x, y: c.y - c.r * 0.35}, {x: c.x, y: c.y}, c.hand);
        return (
          <g opacity={o}>
            <circle cx={c.x + 5} cy={c.y + 9} r={c.r + 10} fill="#000" opacity={0.5} filter={`url(#${id}shadow)`} />
            <circle cx={c.x} cy={c.y} r={c.r + 9} fill="#1A120C" stroke="#3A2A1C" strokeWidth={2} />
            <defs>
              <linearGradient id={`${id}face`} x1="0" y1="0" x2="1" y2="0.4">
                <stop offset="0" stopColor="#5A4430" />
                <stop offset="1" stopColor="#21170F" />
              </linearGradient>
            </defs>
            <circle cx={c.x} cy={c.y} r={c.r} fill={`url(#${id}face)`} />
            {/* 朝灯的左下沿有一道暖色轮廓光 */}
            <path d={`M ${c.x - (c.r + 9) * Math.cos(0.35)} ${c.y + (c.r + 9) * Math.sin(0.35)} A ${c.r + 9} ${c.r + 9} 0 0 1 ${c.x - (c.r + 9) * Math.cos(1.25)} ${c.y - (c.r + 9) * Math.sin(1.25)}`}
              fill="none" stroke={L.rim} strokeWidth={2.5} strokeOpacity={0.75} />
            {Array.from({length: 12}, (_, i) => {
              const a = (i / 12) * Math.PI * 2;
              const r0 = c.r * 0.86, r1 = c.r * (i % 3 === 0 ? 0.72 : 0.79);
              return <line key={i} x1={c.x + Math.sin(a) * r0} y1={c.y - Math.cos(a) * r0} x2={c.x + Math.sin(a) * r1} y2={c.y - Math.cos(a) * r1}
                stroke={L.ink} strokeOpacity={0.5} strokeWidth={i % 3 === 0 ? 3 : 1.6} />;
            })}
            {c.digit && c.dark < 1 && (
              <text x={c.x} y={c.y + c.r * 0.12} textAnchor="middle" dominantBaseline="central" fontFamily={L.serif} fontSize={c.r * 1.05}
                fontWeight={700} fill={L.ink} opacity={1 - c.dark}
                transform={`translate(0 ${c.y}) scale(1 ${Math.max(0.02, c.flip ?? 1)}) translate(0 ${-c.y})`}>{c.digit}</text>
            )}
            <line x1={c.x} y1={c.y} x2={tip.x} y2={tip.y} stroke={L.amber} strokeWidth={3} strokeLinecap="round" />
            <circle cx={c.x} cy={c.y} r={4.5} fill={L.amber} />
            {c.flash > 0 && <circle cx={c.x} cy={c.y} r={c.r + 9} fill={L.cold} opacity={c.flash} />}
          </g>
        );
      })()}

      {/* 灯罩下的一束光、光里的灰尘、地上的光晕（灯晃时光跟着晃） */}
      <g opacity={glow}>
        <g transform={`rotate(${swing} ${lampX} 0)`}>
          <polygon points={`${lampX - sh * 0.8},${lampY} ${lampX + sh * 0.8},${lampY} ${lampX + 330 * s},${floorY} ${lampX - 330 * s},${floorY}`}
            fill={`url(#${id}cone)`} opacity={0.34} filter={`url(#${id}soft)`} />
          {DUST.map((d, i) => {
            const t = ((d.v + f * d.sp / 900) % 1);
            const y = shadeY + sh + t * (floorY - shadeY - sh);
            const half = (sh * 0.8) + (330 * s - sh * 0.8) * t;
            const x = lampX + (d.u - 0.5) * 2 * half * 0.85 + Math.sin(f / 40 + d.ph) * 6 * s;
            return <circle key={i} cx={x} cy={y} r={d.r * s * 0.8} fill={lampC} opacity={(0.2 + 0.32 * Math.sin(f / 25 + d.ph) ** 2) * (1 - t * 0.6)} />;
          })}
        </g>
        <ellipse cx={lampX + 10 * s + swingDx} cy={floorY + 8 * s} rx={380 * s} ry={50 * s} fill={`url(#${id}pool)`} />
      </g>

      {p.children}

      {/* 电到的那一下：冷光从手腕炸开，在人身后，剪影始终不透明 */}
      {burst > 0 && <circle cx={wrist.x} cy={wrist.y} r={(power > 0.6 ? 620 : 70) * s} fill={`url(#${id}burst)`} opacity={burst}
        style={{mixBlendMode: 'screen'}} />}

      {/* 电极的线（有电流在里面跑） */}
      <path d={`M ${w0.x} ${w0.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${box.x} ${box.y}`}
        fill="none" stroke={L.elecGlow} strokeOpacity={0.45 + 0.5 * elecOn} strokeWidth={3.4 * s} />
      <path d={`M ${w0.x} ${w0.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${box.x} ${box.y}`}
        fill="none" stroke={L.elecGlow} strokeOpacity={0.1 + 0.3 * elecOn} strokeWidth={12 * s} filter={`url(#${id}soft)`} />
      {pulsePts.map((q, i) => (
        <g key={i}>
          <circle cx={q.x} cy={q.y} r={16 * s} fill={L.elecGlow} opacity={0.55} filter={`url(#${id}soft)`} />
          <circle cx={q.x} cy={q.y} r={4.5 * s} fill="#FFFFFF" />
        </g>
      ))}
      {/* 电击盒：指针平时停在低处；电下去时甩到满格、红区亮起 */}
      {(p.box ?? !p.wireTo) && (() => {
        const bw = 96 * s, bh = 62 * s, bx = box.x, by = box.y - bh / 2;
        const dc = {x: bx + bw / 2, y: by + bh * 0.74};
        const dr = bh * 0.52;
        const ang = -75 + 150 * (p.dial ?? 0.08);
        const tip = rot({x: dc.x, y: dc.y - dr * 0.92}, dc, ang);
        const redA = rot({x: dc.x, y: dc.y - dr}, dc, 45), redB = rot({x: dc.x, y: dc.y - dr}, dc, 75);
        const hot = p.dialHot ?? 0;
        const needle = hot > 0 ? mix(L.idle, L.red, hot) : p.dialWarm ? L.amber : L.idle;
        return (
          <g>
            <rect x={bx + 10 * s} y={by + bh} width={6 * s} height={floorY - by - bh} fill={L.sil} />
            <rect x={bx + bw - 16 * s} y={by + bh} width={6 * s} height={floorY - by - bh} fill={L.sil} />
            <rect x={bx} y={by} width={bw} height={bh} rx={6 * s} fill="#120D09" stroke={L.rim} strokeOpacity={0.45} strokeWidth={1.6 * s} />
            <path d={`M ${dc.x - dr} ${dc.y} A ${dr} ${dr} 0 0 1 ${dc.x + dr} ${dc.y}`} fill="#1E1610" stroke={L.ink} strokeOpacity={0.4} strokeWidth={1.4 * s} />
            <path d={`M ${redA.x} ${redA.y} A ${dr} ${dr} 0 0 1 ${redB.x} ${redB.y}`} fill="none" stroke={mix(L.idle, L.red, hot)} strokeWidth={4 * s} />
            {hot > 0 && <path d={`M ${redA.x} ${redA.y} A ${dr} ${dr} 0 0 1 ${redB.x} ${redB.y}`} fill="none" stroke={L.red} strokeWidth={14 * s}
              opacity={0.35 * hot} filter={`url(#${id}soft)`} />}
            <line x1={dc.x} y1={dc.y} x2={tip.x} y2={tip.y} stroke={needle} strokeWidth={2.8 * s} strokeLinecap="round" />
            <circle cx={dc.x} cy={dc.y} r={3.2 * s} fill={L.ink} />
            <circle cx={bx + bw - 9 * s} cy={by + 9 * s} r={3.6 * s} fill={k >= 0 && k < 10 ? L.elec : '#FFE9C7'} opacity={0.9} />
          </g>
        );
      })()}

      {/* 灯：线、灯罩、灯泡（晃的时候整个一起晃） */}
      <g transform={`rotate(${swing} ${lampX} 0)`}>
        <defs><linearGradient id={`${id}cord`} x1="0" y1="0" x2="0" y2={shadeY} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#2E2117" stopOpacity={0} /><stop offset={Math.min(0.95, 175 / Math.max(1, shadeY))} stopColor="#2E2117" stopOpacity={0} />
          <stop offset="1" stopColor="#3A2A1C" stopOpacity={1} /></linearGradient></defs>
        <line x1={lampX} y1={0} x2={lampX} y2={shadeY} stroke={`url(#${id}cord)`} strokeWidth={2.5 * s} />
        <circle cx={lampX} cy={shadeY + sh * 0.55} r={170 * s} fill={`url(#${id}bulb)`} opacity={0.6 * glow} />
        <path d={`M ${lampX - sh} ${lampY} L ${lampX - sh * 0.35} ${shadeY - sh * 0.15} L ${lampX + sh * 0.35} ${shadeY - sh * 0.15} L ${lampX + sh} ${lampY} Z`}
          fill="#120D09" stroke={L.rim} strokeOpacity={0.4} strokeWidth={1.4} />
        <ellipse cx={lampX} cy={lampY} rx={sh * 0.95} ry={sh * 0.14} fill={lampC} opacity={0.3 + 0.7 * glow} />
      </g>

      {/* 人和椅子：背后一圈柔光（按灯衰减）→ 不透明的剪影 → 朝灯的一条亮边（按灯衰减） */}
      <g mask={`url(#${id}rimMask)`}><g transform={figT} filter={`url(#${id}halo)`}>{figure}</g></g>
      <g transform={figT}>{figure}</g>
      <g mask={`url(#${id}rimMask)`}><g transform={figT} filter={`url(#${id}rim)`}>{figure}</g></g>

      {/* 电极：绑在脚背上的一条带子加一块金属片；平时暗，片上一点冷光在呼吸，通电时整个亮成蓝白 */}
      <g transform={`translate(${wrist.x} ${wrist.y}) rotate(8)`}>
        <circle r={30 * s * (0.5 + elecOn)} fill={L.elecGlow} opacity={0.5 * elecOn} filter={`url(#${id}soft)`} />
        <rect x={-15 * s} y={-8 * s} width={30 * s} height={14 * s} rx={4 * s} fill="#1C1814" stroke={mix('#5A5048', L.elec, elecOn)} strokeWidth={1.6 * s} />
        <circle cx={0} cy={-1 * s} r={5.5 * s} fill={mix('#3A4450', L.elec, elecOn)} stroke="#8A8F96" strokeWidth={1.2 * s} />
        <circle cx={0} cy={-1 * s} r={2 * s} fill={L.elec} opacity={0.35 + 0.3 * idleBreath + 0.35 * elecOn} />
      </g>

      {p.zap && <Bolts o={wrist} reach={46 * s} n={3} w={1.6 * s} seed={`${id}z${f}`} k={0} />}
      {k >= 0 && [0, 1, 2, 4].includes(k) && (
        <Bolts o={wrist} reach={(55 + 65 * power) * s} n={power > 0.6 ? 4 : 2} w={(1.4 + 1.6 * power) * s} seed={`${id}s`} k={k}
          also={power > 0.6 ? [{w: 2.6 * s, pts: [
            wrist, {x: fig.x + 70 * s, y: fig.y + 60 * s}, {x: fig.x + 62 * s, y: fig.y - (hop + 24) * s},
            {x: fig.x + 10 * s, y: fig.y - (hop + 20) * s}, {x: fig.x - 30 * s, y: fig.y - (hop + 80) * s}, {x: fig.x - 36 * s, y: fig.y - (hop + 150) * s},
          ].map((q, i) => (i === 0 ? q : {x: q.x + (random(`cr${Math.floor(k / 2)}${i}`) - 0.5) * 18 * s, y: q.y}))}] : []} />
      )}
      {k >= 2 && Array.from({length: power > 0.6 ? 5 : 2}, (_, i) => {
        const t = (k - 2 - i * 3) / 30;
        if (t < 0 || t > 1) return null;
        return <circle key={i} cx={wrist.x + (8 + i * 6) * s * t + Math.sin(k / 6 + i) * 6 * s} cy={wrist.y - 20 * s - 110 * s * t}
          r={(8 + 26 * t) * s * (0.6 + 0.4 * power)} fill="#C9C4BC" opacity={0.3 * (1 - t) * (0.5 + 0.5 * power)} filter={`url(#${id}smoke)`} />;
      })}

      {/* 四角压暗 */}
      <rect x={0} y={0} width={w} height={h} fill={`url(#${id}vig)`} />
    </svg>
  );
};

// 小房间：32 间里的一间（“32 人里，9 人选了 A”）。两半，各一盏灯、一个剪影，不用滤镜（32 间一起画也不慢）
export const MiniCell: React.FC<{w: number; h: number; on: number; pick: number; flash: number; dimA: number; dimB: number; seed: number;
  single?: boolean}> = ({w, h, on, pick, flash, dimA, dimB, seed, single}) => {
  const hw = single ? w : (w - 3) / 2;
  const half = (left: number, red: number, dim: number, fx: number) => (
    <div style={{position: 'absolute', left, top: 0, width: hw, height: h, overflow: 'hidden',
      background: `radial-gradient(ellipse 70% 85% at 42% 60%, rgba(120,78,40,${0.75 * on}), #0A0705 75%)`}}>
      <svg width={hw} height={h} viewBox="0 0 952 1080" preserveAspectRatio="none" style={{position: 'absolute', inset: 0}}>
        <polygon points="300,240 410,240 680,880 30,880" fill={L.lamp} opacity={0.18 * on} />
        <ellipse cx={354} cy={210} rx={90} ry={22} fill={L.lamp} opacity={0.9 * on} />
        <g transform="translate(400 648) scale(1.55)"><Figure /></g>
      </svg>
      {red > 0 && <div style={{position: 'absolute', inset: 0, background: '#B8382C', opacity: 0.55 * red, mixBlendMode: 'color'}} />}
      {red > 0 && <div style={{position: 'absolute', inset: 0, background: L.red, opacity: 0.12 * red, mixBlendMode: 'screen'}} />}
      {fx > 0 && <div style={{position: 'absolute', inset: 0, background: L.cold, opacity: fx}} />}
      {dim > 0 && <div style={{position: 'absolute', inset: 0, background: '#000', opacity: dim}} />}
    </div>
  );
  return (
    <div style={{position: 'absolute', width: w, height: h, borderRadius: 3, overflow: 'hidden', background: '#050403',
      boxShadow: `0 0 0 1px rgba(246,198,126,${0.08 + 0.1 * on})`}} data-seed={seed}>
      {half(0, pick, dimA, flash)}
      {!single && <div style={{position: 'absolute', left: hw, top: 0, width: 3, height: h, background: '#2A1D12'}} />}
      {!single && half(hw + 3, 0, dimB, 0)}
    </div>
  );
};

// 胶片颗粒：很淡，每四帧换一次（颗粒换得太勤，文件会很大，抖音再压一遍也只剩噪点）
export const Grain: React.FC<{f: number; o?: number}> = ({f, o = 0.04}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, pointerEvents: 'none', mixBlendMode: 'screen'}}>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={Math.floor(f / 4)} stitchTiles="stitch" />
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 0.95  0 0 0 0 0.88  0 0 0 1.4 -0.55" />
    </filter>
    <rect width={1920} height={1080} filter="url(#grain)" opacity={o} />
  </svg>
);
