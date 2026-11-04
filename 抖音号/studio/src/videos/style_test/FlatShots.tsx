// 画风 A（扁平矢量小人，夜里一盏灯）的五个牌桌镜头和 5 秒小动作片。布局、牌、姿势、时间点都在 scene.ts。
import React, {useId} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {FlatPerson} from '../../components/people/FlatPerson';
import {Chair, PendantLamp, ReachHand, SoftShadow} from '../../components/people/FlatProps';
import {CHIP, ChipStack, Felt, LooseChip, Rail, StandingCard, TableCard} from '../../components/people/FlatCards';
import {EXPR, breath} from '../../components/people/face';
import {ME, OTHER} from '../../components/people/look';
import {nudge, pose, solve} from '../../components/people/rig';
import {CH, CW} from '../../components/people/cards';
import {ALLIN, BOARD, HOLE, L1, L2, L3, L4, L5, L6, OUTS, PUSHER_FACE, THINK, UNSEEN, W, H, miniExpr, miniFlip, miniPeek, miniPose, miniPuff, miniPuff2, rowCard, stillExpr, PEEK} from './scene';

const WALL = '#1C1613';

// 暗房间：墙是暖黑，灯那一带稍亮；四角压暗（id 带上 useId，好几个镜头排在一张图上时不串）
const useUid = () => useId().replace(/[^a-zA-Z0-9]/g, '');
const Room: React.FC<{lx: number; ly: number; r?: number; children?: React.ReactNode}> = ({lx, ly, r = 1100, children}) => {
  const id = useUid();
  return (
  <>
    <defs>
      <radialGradient id={`${id}w`} cx={lx} cy={ly} r={r} gradientUnits="userSpaceOnUse">
        <stop offset="0" stopColor="#3A2B22" />
        <stop offset="0.45" stopColor="#231A15" />
        <stop offset="1" stopColor="#0C0908" />
      </radialGradient>
    </defs>
    <rect width={W} height={H} fill={`url(#${id}w)`} />
    {children}
  </>
  );
};
const Vignette: React.FC = () => {
  const id = useUid();
  return (
    <>
      <defs>
        <radialGradient id={`${id}v`} cx="50%" cy="48%" r="75%">
          <stop offset="0.55" stopColor="#000" stopOpacity={0} />
          <stop offset="1" stopColor="#000" stopOpacity={0.6} />
        </radialGradient>
      </defs>
      <rect width={W} height={H} fill={`url(#${id}v)`} />
    </>
  );
};

// 桌后的牌桌：远沿一条包边，往下是绒布
const NearTable: React.FC<{railY: number; pool: {x: number; y: number}}> = ({railY, pool}) => (
  <g>
    <Felt pts={[{x: -20, y: railY}, {x: W + 20, y: railY}, {x: W + 20, y: H}, {x: -20, y: H}]} lx={pool.x} ly={pool.y} lr={900} sq={0.55}
      line={{cx: 540, cy: railY + 700, rx: 760, ry: 330}} />
    <SoftShadow x={540} y={railY + 40} rx={700} ry={26} o={0.55} />
    <Rail d={`M -60 ${railY} L ${W + 60} ${railY}`} w={58} />
  </g>
);

const hand2screen = (x: number, G: number, s: number, p: {x: number; y: number}) => ({x: x + p.x * s, y: G + p.y * s});
// 吊灯照在脸上：灯的位置换算到身体坐标，暖光从头顶往下淡
const lampGlow = (lamp: {x: number; y: number}, x: number, G: number, s: number) =>
  ({at: {x: (lamp.x - x) / s, y: (lamp.y + 30 - G) / s}, color: '#FFD49A', amount: 0.22, r: 210});

// —— 镜头 1：看底牌的特写 ——
export const A1: React.FC = () => {
  const f = useCurrentFrame();
  const L = L1, s = L.s, G = L.G;
  const r = nudge(PEEK, {shrug: 0.05 * breath(f), chest: -0.4 * breath(f)});
  const e = stillExpr({...EXPR.worry, browIn: 0.95, knit: 0.75, smile: -0.4}, f, 'a1');
  const sk = solve(r);
  const hN = hand2screen(L.x, G, s, sk.wN);
  return (
    <AbsoluteFill style={{background: WALL}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Room lx={L.lamp.x} ly={L.lamp.y + 200}>
          <PendantLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} floorY={L.railY + 200} spread={520} cone={0.16} pool={0} />
        </Room>
        <FlatPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} part="body" light={{x: 0.5, y: -1}} glow={lampGlow(L.lamp, L.x, G, s)} />
        <NearTable railY={L.railY} pool={L.pool} />
        {L.chips.map((c, i) => <ChipStack key={i} x={c.x} y={c.y} R={58} n={c.n} c={CHIP[c.c]} seed={`a1c${i}`} />)}
        <TableCard x={hN.x + L.hole[1].dx} y={hN.y + L.hole[1].dy} s={L.holeS} rot={L.hole[1].rot} face={HOLE[1]} down />
        <TableCard x={hN.x + L.hole[0].dx} y={hN.y + L.hole[0].dy} s={L.holeS} rot={L.hole[0].rot} face={HOLE[0]} down peek={0.95} />
        <FlatPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} part="arms" light={{x: 0.5, y: -1}} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 2：输了一手，瘫在椅背上仰头 ——
export const A2: React.FC = () => {
  const f = useCurrentFrame();
  const L = L2, s = L.s;
  const r = nudge(pose('slump'), {chest: -0.8 * breath(f)});
  const e = stillExpr({...EXPR.blank, lid: 0.55, open: 0.18}, f, 'a2');
  const T = L.table, ty = L.G - 88 * s;
  return (
    <AbsoluteFill style={{background: WALL}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Room lx={L.lamp.x} ly={L.lamp.y + 300}>
          <rect x={0} y={L.G} width={W} height={H - L.G} fill="#120D0B" />
          <PendantLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} floorY={L.G} spread={420} cone={0.2} pool={0.5} />
        </Room>
        <Chair x={L.x - 10 * s} y={L.G} s={s} />
        <FlatPerson pose={r} expr={e} look={ME} x={L.x} y={L.G} s={s} light={{x: 0.8, y: -1}} />
        {/* 牌桌从右边进画：绒布面（看得到一点桌面）、黑皮包边、木桌裙、桌腿；桌上两张翻开的牌（输掉的那手） */}
        <g>
          <SoftShadow x={(T.x0 + T.x1) / 2 + 40} y={L.G + 4} rx={300} ry={20} o={0.65} />
          <rect x={T.x0 + 70} y={ty + 40} width={26} height={L.G - ty - 40} fill="#1A120E" />
          <rect x={T.x0 + 200} y={ty + 40} width={22} height={L.G - ty - 46} fill="#120C0A" />
          <path d={`M ${T.x0 + 20} ${ty + 20} L ${T.x1} ${ty + 20} L ${T.x1} ${ty + 62} L ${T.x0 + 30} ${ty + 62} Z`} fill="#4A3121" />
          <path d={`M ${T.x0 + 30} ${ty + 56} L ${T.x1} ${ty + 56} L ${T.x1} ${ty + 62} L ${T.x0 + 30} ${ty + 62} Z`} fill="#2C1C13" />
          <Felt pts={[{x: T.x0 + 40, y: ty - 70}, {x: T.x1, y: ty - 70}, {x: T.x1, y: ty + 2}, {x: T.x0, y: ty + 2}]} lx={T.x0 + 120} ly={ty - 30} lr={320} sq={0.3} />
          <TableCard x={T.x0 + 115} y={ty - 26} s={0.95} rot={-14} sq={0.3} face={LOST[0]} />
          <TableCard x={T.x0 + 205} y={ty - 34} s={0.95} rot={9} sq={0.3} face={LOST[1]} />
          <Rail d={`M ${T.x0 - 6} ${ty + 6} L ${T.x1 + 40} ${ty + 6}`} w={40} />
        </g>
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};
const LOST = [{r: '7' as const, s: 'C' as const}, {r: '2' as const, s: 'D' as const}];

// —— 镜头 3：桌面俯视，公共牌一排，一只手把一堆筹码推出去 ——
export const A3: React.FC = () => {
  const L = L3;
  return (
    <AbsoluteFill style={{background: WALL}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <rect width={W} height={H} fill="#0E0A09" />
        <Felt pts={[{x: -20, y: L.railY}, {x: W + 20, y: L.railY}, {x: W + 20, y: H}, {x: -20, y: H}]} lx={L.pool.x} ly={L.pool.y} lr={1000} sq={0.7}
          line={{cx: 540, cy: 1180, rx: 640, ry: 400}} />
        <SoftShadow x={540} y={L.railY + 50} rx={700} ry={34} o={0.6} />
        <Rail d={`M -60 ${L.railY} L ${W + 60} ${L.railY}`} w={74} />
        {L.board.map((c, i) => <TableCard key={i} x={c.x} y={c.y} s={L.cardS} rot={c.rot} sq={L.sq} face={BOARD[i]} />)}
        {L.loose.map((c, i) => <LooseChip key={`l${i}`} x={c.x} y={c.y} R={50} c={CHIP[c.c]} seed={`a3l${i}`} sq={L.sq} />)}
        {L.stacks.slice().sort((a, b) => a.y - b.y).map((c, i) => <ChipStack key={i} x={c.x} y={c.y} R={50} n={c.n} c={CHIP[c.c]} sq={L.sq} seed={`a3s${c.x}`} />)}
        <ReachHand x={L.hand.x} y={L.hand.y} s={L.hand.s} r={L.hand.r} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 4：两个人隔着牌桌，左边全推，右边托着腮盯着他 ——
export const A4: React.FC = () => {
  const f = useCurrentFrame();
  const L = L4, s = L.s, T = L.table;
  const rL = nudge(ALLIN, {chest: -0.5 * breath(f)});
  const rR = nudge(THINK, {chest: -0.5 * breath(f + 40)});
  const eL = stillExpr(PUSHER_FACE, f, 'a4l');
  const eR = stillExpr(EXPR.suspect, f, 'a4r');
  const ty = L.G - 88 * s;
  return (
    <AbsoluteFill style={{background: WALL}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Room lx={L.lamp.x} ly={L.lamp.y + 400} r={1000}>
          <rect x={0} y={L.G} width={W} height={H - L.G} fill="#100B09" />
          <PendantLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} floorY={T.far + 40} spread={300} cone={0.2} pool={0} />
        </Room>
        {/* 先画桌面绒布（在人后面），再画人，再画近沿包边、桌裙、牌和筹码，最后画搭在桌上的胳膊 */}
        <SoftShadow x={540} y={L.G + 6} rx={360} ry={22} o={0.7} />
        <Felt pts={[{x: T.x0 + 40, y: T.far}, {x: T.x1 - 40, y: T.far}, {x: T.x1, y: T.near}, {x: T.x0, y: T.near}]} lx={540} ly={T.far + 70} lr={380} sq={0.35}
          line={{cx: 540, cy: T.far + 80, rx: 240, ry: 52}} />
        <FlatPerson pose={rL} expr={eL} look={ME} x={L.left} y={L.G} s={s} part="body" light={{x: 0.6, y: -1}} />
        <FlatPerson pose={rR} expr={eR} look={OTHER} x={L.right} y={L.G} s={s} facing={-1} part="body" light={{x: -0.6, y: -1}} />
        <g>
          <path d={`M ${T.x0 + 60} ${T.near} L ${T.x1 - 60} ${T.near} L ${T.x1 - 120} ${L.G} L ${T.x0 + 120} ${L.G} Z`} fill="#140E0B" />
          <path d={`M ${T.x0 + 170} ${T.near + 50} L ${T.x1 - 170} ${T.near + 50} L ${T.x1 - 190} ${L.G - 6} L ${T.x0 + 190} ${L.G - 6} Z`} fill="#1E1611" />
          <path d={`M ${T.x0 + 10} ${T.near + 8} L ${T.x1 - 10} ${T.near + 8} L ${T.x1 - 20} ${T.near + 52} L ${T.x0 + 20} ${T.near + 52} Z`} fill="#3E2A1D" />
          {L.board.map((c, i) => <TableCard key={i} x={c.x} y={c.y} s={L.cardS} rot={i * 3 - 3} sq={0.34} face={BOARD[i]} shadow={0.4} />)}
          {L.theirs.map((c, i) => <ChipStack key={`t${i}`} x={c.x} y={c.y} R={L.chipR} n={c.n} c={CHIP[c.c]} sq={0.34} seed={`a4t${i}`} />)}
          {L.push.slice().sort((a, b) => a.y - b.y).map((c, i) => <ChipStack key={`p${i}`} x={c.x} y={c.y} R={L.chipR} n={c.n} c={CHIP[c.c]} sq={0.34} seed={`a4p${i}`} />)}
          {L.sliding.map((c, i) => <LooseChip key={`sl${i}`} x={c.x} y={c.y} R={L.chipR} c={CHIP[c.c]} sq={0.34} seed={`a4s${i}`} />)}
          <Rail d={`M ${T.x0 - 6} ${T.near + 8} L ${T.x1 + 6} ${T.near + 8}`} w={34} />
        </g>
        <FlatPerson pose={rL} expr={eL} look={ME} x={L.left} y={L.G} s={s} part="arms" light={{x: 0.6, y: -1}} />
        <FlatPerson pose={rR} expr={eR} look={OTHER} x={L.right} y={L.G} s={s} facing={-1} part="arms" light={{x: -0.6, y: -1}} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 5：一个人站在一长排扣着的牌前，只有几张发亮 ——
export const A5: React.FC = () => {
  const f = useCurrentFrame();
  const L = L5, s = L.s;
  const id = useUid();
  const r = nudge(pose('standLook'), {neck: -10, pitch: -0.25, yaw: -0.05, gx: 1, gy: -0.55, chest: -0.6 * breath(f)});
  const e = stillExpr({...EXPR.worry, browIn: 0.6, knit: 0.4, smile: -0.2, lid: 0}, f, 'a5');
  const cards = Array.from({length: UNSEEN}, (_, i) => i).reverse();
  return (
    <AbsoluteFill style={{background: '#0C0A0B'}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <linearGradient id={`${id}g`} x1="0" y1={L.horizon} x2="0" y2={H} gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#0F1A14" />
            <stop offset="1" stopColor="#1F4A33" />
          </linearGradient>
          <radialGradient id={`${id}s`} cx={L.person.x + 40} cy={L.person.G} r={360} gradientUnits="userSpaceOnUse" gradientTransform={`translate(0 ${L.person.G * 0.7}) scale(1 0.3)`}>
            <stop offset="0" stopColor="#FFE3B0" stopOpacity={0.35} /><stop offset="1" stopColor="#FFE3B0" stopOpacity={0} />
          </radialGradient>
        </defs>
        <rect width={W} height={L.horizon} fill="#0C0A0B" />
        <rect y={L.horizon} width={W} height={H - L.horizon} fill={`url(#${id}g)`} />
        <rect width={W} height={H} fill={`url(#${id}s)`} />
        {cards.map((i) => {
          const c = rowCard(i);
          const glow = OUTS.includes(i) ? 1 : 0;
          return (
            <g key={i}>
              {glow > 0 && <SoftShadow x={c.x} y={c.y + 6 * c.k} rx={CW * c.s * 0.7} ry={20 * c.k} o={0.7} color="#FFC861" />}
              <SoftShadow x={c.x + 26 * c.k} y={c.y + 4 * c.k} rx={CW * c.s * 0.62} ry={12 * c.k} o={0.6} />
              <StandingCard x={c.x} y={c.y} s={c.s} glow={glow} tilt={c.tilt} dim={glow ? 0 : 0.42 + 0.45 * (1 - c.k)} />
            </g>
          );
        })}
        <PendantLamp x={L.person.x + 20} y={330} w={170} top={-20} floorY={L.person.G} spread={250} cone={0.16} pool={0.6} poolW={300} />
        <FlatPerson pose={r} expr={e} look={ME} x={L.person.x} y={L.person.G} s={s} light={{x: 0.7, y: -1}} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};

// —— 5 秒小动作片：看底牌 → 叹气（肩落下）→ 河牌翻开 → 眉毛抬起、松一口气 ——
export const AMini: React.FC = () => {
  const f = useCurrentFrame();
  const L = L6, s = L.s, G = L.G;
  const r = miniPose(f);
  const e = miniExpr(f);
  const sk = solve(r);
  const hN = hand2screen(L.x, G, s, sk.wN);
  const head = hand2screen(L.x, G, s, sk.head);
  const flip = miniFlip(f);
  const puff = Math.max(miniPuff(f), miniPuff2(f));
  return (
    <AbsoluteFill style={{background: WALL}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Room lx={L.lamp.x} ly={L.lamp.y + 200}>
          <PendantLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} floorY={L.railY + 200} spread={480} cone={0.16} pool={0} />
        </Room>
        <FlatPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} part="body" light={{x: 0.5, y: -1}} glow={lampGlow(L.lamp, L.x, G, s)} />
        {/* 呼出的一口气：嘴边一小团淡白，往前飘、散开 */}
        {puff > 0.01 && (
          <g opacity={0.5 * puff}>
            <ellipse cx={head.x + 95 + (1 - puff) * 40} cy={head.y + 150 + (1 - puff) * 10} rx={30 + (1 - puff) * 26} ry={16 + (1 - puff) * 10} fill="#F4EEE4" />
            <ellipse cx={head.x + 140 + (1 - puff) * 60} cy={head.y + 140} rx={18 + (1 - puff) * 18} ry={10 + (1 - puff) * 6} fill="#F4EEE4" />
          </g>
        )}
        <NearTable railY={L.railY} pool={{x: 560, y: 1300}} />
        {L.chips.map((c, i) => <ChipStack key={i} x={c.x} y={c.y} R={52} n={c.n} c={CHIP[c.c]} seed={`a6c${i}`} />)}
        {L.board.map((c, i) => (
          <TableCard key={i} x={c.x} y={c.y} s={L.cardS} rot={c.rot} face={BOARD[i]} flip={i === 4 ? flip : undefined} />
        ))}
        <TableCard x={hN.x + L.hole[1].dx} y={hN.y + L.hole[1].dy} s={L.holeS} rot={L.hole[1].rot} face={HOLE[1]} down />
        <TableCard x={hN.x + L.hole[0].dx} y={hN.y + L.hole[0].dy} s={L.holeS} rot={L.hole[0].rot} face={HOLE[0]} down peek={miniPeek(f)} />
        <FlatPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} part="arms" light={{x: 0.5, y: -1}} />
        <Vignette />
      </svg>
    </AbsoluteFill>
  );
};
