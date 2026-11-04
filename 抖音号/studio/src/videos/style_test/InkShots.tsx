// 画风 B（手绘墨线小人，纸色底）的五个牌桌镜头和 5 秒小动作片。布局和画风 A 用同一组数字（scene.ts）。
// 夜里和暗处：纸上压一层淡墨；灯照到的地方留出纸白。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {InkPerson, INK, PAPER} from '../../components/people/InkPerson';
import {Hatch, InkChair, InkLamp, InkReachHand, InkShadow, Paper, Wash, stroke} from '../../components/people/InkProps';
import {InkChipStack, InkFelt, InkRail, InkStandingCard, InkTableCard} from '../../components/people/InkCards';
import {EXPR, breath} from '../../components/people/face';
import {ME, OTHER} from '../../components/people/look';
import {nudge, pose, solve} from '../../components/people/rig';
import {CardId, CW} from '../../components/people/cards';
import {P} from '../../components/people/geom';
import {ALLIN, BOARD, HOLE, L1, L2, L3, L4, L5, L6, OUTS, PEEK, PUSHER_FACE, THINK, UNSEEN, W, H, miniExpr, miniFlip, miniPeek, miniPose, miniPuff, miniPuff2, rowCard, stillExpr} from './scene';

const TONE: Record<string, number> = {black: 2, navy: 1, cream: 0, amber: 0, plum: 1};

// 暗处：整张纸压一层淡墨，挖出一块椭圆的亮（灯下）
const Dark: React.FC<{holes: {x: number; y: number; rx: number; ry: number}[]; o?: number}> = ({holes, o = 0.42}) => {
  const d = `M -100 -100 H ${W + 100} V ${H + 100} H -100 Z ` + holes.map((h) =>
    `M ${h.x - h.rx} ${h.y} A ${h.rx} ${h.ry} 0 1 0 ${h.x + h.rx} ${h.y} A ${h.rx} ${h.ry} 0 1 0 ${h.x - h.rx} ${h.y} Z`).join(' ');
  return <Wash d={d} o={o} blur={60} rough={60} color="#6E665B" />;
};

const hand2screen = (x: number, G: number, s: number, p: P) => ({x: x + p.x * s, y: G + p.y * s});

// 桌后那张桌：纸白挡住人的下半身，上面一层淡绿，远沿两道线的包边
const NearTable: React.FC<{railY: number; f: number}> = ({railY, f}) => (
  <g>
    <rect x={-20} y={railY} width={W + 40} height={H - railY + 20} fill={PAPER} />
    <InkFelt pts={[{x: -20, y: railY}, {x: W + 20, y: railY}, {x: W + 20, y: H + 20}, {x: -20, y: H + 20}]} frame={f} o={0.42} />
    <InkRail pts={[{x: -20, y: railY - 2}, {x: 300, y: railY + 2}, {x: 700, y: railY - 1}, {x: W + 20, y: railY + 2}]} w={46} frame={f} />
  </g>
);

const ContactSheetPaper: React.FC = () => <Paper w={W} h={H} />;

// —— 镜头 1 ——
export const B1: React.FC = () => {
  const f = useCurrentFrame();
  const L = L1, s = L.s, G = L.G;
  const r = nudge(PEEK, {shrug: 0.05 * breath(f), chest: -0.4 * breath(f)});
  const e = stillExpr({...EXPR.worry, browIn: 0.95, knit: 0.75, smile: -0.4}, f, 'b1');
  const sk = solve(r);
  const hN = hand2screen(L.x, G, s, sk.wN);
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Dark holes={[{x: 600, y: 900, rx: 560, ry: 760}]} />
        <InkLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} frame={f} />
        <InkPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} frame={f} seed="b1p" part="body" weight={0.72} />
        <NearTable railY={L.railY} f={f} />
        {L.chips.map((c, i) => <InkChipStack key={i} x={c.x} y={c.y} R={58} n={c.n} tone={TONE[c.c]} frame={f} seed={`b1c${i}`} />)}
        <InkTableCard x={hN.x + L.hole[1].dx} y={hN.y + L.hole[1].dy} s={L.holeS} rot={L.hole[1].rot} face={HOLE[1]} down frame={f} seed="b1h1" />
        <InkTableCard x={hN.x + L.hole[0].dx} y={hN.y + L.hole[0].dy} s={L.holeS} rot={L.hole[0].rot} face={HOLE[0]} down peek={0.95} frame={f} seed="b1h0" />
        <InkPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} frame={f} seed="b1p" part="arms" weight={0.72} />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 2 ——
const LOST: CardId[] = [{r: '7', s: 'C'}, {r: '2', s: 'D'}];
export const B2: React.FC = () => {
  const f = useCurrentFrame();
  const L = L2, s = L.s;
  const r = nudge(pose('slump'), {chest: -0.8 * breath(f)});
  const e = stillExpr({...EXPR.blank, lid: 0.55, open: 0.18}, f, 'b2');
  const T = L.table, ty = L.G - 88 * s;
  const c = {frame: f, seed: 'b2t', px: 1};
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Dark holes={[{x: 560, y: 1150, rx: 520, ry: 700}]} />
        <InkLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} frame={f} />
        <path d={stroke([{x: -10, y: L.G + 2}, {x: 500, y: L.G - 2}, {x: W + 10, y: L.G + 3}], 3, c, 'floor')} fill={INK} opacity={0.6} />
        <InkChair x={L.x - 10 * s} y={L.G} s={s} frame={f} light />
        <InkPerson pose={r} expr={e} look={ME} x={L.x} y={L.G} s={s} frame={f} seed="b2p" weight={0.85} halo={7} />
        {/* 桌子：桌面一层淡绿、包边两道线、桌裙、两条腿 */}
        <g>
          <InkShadow x={(T.x0 + T.x1) / 2 + 40} y={L.G + 4} rx={280} ry={16} />
          <rect x={T.x0} y={ty - 70} width={T.x1 - T.x0 + 40} height={140} fill={PAPER} />
          <InkFelt pts={[{x: T.x0 + 40, y: ty - 70}, {x: T.x1 + 20, y: ty - 70}, {x: T.x1 + 20, y: ty}, {x: T.x0, y: ty}]} frame={f} seed="b2f" hatch={false} />
          <InkTableCard x={T.x0 + 115} y={ty - 26} s={0.95} rot={-14} sq={0.3} face={LOST[0]} frame={f} seed="b2c0" />
          <InkTableCard x={T.x0 + 205} y={ty - 34} s={0.95} rot={9} sq={0.3} face={LOST[1]} frame={f} seed="b2c1" />
          <InkRail pts={[{x: T.x0 - 6, y: ty + 6}, {x: T.x1 + 40, y: ty + 4}]} w={38} frame={f} seed="b2r" />
          <path d={stroke([{x: T.x0 + 24, y: ty + 28}, {x: T.x1 + 30, y: ty + 30}], 3, c, 'apron')} fill={INK} />
          <path d={stroke([{x: T.x0 + 30, y: ty + 62}, {x: T.x1 + 30, y: ty + 64}], 3, c, 'apron2')} fill={INK} />
          <Hatch lines={Array.from({length: 12}, (_, i) => [{x: T.x0 + 40 + i * 26, y: ty + 34}, {x: T.x0 + 52 + i * 26, y: ty + 58}] as [P, P])} size={1.8} ctx={c} o={0.5} />
          <path d={stroke([{x: T.x0 + 82, y: ty + 64}, {x: T.x0 + 84, y: L.G}], 5, c, 'leg1')} fill={INK} />
          <path d={stroke([{x: T.x0 + 210, y: ty + 64}, {x: T.x0 + 212, y: L.G - 8}], 4, c, 'leg2')} fill={INK} opacity={0.7} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 3 ——
export const B3: React.FC = () => {
  const f = useCurrentFrame();
  const L = L3;
  const c = {frame: f, seed: 'b3', px: 1};
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Wash d={`M -50 -50 H ${W + 50} V ${L.railY} H -50 Z`} o={0.55} blur={8} rough={10} color="#5E574E" />
        <InkFelt pts={[{x: -20, y: L.railY}, {x: W + 20, y: L.railY}, {x: W + 20, y: H + 20}, {x: -20, y: H + 20}]} frame={f} o={0.4} />
        <Dark holes={[{x: 540, y: 1080, rx: 620, ry: 760}]} o={0.3} />
        <path d={stroke(Array.from({length: 25}, (_, i) => {
          const a = Math.PI * (0.06 + 0.88 * (i / 24));
          return {x: 540 - Math.cos(a) * 640, y: 1180 + Math.sin(a) * 400 * -1 + 0};
        }), 2.2, c, 'line')} fill="#476B50" opacity={0.6} />
        <InkRail pts={[{x: -20, y: L.railY}, {x: 540, y: L.railY + 3}, {x: W + 20, y: L.railY - 1}]} w={62} frame={f} seed="b3r" />
        {L.board.map((cd, i) => <InkTableCard key={i} x={cd.x} y={cd.y} s={L.cardS} rot={cd.rot} sq={L.sq} face={BOARD[i]} frame={f} seed={`b3b${i}`} />)}
        {L.loose.map((cd, i) => <InkChipStack key={`l${i}`} x={cd.x} y={cd.y} R={50} n={1} tone={TONE[cd.c]} sq={L.sq} frame={f} seed={`b3l${i}`} />)}
        {L.stacks.slice().sort((a, b) => a.y - b.y).map((cd) => <InkChipStack key={cd.x} x={cd.x} y={cd.y} R={50} n={cd.n} tone={TONE[cd.c]} sq={L.sq} frame={f} seed={`b3s${cd.x}`} />)}
        <InkReachHand x={L.hand.x} y={L.hand.y} s={L.hand.s} r={L.hand.r} frame={f} />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 4 ——
export const B4: React.FC = () => {
  const f = useCurrentFrame();
  const L = L4, s = L.s, T = L.table;
  const rL = nudge(ALLIN, {chest: -0.5 * breath(f)});
  const rR = nudge(THINK, {chest: -0.5 * breath(f + 40)});
  const eL = stillExpr(PUSHER_FACE, f, 'b4l');
  const eR = stillExpr(EXPR.suspect, f, 'b4r');
  const c = {frame: f, seed: 'b4t', px: 1};
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Dark holes={[{x: 540, y: 1050, rx: 560, ry: 560}]} />
        <InkLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} frame={f} />
        <path d={stroke([{x: -10, y: L.G + 2}, {x: 540, y: L.G - 2}, {x: W + 10, y: L.G + 2}], 3, c, 'floor')} fill={INK} opacity={0.6} />
        {/* 绒布在人后面；近沿包边、桌裙、牌和筹码在人前面 */}
        <InkShadow x={540} y={L.G + 4} rx={340} ry={18} />
        <path d={`M ${T.x0 + 40} ${T.far} L ${T.x1 - 40} ${T.far} L ${T.x1} ${T.near} L ${T.x0} ${T.near} Z`} fill={PAPER} />
        <InkFelt pts={[{x: T.x0 + 40, y: T.far}, {x: T.x1 - 40, y: T.far}, {x: T.x1, y: T.near}, {x: T.x0, y: T.near}]} frame={f} seed="b4f" hatch={false} />
        <path d={stroke([{x: T.x0 + 40, y: T.far}, {x: T.x1 - 40, y: T.far}], 2.6, c, 'far')} fill={INK} />
        <InkPerson pose={rL} expr={eL} look={ME} x={L.left} y={L.G} s={s} frame={f} seed="b4l" part="body" weight={0.9} halo={6} />
        <InkPerson pose={rR} expr={eR} look={OTHER} x={L.right} y={L.G} s={s} facing={-1} frame={f} seed="b4r" part="body" weight={0.9} halo={6} />
        <g>
          <path d={`M ${T.x0} ${T.near} L ${T.x1} ${T.near} L ${T.x1} ${T.near + 50} L ${T.x0} ${T.near + 50} Z`} fill={PAPER} />
          <path d={stroke([{x: T.x0 + 20, y: T.near + 48}, {x: T.x1 - 20, y: T.near + 46}], 3, c, 'apron')} fill={INK} />
          <Hatch lines={Array.from({length: 26}, (_, i) => [{x: T.x0 + 30 + i * 27, y: T.near + 24}, {x: T.x0 + 42 + i * 27, y: T.near + 44}] as [P, P])} size={1.8} ctx={c} o={0.45} />
          <path d={stroke([{x: T.x0 + 150, y: T.near + 50}, {x: T.x0 + 160, y: L.G}], 5, c, 'l1')} fill={INK} />
          <path d={stroke([{x: T.x1 - 150, y: T.near + 50}, {x: T.x1 - 160, y: L.G}], 5, c, 'l2')} fill={INK} />
          {L.board.map((cd, i) => <InkTableCard key={i} x={cd.x} y={cd.y} s={L.cardS} rot={i * 3 - 3} sq={0.34} face={BOARD[i]} frame={f} seed={`b4b${i}`} />)}
          {L.theirs.map((cd, i) => <InkChipStack key={`t${i}`} x={cd.x} y={cd.y} R={L.chipR} n={cd.n} tone={TONE[cd.c]} sq={0.34} frame={f} seed={`b4t${i}`} />)}
          {L.push.slice().sort((a, b) => a.y - b.y).map((cd, i) => <InkChipStack key={`p${i}`} x={cd.x} y={cd.y} R={L.chipR} n={cd.n} tone={TONE[cd.c]} sq={0.34} frame={f} seed={`b4p${i}`} />)}
          {L.sliding.map((cd, i) => <InkChipStack key={`sl${i}`} x={cd.x} y={cd.y} R={L.chipR} n={1} tone={TONE[cd.c]} sq={0.34} frame={f} seed={`b4s${i}`} />)}
          {[0, 1, 2].map((i) => <path key={`m${i}`} d={stroke([{x: 655 + i * 6, y: 1205 + i * 32}, {x: 700 + i * 6, y: 1205 + i * 32}], 2.6, c, `mv${i}`)} fill={INK} opacity={0.7} />)}
          <InkRail pts={[{x: T.x0 - 6, y: T.near + 8}, {x: 540, y: T.near + 10}, {x: T.x1 + 6, y: T.near + 7}]} w={30} frame={f} seed="b4r" />
        </g>
        <InkPerson pose={rL} expr={eL} look={ME} x={L.left} y={L.G} s={s} frame={f} seed="b4l" part="arms" weight={0.9} />
        <InkPerson pose={rR} expr={eR} look={OTHER} x={L.right} y={L.G} s={s} facing={-1} frame={f} seed="b4r" part="arms" weight={0.9} />
      </svg>
    </AbsoluteFill>
  );
};

// —— 镜头 5 ——
export const B5: React.FC = () => {
  const f = useCurrentFrame();
  const L = L5, s = L.s;
  const r = nudge(pose('standLook'), {neck: -10, pitch: -0.25, yaw: -0.05, gx: 1, gy: -0.55, chest: -0.6 * breath(f)});
  const e = stillExpr({...EXPR.worry, browIn: 0.6, knit: 0.4, smile: -0.2, lid: 0}, f, 'b5');
  const cards = Array.from({length: UNSEEN}, (_, i) => i).reverse();
  const c = {frame: f, seed: 'b5', px: 1};
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Wash d={`M -50 -50 H ${W + 50} V ${L.horizon} H -50 Z`} o={0.5} blur={30} rough={30} color="#6E665B" />
        <InkFelt pts={[{x: -20, y: L.horizon}, {x: W + 20, y: L.horizon}, {x: W + 20, y: H + 20}, {x: -20, y: H + 20}]} frame={f} seed="b5f" o={0.38} />
        <path d={stroke([{x: -10, y: L.horizon}, {x: 540, y: L.horizon + 2}, {x: W + 10, y: L.horizon - 1}], 2.6, c, 'hor')} fill={INK} opacity={0.6} />
        {cards.map((i) => {
          const cd = rowCard(i);
          const glow = OUTS.includes(i) ? 1 : 0;
          return (
            <g key={i}>
              <InkShadow x={cd.x + 20 * cd.k} y={cd.y + 4 * cd.k} rx={CW * cd.s * 0.6} ry={10 * cd.k} o={0.35} />
              <InkStandingCard x={cd.x} y={cd.y} s={cd.s} glow={glow} frame={f} seed={`b5c${i}`} fade={glow ? 0 : 0.35 * (1 - cd.k)} />
            </g>
          );
        })}
        <InkLamp x={L.person.x + 20} y={330} w={170} top={-20} frame={f} seed="b5l" />
        <InkShadow x={L.person.x + 20} y={L.person.G + 4} rx={110} ry={14} />
        <InkPerson pose={r} expr={e} look={ME} x={L.person.x} y={L.person.G} s={s} frame={f} seed="b5p" weight={0.9} />
      </svg>
    </AbsoluteFill>
  );
};

// —— 5 秒小动作片 ——
export const BMini: React.FC = () => {
  const f = useCurrentFrame();
  const L = L6, s = L.s, G = L.G;
  const r = miniPose(f);
  const e = miniExpr(f);
  const sk = solve(r);
  const hN = hand2screen(L.x, G, s, sk.wN);
  const head = hand2screen(L.x, G, s, sk.head);
  const flip = miniFlip(f);
  const puff = Math.max(miniPuff(f), miniPuff2(f));
  const c = {frame: f, seed: 'b6', px: 1};
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <ContactSheetPaper />
        <Dark holes={[{x: 560, y: 900, rx: 560, ry: 800}]} />
        <InkLamp x={L.lamp.x} y={L.lamp.y} w={L.lamp.w} top={-20} frame={f} />
        <InkPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} frame={f} seed="b6p" part="body" weight={0.75} />
        {/* 呼出的一口气：嘴边一个小卷，往前飘 */}
        {puff > 0.01 && (
          <path d={stroke(Array.from({length: 14}, (_, i) => {
            const t = i / 13, a = t * Math.PI * 3.2;
            return {x: head.x + 110 + (1 - puff) * 40 + t * 60 + Math.cos(a) * 14 * (1 - t * 0.5), y: head.y + 150 + Math.sin(a) * 14 * (1 - t * 0.5) - t * 10};
          }), 3, c, 'puff')} fill={INK} opacity={0.7 * puff} />
        )}
        <NearTable railY={L.railY} f={f} />
        {L.chips.map((cd, i) => <InkChipStack key={i} x={cd.x} y={cd.y} R={52} n={cd.n} tone={TONE[cd.c]} frame={f} seed={`b6c${i}`} />)}
        {L.board.map((cd, i) => (
          <InkTableCard key={i} x={cd.x} y={cd.y} s={L.cardS} rot={cd.rot} face={BOARD[i]} flip={i === 4 ? flip : undefined} frame={f} seed={`b6b${i}`} />
        ))}
        <InkTableCard x={hN.x + L.hole[1].dx} y={hN.y + L.hole[1].dy} s={L.holeS} rot={L.hole[1].rot} face={HOLE[1]} down frame={f} seed="b6h1" />
        <InkTableCard x={hN.x + L.hole[0].dx} y={hN.y + L.hole[0].dy} s={L.holeS} rot={L.hole[0].rot} face={HOLE[0]} down peek={miniPeek(f)} frame={f} seed="b6h0" />
        <InkPerson pose={r} expr={e} look={ME} x={L.x} y={G} s={s} frame={f} seed="b6p" part="arms" weight={0.75} />
      </svg>
    </AbsoluteFill>
  );
};

