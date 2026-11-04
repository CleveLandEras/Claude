// 003《消息提醒》v10 成片画面（Notice003V10）：不教学的观点片。秒数、字幕、事件全读 timeline10.ts（照 videos/003_消息提醒/文案.md 最上面一节）。
// 场景：桌前。主角（没开免打扰：响一下，看一下）→ 另一个人（开了免打扰：过一会儿还是点开）→ 消息冒满 → 大字“怕漏”，群那一行亮暖黄 → 怕没看到的两张虚线卡 → 手伸过去 → 大字“全关 不一定治得了 怕漏” → 办法放在简介 → 结尾问句。
// 桌前那套（暗房间、暖灯、成片小人、真手机）照 Notice9.tsx 搬过来；片里不画设置页、开关、步骤（选题单 V3）。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Chair} from '../../components/people/FlatProps';
import {EXPR, Expr, blink, breath, mixExpr, withBlink} from '../../components/people/face';
import {Look, ME, OTHER} from '../../components/people/look';
import {mixHex} from '../../components/people/geom';
import {Pose, RPose, mixPose, nudge, poseDef, resolve, solve} from '../../components/people/rig';
import {FPerson} from '../002/film/FPerson';
import {AiBadge, AppIcon, CREAM, FilmDefs3, LAMP, Lamp, PhoneBody, RoomBase, SHADOW, Shadow, Sticker, StatusBar, SubBand3, Vignette3} from './film';
import {Beat10, EV10, FPS10, FRAMES10, SC10, Seg10, beatAt10} from './timeline10';

export const NOTICE10_FRAMES = FRAMES10;

const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
const C = {
  bg: '#101219', ink: '#F4F5F8', soft: '#B9BEC9', gray: '#8A8F99', warm: '#FFC94D', warmBg: '#4A3D1C',
  red: '#FF5A4E', green: '#3CC27A', wood: '#3F352D', woodTop: '#5A4B3E',
};

// —— 小工具（同 Notice9.tsx）——
const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => {
  const x = clamp(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
const easeOut = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
const easeBack = (t: number) => {
  const x = clamp(t), c1 = 1.70158, c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};
const pr = (t: number, ab: number[]) => clamp((t - ab[0]) / Math.max(1e-6, ab[1] - ab[0]));
const po = (t: number, ab: number[]) => easeOut(pr(t, ab));
const bump = (t: number, a: number, d = 0.3) => {
  const u = (t - a) / d;
  return u < 0 || u > 1 ? 0 : Math.sin(Math.PI * u);
};
const tw = (s: string, size: number) => [...s].reduce((w, ch) => {
  if (/[　-鿿＀-￯“”‘’…—①-⑳]/.test(ch)) return w + size;
  if (ch === ' ') return w + size * 0.3;
  if (/[0-9]/.test(ch)) return w + size * 0.6;
  return w + size * 0.58;
}, 0);

type PK = [number, RPose, number?, ((x: number) => number)?];
const ptrack = (t: number, keys: PK[]): RPose => {
  let cur = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [ti, p, d = 0.3, fn = ease] = keys[i];
    if (t < ti) break;
    cur = mixPose(cur, p, fn(clamp((t - ti) / d)));
  }
  return cur;
};
type EK = [number, Expr, number?];
const etrack = (t: number, keys: EK[]): Expr => {
  let cur = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [ti, e, d = 0.25] = keys[i];
    if (t < ti) break;
    cur = mixExpr(cur, e, ease((t - ti) / d));
  }
  return cur;
};

const Tx: React.FC<{x: number; y: number; size: number; fill?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number; o?: number; children: React.ReactNode}> = (
  {x, y, size, fill = C.ink, anchor = 'start', weight = 600, o = 1, children},
) => (
  <text x={x} y={y} fontSize={size} fontFamily={SANS} fontWeight={weight} fill={fill} textAnchor={anchor} dominantBaseline="central" opacity={o}>{children}</text>
);

// ================= 人和姿势 =================
const BOARD = poseDef('board');
const P = (base: Pose, o: Pose) => resolve({...base, ...o});
const DESK = P(BOARD, {neck: 4, pitch: 0.3, yaw: 0.45, gaze: {x: 1, y: 0.5}});
const DESK_UP = P(BOARD, {lean: 3, neck: -6, pitch: -0.05, yaw: 0.5, gaze: {x: 1, y: -0.15}});
const DESK_READ = P(BOARD, {lean: 9, chest: 4, neck: -2, pitch: 0.05, yaw: 0.5, gaze: {x: 1, y: 0}});
const DESK_SLUMP = P(BOARD, {lean: 6, chest: 9, neck: 6, shrug: -0.8, pitch: 0.2, yaw: 0.5, gaze: {x: 1, y: 0}});
// 手伸向手机：上身往前探，近侧那只手伸到手机边上
const DESK_REACH = P(BOARD, {lean: 13, chest: 4, neck: -3, pitch: 0.05, yaw: 0.5, gaze: {x: 1, y: 0}, aN: {to: {x: 100, y: -44}, wr: -35}});
const E = EXPR;

type Glow = {at: {x: number; y: number}; color: string; amount: number; r?: number};
const You: React.FC<{fr: number; look: Look; pose: RPose; expr: Expr; x: number; G: number; s: number; seed: string; part?: 'all' | 'body' | 'arms'; glow?: Glow}> = (
  {fr, look, pose, expr, x, G, s, seed, part, glow},
) => {
  const b = breath(fr);
  const r = nudge(pose, {shrug: 0.08 * b, chest: -0.7 * b});
  const e = withBlink(expr, blink(fr, seed));
  return <FPerson pose={r} expr={e} look={look} x={x} y={G} s={s} facing={1} night="#0B0D12" light={{x: -0.25, y: -1}} part={part}
    tint={{color: LAMP, amount: 0.07}} glow={glow} />;
};

// ================= 桌前 =================
const HOOK = {x: 880, G: 900, s: 1.9};
const DESK_Y = HOOK.G - 88 * HOOK.s;
const PB = {x: 1080, y: 180, w: 420, h: 720};
const SC_ = {x: PB.x + 14, y: PB.y + 14, w: PB.w - 28, h: PB.h - 28};
const HS = 1.04, HX = 50.8, HY = -46.2;          // 画面 X = HS·x + HX，Y = HS·y + HY
const DESK_XF = `translate(${HX} ${HY}) scale(${HS})`;

const lookAt = (t: number): Look => (t < SC10.me[1] ? ME : OTHER);
const deskPose = (t: number) => ptrack(t, [
  [0, DESK_READ], [EV10.tagNo, DESK, 0.2],
  [EV10.rings[0] + 0.1, DESK_READ, 0.2], [EV10.rings[0] + 0.85, DESK, 0.25], [EV10.rings[1] + 0.1, DESK_READ, 0.2],
  [EV10.cut, DESK, 0.01], [EV10.reach1, DESK_REACH, 0.35], [EV10.open1 + 0.1, DESK_READ, 0.3], [EV10.slump[0], DESK_SLUMP, 0.5], [EV10.close1, DESK, 0.3],
  [EV10.reach2, DESK_REACH, 0.3], [EV10.open2, DESK_READ, 0.2], [EV10.close2, DESK, 0.12], [EV10.reach3, DESK_REACH, 0.2],
  [EV10.thread[0], DESK_UP, 0.4], [EV10.fear, DESK_READ, 0.3],
  [EV10.bellBig, DESK, 0.3], [EV10.reach4, DESK_REACH, 0.9],
]);
const deskExpr = (t: number) => etrack(t, [
  [0, E.blank], [EV10.rings[0], {...E.surprise, open: 0.3}, 0.15], [EV10.rings[0] + 0.5, E.blank, 0.3], [EV10.rings[1], {...E.surprise, open: 0.3}, 0.15], [EV10.rings[1] + 0.5, E.sighing, 0.3],
  [EV10.cut, E.calm, 0.01], [EV10.reach1 - 0.2, E.worry, 0.25], [EV10.slump[0], E.sighing, 0.4], [EV10.close1, E.calm, 0.3], [EV10.reach2 - 0.2, E.worry, 0.2],
  [EV10.fear, E.worry, 0.3], [EV10.bellBig, E.calm, 0.3], [EV10.reach4 - 0.3, E.worry, 0.4],
]);

// 手机响：只有没开免打扰那一段响；开了免打扰以后手机一直不响不抖
const RINGS = [EV10.buzz0, ...EV10.rings];
const shake = (t: number) => {
  const f = Math.round(t * FPS10);
  const on = RINGS.some((b) => f >= Math.round(b * FPS10) && f < Math.round(b * FPS10) + 8);
  if (!on) return {dx: 0, rot: 0};
  const k = f % 2 === 0 ? 1 : -1;
  return {dx: 5 * k, rot: 2 * k};
};
const screenFlash = (t: number) => {
  let v = 0;
  for (const a of RINGS) v = Math.max(v, bump(t, a, 0.35));
  return v;
};

const MuteBell: React.FC<{s?: number; color?: string; bg?: string}> = ({s = 1, color = '#F4F5F8', bg = '#111318'}) => (
  <g transform={`scale(${s})`}>
    <path d="M -16 10 L -16 -4 Q -16 -20 0 -20 Q 16 -20 16 -4 L 16 10 L 21 15 L -21 15 Z" fill={color} />
    <circle cx={0} cy={21} r={5} fill={color} />
    <line x1={-22} y1={-22} x2={22} y2={24} stroke={bg} strokeWidth={8} />
    <line x1={-22} y1={-22} x2={22} y2={24} stroke={color} strokeWidth={4} strokeLinecap="round" />
  </g>
);

// 第一屏：群列表，班级群 99+
const LIST_ROWS = [{name: '工作群', n: '12'}, {name: '班级群', n: '99+', hi: true}, {name: '小区群', n: '8'}, {name: '亲戚群', n: '34'}];
const ListPage: React.FC<{t: number}> = ({t}) => {
  const pulse = bump(t, EV10.buzz0, 0.4);
  return (
    <g>
      <rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} fill="#111318" />
      <rect x={SC_.x} y={SC_.y} width={SC_.w} height={116} fill="#1C1F26" />
      <Tx x={SC_.x + SC_.w / 2} y={SC_.y + 80} size={52} anchor="middle">微信</Tx>
      {LIST_ROWS.map((r, i) => {
        const y = SC_.y + 126 + i * 130;
        const w = tw(r.n, 50) + 30;
        return (
          <g key={i}>
            {r.hi && <rect x={SC_.x + 6} y={y} width={SC_.w - 12} height={118} rx={18} fill="#262B38" />}
            <AppIcon x={SC_.x + 44} y={y + 59} size={56} kind="chat" />
            <Tx x={SC_.x + 84} y={y + 59} size={50} fill={r.hi ? C.ink : C.soft}>{r.name}</Tx>
            <g transform={`translate(${SC_.x + SC_.w - 14 - w / 2} ${y + 59}) scale(${r.hi ? 1 + 0.18 * pulse : 1})`}>
              <rect x={-w / 2} y={-32} width={w} height={64} rx={32} fill={r.hi ? C.red : '#4A4F5A'} />
              <Tx x={0} y={1} size={50} anchor="middle" weight={700} fill="#FFFFFF">{r.n}</Tx>
            </g>
          </g>
        );
      })}
      {t >= EV10.tapRow - 0.25 && (() => {
        const u = pr(t, [EV10.tapRow, EV10.tapRow + 0.3]);
        const y = SC_.y + 126 + 130 + 59;
        return <circle cx={SC_.x + 170} cy={y} r={26 + 44 * easeOut(u)} fill="none" stroke="#FFFFFF" strokeWidth={6} opacity={t < EV10.tapRow ? pr(t, [EV10.tapRow - 0.25, EV10.tapRow - 0.05]) * 0.8 : 0.9 * (1 - u)} />;
      })()}
    </g>
  );
};

// 群聊：一堆收到、+1，没有要紧的
const MSG_BASE = ['哈哈哈', '[图片]', '好的', '1', '收到', '+1', '好的', '收到', '+1', '哈哈哈'];
const ChatPage: React.FC<{t: number; bell: boolean; fresh?: number[]; slideFrom?: number}> = ({t, bell, fresh = [], slideFrom}) => {
  const slide = slideFrom !== undefined ? po(t, [slideFrom, slideFrom + 0.25]) : 1;
  const freshTexts = ['收到', '收到', '+1'];
  const list: {text: string; at?: number}[] = [...MSG_BASE.map((m) => ({text: m})), ...fresh.filter((a) => t >= a).map((a, i) => ({text: freshTexts[i], at: a}))];
  const H = 88;
  let y = SC_.y + SC_.h - 44 - 40 * pr(t, EV10.scroll);
  const rows: React.ReactNode[] = [];
  for (let i = list.length - 1; i >= 0; i--) {
    const m = list[i];
    const u = m.at !== undefined ? po(t, [m.at, m.at + 0.18]) : 1;
    y -= H * u;
    if (y + H < SC_.y + 100) break;
    const w = tw(m.text, 50) + 40;
    rows.push(
      <g key={i} opacity={u}>
        <rect x={SC_.x + 14} y={y} width={w} height={H - 12} rx={14} fill={m.at !== undefined ? '#3A404C' : '#2A2E37'} />
        <Tx x={SC_.x + 34} y={y + (H - 12) / 2} size={50} fill="#D5D9E0">{m.text}</Tx>
      </g>,
    );
  }
  return (
    <g transform={`translate(${SC_.w * (1 - slide)} 0)`}>
      <rect x={SC_.x - 20} y={SC_.y} width={SC_.w + 20} height={SC_.h} fill="#111318" />
      {rows}
      <rect x={SC_.x} y={SC_.y} width={SC_.w} height={116} fill="#1C1F26" />
      <path d={`M ${SC_.x + 32} ${SC_.y + 66} l -13 13 l 13 13`} fill="none" stroke="#F4F5F8" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
      <Tx x={SC_.x + SC_.w / 2} y={SC_.y + 80} size={52} anchor="middle">班级群</Tx>
      {bell && <g transform={`translate(${SC_.x + SC_.w - 52} ${SC_.y + 80})`}><MuteBell s={0.9} /></g>}
    </g>
  );
};

// 锁屏
const lockTime = (t: number) => (t >= EV10.clock3 ? '21:05' : t >= EV10.clock2 ? '20:52' : t >= EV10.clock1 ? '20:40' : '20:31');
const LockPage: React.FC<{t: number}> = ({t}) => {
  const other = t >= SC10.other[0];
  const flip = Math.max(bump(t, EV10.clock1, 0.3), bump(t, EV10.clock2, 0.3), bump(t, EV10.clock3, 0.25));
  const big = pr(t, [EV10.bellBig, EV10.bellBig + 0.3]);
  const hot = pr(t, [EV10.fear, EV10.fear + 0.25]) * (1 - pr(t, [EV10.cardsOut[0], EV10.cardsOut[1]]));   // 说到“怕漏”：群那一行亮暖黄
  return (
    <g>
      <rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} fill="url(#gWall)" />
      <circle cx={SC_.x + 80} cy={SC_.y + 520} r={170} fill="#8C6BC8" opacity={0.35} filter="url(#fBlur28)" />
      <circle cx={SC_.x + 330} cy={SC_.y + 260} r={140} fill="#5FA3D9" opacity={0.3} filter="url(#fBlur28)" />
      <g transform={`translate(${SC_.x + SC_.w / 2} ${SC_.y + 118}) scale(${1 + 0.12 * flip})`}>
        <Tx x={0} y={0} size={104} anchor="middle" weight={300} fill={mixHex('#EEF2FA', C.warm, flip)}>{lockTime(t)}</Tx>
      </g>
      {!other && EV10.rings.map((a, i) => {
        if (t < a) return null;
        const u = po(t, [a, a + 0.25]);
        const stacked = i === 0 && t >= EV10.rings[1] ? 180 * po(t, [EV10.rings[1], EV10.rings[1] + 0.25]) : 0;
        const y = SC_.y + 200 + stacked - 70 * (1 - u);
        return (
          <g key={i} opacity={pr(t, [a, a + 0.12])}>
            <rect x={SC_.x + 10} y={y} width={SC_.w - 20} height={166} rx={26} fill="#1E2230" opacity={0.94} />
            <AppIcon x={SC_.x + 46} y={y + 50} size={52} kind="chat" />
            <Tx x={SC_.x + 82} y={y + 50} size={50}>班级群</Tx>
            <Tx x={SC_.x + 30} y={y + 118} size={52} weight={700}>{['收到', '+1'][i]}</Tx>
          </g>
        );
      })}
      {other && t >= EV10.bell && (
        <g opacity={pr(t, [EV10.bell, EV10.bell + 0.2])}>
          <rect x={SC_.x + 10} y={SC_.y + SC_.h - 150} width={SC_.w - 20} height={96} rx={24} fill={mixHex('#1E2230', '#3A3320', hot)} opacity={0.9} />
          {hot > 0 && <rect x={SC_.x + 10} y={SC_.y + SC_.h - 150} width={SC_.w - 20} height={96} rx={24} fill="none" stroke={C.warm} strokeWidth={5} opacity={hot} />}
          <g transform={`translate(${SC_.x + 50} ${SC_.y + SC_.h - 102})`}><MuteBell s={0.75} color={mixHex('#AEB4C0', C.warm, hot)} bg="#1E2230" /></g>
          <Tx x={SC_.x + 86} y={SC_.y + SC_.h - 102} size={50} fill={mixHex('#C9CED8', C.warm, hot)}>班级群 99+</Tx>
        </g>
      )}
      {big > 0 && <g transform={`translate(${SC_.x + SC_.w / 2} ${SC_.y + 340}) scale(${0.7 + 0.3 * easeBack(big)})`} opacity={big}><MuteBell s={4.4} color="#F4F5F8" bg="#54608F" /></g>}
    </g>
  );
};

const PhoneScreen: React.FC<{t: number}> = ({t}) => {
  let page: React.ReactNode;
  if (t < EV10.chatIn[1]) page = <><ListPage t={t} />{t >= EV10.chatIn[0] && <ChatPage t={t} bell={false} fresh={EV10.msgs} slideFrom={EV10.chatIn[0]} />}</>;
  else if (t < EV10.tagNo) page = <ChatPage t={t} bell={false} fresh={EV10.msgs} />;
  else if (t >= EV10.open1 && t < EV10.close1) page = <ChatPage t={t} bell slideFrom={EV10.open1} />;
  else if (t >= EV10.open2 && t < EV10.close2) page = <ChatPage t={t} bell slideFrom={EV10.open2} />;
  else page = <LockPage t={t} />;
  return (
    <g>
      <clipPath id="n10scr"><rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} rx={52} /></clipPath>
      <g clipPath="url(#n10scr)">
        {page}
        <rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} fill="#FFFFFF" opacity={0.14 * screenFlash(t)} />
        <StatusBar s={SC_} />
      </g>
    </g>
  );
};

const DeskScene: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const pose = deskPose(t);
  const expr = deskExpr(t);
  const look = lookAt(t);
  const sk0 = shake(t);
  const deskX = HOOK.x + 30 * HOOK.s;
  const fl = screenFlash(t);
  const sk = solve(pose);
  const glow: Glow = {at: {x: sk.head.x + 45, y: sk.head.y + 5}, color: '#BFD4FF', amount: 0.16 + 0.24 * fl, r: 110};
  const pc = {x: PB.x + PB.w / 2, y: PB.y + PB.h / 2};
  return (
    <g>
      <RoomBase />
      <g transform={DESK_XF}>
        <Lamp x={940} k={1} f={fr} spread={1.15} floorY={HOOK.G + 6} seed="hook" />
        <ellipse cx={pc.x} cy={pc.y} rx={520} ry={560} fill="url(#gScreenLight)" opacity={0.35 + 0.4 * fl} style={{mixBlendMode: 'screen'}} />
        <Chair x={HOOK.x - 10 * HOOK.s} y={HOOK.G} s={HOOK.s} />
        <rect x={deskX + 14} y={DESK_Y - 9} width={96} height={9} rx={3} fill="#9AA3B2" />
        <path d={`M ${deskX + 102} ${DESK_Y - 6} L ${deskX + 114} ${DESK_Y - 6} L ${deskX + 136} ${DESK_Y - 118} L ${deskX + 124} ${DESK_Y - 118} Z`} fill="#B7C0CE" />
        <path d={`M ${deskX + 100} ${DESK_Y - 8} L ${deskX + 122} ${DESK_Y - 116}`} stroke="#DCE7FF" strokeWidth={3} opacity={0.6} />
        <You fr={fr} look={look} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="body" glow={glow} />
        <Shadow x={deskX + 180} y={HOOK.G + 4} rx={220} ry={14} o={0.55} />
        <rect x={deskX} y={DESK_Y} width={360} height={18} rx={4} fill={C.woodTop} />
        <rect x={deskX} y={DESK_Y} width={360} height={5} rx={2.5} fill="#7A6652" />
        <rect x={deskX + 16} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <rect x={deskX + 330} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <g transform={`translate(${sk0.dx} 0) rotate(${sk0.rot} ${pc.x} ${pc.y})`}>
          <PhoneBody b={PB} />
          <PhoneScreen t={t} />
        </g>
        <You fr={fr} look={look} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="arms" glow={glow} />
      </g>
      <Overlays t={t} />
    </g>
  );
};

// 画面坐标的东西：贴纸、冒出来的消息、虚线卡
const TAG_X = 1765, TAG_Y = 300;
const BUB = [
  {x: 620, y: 200, s: '收到'}, {x: 330, y: 300, s: '+1'}, {x: 110, y: 170, s: '好的'}, {x: 520, y: 400, s: '[图片]'}, {x: 170, y: 440, s: '收到'}, {x: 700, y: 560, s: '+1'},
  {x: 380, y: 590, s: '哈哈哈'}, {x: 90, y: 620, s: '1'}, {x: 1680, y: 480, s: '收到'}, {x: 1720, y: 640, s: '+1'}, {x: 1660, y: 200, s: '好的'}, {x: 860, y: 150, s: '收到'}, {x: 240, y: 90, s: '+1'}, {x: 560, y: 60, s: '好的'},
];
const Overlays: React.FC<{t: number}> = ({t}) => {
  const tags: {at: number; out: number; text: string; x: number; y: number; size?: number}[] = [
    {at: EV10.tagNo, out: EV10.cut - 0.01, text: '没开免打扰', x: TAG_X, y: TAG_Y, size: 52},
    {at: EV10.tagMute, out: EV10.thread[0], text: '开了免打扰', x: TAG_X, y: TAG_Y, size: 52},
    {at: EV10.bellBig, out: EV10.fadeOut[0], text: '开了免打扰', x: TAG_X, y: TAG_Y, size: 52},
    {at: EV10.unseen, out: EV10.cardsOut[0], text: '没看到？', x: 400, y: 700, size: 56},
  ];
  const bubO = 1 - pr(t, EV10.bubblesOut);
  return (
    <g>
      {t >= EV10.bubbles[0] && bubO > 0 && BUB.map((b, i) => {
        const a = EV10.bubbles[0] + (EV10.bubbles[1] - EV10.bubbles[0]) * Math.pow(i / (BUB.length - 1), 0.8);
        if (t < a) return null;
        const u = easeBack(pr(t, [a, a + 0.2]));
        const w = tw(b.s, 54) + 44, h = 84;
        return (
          <g key={i} opacity={clamp((t - a) * 6) * bubO} transform={`translate(${b.x} ${b.y - 10 * (t - a)}) scale(${u})`}>
            <rect x={5} y={10} width={w} height={h} rx={18} fill="#000" opacity={0.4} filter="url(#fBlur8)" />
            <rect width={w} height={h} rx={18} fill="#2F343F" stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />
            <Tx x={22} y={h / 2} size={54} fill="#E4E7ED">{b.s}</Tx>
          </g>
        );
      })}
      {[{at: EV10.cardA, y: 400, s: '王老师：明早8点前交表'}, {at: EV10.cardB, y: 530, s: '领导：下午三点开会'}].map((c, i) => {
        if (t < c.at || t >= EV10.cardsOut[1]) return null;
        const u = po(t, [c.at, c.at + 0.3]);
        const o = pr(t, [c.at, c.at + 0.2]) * (1 - pr(t, EV10.cardsOut));
        const w = tw(c.s, 52) + 60;
        return (
          <g key={i} opacity={o} transform={`translate(${70 - 30 * (1 - u)} ${c.y})`}>
            <rect width={w} height={104} rx={22} fill="rgba(74,61,28,0.55)" stroke={C.warm} strokeWidth={4} strokeDasharray="16 12" />
            <Tx x={30} y={52} size={52} fill="#FFE7AE">{c.s}</Tx>
          </g>
        );
      })}
      {tags.map((s, i) => {
        if (t < s.at || t >= s.out + 0.2) return null;
        return <Sticker key={i} x={s.x} y={s.y} text={s.text} size={s.size ?? 56} pop={easeBack(pr(t, [s.at, s.at + 0.25]))} o={1 - pr(t, [s.out, s.out + 0.2])} />;
      })}
    </g>
  );
};

// 大字（HTML）：开头的题目、怕漏、全关 不一定治得了 怕漏
const BIG: React.CSSProperties = {position: 'absolute', fontFamily: SANS, fontWeight: 800, textAlign: 'center', whiteSpace: 'nowrap', textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'};
const BigText: React.FC<{t: number}> = ({t}) => {
  const titleO = 1 - pr(t, [EV10.tagNo - 0.15, EV10.tagNo]);
  const fearIn = t >= EV10.fear && t < EV10.cardsOut[1];
  const fearU = easeBack(pr(t, [EV10.fear, EV10.fear + 0.3]));
  const fearO = pr(t, [EV10.fear, EV10.fear + 0.1]) * (1 - pr(t, EV10.cardsOut));
  const lines = [{at: EV10.line1, s: '全关', size: 124, y: 150, c: CREAM}, {at: EV10.line2, s: '不一定治得了', size: 100, y: 318, c: CREAM}, {at: EV10.line3, s: '怕漏', size: 176, y: 470, c: C.warm}];
  const lineO = 1 - pr(t, EV10.fadeOut);
  return (
    <>
      {titleO > 0 && <div style={{...BIG, left: 0, width: 1920, top: 26, fontWeight: 700, fontSize: 88, lineHeight: '106px', color: '#FFF8EC', opacity: titleO}}>群里又 99+</div>}
      {fearIn && <div style={{...BIG, left: 60, width: 640, top: 130, fontSize: 190, lineHeight: '220px', color: C.warm, opacity: fearO, transform: `scale(${0.7 + 0.3 * fearU})`}}>怕漏</div>}
      {lines.map((l, i) => (t >= l.at && lineO > 0 ? (
        <div key={i} style={{...BIG, left: 60, width: 640, top: l.y, fontSize: l.size, lineHeight: `${l.size * 1.2}px`, color: l.c, opacity: pr(t, [l.at, l.at + 0.12]) * lineO, transform: `scale(${(0.8 + 0.2 * easeBack(pr(t, [l.at, l.at + 0.25]))) * (1 + (i === 2 ? 0.2 : 0.06) * pr(t, [l.at + 0.25, EV10.fadeOut[0]]))})`}}>{l.s}</div>
      ) : null))}
    </>
  );
};

// 办法放在简介
const Hint: React.FC<{t: number}> = ({t}) => {
  const u = po(t, EV10.hintIn);
  const bob = 20 * Math.sin((t - EV10.hintIn[0]) * 5);
  const push = 1 + 0.1 * pr(t, [EV10.hintIn[1], SC10.end]);       // 慢慢推近，不让整幅停住
  return (
    <>
      <div style={{...BIG, left: 0, width: 1920, top: 330, fontSize: 104, lineHeight: '130px', color: '#FFF8EC', opacity: u, transform: `translateY(${(1 - u) * 24}px) scale(${push})`}}>办法放在简介</div>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', opacity: u}}>
        <path d={`M 960 ${500 + bob} v 90 m -40 -40 l 40 40 l 40 -40`} fill="none" stroke={C.warm} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </>
  );
};

// 结尾：问句，空框里轮流闪过几个群名
const GUESS = ['班级群', '工作群', '家长群', '小区群'];
const Ending: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const u = po(t, EV10.endIn);
  const cur = Math.floor((t - EV10.endIn[1]) / 0.5) % 2 === 0;
  return (
    <>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <FilmDefs3 />
        <RoomBase />
        <Lamp x={960} k={0.9} f={fr} spread={1.2} seed="end" />
        <Vignette3 o={0.8} />
      </svg>
      <div style={{...BIG, left: 0, width: 1920, top: 220, fontSize: 116, lineHeight: '146px', color: '#FFF8EC', opacity: u, transform: `scale(${lerp(0.9, 1, easeBack(u))})`}}>你最怕漏哪个群？</div>
      <div style={{position: 'absolute', left: 660, top: 440, width: 600, height: 150, borderRadius: 24, border: `6px solid ${C.warm}`, background: 'rgba(0,0,0,0.4)', opacity: pr(t, [EV10.endIn[0] + 0.3, EV10.endIn[0] + 0.5])}}>
        <div style={{position: 'absolute', left: 40, top: 26, width: 8, height: 90, background: C.warm, opacity: cur ? 1 : 0}} />
        {EV10.guess.map((a, i) => {
          const b = a + 0.62;
          if (t < a || t >= b) return null;
          return <div key={i} style={{position: 'absolute', left: 70, top: 26, fontFamily: SANS, fontWeight: 600, fontSize: 80, lineHeight: '96px', color: C.soft, opacity: pr(t, [a, a + 0.1]) * (1 - pr(t, [b - 0.1, b]))}}>{GUESS[i]}</div>;
        })}
      </div>
    </>
  );
};

// ================= 字幕 =================
const SubText: React.FC<{beat: Beat10; t: number}> = ({beat, t}) => {
  if (!beat.sub.length) return null;
  const size = 64;
  const o = pr(t, [beat.t0, beat.t0 + 0.07]);
  return (
    <div style={{position: 'absolute', left: 0, width: 1920, top: 1000 - size * 0.98, height: size * 1.2, display: 'flex', justifyContent: 'center',
      fontFamily: SANS, fontWeight: 600, fontSize: size, lineHeight: `${size * 1.2}px`, color: CREAM, whiteSpace: 'pre', opacity: o, textShadow: SHADOW}}>
      {beat.sub.map((sg: Seg10, i) => (typeof sg === 'string'
        ? <span key={i}>{sg}</span>
        : <span key={i} style={{color: sg[1] === 'warm' ? C.warm : C.gray}}>{sg[0]}</span>))}
    </div>
  );
};
const LowBand: React.FC = () => (
  <div style={{position: 'absolute', left: 0, top: 880, width: 1920, height: 200,
    background: 'linear-gradient(180deg, rgba(8,9,13,0) 0%, rgba(8,9,13,0.8) 40%, rgba(8,9,13,0.92) 100%)'}} />
);

export const Notice10: React.FC<{atFrame?: number}> = ({atFrame}) => {
  const cf = useCurrentFrame();
  const fr = atFrame ?? cf;                       // 封面用：固定画某一帧
  const t = fr / FPS10;
  const b = beatAt10(t);
  const desk = t < SC10.end;
  const hint = t >= SC10.hint[0] && t < SC10.end;
  const end = t >= SC10.end;
  const dim = 0.86 * pr(t, EV10.fadeOut);
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {desk && (
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <FilmDefs3 />
          <DeskScene t={Math.min(t, EV10.fadeOut[1])} fr={fr} />
          <Vignette3 o={0.85} />
          {dim > 0 && <rect width={1920} height={1080} fill="#0A0B0F" opacity={dim} />}
        </svg>
      )}
      {desk && !hint ? <SubBand3 /> : <LowBand />}
      {desk && <BigText t={t} />}
      {hint && <Hint t={t} />}
      {end && <Ending t={t} fr={fr} />}
      <SubText beat={b} t={t} />
      <AiBadge />
    </AbsoluteFill>
  );
};
