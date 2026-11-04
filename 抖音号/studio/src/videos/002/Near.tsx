// 近景：画风 A 的人。你在左，对手在右，面对面，光点在两人之间走；右上方一排 10 个点是你这一代碰到的 10 个人。
// 每一拍演什么照分镜第四节；时间点全从 timeline.json 的 ev 来。
import React from 'react';
import {RPose, mixPose} from '../../components/people/rig';
import {Expr} from '../../components/people/face';
import {COL, D, FPS, GRABHAND, I, NAME, SANS, barLen, beat, clamp, ease, easeIn, easeOut, ev, eva, evn, genAt, lerp, prog} from './lib';
import {Bar, EX, GrabHand, Man, POSE, PoseKey, Spark, Tag, exTrack, handAt, headTop, track} from './people';

export const NL = {G: 1170, s: 3.15, youX: 470, oppX: 1190};
export const OPEN = {G: 1240, s: 3.2, youX: 560, oppX: 1300};
const ROW = (i: number) => ({x: 930 + i * 76, y: 240});
const ROW_R = 32;
const FLOOR = 780;
const T = (s: number) => Math.round(s * FPS);

// —— 背景：暗房间，一盏灯只照你 ——
export const Room: React.FC<{x: number; o?: number}> = ({x, o = 1}) => (
  <g opacity={o}>
    <rect width={1920} height={1080} fill="#11141B" />
    <circle cx={x} cy={560} r={720} fill="url(#lampGlow)" />
  </g>
);

// —— 一排 10 个人 ——
export const Row10: React.FC<{opp: number[]; hi?: (i: number) => number; o?: number; pulse?: (i: number) => number}> = ({opp, hi, o = 1, pulse}) => (
  <g opacity={o}>
    {opp.map((s, i) => {
      const p = ROW(i);
      const h = hi ? hi(i) : 0.4;
      const pu = pulse ? pulse(i) : 0;
      return (
        <g key={i} opacity={clamp(0.4 + 0.6 * h)}>
          {h > 0.7 && <circle cx={p.x} cy={p.y} r={ROW_R + 9} fill="none" stroke="#FFFFFF" strokeWidth={4} opacity={0.8} />}
          <circle cx={p.x} cy={p.y} r={ROW_R * (1 + 0.25 * pu)} fill={COL[s]} />
          <circle cx={p.x - ROW_R * 0.34} cy={p.y - 4} r={ROW_R * 0.2} fill="#fff" /><circle cx={p.x + ROW_R * 0.34} cy={p.y - 4} r={ROW_R * 0.2} fill="#fff" />
          <circle cx={p.x - ROW_R * 0.34} cy={p.y - 3} r={ROW_R * 0.1} fill="#15171C" /><circle cx={p.x + ROW_R * 0.34} cy={p.y - 3} r={ROW_R * 0.1} fill="#15171C" />
        </g>
      );
    })}
  </g>
);

// —— 光点的几种走法 ——
type Pt = {x: number; y: number};
type Act = {t: number; kind: 'give' | 'back' | 'grab' | 'myGrab' | 'slipMe' | 'slipOpp' | 'warm' | 'toRow' | 'fromRow' | 'rowGrab'; k?: number; d?: number};
const arc = (a: Pt, b: Pt, u: number, h = 60) => ({x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) - Math.sin(u * Math.PI) * h});

const Acts: React.FC<{f: number; acts: Act[]; me: Pt; opp: Pt; until: number}> = ({f, acts, me, opp, until}) => {
  const out: React.ReactNode[] = [];
  acts.forEach((a, i) => {
    const d = a.d ?? 8;
    const u = (f - a.t) / d;
    const key = `${a.kind}${i}`;
    if (a.kind === 'slipMe' || a.kind === 'slipOpp') {
      // 手滑：光点放大，往两人中间滑出去、落地，落地那一下闪一圈，落下的光点一直亮着
      if (u < 0 || f >= until) return;
      const from = a.kind === 'slipMe' ? me : opp;
      const dir = a.kind === 'slipMe' ? 1 : -1;
      const fall = clamp(u / 1.2);
      const x = from.x + dir * 120 * easeOut(fall), y = lerp(from.y, FLOOR, easeIn(fall));
      if (fall < 1) {
        out.push(<Spark key={key} x={x} y={y} r={44} />);
        return;
      }
      const k = u - 1.2;                       // 落地以后（单位：d 帧）
      const pulse = 1 + 0.12 * Math.sin(k * 2.2);
      out.push(
        <g key={key}>
          <ellipse cx={x} cy={FLOOR + 30} rx={70} ry={16} fill="#FFF1D6" opacity={0.35} />
          <Spark x={x} y={FLOOR} r={38 * pulse} />
          <circle cx={x} cy={FLOOR} r={52 * pulse} fill="none" stroke="#FFF1D6" strokeWidth={5} opacity={0.6} />
        </g>,
      );
      if (k < 0.9) {
        const q = k / 0.9;
        out.push(
          <g key={`${key}f`} opacity={1 - q}>
            <circle cx={x} cy={FLOOR} r={50 + 170 * q} fill="none" stroke="#FFFFFF" strokeWidth={10} />
            <circle cx={x} cy={FLOOR} r={60 * (1 - q) + 30} fill="#FFFFFF" opacity={0.7} />
            {Array.from({length: 10}, (_, j) => {
              const an = (j / 10) * Math.PI * 2;
              const r0 = 70 + 60 * q, r1 = 120 + 140 * q;
              return <line key={j} x1={x + Math.cos(an) * r0} y1={FLOOR + Math.sin(an) * r0} x2={x + Math.cos(an) * r1} y2={FLOOR + Math.sin(an) * r1}
                stroke="#FFFFFF" strokeWidth={8} strokeLinecap="round" />;
            })}
          </g>,
        );
      }
      return;
    }
    if (u < 0 || u > 1.35) return;
    const fade = u > 1 ? 1 - (u - 1) / 0.35 : 1;
    if (a.kind === 'give' || a.kind === 'back' || a.kind === 'warm' || a.kind === 'toRow' || a.kind === 'fromRow') {
      const A = a.kind === 'give' || a.kind === 'toRow' ? me : a.kind === 'fromRow' ? ROW(a.k!) : opp;
      const B = a.kind === 'toRow' ? ROW(a.k!) : a.kind === 'give' ? opp : me;
      const p = arc(A, B, ease(Math.min(1, u)), a.kind === 'toRow' || a.kind === 'fromRow' ? 30 : 70);
      const small = a.kind === 'toRow' || a.kind === 'fromRow';
      out.push(<Spark key={key} x={p.x} y={p.y} r={a.kind === 'warm' ? 42 : small ? 20 : 32} o={fade} warm={a.kind === 'warm' ? 1 : 0} />);
      return;
    }
    // 抢：先伸过来一只橙红的手，再连手带光点拿回去
    const own = a.kind === 'grab' || a.kind === 'rowGrab' ? opp : me;
    const target = a.kind === 'grab' || a.kind === 'rowGrab' ? me : opp;
    const home = a.kind === 'rowGrab' ? ROW(a.k!) : own;
    const meet = a.kind === 'rowGrab' ? {x: lerp(target.x, home.x, 0.25), y: lerp(target.y, home.y, 0.25)} : target;
    if (u <= 0.45) {
      const p = arc(home, meet, easeOut(u / 0.45), 20);
      out.push(<Spark key={`${key}s`} x={target.x + (a.kind === 'rowGrab' ? (meet.x - target.x) * (u / 0.45) : 0)} y={target.y + (a.kind === 'rowGrab' ? (meet.y - target.y) * (u / 0.45) : 0)} r={32} />);
      out.push(<GrabHand key={key} x={p.x} y={p.y} dir={Math.atan2(meet.y - home.y, meet.x - home.x) * 180 / Math.PI} />);
    } else {
      const p = arc(meet, home, ease(Math.min(1, (u - 0.45) / 0.55)), 20);
      out.push(<Spark key={`${key}s`} x={p.x} y={p.y} r={32} o={fade} />);
      out.push(<GrabHand key={key} x={p.x} y={p.y} o={fade} dir={Math.atan2(meet.y - home.y, meet.x - home.x) * 180 / Math.PI} />);
    }
  });
  return <>{out}</>;
};

// 两根条并排比长短（左对齐，上下叠）
const Compare: React.FC<{a: number; ca: string; b: number; cb: string; o: number; x?: number; y?: number}> = ({a, ca, b, cb, o, x = 640, y = 262}) => (
  <g opacity={o}>
    <circle cx={x - 34} cy={y} r={14} fill={ca} /><Bar x={x} y={y} len={barLen(a) * ease(o)} color={ca} align="left" />
    <circle cx={x - 34} cy={y + 52} r={14} fill={cb} /><Bar x={x} y={y + 52} len={barLen(b) * ease(o)} color={cb} align="left" />
  </g>
);

type Who = {strategy: number; pose: RPose; expr: Expr; x: number; o?: number; recolor?: {to: number; p: number}; seed?: string; facing?: 1 | -1};

const Pair: React.FC<{f: number; me: Who; opp?: Who; L?: typeof NL}> = ({f, me, opp, L = NL}) => (
  <>
    <Man f={f} pose={me.pose} expr={me.expr} strategy={me.strategy} who="me" x={me.x} G={L.G} s={L.s} opacity={me.o} recolor={me.recolor} seed="me" />
    {opp && (opp.o ?? 1) > 0.01 && (
      <Man f={f} pose={opp.pose} expr={opp.expr} strategy={opp.strategy} who="other" x={opp.x} G={L.G} s={L.s} facing={opp.facing ?? -1}
        opacity={opp.o} recolor={opp.recolor} seed={opp.seed ?? 'opp'} />
    )}
  </>
);

const youTag = (o = 1) => <Tag x={215} y={470} text="你" bg="rgba(255,255,255,0.16)" size={88} o={o} />;
const oppTag = (s: number, o = 1, y = 470) => <Tag x={NL.oppX + 270} y={y} text={NAME(s) === '宽容的以牙还牙' ? '会原谅' : NAME(s)} bg={COL[s]} size={80} o={o} />;
const rowLabel = (opp: number[], s: number, o: number) => {
  const xs = opp.map((v, i) => (v === s ? ROW(i).x : null)).filter((v) => v !== null) as number[];
  if (!xs.length) return null;
  const cx = clamp((Math.min(...xs) + Math.max(...xs)) / 2, 1130, 1500);
  return <Tag x={cx} y={328} text={s === I.GTFT ? '会原谅' : NAME(s)} bg={COL[s]} size={80} o={o} />;
};
const headBar = (r: RPose, x: number, facing: 1 | -1, len: number, color = '#EEF1F6', glow = 0, o = 1, dy = 0) => {
  const h = headTop(r, x, NL.G, NL.s, facing);
  return <Bar x={h.x} y={h.y - 40 + dy} len={len} color={color} glow={glow} o={o} />;
};

// —— 第 0 秒：你把光点递出去，骗子一把抢走 ——
export const NearOpen: React.FC<{f: number; o?: number; scale?: number}> = ({f, o = 1, scale = 1}) => {
  const L = OPEN;
  // 放慢：手 0–0.5 秒慢慢伸到光点；0.5–0.85 秒连光点一起拿走；0.85–1.2 秒转身；之后多停一会儿
  const [r0, r1] = eva('S01', 'reachIn');
  const [g0, g1] = eva('S01', 'grab');
  const [ta0, ta1] = eva('S01', 'turnAway');
  const myPose = POSE.give;
  const myE = exTrack(f, [[0, 'calm'], [evn('S01', 'blank') - 2, 'calm'], [evn('S01', 'blank') + 3, 'blank'], ...eva('S01', 'worry').map((t, i) => [t, i ? 'worry' : 'blank'] as [number, string])]);
  const turned = f >= (ta0 + ta1) / 2;
  const half = mixPose(POSE.idle, POSE.reach, 0.55);
  const oppPose = turned ? track(f, [[ta0, 'pull'], [ta1, 'idle']]) : track(f, [[r0, half], [r1, 'reach'], [g0, 'reach'], [g1, 'pull']]);
  const oppX = OPEN.oppX + (turned ? 70 * ease(prog(f, [ta0, ta1 + 6])) : 0);
  const facing: 1 | -1 = turned ? 1 : -1;
  const myHands = handAt(myPose, L.youX, L.G, L.s, 1);
  const oppHand = handAt(oppPose, oppX, L.G, L.s, facing);
  const gp = ease(prog(f, [g0, g1]));
  const sp = f < g0 ? myHands : f < g1 ? {x: lerp(myHands.x, oppHand.x, gp), y: lerp(myHands.y, oppHand.y, gp)} : oppHand;
  const hd = headTop(myPose, L.youX, L.G, L.s, 1);
  const ohd = headTop(POSE.reach, OPEN.oppX, L.G, L.s, -1);
  return (
    <g opacity={o} transform={`translate(${L.youX} ${700}) scale(${scale}) translate(${-L.youX} ${-700})`}>
      <Room x={L.youX} />
      <Man f={f} pose={myPose} expr={myE} strategy={I.ALLC} who="me" x={L.youX} G={L.G} s={L.s} seed="me" />
      <Man f={f} pose={oppPose} expr={EX.cold} strategy={I.ALLD} who="other" x={oppX} G={L.G} s={L.s} facing={facing} seed="sw" />
      {/* 只有抢这一下用橙红的手 */}
      {f <= g1 + 4 && <GrabHand x={oppHand.x} y={oppHand.y} r={32} dir={180} />}
      <Spark x={sp.x} y={sp.y} />
      <Tag x={hd.x} y={hd.y - 60} text="你 · 老实人" bg="rgba(255,255,255,0.16)" size={88} />
      <Tag x={ohd.x} y={ohd.y - 56} text="骗子" bg={COL[I.ALLD]} size={80} />
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
    const [g0, g1] = eva(id, 'gives');
    const opp = you[gen].opp;
    const acts: Act[] = [];
    let returns = 0;
    for (let i = 0; i < 10; i++) {
      const t = Math.round(lerp(g0, g1 - 8, i / 9));
      acts.push({t, kind: 'toRow', k: i, d: 7});
      const s = you[genAt(t)].opp[i];
      if (s !== I.ALLD) {
        acts.push({t: t + 7, kind: 'fromRow', k: i, d: 7});
        if (f >= t + 14) returns++;
      }
    }
    const r = POSE.give;
    const len = barLen(you[gen].sc) * clamp(0.25 + returns / 8);
    return (
      <>
        <Room x={meX} />
        <Row10 opp={opp} hi={() => 0.75} pulse={(i) => acts.some((a) => a.kind === 'toRow' && a.k === i && f >= a.t + 7 && f < a.t + 11) ? 1 : 0} />
        <Pair f={f} me={{strategy: I.ALLC, pose: r, expr: EX.calm, x: meX}} />
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
        <Room x={meX} />
        <Row10 opp={opp} hi={(i) => (f >= hiT && opp[i] === I.ALLD ? 1 : 0.15)} />
        {rowLabel(opp, I.ALLD, prog(f, [evn(id, 'label'), evn(id, 'label') + 5]))}
        <Pair f={f} me={{strategy: I.ALLC, pose: r, expr: e, x: meX}} />
        {headBar(r, meX, 1, len)}
        {youTag()}
        <Acts f={f} acts={acts} me={myHand(POSE.give)} opp={myHand(POSE.give)} until={b.f1} />
      </>
    );
  }

  if (id === 'S08') {
    // 谁都会手滑：特写你的手，连着递 20 次，第 14 次滑掉落地
    const r = POSE.give;
    const h = myHand(r);
    const z = 1 + 1.3 * ease(prog(f, eva(id, 'zoomIn'))) - 1.3 * ease(prog(f, eva(id, 'zoomOut')));
    const [g0, g1] = eva(id, 'gives');
    const slip = ev(id, 'slipIndex') as number;
    const acts: React.ReactNode[] = [];
    for (let i = 0; i < 20; i++) {
      const t = lerp(g0, g1, i / 19);
      const u = (f - t) / 6;
      if (u < 0) continue;
      if (i === slip) {
        const fall = clamp(u / 1.5);
        const y = lerp(h.y, FLOOR, easeIn(fall));
        acts.push(<Spark key={i} x={h.x + 60 * fall} y={y} r={fall >= 1 ? 38 : 44} />);
        if (fall >= 1 && u < 3) {
          const q = (u - 1.5) / 1.5;
          acts.push(
            <g key={`${i}f`} opacity={1 - q}>
              <circle cx={h.x + 60} cy={FLOOR} r={50 + 170 * q} fill="none" stroke="#FFFFFF" strokeWidth={10} />
              <circle cx={h.x + 60} cy={FLOOR} r={60 * (1 - q) + 30} fill="#FFFFFF" opacity={0.7} />
            </g>,
          );
        }
      } else if (u < 1) {
        acts.push(<Spark key={i} x={h.x + 520 * easeOut(u)} y={h.y - 30 * Math.sin(u * Math.PI)} r={32} o={1 - u * 0.6} />);
      }
    }
    const slipT = lerp(g0, g1, slip / 19);
    const e = exTrack(f, [[b.f0, 'calm'], [slipT + 6, 'calm'], [slipT + 10, 'surprise']]);
    return (
      <g transform={`translate(${h.x} ${h.y}) scale(${z}) translate(${-h.x} ${-h.y})`}>
        <Room x={meX} />
        <Pair f={f} me={{strategy: I.ALLC, pose: r, expr: e, x: meX}} />
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
    const opR = track(f, [[c0, 'idle'], [c1, 'cross']]);
    const [st0, st1] = eva(id, 'stun');
    const opE = exTrack(f, [[st0 - 1, 'calm'], [st0 + 3, 'surprise'], [st1, 'surprise'], [c1, 'cold']]);
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
        <Room x={meX} />
        <Row10 opp={opp} hi={(i) => (i === pickI ? 1 : 0.15)} />
        {wp < 1 && <circle cx={lerp(start.x, oh.x, wp)} cy={lerp(start.y, oh.y + 150, wp)} r={lerp(ROW_R, 90, wp)} fill={COL[I.GRIM]} opacity={1 - wp * 0.6} />}
        <Pair f={f} me={{strategy: I.ALLC, pose: myR, expr: myE, x: meX}}
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
    const rc = ease(prog(f, eva(id, 'recolor')));
    const look = you[4].look!;
    return (
      <>
        <Room x={meX} />
        <Row10 opp={you[4].opp} o={0.6} />
        <Pair f={f} me={{strategy: I.ALLC, pose: myR, expr: exTrack(f, [[b.f0, 'sad'], [evn(id, 'bars') + 10, 'blank']]), x: meX, recolor: {to: I.GRIM, p: rc}}}
          opp={{strategy: I.GRIM, pose: POSE.cross, expr: EX.cold, x: opX, o: 1 - sw}} />
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
    const myR = track(f, [[s12.f0, 'give'], [c0, 'give'], [c1, 'cross']]);
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
      : exTrack(f, [[s12.f0, 'calm'], [eva('S12', 'stun')[0] - 1, 'calm'], [eva('S12', 'stun')[0] + 3, 'surprise'], [eva('S12', 'stun')[1], 'surprise'], [c1, 'cold']]);
    const opE = exTrack(f, [[s12.f0, 'calm'], [grabs[0], 'calm'], [grabs[1], 'worry'], [grabs[3], 'sad']]);
    return (
      <>
        <Room x={meX} />
        <Row10 opp={you[7].opp} o={0.6} />
        <Pair f={f} me={{strategy: I.GRIM, pose: myR, expr: myE, x: meX}}
          opp={{strategy: I.ALLC, pose: POSE.give, expr: opE, x: opX}} />
        {oppTag(I.ALLC)}
        {headBar(POSE.give, meX, 1, len, '#EEF1F6', id === 'S13' ? grow : 0)}
        {youTag()}
        {Array.from({length: pile}, (_, i) => <Spark key={`p${i}`} x={meX - 200 + (i % 2) * 60} y={760 - Math.floor(i / 2) * 56 - (i % 2) * 20} r={26} />)}
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
    const rc = ease(prog(f, eva(id, 'recolor')));
    return (
      <>
        <Room x={meX} />
        <Row10 opp={opp} hi={(i) => (opp[i] === I.TFT && f >= evn(id, 'label') ? 0.9 : 0.15)} />
        {rowLabel(you[108].opp, I.TFT, prog(f, [evn(id, 'label'), evn(id, 'label') + 4]) * (1 - prog(f, [w0, w0 + 4])))}
        {wp > 0 && wp < 1 && <circle cx={lerp(start.x, oh.x, wp)} cy={lerp(start.y, oh.y + 150, wp)} r={lerp(ROW_R, 90, wp)} fill={COL[I.TFT]} opacity={1 - wp * 0.6} />}
        <Pair f={f} me={{strategy: I.GRIM, pose: myR, expr: exTrack(f, [[b.f0, 'cold'], [evn(id, 'bars'), 'blank']]), x: meX, recolor: {to: I.TFT, p: rc}}}
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
    // 你滑一下，他还一下，你再还一下：一道橙红的“抢”在两人之间来回；两人的脸越来越僵；中间一排 10 格亮 5 暗 5
    const slip = evn('S20', 'slip');
    const acts: Act[] = [{t: slip, kind: 'slipMe'}];
    const [p0, p1] = eva('S21', 'pong');
    const stiff = prog(f, [p0, p1]);
    const myE = exTrack(f, [[beat('S20').f0, 'calm'], [slip + 3, 'surprise'], [p0, 'blank'], [p1, 'stiff']]);
    const [st0, st1] = eva('S20', 'stun');
    const opE = exTrack(f, [[beat('S20').f0, 'calm'], [st0 - 1, 'calm'], [st0 + 3, 'surprise'], [st1, 'surprise'], [p1, 'stiff']]);
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
          <line x1={back.x} y1={back.y} x2={pnt.x} y2={pnt.y} stroke={GRABHAND} strokeWidth={22} strokeLinecap="round" opacity={0.7} />
          <GrabHand x={pnt.x} y={pnt.y} dir={leg % 2 === 0 ? 0 : 180} />
        </g>
      );
    }
    const cellsO = prog(f, [evn('S21', 'cells'), evn('S21', 'cells') + 6]);
    const lit = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0];
    const wob = id === 'S21' ? Math.sin((f - p0) / 3) * 22 * stiff : 0;
    return (
      <>
        <Room x={meX} />
        <Pair f={f} me={{strategy: I.TFT, pose: POSE.give, expr: myE, x: meX}}
          opp={{strategy: I.TFT, pose: POSE.give, expr: opE, x: opX}} />
        {oppTag(I.TFT)}
        {id === 'S20' && headBar(POSE.give, meX, 1, barLen(you[140].sc))}
        {id === 'S21' && (
          <>
            <g opacity={cellsO}>
              {lit.map((l, i) => (
                <rect key={i} x={830 - (10 * 90 + 9 * 10) / 2 + i * 100} y={212} width={90} height={90} rx={12}
                  fill={l ? '#FFE3B0' : '#2A2D36'} stroke="#FFFFFF" strokeOpacity={0.25} strokeWidth={3} />
              ))}
            </g>
            <Bar x={830} y={352} len={barLen(you[150].sc) * 0.75 + wob} full={300} />
          </>
        )}
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
    const rc = id === 'S23' ? ease(prog(f, eva('S23', 'recolor'))) : 0;
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
        streaks.push(<g key={j} opacity={1 - u * 0.5}><line x1={lerp(from.x, pnt.x, 0.7)} y1={lerp(from.y, pnt.y, 0.7)} x2={pnt.x} y2={pnt.y}
          stroke={GRABHAND} strokeWidth={10} strokeLinecap="round" /><circle cx={pnt.x} cy={pnt.y} r={12} fill={GRABHAND} /></g>);
      });
    }
    const greenO = prog(f, eva('S22', 'rowGreen'));
    return (
      <>
        <Room x={meX} />
        <Row10 opp={opp} hi={(i) => (opp[i] === I.GTFT && greenO > 0.5 && id === 'S22' ? 0.9 : 0.15)} />
        {id === 'S22' && rowLabel(opp, I.GTFT, prog(f, [evn('S22', 'label'), evn('S22', 'label') + 4]) * (1 - prog(f, [w0, w0 + 4])))}
        <Pair f={f} me={{strategy: I.TFT, pose: myR, expr: myE, x: meX, recolor: {to: I.GTFT, p: rc}}}
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

// —— 结尾：你只有一遍；转身面对镜头，眨眼，呼吸；镜头慢推（每秒放大约 1.5%），推到片尾 ——
// 你站在右边 x = 1400：带走句那拍另外三个你在左边淡入，你原地不动
export const END_X = 1400;
export const endPush = (f: number) => {
  const z = Math.pow(1.015, Math.max(0, f - evn('S27', 'pushFrom')) / FPS);
  const fx = END_X, fy = 500;
  return `translate(${fx} ${fy}) scale(${z}) translate(${-fx} ${-fy})`;
};
export const EndYou: React.FC<{f: number; o?: number; tagO?: number}> = ({f, o = 1, tagO = 1}) => {
  const [t0, t1] = eva('S28', 'turn');
  const r = track(f, [[t0, 'idle'], [t1, 'front']]);
  const x = END_X;
  // 两个选项出来以后各眨一次眼，最后 1 秒里再眨一次
  const blinks = [evn('S28', 'opt1') + 12, evn('S28', 'opt2') + 14, beat('S29').f0 + 10];
  return (
    <g opacity={o}>
      <Room x={x} />
      <g transform={endPush(f)}>
        <Man f={f} pose={r} expr={exTrack(f, [[t0, 'calm'], [t1, 'calm']])} strategy={I.GTFT} who="me" x={x} G={NL.G} s={NL.s}
          seed="end" breathAmp={1.8} blinks={blinks} />
        <Tag x={x - 330} y={470} text="你" bg="rgba(255,255,255,0.16)" size={88} o={tagO} />
      </g>
    </g>
  );
};

export const isNear = (id: string) => ['S06', 'S07', 'S08', 'S09', 'S10', 'S12', 'S13', 'S18', 'S20', 'S21', 'S22', 'S23'].includes(id);
export type {PoseKey};
