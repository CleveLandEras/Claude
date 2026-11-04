// 002 成片：近景。画风 A 的人（FPerson）。你在左，对手在右，面对面，光点在两人之间走；右上方一排 10 个小圆脸是你这一代碰到的 10 个人。
// 每一拍演什么照分镜第四节；时间点全从 timeline.json 的 ev 来（从灰框 Near.tsx 复制过来，只换画法，不动时间）。
// 光：头顶一盏灯（在画面上方外面），一束暖光照在你身上，身后墙上一圈光；对手站在光边上，压暗一点（灯只照你）。
// 灯的冷暖跟着这一代的合作率走：世界冷了，这盏灯也变冷、变暗。
import React from 'react';
import {random} from 'remotion';
import {RPose, mixPose} from '../../../components/people/rig';
import {Expr} from '../../../components/people/face';
import {mixHex} from '../../../components/people/geom';
import {COL, D, FPS, GRABHAND, I, TL, barLen, beat, clamp, ease, easeIn, easeOut, ev, eva, evn, genAt, lerp, muteO, prog, tagText} from '../lib';
import {Bar, EX, FaceDot, GrabHand, Man, POSE, PoseKey, Spark, TPose, Tag, YOU_BG, YOU_FG, exTrack, handAt, headTop, still, tagWidth, track} from './fpeople';
import {mutedCol, warmthAt} from './FCrowd';

export const NL = {G: 1170, s: 3.15, youX: 470, oppX: 1190};
export const OPEN = {G: 1240, s: 3.2, youX: 560, oppX: 1300};
const ROW = (i: number) => ({x: 930 + i * 76, y: 240 + Math.sin((i / 9) * Math.PI) * -6});
const ROW_R = 31;
const FLOOR = 780;
const T = (s: number) => Math.round(s * FPS);
// 刷色用的缓动：比 ease 平（最快处每帧走 1.5/帧数），染色带一帧帧连着往下走，不跳
const smooth = (t: number) => { const x = clamp(t); return x * x * (3 - 2 * x); };
const OPP_DIM = 0.16;

// 灯光的颜色：暖（合作多）↔ 冷（合作少）
export const lampColor = (w: number) => mixHex('#9FB6DA', '#FFD7A0', w);

// —— 背景：暗房间，头顶一盏灯，一束光照着你；身后墙上一圈光；光里飘着几粒灰（接《等待》） ——
export const Room: React.FC<{x: number; o?: number; gen?: number; f?: number; spread?: number}> = ({x, o = 1, gen = 0, f = 0, spread = 1}) => {
  const w = warmthAt(gen);
  const lc = lampColor(w);
  const k = 0.55 + 0.45 * w;
  const dust = Array.from({length: 26}, (_, i) => {
    const sx = x + (random(`dx${i}`) - 0.5) * 520 * spread;
    const sy = ((random(`dy${i}`) * 1100 + f * (0.25 + random(`dv${i}`) * 0.5)) % 1100) - 20;
    const tw = 0.4 + 0.6 * Math.abs(Math.sin(f / 23 + i));
    return <circle key={i} cx={sx + Math.sin(f / 40 + i) * 14} cy={sy} r={1.6 + random(`dr${i}`) * 2.2} fill={lc} opacity={0.35 * tw * k} />;
  });
  return (
    <g opacity={o}>
      <rect width={1920} height={1080} fill="#0D1016" />
      <rect width={1920} height={1080} fill={mixHex('#151922', '#1B1712', w)} opacity={0.9} />
      <ellipse cx={x} cy={560} rx={720 * spread} ry={600} fill="url(#gRoomPool)" opacity={0.85 * k} style={{mixBlendMode: 'screen'}} />
      <ellipse cx={x} cy={560} rx={720 * spread} ry={600} fill={lc} opacity={0.0} />
      <polygon points={`${x - 110 * spread},-40 ${x + 110 * spread},-40 ${x + 470 * spread},1080 ${x - 470 * spread},1080`} fill="url(#gCone)" opacity={0.55 * k}
        filter="url(#fBlur24)" style={{mixBlendMode: 'screen'}} />
      <g style={{mixBlendMode: 'screen'}}>{dust}</g>
      <rect width={1920} height={1080} fill={lc} opacity={0.05} style={{mixBlendMode: 'soft-light'}} />
    </g>
  );
};
export const RoomDefs: React.FC<{gen?: number}> = ({gen = 0}) => {
  const lc = lampColor(warmthAt(gen));
  return (
    <defs>
      <radialGradient id="gRoomPool">
        <stop offset="0" stopColor={mixHex('#3A3128', lc, 0.25)} stopOpacity={1} />
        <stop offset="0.5" stopColor={mixHex('#241F1B', lc, 0.1)} stopOpacity={0.6} />
        <stop offset="1" stopColor="#0D1016" stopOpacity={0} />
      </radialGradient>
      <linearGradient id="gCone" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={lc} stopOpacity={0.5} />
        <stop offset="0.6" stopColor={lc} stopOpacity={0.16} />
        <stop offset="1" stopColor={lc} stopOpacity={0} />
      </linearGradient>
    </defs>
  );
};

// —— 一排 10 个人：带眼睛的小圆脸，和点阵里的人一个样；第五版第二轮：还没讲到的打法（蓝、绿、灰）跟点阵一样压暗、降饱和 ——
export const Row10: React.FC<{opp: number[]; hi?: (i: number) => number; o?: number; pulse?: (i: number) => number; f?: number}> = ({opp, hi, o = 1, pulse, f = 0}) => (
  <g opacity={o}>
    {opp.map((s, i) => {
      const p = ROW(i);
      const h = hi ? hi(i) : 0.4;
      const pu = pulse ? pulse(i) : 0;
      const lid = (Math.floor(f + i * 37) % 97) < 4 ? 1 : 0;
      return (
        <g key={i} opacity={clamp(0.35 + 0.65 * h) * muteO(f, s)}>
          {h > 0.7 && <circle cx={p.x} cy={p.y} r={ROW_R + 10} fill="none" stroke="#FFF6E6" strokeWidth={4} opacity={0.85} />}
          <FaceDot x={p.x} y={p.y} r={ROW_R * (1 + 0.22 * pu)} color={mutedCol(f, s)} lid={lid} gx={-0.6} gy={0.5} />
        </g>
      );
    })}
  </g>
);

// —— 光点的几种走法 ——
type Pt = {x: number; y: number};
type Act = {t: number; kind: 'give' | 'back' | 'grab' | 'myGrab' | 'slipMe' | 'slipOpp' | 'warm' | 'toRow' | 'fromRow' | 'rowGrab'; k?: number; d?: number};
const arc = (a: Pt, b: Pt, u: number, h = 60) => ({x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) - Math.sin(u * Math.PI) * h});

// 落地的光点：在地上轻轻跳着亮，下面一块软影；落地那一下闪一圈白光、溅出十道光线
const Dropped: React.FC<{x: number; k: number}> = ({x, k}) => {
  const bounce = k < 0.9 ? Math.abs(Math.sin(k * Math.PI / 0.9)) * 26 * (1 - k / 0.9) : 0;
  const pulse = 1 + 0.08 * Math.sin(k * 2.2);
  return (
    <g>
      <Spark x={x} y={FLOOR - bounce} r={38 * pulse} ground={FLOOR + 30} />
      {k < 0.9 && (() => {
        const q = k / 0.9;
        return (
          <g opacity={1 - q}>
            <circle cx={x} cy={FLOOR} r={50 + 170 * q} fill="none" stroke="#FFF4DE" strokeWidth={10 * (1 - q) + 2} />
            <circle cx={x} cy={FLOOR} r={60 * (1 - q) + 30} fill="#FFF6E6" opacity={0.6} filter="url(#fBlur8)" />
            {Array.from({length: 10}, (_, j) => {
              const an = (j / 10) * Math.PI * 2 + 0.3;
              const r0 = 70 + 70 * q, r1 = 110 + 150 * q;
              return <line key={j} x1={x + Math.cos(an) * r0} y1={FLOOR + Math.sin(an) * r0 * 0.8} x2={x + Math.cos(an) * r1} y2={FLOOR + Math.sin(an) * r1 * 0.8}
                stroke="#FFF1D6" strokeWidth={7} strokeLinecap="round" />;
            })}
          </g>
        );
      })()}
    </g>
  );
};

const Acts: React.FC<{f: number; acts: Act[]; me: Pt; opp: Pt; until: number}> = ({f, acts, me, opp, until}) => {
  const out: React.ReactNode[] = [];
  acts.forEach((a, i) => {
    const d = a.d ?? 8;
    const u = (f - a.t) / d;
    const key = `${a.kind}${i}`;
    if (a.kind === 'slipMe' || a.kind === 'slipOpp') {
      if (u < 0 || f >= until) return;
      const from = a.kind === 'slipMe' ? me : opp;
      const dir = a.kind === 'slipMe' ? 1 : -1;
      const fall = clamp(u / 1.2);
      const x = from.x + dir * 120 * easeOut(fall), y = lerp(from.y, FLOOR, easeIn(fall));
      if (fall < 1) {
        out.push(<Spark key={key} x={x} y={y} r={44} ground={FLOOR + 30} />);
        return;
      }
      out.push(<Dropped key={key} x={x} k={u - 1.2} />);
      return;
    }
    if (u < 0 || u > 1.35) return;
    const fade = u > 1 ? 1 - (u - 1) / 0.35 : 1;
    if (a.kind === 'give' || a.kind === 'back' || a.kind === 'warm' || a.kind === 'toRow' || a.kind === 'fromRow') {
      const A = a.kind === 'give' || a.kind === 'toRow' ? me : a.kind === 'fromRow' ? ROW(a.k!) : opp;
      const B = a.kind === 'toRow' ? ROW(a.k!) : a.kind === 'give' ? opp : me;
      const p = arc(A, B, ease(Math.min(1, u)), a.kind === 'toRow' || a.kind === 'fromRow' ? 30 : 70);
      const small = a.kind === 'toRow' || a.kind === 'fromRow';
      // 第四版：S06 压到 0.8 秒，递出去的光点放大到 26（原来 20），递回来的小一号、淡一点，先读出“你在给”
      const sr = a.kind === 'warm' ? 44 : a.kind === 'toRow' ? 26 : small ? 18 : 32;
      out.push(<Spark key={key} x={p.x} y={p.y} r={sr} o={fade * (a.kind === 'fromRow' ? 0.85 : 1)} warm={a.kind === 'warm' ? 1 : 0} />);
      return;
    }
    // 抢：一只橙红的手张开五指伸过来，攥住光点，连手带光点拿回去
    const own = a.kind === 'grab' || a.kind === 'rowGrab' ? opp : me;
    const target = a.kind === 'grab' || a.kind === 'rowGrab' ? me : opp;
    const home = a.kind === 'rowGrab' ? ROW(a.k!) : own;
    const meet = a.kind === 'rowGrab' ? {x: lerp(target.x, home.x, 0.25), y: lerp(target.y, home.y, 0.25)} : target;
    const dirIn = Math.atan2(meet.y - home.y, meet.x - home.x) * 180 / Math.PI;
    const r = a.kind === 'rowGrab' ? 30 : 32;
    if (u <= 0.45) {
      const q = u / 0.45;
      const p = arc(home, meet, easeOut(q), 20);
      const sp = a.kind === 'rowGrab' ? {x: lerp(target.x, meet.x, q), y: lerp(target.y, meet.y, q)} : target;
      out.push(<Spark key={`${key}s`} x={sp.x} y={sp.y} r={32} />);
      out.push(<GrabHand key={key} x={p.x - Math.cos(dirIn * Math.PI / 180) * r * 0.4} y={p.y - Math.sin(dirIn * Math.PI / 180) * r * 0.4} r={r} dir={dirIn}
        close={clamp((q - 0.75) / 0.25)} trail={1 - q * 0.5} sleeve={0.9} />);
    } else {
      const p = arc(meet, home, ease(Math.min(1, (u - 0.45) / 0.55)), 20);
      out.push(<Spark key={`${key}s`} x={p.x} y={p.y} r={30} o={fade} glow={0.6} />);
      out.push(<GrabHand key={key} x={p.x - Math.cos(dirIn * Math.PI / 180) * r * 0.3} y={p.y - Math.sin(dirIn * Math.PI / 180) * r * 0.3} r={r} o={fade} dir={dirIn} close={1} sleeve={0.9} />);
    }
  });
  return <>{out}</>;
};

// 两根条并排比长短（左对齐，上下叠），左边各一个小圆脸认人。
// 第五版：去掉条右端的分数（第四版加的）：字幕只说“他过得比你好”，条本身就是“过得好不好”，不再讲分数这条游戏规则
const CMP = {x: 600, y: 248, gap: 74, full: 560, h: 56};
const Compare: React.FC<{a: number; ca: string; b: number; cb: string; o: number; x?: number; y?: number}> = ({a, ca, b, cb, o, x = CMP.x, y = CMP.y}) => (
  <g opacity={o}>
    <FaceDot x={x - 50} y={y} r={26} color={ca} gx={0.8} />
    <Bar x={x} y={y} len={barLen(a, CMP.full) * ease(o)} full={CMP.full} h={CMP.h} color={ca} align="left" />
    <FaceDot x={x - 50} y={y + CMP.gap} r={26} color={cb} gx={0.8} />
    <Bar x={x} y={y + CMP.gap} len={barLen(b, CMP.full) * ease(o)} full={CMP.full} h={CMP.h} color={cb} align="left" />
  </g>
);

type Who = {strategy: number; pose: RPose | TPose; expr: Expr; x: number; o?: number; recolor?: {to: number; p: number}; seed?: string; facing?: 1 | -1; dim?: number; noBlink?: number[][]};

const Pair: React.FC<{f: number; me: Who; opp?: Who; L?: typeof NL; gen?: number}> = ({f, me, opp, L = NL, gen = 0}) => {
  const lc = lampColor(warmthAt(gen));
  return (
    <>
      <Man f={f} pose={me.pose} expr={me.expr} strategy={me.strategy} who="me" x={me.x} G={L.G} s={L.s} opacity={me.o} recolor={me.recolor} seed="me"
        tint={{color: lc, amount: 0.08}} dim={me.dim ?? 0} noBlink={me.noBlink ?? HOLD} />
      {opp && (opp.o ?? 1) > 0.01 && (
        <Man f={f} pose={opp.pose} expr={opp.expr} strategy={opp.strategy} who="other" x={opp.x} G={L.G} s={L.s} facing={opp.facing ?? -1}
          opacity={opp.o} recolor={opp.recolor} seed={opp.seed ?? 'opp'} dim={opp.dim ?? OPP_DIM} tint={{color: lc, amount: 0.04}} noBlink={opp.noBlink ?? HOLD} />
      )}
    </>
  );
};

// 愣住、嘴角翘的那几段不自动眨眼（三处手滑后的愣住、你比 99% 的人分高）
const HOLD: number[][] = [
  [eva('S09', 'stun')[0] - 2, eva('S09', 'stun')[1] + 8], [eva('S12', 'stun')[0] - 2, eva('S12', 'stun')[1] + 8],
  [eva('S13', 'smirk')[0], beat('S13').f1], [eva('S20', 'stun')[0] - 2, eva('S20', 'stun')[1] + 8],
];
const youTag = (o = 1) => <Tag x={215} y={470} text="你" bg={YOU_BG} fg={YOU_FG} size={88} o={o} point="none" tilt={-2} />;
// 第五版：人身上的标签统一用 lib 的 tagText（骗子“狠·只拿不给”、记仇“狠·记一辈子”、有来有往、会原谅、老实人）。
// 对面那个人的标签挂在他后脑勺那一侧（x 1460）；“狠·记一辈子”排成两行（上“狠”、下“记一辈子”），牌子宽约 290 px，
// 和第四版“记仇”两个字差不多宽，不往左压到他的脸，右沿也不过 x 1680（右下角留给平台按钮）
const TAG_RIGHT = 1680;
const oppTag = (s: number, o = 1, y = 470) => {
  const text = tagText(s);
  return <Tag x={NL.oppX + 270} y={y} text={text} bg={COL[s]} size={80} o={o} point="none" tilt={2} pop={ease(clamp(o * 1.4))} stack />;
};
const rowLabel = (opp: number[], s: number, o: number) => {
  const xs = opp.map((v, i) => (v === s ? ROW(i).x : null)).filter((v) => v !== null) as number[];
  if (!xs.length) return null;
  const text = tagText(s);
  const W = tagWidth(text, 80) + 80 * 0.66;
  const cx = clamp((Math.min(...xs) + Math.max(...xs)) / 2, 1130, Math.min(1500, TAG_RIGHT - W / 2 - 6));
  return <Tag x={cx} y={340} text={text} bg={COL[s]} size={80} o={o} tilt={-1} pop={ease(clamp(o * 1.4))} />;
};
// 你头顶的分数条（第五版去掉左边的“分”字：条就是“过得好不好”）
const headBar = (r: RPose, x: number, facing: 1 | -1, len: number, color = '#F1EBDD', glow = 0, o = 1, dy = 0, shine?: number) => {
  const h = headTop(r, x, NL.G, NL.s, facing);
  const by = h.y - 46 + dy;
  return <Bar x={h.x} y={by} len={len} color={color} glow={glow} o={o} h={56} shine={shine} />;
};

// —— 第 0 秒：你把光点递出去，骗子一把抢走 ——
export const NearOpen: React.FC<{f: number; o?: number; scale?: number; tf?: string; noRoom?: boolean}> = ({f, o = 1, scale = 1, tf, noRoom}) => {
  const L = OPEN;
  const [r0, r1] = eva('S01', 'reachIn');
  const [g0, g1] = eva('S01', 'grab');
  const [ta0, ta1] = eva('S01', 'turnAway');
  // 你：一直递着；被抢以后手还空伸着，脸先愣住，再发愁
  const myPose = f < g1 + 6 ? POSE.give : track(f, [[g1 + 6, 'give'], [g1 + 30, mixPose(POSE.give, POSE.hunch, 0.35)]]);
  const myE = exTrack(f, [[0, 'calm'], [evn('S01', 'blank') - 3, 'calm'], [evn('S01', 'blank') + 2, 'stun'], [eva('S01', 'worry')[0] + 2, 'stun'], [eva('S01', 'worry')[1], 'worry']]);
  const turned = f >= (ta0 + ta1) / 2;
  const half = mixPose(POSE.idle, POSE.reach, 0.78);
  const oppPose0 = turned ? track(f, [[ta0, 'pull'], [ta1, 'idle']]) : track(f, [[r0, half], [r1, 'reach'], [g0, 'reach'], [g1, 'pull']]);
  // 抢的那只手用橙红画（只有“抢”用这个颜色）；这时候他自己的手不画
  const grabbing = !turned;
  const oppPose = grabbing ? {...oppPose0, hN: 'pocket' as const} : {...oppPose0, hN: 'fist' as const};
  const oppX = OPEN.oppX + (turned ? 70 * ease(prog(f, [ta0, ta1 + 6])) : 0);
  const facing: 1 | -1 = turned ? 1 : -1;
  const myHands = {x: (handAt(myPose, L.youX, L.G, L.s, 1, true).x + handAt(myPose, L.youX, L.G, L.s, 1, false).x) / 2 + 6, y: handAt(myPose, L.youX, L.G, L.s, 1, true).y - 22};
  const oppHand = handAt(oppPose, oppX, L.G, L.s, facing);
  const gp = ease(prog(f, [g0, g1]));
  const sp = f < g0 ? myHands : grabbing ? {x: lerp(myHands.x, oppHand.x - 10, gp), y: lerp(myHands.y, oppHand.y, gp)} : {x: oppHand.x + 8, y: oppHand.y - 6};
  const hd = headTop(POSE.give, L.youX, L.G, L.s, 1);
  const ohd = headTop(POSE.reach, OPEN.oppX, L.G, L.s, -1);
  const close = clamp((f - (g0 - 3)) / 6);
  const t = tf ?? `translate(${L.youX} ${700}) scale(${scale}) translate(${-L.youX} ${-700})`;
  return (
    <g opacity={o} transform={t}>
      {!noRoom && <Room x={L.youX} f={f} />}
      <Man f={f} pose={myPose} expr={myE} strategy={I.ALLC} who="me" x={L.youX} G={L.G} s={L.s} seed="me" tint={{color: lampColor(1), amount: 0.08}} noBlink={[[0, 60]]} />
      <Man f={f} pose={oppPose} expr={turned ? EX.smirk : EX.cold} strategy={I.ALLD} who="other" x={oppX} G={L.G} s={L.s} facing={facing} seed="sw" dim={0.08} />
      {!turned && <Spark x={sp.x} y={sp.y} r={34} />}
      {grabbing && <GrabHand x={oppHand.x} y={oppHand.y} r={34} dir={180 + (1 - close) * 8} close={close} sleeve={0} trail={f < g0 ? 0.6 : 0} />}
      {turned && <Spark x={sp.x} y={sp.y} r={30} glow={0.7} />}
      <Tag x={hd.x} y={hd.y - 66} text="你 · 老实人" bg={YOU_BG} fg={YOU_FG} size={88} tilt={-1.5} />
      {/* 第五版：对面那个人只写“狠”（“你 · 老实人”不变） */}
      <Tag x={ohd.x + 10} y={ohd.y - 60} text="狠" bg={COL[I.ALLD]} size={80} tilt={2} />
    </g>
  );
};

// —— 近景各拍 ——
export const NearBeat: React.FC<{f: number; id: string}> = ({f, id}) => {
  const b = beat(id);
  const gen = genAt(f);
  const you = D.you;
  const meX = NL.youX, opX = NL.oppX;
  const myHand = (r: RPose) => handAt(r, meX, NL.G, NL.s, 1);
  const opHand = (r: RPose, x = opX) => handAt(r, x, NL.G, NL.s, -1);

  if (id === 'S06') {
    // 你对谁都好：给一排 10 个人挨个递光点；老实人那边也递回来，你的条变长
    // 第四版压到 0.8 秒：一排固定成第 4 代碰到的那 10 个人（S07 抢你的 4 个骗子就在里面），不再每代换一排，免得 0.8 秒里换 4 次色
    const [g0, g1] = eva(id, 'gives');
    const opp = you[4].opp;
    const acts: Act[] = [];
    let returns = 0;
    for (let i = 0; i < 10; i++) {
      const t = Math.round(lerp(g0, g1 - 8, i / 9));
      acts.push({t, kind: 'toRow', k: i, d: 7});
      const s = opp[i];
      if (s !== I.ALLD) {
        acts.push({t: t + 7, kind: 'fromRow', k: i, d: 7});
        if (f >= t + 14) returns++;
      }
    }
    const r = POSE.give;
    const len = barLen(you[gen].sc) * clamp(0.25 + returns / 8);
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={opp} hi={() => 0.75} pulse={(i) => acts.some((a) => a.kind === 'toRow' && a.k === i && f >= a.t + 7 && f < a.t + 11) ? 1 : 0} />
        <Pair f={f} gen={gen} me={{strategy: I.ALLC, pose: r, expr: EX.calm, x: meX}} />
        {headBar(r, meX, 1, len)}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(r)} opp={myHand(r)} until={b.f1} />
      </>
    );
  }

  if (id === 'S07') {
    // 可总有人只拿，不给：4 个橙点亮起，4 只橙红的手伸下来抢，你的条一截截往下掉，你缩起肩
    const opp = you[4].opp;
    const hiT = evn(id, 'highlight');
    const grabs = eva(id, 'grabs');
    const orange = opp.map((s, i) => (s === I.ALLD ? i : -1)).filter((i) => i >= 0);
    const acts: Act[] = grabs.map((t, j) => ({t, kind: 'rowGrab', k: orange[j % orange.length], d: 9}));
    const done = grabs.filter((t) => f >= t + 9).length;
    const r = track(f, [[eva(id, 'shrink')[0], 'give'], [eva(id, 'shrink')[1], 'hunch']]);
    const e = exTrack(f, [[b.f0, 'calm'], [grabs[0] + 4, 'worry'], [grabs[3], 'sad']]);
    const len = lerp(barLen(you[3].sc), barLen(you[4].sc), done / 4);
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={opp} hi={(i) => (f >= hiT && opp[i] === I.ALLD ? 1 : 0.15)} />
        {rowLabel(opp, I.ALLD, prog(f, [evn(id, 'label'), evn(id, 'label') + 5]))}
        <Pair f={f} gen={gen} me={{strategy: I.ALLC, pose: r, expr: e, x: meX}} />
        {headBar(r, meX, 1, len)}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(POSE.give)} opp={myHand(POSE.give)} until={b.f1} />
      </>
    );
  }

  if (id === 'S08') {
    // 谁都会手滑：特写你的手，连着递 20 次，第 14 次（slipIndex）滑掉落地
    // 第七版追加：第六稿把这一拍压到 0.9 秒，原来第 14 颗 329.4 帧出手、9 帧后落地，落地闪光在 339 帧切走前露不到 1 帧。
    // 拍的起止、gives 的起止都不动，只在 gives 里重新排：滑掉的那颗在 SLIP_AT = 拍尾 − 7（落地闪露 7 帧）− 7（下落 7 帧）出手，
    // 前 13 颗均匀排在 gives 起点到 SLIP_AT 之间，后 6 颗均匀排在 SLIP_AT 到 gives 终点之间（音效照同一个公式：giveAt / SLIP_AT / 落地 = SLIP_AT + 7）
    const r = POSE.give;
    const h = myHand(r);
    const z = 1 + 1.3 * ease(prog(f, eva(id, 'zoomIn'))) - 1.3 * ease(prog(f, eva(id, 'zoomOut')));
    const [g0, g1] = eva(id, 'gives');
    const slip = ev(id, 'slipIndex') as number;
    const FALL = 7, FLASH = 9;
    // 特写放大 2.3 倍：原来的地面 y 780 会落到画面 y 约 920，压在字幕带的暗处、闪光圈还出画。这一拍的“地”抬到放大后画面 y 790（字幕带上沿附近），
    // 闪光的圈按 1/1.6 缩回来（比别处的落地闪大一点，是特写）
    const ZMAX = 2.3;
    const landY = h.y + (790 - h.y) / ZMAX;
    const fk = 1 / 1.6;
    const slipAt = Math.min(lerp(g0, g1, slip / 19), b.f1 - 7 - FALL);
    const giveAt = (i: number) => (i <= slip ? lerp(g0, slipAt, i / slip) : lerp(slipAt, g1, (i - slip) / (19 - slip)));
    const acts: React.ReactNode[] = [];
    for (let i = 0; i < 20; i++) {
      const t = giveAt(i);
      const u = (f - t) / 6;
      if (u < 0) continue;
      if (i === slip) {
        const fall = clamp((f - t) / FALL);
        const y = lerp(h.y, landY, easeIn(fall));
        acts.push(<Spark key={i} x={h.x + 60 * fall} y={y} r={fall >= 1 ? 30 : 34} ground={landY + 14} />);
        const q = (f - t - FALL) / FLASH;
        if (q >= 0 && q < 1) {
          acts.push(
            <g key={`${i}f`} opacity={1 - q}>
              <circle cx={h.x + 60} cy={landY} r={(50 + 170 * q) * fk} fill="none" stroke="#FFF4DE" strokeWidth={8 * fk} />
              <circle cx={h.x + 60} cy={landY} r={(60 * (1 - q) + 30) * fk} fill="#FFF6E6" opacity={0.75} filter="url(#fBlur8)" />
              {Array.from({length: 10}, (_, j) => {
                const an = (j / 10) * Math.PI * 2 + 0.3;
                const r0 = (70 + 70 * q) * fk, r1 = (110 + 150 * q) * fk;
                return <line key={j} x1={h.x + 60 + Math.cos(an) * r0} y1={landY + Math.sin(an) * r0 * 0.8} x2={h.x + 60 + Math.cos(an) * r1}
                  y2={landY + Math.sin(an) * r1 * 0.8} stroke="#FFF1D6" strokeWidth={6 * fk} strokeLinecap="round" />;
              })}
            </g>,
          );
        }
      } else if (u < 1) {
        acts.push(<Spark key={i} x={h.x + 520 * easeOut(u)} y={h.y - 30 * Math.sin(u * Math.PI)} r={32} o={1 - u * 0.6} />);
      }
    }
    const e = exTrack(f, [[b.f0, 'calm'], [slipAt + 4, 'calm'], [slipAt + 8, 'surprise']]);
    return (
      <g transform={`translate(${h.x} ${h.y}) scale(${z}) translate(${-h.x} ${-h.y})`}>
        <Room x={meX} gen={gen} f={f} />
        <Pair f={f} gen={gen} me={{strategy: I.ALLC, pose: r, expr: e, x: meX}} />
        {headBar(r, meX, 1, barLen(you[4].sc))}
        {youTag()}
        {acts}
      </g>
    );
  }

  if (id === 'S09') {
    // 你手滑一次，记仇的人就再也不对你好：粉点走下来变成粉衣人；你滑掉一颗，他抱起胳膊，之后你每递一次他都抢
    const opp = you[4].opp;
    const pickI = opp.indexOf(I.GRIM);
    const [w0, w1] = eva(id, 'walkDown');
    const wp = ease(prog(f, [w0, w1]));
    const [c0, c1] = eva(id, 'crossArms');
    const [st0, st1] = eva(id, 'stun');
    const opR = track(f, [[st0, 'idle'], [st0 + 4, 'startle'], [c0, 'startle'], [c1, 'cross']]);
    const opE = exTrack(f, [[st0 - 1, 'calm'], [st0 + 3, 'stun'], [st1, 'stun'], [c1, 'angry'], [c1 + 14, 'cold']]);
    const slip = evn(id, 'slip');
    const myR = POSE.give;
    const acts: Act[] = [
      {t: evn(id, 'giveOk'), kind: 'give', d: 7}, {t: evn(id, 'giveOk') + 6, kind: 'back', d: 7},
      {t: slip, kind: 'slipMe'},
      ...eva(id, 'grabs').map((t) => ({t, kind: 'grab', d: 9} as Act)),
    ];
    const myE = exTrack(f, [[b.f0, 'calm'], [slip + 2, 'calm'], [slip + 6, 'worry'], [eva(id, 'grabs')[1], 'sad']]);
    const start = ROW(pickI);
    const oh = headTop(POSE.idle, opX, NL.G, NL.s, -1);
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={opp} hi={(i) => (i === pickI ? 1 : 0.15)} />
        {wp < 1 && <circle cx={lerp(start.x, oh.x, wp)} cy={lerp(start.y, oh.y + 150, wp)} r={lerp(ROW_R, 90, wp)} fill={COL[I.GRIM]} opacity={1 - wp * 0.6} />}
        <Pair f={f} gen={gen} me={{strategy: I.ALLC, pose: myR, expr: myE, x: meX}}
          opp={{strategy: I.GRIM, pose: opR, expr: opE, x: opX, o: wp}} />
        {oppTag(I.GRIM, prog(f, [evn(id, 'label'), evn(id, 'label') + 5]))}
        {headBar(myR, meX, 1, barLen(you[4].sc))}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(myR)} opp={opHand(POSE.reach)} until={b.f1} />
      </>
    );
  }

  if (id === 'S10') {
    // 坑人的分比你高。你学了他：转头看另一个粉衣人，两根条并排，他的长一倍多；你的连帽衫从上往下刷成粉
    const sw = ease(prog(f, eva(id, 'other')));
    const myR = track(f, [[eva(id, 'turnHead')[0], 'give'], [eva(id, 'turnHead')[1], 'lookUp']]);
    const bars = prog(f, [evn(id, 'bars'), evn(id, 'bars') + 9]);
    const rc = smooth(prog(f, eva(id, 'recolor')));
    const look = you[4].look!;
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={you[4].opp} o={0.6 * (1 - bars)} />
        <Pair f={f} gen={gen} me={{strategy: I.ALLC, pose: myR, expr: exTrack(f, [[b.f0, 'sad'], [evn(id, 'bars') + 10, 'blank']]), x: meX, recolor: {to: I.GRIM, p: rc}}}
          opp={{strategy: I.GRIM, pose: still('cross'), expr: EX.cold, x: opX, o: 1 - sw}} />
        <Man f={f} pose={POSE.idle} expr={EX.smile} strategy={I.GRIM} who="other" x={opX + 20} G={NL.G} s={NL.s} facing={-1} opacity={sw} seed="look4" />
        {oppTag(I.GRIM, sw)}
        <Compare a={you[4].sc} ca={COL[I.ALLC]} b={look} cb={COL[I.GRIM]} o={bars} />
        {bars < 0.05 && headBar(POSE.give, meX, 1, barLen(you[4].sc))}
        {youTag()}
      </>
    );
  }

  if (id === 'S12' || id === 'S13') {
    // 后来，老实人一手滑，你也一直坑他：镜像 S09。他滑掉一颗，你抱起胳膊，一直抢；光点往你这边堆
    // 这一代，你比 99% 的人分高：你的条一路伸长、发亮，嘴角一边翘起来
    const s12 = beat('S12');
    const slip = evn('S12', 'slip');
    const [c0, c1] = eva('S12', 'crossArms');
    const st12 = eva('S12', 'stun');
    const myR = track(f, [[s12.f0, 'give'], [st12[0], 'give'], [st12[0] + 4, 'startle'], [c0, 'startle'], [c1, 'cross']]);
    const grabs = eva('S12', 'grabs');
    const acts: Act[] = [
      {t: evn('S12', 'giveOk'), kind: 'give', d: 7}, {t: evn('S12', 'giveOk') + 6, kind: 'back', d: 7},
      {t: slip, kind: 'slipOpp'},
      ...grabs.map((t) => ({t, kind: 'myGrab', d: 9} as Act)),
    ];
    const pile = grabs.filter((t) => f >= t + 9).length;
    const grow = id === 'S13' ? ease(prog(f, eva('S13', 'grow'))) : 0;
    const len = lerp(barLen(you[6].sc), barLen(you[7].sc) * 0.82, pile / 4) + grow * (barLen(you[7].sc) - barLen(you[7].sc) * 0.82);
    const myE = id === 'S13'
      ? exTrack(f, [[eva('S13', 'smirk')[0], 'cold'], [eva('S13', 'smirk')[1], 'smirk']])
      : exTrack(f, [[s12.f0, 'calm'], [eva('S12', 'stun')[0] - 1, 'calm'], [eva('S12', 'stun')[0] + 3, 'stun'], [eva('S12', 'stun')[1], 'stun'], [c1, 'angry'], [c1 + 12, 'cold']]);
    const opE = exTrack(f, [[s12.f0, 'calm'], [grabs[0], 'calm'], [grabs[1], 'worry'], [grabs[3], 'sad']]);
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={you[7].opp} o={0.6} />
        <Pair f={f} gen={gen} me={{strategy: I.GRIM, pose: myR, expr: myE, x: meX}}
          opp={{strategy: I.ALLC, pose: POSE.give, expr: opE, x: opX}} />
        {oppTag(I.ALLC)}
        {/* 你比 99% 的人分高：条长到头以后一直发亮，一道光从左往右扫过去（每 0.6 秒一次） */}
        {headBar(POSE.give, meX, 1, len, '#F1EBDD', id === 'S13' ? grow * (0.8 + 0.2 * Math.sin(f / 4)) : 0, 1, 0,
          id === 'S13' && grow >= 1 ? ((f - eva('S13', 'grow')[1]) % 18) / 18 : undefined)}
        {youTag()}
        {Array.from({length: pile}, (_, i) => <Spark key={`p${i}`} x={meX - 205 + (i % 2) * 62 + (i === 3 ? 30 : 0)} y={i < 2 ? 752 : 704 - (i % 2) * 8} r={27} ground={i < 2 ? 780 : undefined} glow={0.7} />)}
        <Acts f={f} acts={acts} me={myHand(POSE.give)} opp={opHand(POSE.give)} until={beat('S13').f1} />
      </>
    );
  }

  if (id === 'S18') {
    // 身边的人渐渐成了以牙还牙，你又学了：一排变蓝；一个蓝衣人走下来，你递他就递，你抢他下一步就抢；看他的条比你长，你粉→蓝
    const opp = you[gen].opp;
    const [w0, w1] = eva(id, 'walkDown');
    const wp = ease(prog(f, [w0, w1]));
    const pickI = Math.max(0, you[108].opp.indexOf(I.TFT));
    const start = ROW(pickI);
    const oh = headTop(POSE.idle, opX, NL.G, NL.s, -1);
    const acts: Act[] = [
      {t: evn(id, 'give'), kind: 'give', d: 6}, {t: evn(id, 'giveBack'), kind: 'back', d: 6},
      {t: evn(id, 'grab'), kind: 'myGrab', d: 7}, {t: evn(id, 'grabBack'), kind: 'grab', d: 7},
    ];
    const myR = track(f, [[eva(id, 'turnHead')[0], 'give'], [eva(id, 'turnHead')[1], 'lookUp']]);
    const bars = prog(f, [evn(id, 'bars'), evn(id, 'bars') + 6]);
    const rc = smooth(prog(f, eva(id, 'recolor')));
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={opp} hi={(i) => (opp[i] === I.TFT && f >= evn(id, 'label') ? 0.9 : 0.15)} o={1 - bars} />
        {rowLabel(you[108].opp, I.TFT, prog(f, [evn(id, 'label'), evn(id, 'label') + 4]) * (1 - prog(f, [w0, w0 + 4])))}
        {wp > 0 && wp < 1 && <circle cx={lerp(start.x, oh.x, wp)} cy={lerp(start.y, oh.y + 150, wp)} r={lerp(ROW_R, 90, wp)} fill={COL[I.TFT]} opacity={1 - wp * 0.6} />}
        <Pair f={f} gen={gen} me={{strategy: I.GRIM, pose: myR, expr: exTrack(f, [[b.f0, 'cold'], [evn(id, 'bars'), 'blank']]), x: meX, recolor: {to: I.TFT, p: rc}}}
          opp={{strategy: I.TFT, pose: POSE.give, expr: EX.calm, x: opX, o: wp}} />
        {oppTag(I.TFT, wp)}
        <Compare a={you[108].sc} ca={COL[I.GRIM]} b={you[108].look!} cb={COL[I.TFT]} o={bars} />
        {bars < 0.05 && headBar(POSE.give, meX, 1, barLen(you[gen].sc))}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(POSE.give)} opp={opHand(POSE.give)} until={b.f1} />
      </>
    );
  }

  if (id === 'S20' || id === 'S21') {
    // 可手滑，一直都在：你和一个蓝衣人面对面，你手里的光点“啪”地掉了
    // 一来一回，没完没了：一道橙红的“抢”在两人之间来回；两人的脸越来越僵（第四版去掉了中间那排 10 格）
    const slip = evn('S20', 'slip');
    const acts: Act[] = [{t: slip, kind: 'slipMe'}];
    const [p0, p1] = eva('S21', 'pong');
    const stiff = prog(f, [p0, p1]);
    const myE = exTrack(f, [[beat('S20').f0, 'calm'], [slip + 3, 'surprise'], [p0, 'blank'], [p1, 'stiff']]);
    const [st0, st1] = eva('S20', 'stun');
    const opE = exTrack(f, [[beat('S20').f0, 'calm'], [st0 - 1, 'calm'], [st0 + 3, 'stun'], [st1, 'stun'], [st1 + 8, 'angry'], [p1, 'stiff']]);
    const opR = track(f, [[st0, 'give'], [st0 + 4, 'startle'], [st1, 'startle'], [st1 + 10, 'give']]);
    const me = myHand(POSE.give), op = opHand(POSE.give);
    let pong: React.ReactNode = null;
    if (f >= p0 && f < p1) {
      const per = T(0.4);
      const k = (f - p0) / per;
      const leg = Math.floor(k);
      const u = k - leg;
      const A = leg % 2 === 0 ? me : op, B = leg % 2 === 0 ? op : me;
      const pnt = arc(A, B, ease(u), 40);
      const back = arc(A, B, ease(Math.max(0, u - 0.12)), 40);
      pong = (
        <g>
          <line x1={back.x} y1={back.y} x2={pnt.x} y2={pnt.y} stroke={GRABHAND} strokeWidth={14} strokeLinecap="round" opacity={0.45} />
          <GrabHand x={pnt.x} y={pnt.y} r={30} dir={leg % 2 === 0 ? 0 : 180} close={clamp((u - 0.7) / 0.3)} trail={0.8} sleeve={0.9} />
        </g>
      );
    }
    // 第四版：S21 不再画那排 10 格；头顶的条接着 S20 画（同一根、同一个长度口径），一来一回时上下抖、原地不涨，乒乓停了抖也停，接上 S22
    const wob = id === 'S21' ? Math.sin((f - p0) / 3) * 22 * stiff * (1 - prog(f, [p1 - 6, p1])) : 0;
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Pair f={f} gen={gen} me={{strategy: I.TFT, pose: POSE.give, expr: myE, x: meX}}
          opp={{strategy: I.TFT, pose: opR, expr: opE, x: opX}} />
        {oppTag(I.TFT)}
        {id === 'S20' && headBar(POSE.give, meX, 1, barLen(you[140].sc))}
        {id === 'S21' && headBar(POSE.give, meX, 1, barLen(you[gen].sc) + wob)}
        {youTag()}
        <Acts f={f} acts={acts} me={me} opp={op} until={beat('S21').f1} />
        {pong}
      </>
    );
  }

  if (id === 'S22' || id === 'S23') {
    // 会原谅的人：会还手，也会先停手。一排冒出绿点，标“会原谅”；绿衣人被抢三次，前两次抢回去，第三次照样递出暖光点
    // 他们的分最高。你也学会了原谅：转头看他，两根条他的长；你蓝→绿；下一代飞向你的“抢”稀了一半多
    const s22 = beat('S22');
    const opp = you[gen].opp;
    const [w0, w1] = eva('S22', 'walkDown');
    const wp = ease(prog(f, [w0, w1]));
    const grabs = eva('S22', 'grabs'), backs = eva('S22', 'grabBacks');
    const acts: Act[] = [
      ...grabs.map((t) => ({t, kind: 'myGrab', d: 6} as Act)),
      ...backs.map((t) => ({t, kind: 'grab', d: 6} as Act)),
      {t: evn('S22', 'warm'), kind: 'warm', d: 8},
      {t: evn('S22', 'giveBack'), kind: 'give', d: 7},
    ];
    const pa = eva('S22', 'pause');
    const myE = id === 'S22'
      ? exTrack(f, [[s22.f0, 'stiff'], [pa[0], 'stiff'], [pa[0] + 3, 'surprise'], [pa[1] + 4, 'calm']])
      : exTrack(f, [[beat('S23').f0, 'calm'], [eva('S23', 'relief')[0], 'calm'], [eva('S23', 'relief')[1], 'relief']]);
    const myR = id === 'S23' ? track(f, [[eva('S23', 'turnHead')[0], 'give'], [eva('S23', 'turnHead')[1], 'lookUp']]) : POSE.give;
    const bars = id === 'S23' ? prog(f, [evn('S23', 'bars'), evn('S23', 'bars') + 8]) : 0;
    const rc = id === 'S23' ? smooth(prog(f, eva('S23', 'recolor'))) : 0;
    // 飞向你的“抢”：第 166 代每 0.15 秒一道，第 167 代每 0.34 秒一道（716 → 317 回，只画不说）
    const streaks: React.ReactNode[] = [];
    if (id === 'S23') {
      const me = myHand(POSE.give);
      const [d0, d1] = eva('S23', 'grabsDense'), [s0, s1] = eva('S23', 'grabsSparse');
      const times: number[] = [];
      for (let t = d0; t < d1; t += T(0.15)) times.push(t);
      for (let t = s0; t < s1; t += T(0.34)) times.push(t);
      times.forEach((t, j) => {
        const u = (f - t) / 7;
        if (u < 0 || u > 1) return;
        const from = ROW((j * 7) % 10);
        const pnt = {x: lerp(from.x, me.x + 40, easeIn(u)), y: lerp(from.y, me.y - 120, easeIn(u))};
        const ang = Math.atan2(me.y - 120 - from.y, me.x + 40 - from.x) * 180 / Math.PI;
        streaks.push(<GrabHand key={j} x={pnt.x} y={pnt.y} r={20} dir={ang} close={clamp((u - 0.7) / 0.3)} trail={1} sleeve={0.8} o={1 - u * 0.4} />);
      });
    }
    const greenO = prog(f, eva('S22', 'rowGreen'));
    return (
      <>
        <Room x={meX} gen={gen} f={f} />
        <Row10 f={f} opp={opp} hi={(i) => (opp[i] === I.GTFT && greenO > 0.5 && id === 'S22' ? 0.9 : 0.15)} o={1 - bars} />
        {id === 'S22' && rowLabel(opp, I.GTFT, prog(f, [evn('S22', 'label'), evn('S22', 'label') + 4]) * (1 - prog(f, [w0, w0 + 4])))}
        <Pair f={f} gen={gen} me={{strategy: I.TFT, pose: myR, expr: myE, x: meX, recolor: {to: I.GTFT, p: rc}}}
          opp={{strategy: I.TFT, pose: POSE.give, expr: EX.stiff, x: opX, o: 1 - wp}} />
        <Man f={f} pose={POSE.give} expr={EX.calm} strategy={I.GTFT} who="other" x={opX} G={NL.G} s={NL.s} facing={-1} opacity={wp} seed="gt" />
        {oppTag(I.GTFT, wp)}
        {id === 'S23' && <Compare a={you[166].sc} ca={COL[I.TFT]} b={you[166].look!} cb={COL[I.GTFT]} o={bars} />}
        {bars < 0.05 && headBar(POSE.give, meX, 1, barLen(you[gen].sc))}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(POSE.give)} opp={opHand(POSE.give)} until={beat('S23').f1} />
        {streaks}
      </>
    );
  }
  return null;
};

// —— 结尾：你只有一遍；镜头慢推（每秒放大约 1.5%），推到片尾 ——
// 你站在右边 x = 1400。S27h 前后推得快一点（约 3.5 倍），不整幅静止；
// 第五版：S27h 直接接 S28（S27b 删了，四个你挪到 S25）。S28 一开头（fourOut）镜头就平移，你落回开头你站的位置（OPEN 那一套：x 560、地面 1240、3.2 倍），
// “你”标签跟着你从头左边滑到头顶（开头“你 · 老实人”的位置）；右边原来骗子站的地方空着、顶灯亮着；
// 你转向那块空光，双手托着光点（开头递光点的姿势，光点没递出去）；S29 开始前 0.62 秒转头看镜头，停在这一帧，最后一帧接 0 秒
export const END_X = 1400;
export const END = {G: 1090, s: 2.95, lampY: 130};
type EC = {k: number; tx: number; ty: number};             // 屏幕 = k × 世界 + t（世界 = 结尾那套坐标）
const K_END = OPEN.s / END.s;
const T_END = {tx: OPEN.youX - K_END * END_X, ty: OPEN.G - K_END * END.G};   // 你的脚落到开头你的脚
const PUSH_RATE = Math.log(1.015) / FPS;
const smoothE = (t: number) => { const x = clamp(t); return x * x * (3 - 2 * x); };
const pushBoost = (fr: number) => {
  const a = evn('S27', 'pushFrom'), b = beat('S27h').f0, c = beat('S27h').f1, d = c + 30;
  if (fr < a || fr > d) return 0;
  if (fr < b) return smoothE((fr - a) / (b - a));
  if (fr < c) return 1;
  return 1 - smoothE((fr - c) / (d - c));
};
const pushZ = (f: number) => {
  const a = evn('S27', 'pushFrom');
  if (f <= a) return 1;
  let s = 0;
  for (let x = a; x < f; x++) s += PUSH_RATE * (1 + 2.5 * pushBoost(x + 0.5)) * Math.min(1, f - x);
  return Math.exp(s);
};
const ecPush = (f: number): EC => { const z = pushZ(f); return {k: z, tx: END_X * (1 - z), ty: 600 * (1 - z)}; };
// 平移完以后：从比开头构图小 3.5% 的地方很慢地推（越推越慢），最后一帧正好是开头的构图
const LOOP_C = {x: OPEN.youX + 140, y: 620};
const ecLoop = (f: number): EC => {
  const p0 = eva('S28', 'fourOut')[0] + PAN_LEN;
  const u = clamp((f - p0) / (TL.frames - 1 - p0));
  const r = lerp(0.965, 1, 1 - (1 - u) * (1 - u));
  return {k: K_END * r, tx: LOOP_C.x + r * (T_END.tx - LOOP_C.x), ty: LOOP_C.y + r * (T_END.ty - LOOP_C.y)};
};
const PAN_LEN = 16;     // 平移 16 帧：从 fourOut 开头起（fourOut 只有 10 帧，多 6 帧让镜头落稳）
const ecMix = (a: EC, b: EC, u: number): EC => {
  const k = Math.exp(lerp(Math.log(a.k), Math.log(b.k), u));
  const px = lerp(a.k * END_X + a.tx, b.k * END_X + b.tx, u), py = lerp(a.k * END.G + a.ty, b.k * END.G + b.ty, u);
  return {k, tx: px - k * END_X, ty: py - k * END.G};
};
export const endCam = (f: number): EC => {
  const a = eva('S28', 'fourOut')[0];
  if (f < a) return ecPush(f);
  const u = ease(prog(f, [a, a + PAN_LEN]));
  return u >= 1 ? ecLoop(f) : ecMix(ecPush(f), ecLoop(f), u);
};
const ecStr = (c: EC) => `matrix(${c.k} 0 0 ${c.k} ${c.tx} ${c.ty})`;
export const endPush = (f: number) => ecStr(endCam(f));
// 每个“你”头顶一盏吊灯：灯罩、灯泡、一束光、身后一圈光。warm 0..1：0 是冷、暗的灯（粉衣那个），1 是最暖最亮的（绿衣那个）
export const YouLamp: React.FC<{x: number; warm: number; on?: number; y?: number; G?: number}> = ({x, warm, on = 1, y = 178, G = NL.G}) => {
  const lc = mixHex('#8E9BB3', '#FFD596', warm);
  const k = (0.25 + 0.75 * warm) * on;
  return (
    <g>
      <ellipse cx={x} cy={560} rx={300} ry={420} fill={lc} opacity={0.16 * k} filter="url(#fBlur24)" />
      <polygon points={`${x - 34},${y} ${x + 34},${y} ${x + 250},${G - 300} ${x - 250},${G - 300}`} fill={lc} opacity={0.22 * k} filter="url(#fBlur12)"
        style={{mixBlendMode: 'screen'}} />
      <line x1={x} y1={-10} x2={x} y2={y - 40} stroke="#2B2620" strokeWidth={4} />
      <circle cx={x} cy={y + 6} r={90} fill={lc} opacity={0.4 * k} filter="url(#fBlur12)" />
      <path d={`M ${x - 14} ${y - 42} L ${x + 14} ${y - 42} C ${x + 20} ${y - 22} ${x + 44} ${y - 10} ${x + 52} ${y} L ${x - 52} ${y} C ${x - 44} ${y - 10} ${x - 20} ${y - 22} ${x - 14} ${y - 42} Z`}
        fill="#3A2F27" />
      <path d={`M ${x - 14} ${y - 42} L ${x - 2} ${y - 42} C ${x - 6} ${y - 22} ${x - 20} ${y - 8} ${x - 25} ${y} L ${x - 52} ${y} C ${x - 44} ${y - 10} ${x - 20} ${y - 22} ${x - 14} ${y - 42} Z`}
        fill="#4E3F33" />
      <ellipse cx={x} cy={y} rx={52} ry={8} fill={mixHex('#3A2F27', lc, 0.35 + 0.6 * k)} />
      <ellipse cx={x} cy={y + 3} rx={18} ry={10} fill={mixHex('#5A5550', '#FFF6E2', k)} />
    </g>
  );
};

// 右边那块空光：一盏亮着的顶灯，光柱里飘着灰，没有人（朋友没来）
const R_W = (OPEN.oppX - T_END.tx) / K_END;      // 世界坐标：平移完正好落在开头骗子站的 x
const EmptyLight: React.FC<{x: number; G: number; f: number}> = ({x, G, f}) => {
  const lc = '#FFD596';
  const dust = Array.from({length: 18}, (_, i) => {
    const t = ((random(`ey${i}`) * 900 + f * (0.3 + random(`ev${i}`) * 0.5)) % 900) / 900;
    const y = 180 + t * 760;
    const w = 40 + ((y - 180) / 760) * 220;
    const sx = x + (random(`ex${i}`) - 0.5) * 2 * w + Math.sin(f / 37 + i) * 10;
    return <circle key={i} cx={sx} cy={y} r={1.6 + random(`er${i}`) * 2.2} fill={lc} opacity={0.4 * (0.4 + 0.6 * Math.abs(Math.sin(f / 21 + i)))} />;
  });
  return (
    <g>
      <YouLamp x={x} warm={1} on={1} y={END.lampY} G={G} />
      <ellipse cx={x} cy={600} rx={260} ry={330} fill={lc} opacity={0.07} filter="url(#fBlur24)" />
      <g style={{mixBlendMode: 'screen'}}>{dust}</g>
    </g>
  );
};

// 第七版重排：morph（0..1）是 S27 从四个你那一排过渡到结尾：0 = 四个你里绿衣那个（x 1510、地面 1220、3.0 倍、朝右、笑），
// 1 = 结尾的你（END_X、END.G、END.s、朝左）。途中走过去、经正面转身（正面那一帧换朝向）、灯跟着挪到结尾的高度，房间和“你”标签淡入
const FG = {x: 1510, G: 1220, s: 3.0, lampY: 212};
export const EndYou: React.FC<{f: number; o?: number; tagO?: number; lamp?: number; morph?: number}> = ({f, o = 1, tagO = 1, lamp = 1, morph = 1}) => {
  const mo = clamp(morph);
  const [fo0] = eva('S28', 'fourOut');
  const [t0, t1] = eva('S28', 'turn');
  const tm = Math.round((t0 + t1) / 2);
  const late = f >= fo0;
  const look0 = beat('S29').f0 - Math.round(0.62 * FPS), look1 = look0 + 12;     // S29 前 0.62 秒（第五版约 58.0 秒）转头看镜头
  const cam = endCam(f);
  const x = lerp(FG.x, END_X, mo);
  const GW = lerp(FG.G, END.G, mo), SW = lerp(FG.s, END.s, mo);
  // 转身：朝左侧身 → 正面（这一帧换朝向）→ 朝右、双手托起光点（开头递光点的姿势）→ 58.4 秒转头看镜头
  const facing: 1 | -1 = mo < 0.5 ? 1 : late && f >= tm ? 1 : -1;
  const sm = (t: number) => { const q = clamp(t); return q * q * (3 - 2 * q); };
  const r = mo < 1 ? {...(mo < 0.5 ? mixPose(POSE.idle, POSE.front0, sm(mo / 0.5)) : mixPose(POSE.front0, POSE.idle, sm((mo - 0.5) / 0.5))), cx: 0}
    : !late ? still('idle')
    : f < tm ? track(f, [[t0, 'idle'], [tm, 'front0']])
    : track(f, [[tm, 'front0'], [t1, 'give'], [look0, 'give'], [look1, 'endLook']]);
  const e = late ? exTrack(f, [[t0, 'calm'], [look0, 'calm'], [look1, 'soft']]) : mo < 1 ? exTrack(mo * 100, [[0, 'smile'], [100, 'calm']]) : EX.calm;
  const blinks = [tm - 2, evn('S28', 'opt2') + 14, look0 - 5, beat('S29').f0 + 8];   // 第四版选项提前到 56.7 / 57.0：两次眨眼别挤在一起；转头前眨一下
  // 光点：转到朝右时在两手之间亮起来，发暖光（世界坐标；开头是手中间往右 6、往上 22 个屏幕像素）
  const sp = late && f >= tm ? clamp((f - tm - 2) / 9) : 0;
  const hands = (() => {
    const a = handAt(r, x, END.G, END.s, 1, true), b = handAt(r, x, END.G, END.s, 1, false);
    return {x: (a.x + b.x) / 2 + 6 / K_END, y: a.y - 22 / K_END};
  })();
  // 头顶那个“你”：平移以后挂在开头“你 · 老实人”那个位置；第五版平移时从头左边（S27h 的位置）跟着镜头滑过去，不消失再冒出来
  const hd = headTop(POSE.give, OPEN.youX, OPEN.G, OPEN.s, 1);
  const tagW = {x: (hd.x - T_END.tx) / K_END, y: (hd.y - 66 - T_END.ty) / K_END};
  const tagA = {x: x - 310, y: 420, size: 88, tilt: -2};
  const sx = (wx: number) => cam.k * wx + cam.tx;
  const gS = cam.k * GW + cam.ty;
  const panU = late ? ease(prog(f, [fo0, fo0 + PAN_LEN])) : 0;
  const breathAmp = lerp(1, 1.8 + 0.6 * pushBoost(f), mo);
  return (
    <g opacity={o}>
      <g opacity={mo}><Room x={sx(x)} gen={300} f={f} spread={lerp(0.8, 1, panU)} /></g>
      {late && sx(R_W) < 2300 && <EmptyLight x={sx(R_W)} G={gS} f={f} />}
      <g opacity={lamp}><YouLamp x={sx(x)} warm={1} y={lerp(FG.lampY, END.lampY, mo)} G={gS} /></g>
      <g transform={ecStr(cam)}>
        <Man f={f} pose={r} expr={e} strategy={I.GTFT} who="me" x={x} G={GW} s={SW}
          facing={facing} seed="end" breathAmp={breathAmp} blinks={late ? blinks : []} noBlink={late ? [[fo0, 99999]] : []} tint={{color: '#FFD596', amount: 0.1}} />
        {sp > 0 && <Spark x={hands.x} y={hands.y} r={(34 / K_END) * easeOut(sp) * (1 + 0.04 * Math.sin(f / 6))} warm={0.6} glow={1.1} />}
        {(() => {
          const u = panU;
          const tx = lerp(tagA.x, tagW.x, u), ty = lerp(tagA.y, tagW.y, u) - Math.sin(Math.PI * u) * 40;
          const size = lerp(tagA.size, 88 / K_END, u), tilt = lerp(tagA.tilt, -1.5, u);
          // 底下一块不带尖角的牌子一直不透明，带尖角的那块叠在上面淡入（只有尖角是淡入的）
          return (
            <>
              {u < 1 && <Tag x={tx} y={ty} text="你" bg={YOU_BG} fg={YOU_FG} size={size} o={tagO * ease(clamp((mo - 0.55) / 0.45))} point="none" tilt={tilt} />}
              {u > 0 && <Tag x={tx} y={ty} text="你" bg={YOU_BG} fg={YOU_FG} size={size} o={tagO * u} tilt={tilt} />}
            </>
          );
        })()}
      </g>
    </g>
  );
};

export const isNear = (id: string) => ['S06', 'S07', 'S08', 'S09', 'S10', 'S12', 'S13', 'S18', 'S18b', 'S20', 'S21', 'S22', 'S23'].includes(id);
export type {PoseKey};
