// 002《被坑多了，你会变狠吗？》封面：竖版 3:4（1080×1440）、横版 4:3（1440×1080）。
// 画的是片子 48.9–51.4 秒那拍：四个你站成一排（黄、红、蓝、绿，同一个翘毛），亮度 = 那一段的平均分；
// 红衣（狠）在暗处抱着胳膊，绿衣（会原谅）在暖光里。第五版只换颜色：骗子、记仇都是红色家族（lib.ts 的 COL_OVERRIDE）。竖版下面一条历史条（真数据，不加字）。
// 字都在画面中间 80% 以内；竖版的字还要躲开 9:16 和 1:1 两种中间裁切（x 135–945、y 180–1260），横版躲开 1:1（x 180–1260）。
// 只读引用 people.tsx / lib.ts / Overlay.tsx / components/people，不改它们。
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FlatPerson} from '../../components/people/FlatPerson';
import {mixHex} from '../../components/people/geom';
import {RPose, resolve} from '../../components/people/rig';
import {EX, POSE, lookFor} from './people';
import {D, I, SANS} from './lib';
import {HistBar} from './Overlay';

const BG = '#0F1117';
const NIGHT = '#0B0D12';
const HOT = '#FF7A5C';   // “变狠”两个字：第五版跟着片子换成“狠”的红提亮一档（同字幕里“拉黑”的 COL_HI.GRIM）

// 灯的亮度和片子同一个算法：这一段的平均分（1.99 / 1.46 / 2.39 / 2.83）归一化 → 黄 0.39、粉 0、蓝 0.67、绿 1
const lo = Math.min(...D.youAvg), hi = Math.max(...D.youAvg);
const K = D.youAvg.map((v) => (v - lo) / (hi - lo));

// 姿势：默认用片子里的（四分之三侧面）；yaw 给了就按同样的参数重新解一遍（试“转过来面对镜头”）
const STAND = {pelvis: -2, lean: 1, chest: 1, neck: 2, lN: {hip: 3, knee: 0}, lF: {hip: 10, knee: 10}, ground: true};
const idleAt = (yaw: number): RPose => resolve({...STAND, yaw, aN: {sh: 4, el: 14}, aF: {sh: -4, el: 14}, hN: 'limp', hF: 'limp'});
const crossAt = (yaw: number): RPose => resolve({...STAND, yaw, lean: -3, neck: -4, front: true,
  aN: {to: {x: -12, y: -36}, bend: 1}, aF: {to: {x: 18, y: -40}, bend: -1}, hN: 'fist', hF: 'fist'});

const FOUR = [
  {s: I.ALLC, cross: false, e: EX.calm},
  {s: I.GRIM, cross: true, e: EX.cold},
  {s: I.TFT, cross: false, e: EX.stiff},
  {s: I.GTFT, cross: false, e: EX.smile},
];

type Lay = {
  size: number; title: React.CSSProperties; shift: [number, number];   // 两行各往右挪多少 em（补句末标点留下的空）
  xs: number[]; G: number; s: number; facing: 1 | -1; lampY: number;
  hist?: {x0: number; x1: number; y0: number; y1: number};
};
const TALL: Lay = {
  size: 140, title: {left: 0, right: 0, top: 190, textAlign: 'center'}, shift: [0.34, 0.24],
  xs: [220, 428, 636, 844], G: 1168, s: 1.85, facing: 1, lampY: 578,
  hist: {x0: 120, x1: 960, y0: 1218, y1: 1258},
};
const WIDE: Lay = {
  size: 102, title: {left: 200, top: 366, textAlign: 'left'}, shift: [0, 0],
  xs: [892, 1036, 1180, 1324], G: 960, s: 1.72, facing: -1, lampY: 300,
  hist: {x0: 204, x1: 756, y0: 634, y1: 662},
};

const Defs: React.FC<{L: Lay}> = ({L}) => (
  <defs>
    <radialGradient id="cvWarm"><stop offset="0" stopColor="#FFD9A0" stopOpacity={0.5} /><stop offset="1" stopColor="#FFD9A0" stopOpacity={0} /></radialGradient>
    <radialGradient id="cvPool"><stop offset="0" stopColor="#FFDDB0" stopOpacity={0.6} /><stop offset="1" stopColor="#FFDDB0" stopOpacity={0} /></radialGradient>
    <radialGradient id="cvShade"><stop offset="0" stopColor={NIGHT} stopOpacity={0.85} /><stop offset="1" stopColor={NIGHT} stopOpacity={0} /></radialGradient>
    <linearGradient id="cvCone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stopColor="#FFD9A0" stopOpacity={0.6} />
      <stop offset="1" stopColor="#FFD9A0" stopOpacity={0.18} />
    </linearGradient>
    <radialGradient id="cvVig" cx="0.5" cy="0.5" r="0.75">
      <stop offset="0.55" stopColor="#000" stopOpacity={0} /><stop offset="1" stopColor="#000" stopOpacity={0.55} />
    </radialGradient>
    {L.hist && <clipPath id="cvHist"><rect x={L.hist.x0} y={L.hist.y0} width={L.hist.x1 - L.hist.x0} height={L.hist.y1 - L.hist.y0} rx={(L.hist.y1 - L.hist.y0) / 2} /></clipPath>}
  </defs>
);

const Row: React.FC<{L: Lay; yaw?: number}> = ({L, yaw}) => {
  const {G, s, facing} = L;
  const people = FOUR.map((q, i) => {
    const k = K[i];
    const pose = yaw === undefined ? (q.cross ? POSE.cross : POSE.idle) : (q.cross ? crossAt(yaw) : idleAt(yaw));
    const base = lookFor(q.s, 'me');
    // 绿衣在暖光里：皮肤、衣服往暖白偏一点；其余按离灯远近往夜色压
    const look = k > 0.9 ? {...base, skin: mixHex(base.skin, '#FFE6C4', 0.25), top: mixHex(base.top, '#FFE6B0', 0.08)} : base;
    return (
      <FlatPerson key={i} pose={pose} expr={q.e} look={look} x={L.xs[i]} y={G} s={s} facing={facing}
        dim={0.62 * (1 - k)} night={NIGHT} light={{x: -0.35 * facing, y: -1}} />
    );
  });
  // 挨得近时脸那一侧要压在邻居的后脑上：脸朝右就从右往左画
  const ordered = facing === 1 ? [...people].reverse() : people;
  return (
    <>
      {/* 光：每人头上一盏灯（片子 S25 同款，按 s 缩放），灯下一束光、上身一团暖光、脚下一圈光，亮度 = K；粉衣那盏不亮，再压一层暗 */}
      {FOUR.map((q, i) => {
        const x = L.xs[i], k = K[i];
        const u = s / 3.2;   // 片子里四个你是 s = 3.2
        const ly = L.lampY;
        const lamp = (
          <g>
            <rect x={x - 44 * u} y={ly - 30 * u} width={88 * u} height={28 * u} rx={7 * u} fill="#3A3D46" />
            {k > 0.01 && <circle cx={x} cy={ly + 6 * u} r={60 * u} fill="#FFE2B0" opacity={0.12 + 0.5 * k} />}
            <circle cx={x} cy={ly + 6 * u} r={30 * u} fill={k > 0.6 ? '#FFD38A' : k > 0.2 ? '#F1E4CC' : '#4A4D57'} />
          </g>
        );
        if (k <= 0.01) {
          return <g key={`l${i}`}><ellipse cx={x} cy={G - 150 * s} rx={95 * s} ry={190 * s} fill="url(#cvShade)" />{lamp}</g>;
        }
        return (
          <g key={`l${i}`}>
            <polygon points={`${x - 30 * u},${ly + 10 * u} ${x + 30 * u},${ly + 10 * u} ${x + 78 * s},${G + 6} ${x - 78 * s},${G + 6}`}
              fill="url(#cvCone)" opacity={0.1 + 0.45 * k} />
            <circle cx={x} cy={G - 190 * s} r={(80 + 70 * k) * s} fill="url(#cvWarm)" opacity={0.2 + 0.8 * k} />
            <ellipse cx={x} cy={G + 4} rx={(60 + 40 * k) * s} ry={16 * s} fill="url(#cvPool)" opacity={0.25 + 0.75 * k} />
            {lamp}
          </g>
        );
      })}
      {ordered}
    </>
  );
};

// tune：试版面用（--props 传），定稿不传
export const Cover002: React.FC<{w: number; h: number; yaw?: number; tune?: Partial<Lay>}> = ({w, h, yaw, tune}) => {
  const tall = h > w;
  const L = {...(tall ? TALL : WIDE), ...(tune ?? {})};
  return (
    <AbsoluteFill style={{background: BG}}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{position: 'absolute', inset: 0}}>
        <Defs L={L} />
        <Row L={L} yaw={yaw} />
        <rect width={w} height={h} fill="url(#cvVig)" />
        {L.hist && (
          <g clipPath="url(#cvHist)">
            <HistBar counts={D.counts} x0={L.hist.x0} x1={L.hist.x1} y0={L.hist.y0} y1={L.hist.y1} upTo={300} />
          </g>
        )}
      </svg>
      <div lang="zh-Hans" style={{position: 'absolute', ...L.title, fontFamily: SANS, fontWeight: 600, fontSize: L.size,
        lineHeight: 1.16, color: '#F6F7FA', whiteSpace: 'nowrap', letterSpacing: '-0.01em', textShadow: '0 6px 30px rgba(0,0,0,0.65)'}}>
        <div style={{transform: `translateX(${L.shift[0]}em)`}}>被坑多了，</div>
        <div style={{transform: `translateX(${L.shift[1]}em)`}}>你会<span style={{color: HOT}}>变狠</span>吗？</div>
      </div>
      <div lang="zh-Hans" style={{position: 'absolute', left: 56, top: 44, fontFamily: SANS, fontWeight: 500, fontSize: 30,
        color: 'rgba(200,206,222,0.62)', letterSpacing: '0.1em'}}>AI 生成</div>
    </AbsoluteFill>
  );
};
