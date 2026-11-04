// 003《消息提醒》第八版成片画面（Notice003V8）。秒数、字幕、事件全读 timeline8.ts（照 videos/003_消息提醒/文案.md 第八版，11/02 锁定）。
// 场景：桌前（0–3.4、7.6–16.6、46.2–55.4）→ 两张看数大卡（3.4–7.6）→ 微信群聊设置页（16.6–46.2）→ 顺带（55.4–61）→ 清单屏（61–66.2）→ 结尾。
// 桌前那套（暗房间、暖灯、成片小人、真手机、横幅喷满再震散）照 Gray003.tsx 的成片画法搬过来，按第八版的事件重排；设置页、顺带、清单、结尾是新画的。
// 设置页是示意界面，全用代码画，不用截图；不画任何 App 的商标。
import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {Chair} from '../../components/people/FlatProps';
import {EXPR, Expr, blink, breath, mixExpr, withBlink} from '../../components/people/face';
import {ME} from '../../components/people/look';
import {mixHex} from '../../components/people/geom';
import {Pose, RPose, mixPose, nudge, poseDef, resolve, solve} from '../../components/people/rig';
import {FPerson} from '../002/film/FPerson';
import {AiBadge, AppIcon, CREAM, FilmDefs3, LAMP, Lamp, PhoneBody, RoomBase, SHADOW, Shadow, Sticker, StatusBar, SubBand3, Vignette3} from './film';
import {Beat8, EV8, FPS8, FRAMES8, SC8, Seg8, beatAt8} from './timeline8';

export const NOTICE8_FRAMES = FRAMES8;

const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
const C = {
  bg: '#101219', ink: '#F4F5F8', soft: '#B9BEC9', gray: '#8A8F99', warm: '#FFC94D', warmBg: '#4A3D1C',
  red: '#FF5A4E', green: '#3CC27A', wood: '#3F352D', woodTop: '#5A4B3E',
  page: '#111318', row: '#1C1F27', line: '#2A2E38', off: '#3A3E48',
};

// —— 小工具（同 Gray003.tsx）——
const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => {
  const x = clamp(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
const easeOut = (t: number) => 1 - Math.pow(1 - clamp(t), 3);
const easeIn = (t: number) => Math.pow(clamp(t), 3);
const easeBack = (t: number) => {
  const x = clamp(t), c1 = 1.70158, c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};
const pr = (t: number, ab: number[]) => clamp((t - ab[0]) / Math.max(1e-6, ab[1] - ab[0]));
const pe = (t: number, ab: number[]) => ease(pr(t, ab));
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

// ================= 人和姿势（同 Gray003.tsx） =================
const BOARD = poseDef('board');
const P = (base: Pose, o: Pose) => resolve({...base, ...o});
const DESK = P(BOARD, {neck: 4, pitch: 0.3, yaw: 0.45, gaze: {x: 1, y: 0.5}});
const DESK_UP = P(BOARD, {lean: 3, neck: -6, pitch: -0.05, yaw: 0.5, gaze: {x: 1, y: -0.15}});
const DESK_READ = P(BOARD, {lean: 9, chest: 4, neck: -2, pitch: 0.05, yaw: 0.5, gaze: {x: 1, y: 0}});
const DESK_SLUMP = P(BOARD, {lean: 6, chest: 9, neck: 6, shrug: -0.8, pitch: 0.2, yaw: 0.5, gaze: {x: 1, y: 0}});
const DESK_BACK = P(BOARD, {lean: -6, chest: -2, neck: -2, pitch: 0.1, yaw: 0.45, gaze: {x: 1, y: 0.2}});
const DESK_NOD = P(BOARD, {lean: 4, neck: 4, pitch: 0.25, yaw: 0.5, gaze: {x: 1, y: 0.1}});
const E = EXPR;
const SMILE: Expr = {...E.calm, smile: 0.6, lid: 0.2, blush: 0.7};

type Glow = {at: {x: number; y: number}; color: string; amount: number; r?: number};
const You: React.FC<{fr: number; pose: RPose; expr: Expr; x: number; G: number; s: number; seed: string; part?: 'all' | 'body' | 'arms'; glow?: Glow}> = (
  {fr, pose, expr, x, G, s, seed, part, glow},
) => {
  const b = breath(fr);
  const r = nudge(pose, {shrug: 0.08 * b, chest: -0.7 * b});
  const e = withBlink(expr, blink(fr, seed));
  return <FPerson pose={r} expr={e} look={ME} x={x} y={G} s={s} facing={1} night="#0B0D12" light={{x: -0.25, y: -1}} part={part}
    tint={{color: LAMP, amount: 0.07}} glow={glow} />;
};

// ================= 桌前 =================
const HOOK = {x: 880, G: 900, s: 1.9};
const DESK_Y = HOOK.G - 88 * HOOK.s;
const PB = {x: 1080, y: 180, w: 420, h: 720};
const SC = {x: PB.x + 14, y: PB.y + 14, w: PB.w - 28, h: PB.h - 28};
const HS = 1.04, HX = 50.8, HY = -46.2;          // 画面 X = HS·x + HX，Y = HS·y + HY
const PUSH_C = {x: 987, y: 680};
const CAM_PUSH = [7.6, 8.35], CAM_BACK = [8.5, 9.0];
const pushK = (t: number) => 1 + 0.15 * pe(t, CAM_PUSH) * (1 - pe(t, CAM_BACK));
const deskXf = (t: number) => {
  const k = pushK(t);
  return `translate(${PUSH_C.x} ${PUSH_C.y}) scale(${k}) translate(${-PUSH_C.x} ${-PUSH_C.y}) translate(${HX} ${HY}) scale(${HS})`;
};
const toScreen = (x: number, y: number) => ({x: HS * x + HX, y: HS * y + HY});

const deskPose = (t: number) => ptrack(t, [
  [0, DESK], [EV8.buzz[0], DESK_UP, 0.3], [EV8.chatIn[0], DESK_READ, 0.4], [EV8.slump[0], DESK_SLUMP, 0.5],
  [SC8.settings[1], DESK_UP, 0.01], [EV8.turnBack[0], DESK, 0.4], [EV8.look[0], DESK_UP, 0.3], [EV8.nod[0], DESK_NOD, 0.2], [EV8.nod[0] + 0.25, DESK_BACK, 0.4],
]);
const deskExpr = (t: number) => etrack(t, [
  [0, E.calm], [EV8.buzz[0], {...E.surprise, open: 0.3}, 0.15], [1.0, E.calm, 0.4], [EV8.burst[0], {...E.surprise, open: 0.5}, 0.15],
  [EV8.keyA, E.worry, 0.3], [EV8.silentTag, E.sad, 0.3], [EV8.noisy[0], {...E.surprise, open: 0.3}, 0.15], [EV8.slump[0], E.sad, 0.4],
  [SC8.settings[1], E.calm, 0.01], [EV8.testOk, SMILE, 0.3], [EV8.turnBack[0], E.calm, 0.4], [EV8.look[0], SMILE, 0.3],
]);

// 手机响：每响一下抖 8 帧、屏幕一闪
const RINGS = [...EV8.buzz, ...EV8.noisy, EV8.testMsg, EV8.keyRing];
const shake = (t: number) => {
  const f = Math.round(t * FPS8);
  const on = RINGS.some((b) => f >= Math.round(b * FPS8) && f < Math.round(b * FPS8) + 8) || (t >= EV8.countRun[0] && t < EV8.countRun[1]);
  if (!on) return {dx: 0, rot: 0};
  const k = f % 2 === 0 ? 1 : -1;
  return {dx: 5 * k, rot: 2 * k};
};
const screenFlash = (t: number) => {
  let v = 0;
  for (const a of RINGS) v = Math.max(v, bump(t, a, 0.35));
  if (t >= EV8.countRun[0] && t < EV8.countRun[1]) v = Math.max(v, 0.6 * Math.abs(Math.sin(t * 38)));
  return v;
};

type Ban = {at: number; title: string; icon: 'bag' | 'chat' | 'flame'; sub?: string; warm?: boolean; out?: number};
const BANS_A: Ban[] = [
  {at: EV8.buzz[0], title: '限时秒杀', icon: 'bag'},
  {at: EV8.buzz[1], title: '热点新闻', icon: 'flame'},
  {at: EV8.buzz[2], title: '工作群(52)', icon: 'chat'},
  {at: EV8.buzz[3], title: '家长群(12)', icon: 'chat'},
];
const BANS_C: Ban[] = [
  {at: EV8.testMsg, title: '班级群 · 小李', icon: 'chat', sub: '@你 测试一下', out: EV8.quiet[0] - 0.3},
  {at: EV8.keyRing, title: '班级群 · 王老师', icon: 'chat', sub: '明早8点前交表', warm: true},
];
const BANNER_Y = SC.y + 200;
const Banners: React.FC<{t: number; list: Ban[]}> = ({t, list}) => {
  const BH = 100, SUBH = 66;
  const hgt = (b: Ban) => BH + (b.sub ? SUBH : 0);
  return (
    <g>
      {list.map((n, i) => {
        if (t < n.at) return null;
        const fade = n.out !== undefined ? 1 - pr(t, [n.out, n.out + 0.25]) : 1;
        if (fade <= 0) return null;
        const below = list.reduce((s, m, j) => (j > i && t >= m.at && (m.out === undefined || t < m.out) ? s + (hgt(m) + 14) * po(t, [m.at, m.at + 0.25]) : s), 0);
        const y = BANNER_Y + below - 70 * (1 - po(t, [n.at, n.at + 0.25]));
        const o = pr(t, [n.at, n.at + 0.12]) * fade;
        const h = hgt(n);
        return (
          <g key={i} opacity={o}>
            <rect x={SC.x + 10} y={y + 6} width={SC.w - 20} height={h} rx={26} fill="#000" opacity={0.3} filter="url(#fBlur8)" />
            <rect x={SC.x + 10} y={y} width={SC.w - 20} height={h} rx={26} fill={n.warm ? '#3A3320' : '#1E2230'} opacity={0.92} />
            <rect x={SC.x + 10} y={y} width={SC.w - 20} height={h} rx={26} fill="none" stroke={n.warm ? C.warm : '#FFFFFF'} strokeOpacity={n.warm ? 1 : 0.08} strokeWidth={n.warm ? 4 : 2} />
            <AppIcon x={SC.x + 46} y={y + 50} size={52} kind={n.icon} />
            <Tx x={SC.x + 82} y={y + 50} size={n.sub ? 42 : 54} weight={600} fill="#F4F5F8">{n.title}</Tx>
            {n.sub && <Tx x={SC.x + 30} y={y + BH + 18} size={52} weight={700} fill={n.warm ? C.warm : '#F4F5F8'}>{n.sub}</Tx>}
          </g>
        );
      })}
    </g>
  );
};

// 群聊：消息从下往上排（最后一条贴底），新消息进来整列往上推
type Msg = {who?: string; text: string; key?: 'warm'; at?: number; hiAt?: number};
const BASE: Msg[] = [
  {text: '收到'}, {text: '+1'}, {text: '[图片]'}, {text: '好的'}, {text: '收到'}, {text: '哈哈哈'}, {text: '1'}, {text: '收到'},
  {who: '@所有人', text: '明早8点前交表', key: 'warm', hiAt: EV8.keyA}, {text: '+1'}, {text: '收到'},
  {who: '王老师', text: '周五开家长会', key: 'warm', hiAt: EV8.keyB}, {text: '好的'},
];
const ADDED: Msg[] = [
  {who: '王老师', text: '明天穿校服', key: 'warm', at: EV8.silentMsg, hiAt: EV8.silentMsg},
  ...EV8.noisy.map((a, i) => ({text: ['收到', '+1', '好的', '收到', '+1'][i], at: a})),
];
const MH = (m: Msg) => (m.who ? 132 : 76);
const GAP = 12;
const ChatPage: React.FC<{t: number}> = ({t}) => {
  const slide = po(t, EV8.chatIn);
  const scrollOff = 6 * 88 * (1 - easeOut(pr(t, EV8.chatScroll)));   // 一开始停在上面 6 条，滚到底
  const list = [...BASE, ...ADDED.filter((m) => t >= (m.at ?? 0))];
  const bottom = SC.y + SC.h - 40;
  let y = bottom + scrollOff;
  const rows: React.ReactNode[] = [];
  for (let i = list.length - 1; i >= 0; i--) {
    const m = list[i];
    // 新进来的那条：0.2 秒从下面顶上来
    const inU = m.at !== undefined ? po(t, [m.at, m.at + 0.2]) : 1;
    const h = MH(m) * inU;
    y -= h;
    if (y + h < SC.y + 100) break;
    const key = m.key === 'warm';
    const hl = key && m.hiAt !== undefined ? pe(t, [m.hiAt, m.hiAt + 0.25]) : 0;
    const w = Math.max(tw(m.text, 50), m.who ? tw(m.who, 44) : 0) + 34;
    rows.push(
      <g key={i} opacity={inU}>
        {hl > 0 && <rect x={SC.x + 2} y={y - 6} width={w + 22} height={MH(m) - GAP + 12} rx={20} fill={C.warm} opacity={0.2 * hl} />}
        <rect x={SC.x + 12} y={y} width={w} height={MH(m) - GAP} rx={14} fill={key ? mixHex('#2A2E37', C.warmBg, hl) : '#2A2E37'} stroke={C.warm} strokeWidth={5 * hl} />
        {m.who && <Tx x={SC.x + 28} y={y + 34} size={44} fill={mixHex('#C9CED8', C.warm, hl)}>{m.who}</Tx>}
        <Tx x={SC.x + 28} y={y + (m.who ? 88 : (MH(m) - GAP) / 2)} size={50} fill={key ? mixHex(C.ink, C.warm, hl) : '#D5D9E0'}>{m.text}</Tx>
      </g>,
    );
    y -= GAP * 0;
  }
  const bell = t >= EV8.bellOn && t < EV8.bellOff + 0.2 ? po(t, [EV8.bellOn, EV8.bellOn + 0.2]) * (1 - pr(t, [EV8.bellOff, EV8.bellOff + 0.2])) : 0;
  return (
    <g transform={`translate(${SC.w * (1 - slide)} 0)`}>
      <rect x={SC.x - 20} y={SC.y} width={SC.w + 20} height={SC.h} fill="#111318" />
      {rows}
      <rect x={SC.x} y={SC.y} width={SC.w} height={116} fill="#1C1F26" />
      <path d={`M ${SC.x + 32} ${SC.y + 66} l -13 13 l 13 13`} fill="none" stroke="#F4F5F8" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
      <Tx x={SC.x + SC.w / 2 - 20 * bell} y={SC.y + 80} size={52} anchor="middle">班级群</Tx>
      {bell > 0 && <g transform={`translate(${SC.x + SC.w - 52} ${SC.y + 80}) scale(${0.8 + 0.2 * easeBack(bell)})`} opacity={bell}><MuteBell s={0.9} /></g>}
    </g>
  );
};
const MuteBell: React.FC<{s?: number; color?: string}> = ({s = 1, color = '#F4F5F8'}) => (
  <g transform={`scale(${s})`}>
    <path d="M -16 10 L -16 -4 Q -16 -20 0 -20 Q 16 -20 16 -4 L 16 10 L 21 15 L -21 15 Z" fill={color} />
    <circle cx={0} cy={21} r={5} fill={color} />
    <line x1={-22} y1={-22} x2={22} y2={24} stroke="#111318" strokeWidth={8} />
    <line x1={-22} y1={-22} x2={22} y2={24} stroke={color} strokeWidth={4} strokeLinecap="round" />
  </g>
);

// 锁屏（开头、测一下、只在该响的时候响）
const LockPage: React.FC<{t: number}> = ({t}) => {
  const late = t >= SC8.settings[1];
  // 50.4–52.8：群里还在进（免打扰），只在锁屏底下一行灰字里涨，不亮不抖
  const quietOn = late && t >= EV8.quiet[0];
  const n = quietOn ? Math.min(9, 1 + Math.floor((t - EV8.quiet[0]) / 0.3)) : 0;
  return (
    <g>
      <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill="url(#gWall)" />
      <circle cx={SC.x + 80} cy={SC.y + 520} r={170} fill="#8C6BC8" opacity={0.35} filter="url(#fBlur28)" />
      <circle cx={SC.x + 330} cy={SC.y + 260} r={140} fill="#5FA3D9" opacity={0.3} filter="url(#fBlur28)" />
      <Tx x={SC.x + SC.w / 2} y={SC.y + 118} size={104} anchor="middle" weight={300} fill="#EEF2FA">{late ? '20:47' : '20:31'}</Tx>
      <Banners t={t} list={late ? BANS_C : BANS_A} />
      {quietOn && (
        <g opacity={pr(t, [EV8.quiet[0], EV8.quiet[0] + 0.2])}>
          <rect x={SC.x + 10} y={SC.y + SC.h - 150} width={SC.w - 20} height={96} rx={24} fill="#1E2230" opacity={0.7} />
          <g transform={`translate(${SC.x + 50} ${SC.y + SC.h - 102})`}><MuteBell s={0.75} color="#AEB4C0" /></g>
          <Tx x={SC.x + 86} y={SC.y + SC.h - 102} size={44} fill="#C9CED8">{n} 条新消息</Tx>
        </g>
      )}
    </g>
  );
};

const PhoneScreen: React.FC<{t: number}> = ({t}) => {
  const chat = t >= EV8.chatIn[0] && t < SC8.settings[0];
  const lockUnder = t < EV8.chatIn[1] || t >= SC8.settings[1];
  return (
    <g>
      <clipPath id="n8scr"><rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} rx={52} /></clipPath>
      <g clipPath="url(#n8scr)">
        {lockUnder && <LockPage t={t} />}
        {chat && <ChatPage t={t} />}
        <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill="#FFFFFF" opacity={0.14 * screenFlash(t)} />
        <StatusBar s={SC} />
      </g>
    </g>
  );
};

// 横幅喷满画面再震散（同 Gray003.tsx 的 Burst，按第八版时间）
const BURST_NAMES = ['限时秒杀', '热点新闻', '工作群(52)', '家长群(12)', '快递已签收', '直播开始了', '红包到账', '新闻快讯',
  '小区群(99+)', '你有新消息', '优惠券到期', '同学群(8)', '热搜爆了', '会员续费', '亲戚群(5)', '好友点赞', '外卖已送达', '步数排行',
  '新品上架', '视频更新', '账单提醒', '系统更新', '天气预警', '评论回复', '体力满了', '签到提醒', '班级群(99+)'];
const BURST_ICON: ('bag' | 'chat' | 'flame')[] = ['bag', 'flame', 'chat'];
const HEAD_BOX = {x0: 850, x1: 1100, y0: 400, y1: 660};
const BURST = (() => {
  const rows = [1000, 900, 800, 700, 590, 470, 350, 230, 130];
  const pts: {x: number; y: number; r: number; name: string; icon: 'bag' | 'chat' | 'flame'; w: number}[] = [];
  let n = 0;
  rows.forEach((y, ri) => {
    for (let x = 140 + (ri % 2) * 210; x < 1920 && pts.length < 40; x += 430) {
      const jx = x + (random(`bx${ri}-${x}`) - 0.5) * 90, jy = y + (random(`by${ri}-${x}`) - 0.5) * 40;
      if (jx > HEAD_BOX.x0 - 150 && jx < HEAD_BOX.x1 + 150 && jy > HEAD_BOX.y0 - 40 && jy < HEAD_BOX.y1 - 20) continue;
      const name = BURST_NAMES[n % BURST_NAMES.length];
      pts.push({x: jx, y: jy, r: (random(`br${ri}-${x}`) - 0.5) * 14, name, icon: BURST_ICON[n % 3], w: 120 + tw(name, 56)});
      n++;
    }
  });
  return pts.slice(0, 27);
})();
const BURST_T = BURST.map((_, i) => EV8.burst[0] + (EV8.burst[1] - 0.2 - EV8.burst[0]) * Math.pow(i / (BURST.length - 1), 0.8));
const BURST_FROM = {x: 1392, y: 500};
const Burst: React.FC<{t: number}> = ({t}) => {
  if (t < EV8.burst[0] || t >= EV8.shatter[1]) return null;
  const sh = pr(t, EV8.shatter);
  return (
    <g>
      {BURST.map((b, i) => {
        const s0 = BURST_T[i];
        if (t < s0) return null;
        const u = pr(t, [s0, s0 + 0.22]);
        const e = easeBack(u);
        let x = lerp(BURST_FROM.x, b.x, easeOut(u)), y = lerp(BURST_FROM.y, b.y, easeOut(u));
        let rot = b.r * e, o = clamp(u * 5), sc = lerp(0.3, 1, e);
        if (sh > 0) {
          const dx = b.x - 960, dy = b.y - 540, d = Math.max(1, Math.hypot(dx, dy));
          x += (dx / d) * 520 * easeIn(sh); y += (dy / d) * 520 * easeIn(sh);
          rot += 25 * sh * (b.r >= 0 ? 1 : -1); o *= 1 - sh; sc *= 1 + 0.15 * sh;
        }
        const w = b.w, h = 104;
        return (
          <g key={i} opacity={o} transform={`translate(${x} ${y}) rotate(${rot}) scale(${sc})`}>
            <rect x={-w / 2 + 6} y={-h / 2 + 12} width={w} height={h} rx={28} fill="#000" opacity={0.45} filter="url(#fBlur8)" />
            <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={28} fill="#22273A" />
            <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={28} fill="none" stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />
            <AppIcon x={-w / 2 + 44} y={0} size={56} kind={b.icon} />
            <Tx x={-w / 2 + 84} y={0} size={56} weight={600} fill="#F4F5F8">{b.name}</Tx>
          </g>
        );
      })}
    </g>
  );
};

const DeskScene: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const pose = deskPose(t);
  const expr = deskExpr(t);
  const sk0 = shake(t);
  const deskX = HOOK.x + 30 * HOOK.s;
  const fl = screenFlash(t);
  const sk = solve(pose);
  const glow: Glow = {at: {x: sk.head.x + 45, y: sk.head.y + 5}, color: '#BFD4FF', amount: 0.16 + 0.24 * fl, r: 110};
  const pc = {x: PB.x + PB.w / 2, y: PB.y + PB.h / 2};
  return (
    <g>
      <RoomBase />
      <g transform={deskXf(t)}>
        <Lamp x={940} k={1} f={fr} spread={1.15} floorY={HOOK.G + 6} seed="hook" />
        <ellipse cx={pc.x} cy={pc.y} rx={520} ry={560} fill="url(#gScreenLight)" opacity={0.35 + 0.4 * fl} style={{mixBlendMode: 'screen'}} />
        <Chair x={HOOK.x - 10 * HOOK.s} y={HOOK.G} s={HOOK.s} />
        <rect x={deskX + 14} y={DESK_Y - 9} width={96} height={9} rx={3} fill="#9AA3B2" />
        <path d={`M ${deskX + 102} ${DESK_Y - 6} L ${deskX + 114} ${DESK_Y - 6} L ${deskX + 136} ${DESK_Y - 118} L ${deskX + 124} ${DESK_Y - 118} Z`} fill="#B7C0CE" />
        <path d={`M ${deskX + 100} ${DESK_Y - 8} L ${deskX + 122} ${DESK_Y - 116}`} stroke="#DCE7FF" strokeWidth={3} opacity={0.6} />
        <You fr={fr} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="body" glow={glow} />
        <Shadow x={deskX + 180} y={HOOK.G + 4} rx={220} ry={14} o={0.55} />
        <rect x={deskX} y={DESK_Y} width={360} height={18} rx={4} fill={C.woodTop} />
        <rect x={deskX} y={DESK_Y} width={360} height={5} rx={2.5} fill="#7A6652" />
        <rect x={deskX + 16} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <rect x={deskX + 330} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <g transform={`translate(${sk0.dx} 0) rotate(${sk0.rot} ${pc.x} ${pc.y})`}>
          <PhoneBody b={PB} />
          <PhoneScreen t={t} />
        </g>
        <You fr={fr} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="arms" glow={glow} />
      </g>
      <Burst t={t} />
      <DeskStickers t={t} />
    </g>
  );
};

// 桌前的贴纸（画面坐标）：没提醒（左边，指着手机）、怎么测，看简介
const DeskStickers: React.FC<{t: number}> = ({t}) => {
  const items: {at: number; out: number; text: string; x: number; y: number; ring?: boolean}[] = [
    {at: EV8.silentTag, out: EV8.bellOff, text: '没提醒', x: 1765, y: 620},
    {at: EV8.testTag, out: EV8.quiet[0] - 0.3, text: '怎么测，看简介', x: 470, y: 560},
  ];
  return (
    <g>
      {items.map((s, i) => {
        if (t < s.at || t >= s.out + 0.2) return null;
        const pop = easeBack(pr(t, [s.at, s.at + 0.25]));
        const o = 1 - pr(t, [s.out, s.out + 0.2]);
        return <Sticker key={i} x={s.x} y={s.y} text={s.text} size={56} pop={pop} o={o} />;
      })}
      {t >= EV8.testOk && t < EV8.quiet[0] && (() => {
        const p = toScreen(PB.x + PB.w - 40, PB.y + 230);
        const u = easeBack(pr(t, [EV8.testOk, EV8.testOk + 0.3]));
        const o = 1 - pr(t, [EV8.quiet[0] - 0.3, EV8.quiet[0]]);
        return (
          <g transform={`translate(${p.x + 40} ${p.y}) scale(${u})`} opacity={o}>
            <circle r={52} fill={C.green} />
            <path d="M -22 2 L -6 18 L 24 -16" fill="none" stroke="#FFFFFF" strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
          </g>
        );
      })()}
    </g>
  );
};

// 计数（桌前左边）
const deskCount = (t: number) => {
  let n = 0;
  EV8.buzz.forEach((a, i) => { if (t >= a) n = i + 1; });
  if (t >= EV8.countRun[0]) n = Math.round(4 + 83 * Math.pow(pr(t, EV8.countRun), 1.25));
  EV8.noisy.forEach((a) => { if (t >= a) n += 1; });
  return n;
};
const COUNTER_AT = {x: 230, y: 514};
const DeskText: React.FC<{t: number}> = ({t}) => {
  const showCount = t < SC8.settings[0] && !(t >= SC8.cards[0] && t < SC8.cards[1]);
  const titleO = 1 - pr(t, [SC8.cards[0], SC8.cards[0] + 0.2]);
  const n = deskCount(t);
  let pop = 0;
  for (const a of [...EV8.buzz, ...EV8.noisy]) pop = Math.max(pop, bump(t, a, 0.25));
  const k = pushK(t);
  const cx = (COUNTER_AT.x - PUSH_C.x) * k + PUSH_C.x, cy = (COUNTER_AT.y - PUSH_C.y) * k + PUSH_C.y;
  const inBurst = t >= EV8.burst[0] && t < CAM_BACK[1];
  return (
    <>
      {titleO > 0 && (
        <div style={{position: 'absolute', left: 0, width: 1920, top: 26, textAlign: 'center', fontFamily: SANS, fontWeight: 700, fontSize: 88, lineHeight: '106px',
          color: '#FFF8EC', opacity: titleO, textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'}}>你今天收到多少条通知？</div>
      )}
      {showCount && (
        <div style={{position: 'absolute', left: cx, top: cy, fontFamily: SANS, fontWeight: 600, fontSize: 60, color: CREAM, whiteSpace: 'nowrap', lineHeight: '72px',
          transformOrigin: 'center center', transform: `scale(${1 + 0.1 * pop})`, textShadow: SHADOW,
          background: inBurst ? 'rgba(10,11,16,0.92)' : 'transparent', borderRadius: 16, padding: '0 14px'}}>
          今天收到<span style={{fontVariantNumeric: 'tabular-nums', display: 'inline-block', textAlign: 'center', background: 'rgba(0,0,0,0.45)', borderRadius: 14,
            margin: '0 10px', minWidth: 110}}>{n}</span>条
        </div>
      )}
    </>
  );
};

// ================= 两张看数大卡 3.4–7.6 =================
const Cards: React.FC<{t: number}> = ({t}) => {
  const inU = po(t, EV8.cardsIn);
  const out = 1 - pr(t, EV8.cardsOut);
  const leftOn = t >= EV8.cardL && t < EV8.cardR;
  const rightOn = t >= EV8.cardR;
  const rIn = po(t, [EV8.cardR, EV8.cardR + 0.25]);
  const card = (x: number, on: boolean, kids: React.ReactNode) => (
    <div style={{position: 'absolute', left: x, top: 110, width: 840, height: 740, borderRadius: 40, background: '#1C2029',
      border: `6px solid ${on ? C.warm : '#2E3440'}`, boxShadow: on ? '0 0 40px rgba(255,201,77,0.25)' : 'none', fontFamily: SANS, color: C.ink, padding: '50px 60px', boxSizing: 'border-box'}}>
      {kids}
    </div>
  );
  const line = (s: string, i: number, at: number) => (
    <div key={i} style={{fontSize: 64, fontWeight: 700, lineHeight: '96px', whiteSpace: 'nowrap', opacity: pr(t, [at + i * 0.12, at + i * 0.12 + 0.15])}}>{s}</div>
  );
  return (
    <div style={{position: 'absolute', inset: 0, opacity: out}}>
      <div style={{position: 'absolute', inset: 0, background: 'rgba(10,11,15,0.88)', opacity: inU}} />
      <div style={{position: 'absolute', inset: 0, opacity: inU, transform: `translateY(${(1 - inU) * 40}px)`}}>
        {card(100, leftOn, (
          <>
            <div style={{fontSize: 76, fontWeight: 800, lineHeight: '96px', color: C.warm}}>iPhone</div>
            <div style={{height: 30}} />
            {['设置 → 屏幕时间', '看今天的报告', '往下翻到“通知”'].map((s, i) => line(s, i, EV8.cardL))}
            <div style={{fontSize: 50, fontWeight: 500, lineHeight: '70px', color: C.soft, marginTop: 34, opacity: pr(t, [EV8.cardL + 0.4, EV8.cardL + 0.55])}}>有的叫“屏幕使用时间”</div>
          </>
        ))}
        {card(980, rightOn, (
          <>
            <div style={{fontSize: 76, fontWeight: 800, lineHeight: '96px', color: C.warm}}>其他手机</div>
            <div style={{fontSize: 50, fontWeight: 600, lineHeight: '64px', color: C.soft, opacity: rIn}}>或没开过屏幕时间</div>
            <div style={{height: 0}} />
            <div style={{opacity: rIn}}>{['拉出通知栏', '看还堆着几条'].map((s, i) => line(s, i, EV8.cardR))}</div>
            <div style={{fontSize: 50, fontWeight: 500, lineHeight: '70px', color: C.soft, marginTop: 66, opacity: pr(t, [EV8.cardR + 0.4, EV8.cardR + 0.55])}}>只算没清掉的，比实际少</div>
          </>
        ))}
      </div>
    </div>
  );
};

// ================= 微信群聊设置页 16.6–46.2 =================
const PN = {x: 560, y: 110, w: 800, h: 740};
const PK = 1.12;                                   // 设置页整体放大（以面板顶边中点为准）
const sy = (rel: number) => PN.y + rel * PK;        // 面板里的一行，在画面上的 y
const RH = 110;
const RY = {name: 120, mute: 230, fold: 340, row2: 450, slots: 570};     // 每行顶边（相对面板）
const TOG_X = PN.x + PN.w - 90;
const Toggle: React.FC<{x: number; y: number; on: number}> = ({x, y, on}) => {
  const w = 108, h = 62, k = clamp(on);
  return (
    <g>
      <rect x={x - w / 2} y={y - h / 2} width={w} height={h} rx={h / 2} fill={mixHex(C.off, C.green, k)} />
      <circle cx={x - w / 2 + h / 2 + (w - h) * k} cy={y} r={h / 2 - 5} fill="#F4F5F8" />
    </g>
  );
};
const Row: React.FC<{y: number; label: string; o?: number; dy?: number; right?: React.ReactNode; dim?: boolean}> = ({y, label, o = 1, dy = 0, right, dim}) => (
  <g opacity={o} transform={`translate(0 ${dy})`}>
    <rect x={PN.x} y={PN.y + y} width={PN.w} height={RH} fill={C.row} />
    <rect x={PN.x + 40} y={PN.y + y + RH - 2} width={PN.w - 40} height={2} fill={C.line} />
    <Tx x={PN.x + 40} y={PN.y + y + RH / 2} size={54} fill={dim ? C.soft : C.ink}>{label}</Tx>
    {right}
  </g>
);
const Chevron: React.FC<{x: number; y: number}> = ({x, y}) => (
  <path d={`M ${x - 8} ${y - 16} l 16 16 l -16 16`} fill="none" stroke="#8A8F99" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
);
const HlBox: React.FC<{y: number; o: number}> = ({y, o}) => (o > 0 ? (
  <rect x={PN.x + 6} y={PN.y + y + 4} width={PN.w - 12} height={RH - 8} rx={16} fill="none" stroke={C.warm} strokeWidth={6} opacity={o} />
) : null);
const Tap: React.FC<{t: number; at: number; x: number; y: number}> = ({t, at, x, y}) => {
  if (t < at - 0.3 || t > at + 0.45) return null;
  const pre = pr(t, [at - 0.3, at - 0.1]);
  const u = pr(t, [at, at + 0.4]);
  return (
    <g>
      {t < at + 0.12 && <circle cx={x} cy={y} r={26} fill="#FFFFFF" opacity={0.85 * pre} />}
      {t >= at && <circle cx={x} cy={y} r={26 + 50 * easeOut(u)} fill="none" stroke="#FFFFFF" strokeWidth={6} opacity={0.9 * (1 - u)} />}
    </g>
  );
};
const AVA: Record<string, string> = {王: '#C77D4A', 领: '#5C7FC9', 张: '#4FA37A', 刘: '#A86BC2', 陈: '#C9605E'};
const Ava: React.FC<{x: number; y: number; ch: string; o?: number; sc?: number; red?: number}> = ({x, y, ch, o = 1, sc = 1, red = 0}) => (
  <g transform={`translate(${x} ${y}) scale(${sc})`} opacity={o}>
    <circle r={52} fill={AVA[ch] ?? '#777'} />
    <Tx x={0} y={2} size={52} anchor="middle" weight={700}>{ch}</Tx>
    {red > 0 && <circle r={60} fill="none" stroke={C.red} strokeWidth={7} opacity={red} />}
  </g>
);
const SLOT_X = (i: number) => PN.x + 90 + i * 128;
const SLOT_Y = PN.y + RY.slots + 80;
const Slots: React.FC<{o: number}> = ({o}) => (o > 0 ? (
  <g opacity={o}>
    <rect x={PN.x} y={PN.y + RY.slots - 10} width={PN.w} height={180} fill={C.row} />
    {[0, 1, 2, 3].map((i) => <circle key={i} cx={SLOT_X(i)} cy={SLOT_Y} r={52} fill="none" stroke="#5A606C" strokeWidth={4} strokeDasharray="10 8" />)}
    <Tx x={PN.x + PN.w - 40} y={SLOT_Y} size={44} anchor="end" fill={C.soft}>最多 4 个</Tx>
  </g>
) : null);
// 一个头像从 (fx, fy) 飞进空位 i
const flyAva = (t: number, at: number, ch: string, i: number, fx: number, fy: number, key: string, extra?: {red?: number; o?: number}) => {
  if (t < at) return null;
  const u = pr(t, [at, at + 0.3]);
  const x = lerp(fx, SLOT_X(i), easeOut(u)), y = lerp(fy, SLOT_Y, easeOut(u)) - 60 * Math.sin(Math.PI * u);
  return <Ava key={key} x={x} y={y} ch={ch} sc={lerp(0.5, 1, easeBack(u))} o={extra?.o ?? 1} red={extra?.red} />;
};

const SubPage: React.FC<{t: number}> = ({t}) => {
  const allOn = pe(t, [EV8.tapAll + 0.02, EV8.tapAll + 0.17]);
  const swHl = (i: number) => {
    const a = EV8.sw[i], b = i < 2 ? EV8.sw[i + 1] : EV8.tapAdd - 0.35;
    return t >= a && t < b ? pr(t, [a, a + 0.12]) : 0;
  };
  const addHl = t >= EV8.tapAdd - 0.35 && t < EV8.adds[1] + 0.6 ? 1 : 0;
  const plus = {x: PN.x + PN.w - 70, y: PN.y + RY.fold + RH + 20 + RH / 2};
  return (
    <g>
      <rect x={PN.x} y={PN.y} width={PN.w} height={PN.h} fill={C.page} />
      <rect x={PN.x} y={PN.y} width={PN.w} height={110} fill="#1A1D24" />
      <path d={`M ${PN.x + 44} ${PN.y + 40} l -16 16 l 16 16`} fill="none" stroke="#F4F5F8" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
      <Tx x={PN.x + PN.w / 2} y={PN.y + 56} size={52} anchor="middle" weight={700}>以下消息仍通知</Tx>
      <Row y={RY.name} label="@我" right={<Toggle x={TOG_X} y={PN.y + RY.name + RH / 2} on={1} />} />
      <Row y={RY.mute} label="@所有人" right={<Toggle x={TOG_X} y={PN.y + RY.mute + RH / 2} on={allOn} />} />
      <Row y={RY.fold} label="群公告" right={<Toggle x={TOG_X} y={PN.y + RY.fold + RH / 2} on={1} />} />
      <Row y={RY.fold + RH + 20} label="添加成员" right={(
        <g>
          <circle cx={plus.x} cy={plus.y} r={34} fill="none" stroke="#C9CED8" strokeWidth={4} />
          <path d={`M ${plus.x - 16} ${plus.y} h 32 M ${plus.x} ${plus.y - 16} v 32`} stroke="#C9CED8" strokeWidth={5} strokeLinecap="round" />
        </g>
      )} />
      <HlBox y={RY.name} o={swHl(0)} />
      <HlBox y={RY.mute} o={swHl(1)} />
      <HlBox y={RY.fold} o={swHl(2)} />
      <HlBox y={RY.fold + RH + 20} o={addHl} />
      <Slots o={po(t, [EV8.tapAdd - 0.35, EV8.tapAdd - 0.1])} />
      {flyAva(t, EV8.adds[0], '王', 0, plus.x, plus.y, 'a0')}
      {flyAva(t, EV8.adds[1], '领', 1, plus.x, plus.y, 'a1')}
      <Tap t={t} at={EV8.tapAll} x={TOG_X} y={PN.y + RY.mute + RH / 2} />
      <Tap t={t} at={EV8.tapAdd} x={plus.x} y={plus.y} />
    </g>
  );
};

// 子页上方弹下的两条 @所有人 横幅
const AllBanners: React.FC<{t: number}> = ({t}) => {
  if (t < EV8.allBanners[0] || t >= EV8.subOut[1]) return null;
  const out = 1 - pr(t, EV8.subOut);
  const list = [
    {at: EV8.allBanners[0], sub: '@所有人 帮忙投个票', warm: false},
    {at: EV8.allBanners[1], sub: '@所有人 明早8点前交表', warm: true},
  ];
  const H = 150;
  return (
    <g opacity={out}>
      {list.map((b, i) => {
        if (t < b.at) return null;
        const below = list.reduce((s, m, j) => (j > i && t >= m.at ? s + (H + 14) * po(t, [m.at, m.at + 0.25]) : s), 0);
        const y = PN.y + 20 + below - 80 * (1 - po(t, [b.at, b.at + 0.25]));
        const x0 = PN.x + 30, w = PN.w - 60;
        return (
          <g key={i} opacity={pr(t, [b.at, b.at + 0.12])}>
            <rect x={x0 + 6} y={y + 12} width={w} height={H} rx={28} fill="#000" opacity={0.5} filter="url(#fBlur8)" />
            <rect x={x0} y={y} width={w} height={H} rx={28} fill={b.warm ? '#3A3320' : '#262B38'} />
            <rect x={x0} y={y} width={w} height={H} rx={28} fill="none" stroke={b.warm ? C.warm : '#FFFFFF'} strokeOpacity={b.warm ? 1 : 0.12} strokeWidth={b.warm ? 5 : 2} />
            <AppIcon x={x0 + 50} y={y + 48} size={50} kind="chat" />
            <Tx x={x0 + 90} y={y + 48} size={48} fill="#E4E7ED">班级群</Tx>
            <Tx x={x0 + 30} y={y + 108} size={50} weight={700} fill={b.warm ? C.warm : '#F4F5F8'}>{b.sub}</Tx>
          </g>
        );
      })}
    </g>
  );
};

const SettingsScene: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const inU = po(t, EV8.setIn);
  const outU = pe(t, EV8.setOut);
  const muteOn = pe(t, [EV8.tapMute + 0.02, EV8.tapMute + 0.17]) * (1 - pe(t, [EV8.tapMuteOff + 0.02, EV8.tapMuteOff + 0.17]));
  const collapse = pe(t, [EV8.tapMuteOff + 0.1, EV8.tapMuteOff + 0.45]);
  const rows = po(t, EV8.rowsOut) * (1 - collapse);
  const foldOn = 1 - pe(t, [EV8.tapFold + 0.02, EV8.tapFold + 0.17]);
  const hl1 = t >= EV8.hl1 && t < EV8.hl2 ? pr(t, [EV8.hl1, EV8.hl1 + 0.15]) : 0;
  const hl2 = t >= EV8.hl2 && t < EV8.tapMuteOff ? pr(t, [EV8.hl2, EV8.hl2 + 0.15]) : 0;
  const sub = t >= EV8.subIn[0] && t < EV8.subOut[1] ? po(t, EV8.subIn) * (1 - pe(t, EV8.subOut)) : 0;
  const m1 = pe(t, EV8.morph), m2 = pe(t, EV8.morph2);
  const slots = po(t, EV8.slotsIn) * (1 - collapse);
  // 面板抖：@所有人 横幅来的时候
  let shk = 0;
  for (const a of EV8.allBanners) { const f = Math.round((t - a) * FPS8); if (f >= 0 && f < 8) shk = f % 2 === 0 ? 5 : -5; }
  const row2Label = (
    <g>
      <g opacity={(1 - m1)}>
        <Tx x={PN.x + 40} y={PN.y + RY.row2 + RH / 2} size={54}>以下消息仍通知</Tx>
        <Chevron x={PN.x + PN.w - 50} y={PN.y + RY.row2 + RH / 2} />
      </g>
      <g opacity={m1 * (1 - m2)}>
        <Tx x={PN.x + 40} y={PN.y + RY.row2 + RH / 2} size={54}>关注的群成员</Tx>
        <Chevron x={PN.x + PN.w - 50} y={PN.y + RY.row2 + RH / 2} />
      </g>
      <g opacity={m2}>
        <rect x={PN.x + 30} y={PN.y + RY.row2 + 16} width={PN.w - 60} height={RH - 32} rx={14} fill="none" stroke="#6A707C" strokeWidth={4} strokeDasharray="14 10" />
        <Tx x={PN.x + PN.w / 2} y={PN.y + RY.row2 + RH / 2} size={56} anchor="middle" fill={C.soft} weight={700}>？</Tx>
      </g>
    </g>
  );
  // 第二种、第三种：空位和头像
  const pre5 = 1 - pr(t, [EV8.morph2[0], EV8.morph2[0] + 0.25]);
  const five = ['王', '领', '张', '刘', '陈'];
  const fromR = {x: PN.x + PN.w + 220, y: PN.y + RY.row2 + RH / 2};
  const bnc = pr(t, [EV8.bounce, EV8.bounce + 0.45]);
  const chips = [{text: '王老师'}, {text: '领导'}, {text: '@所有人'}];
  const chipsO = 1 - pr(t, EV8.chipsOut);
  return (
    <g opacity={inU * (1 - outU)} transform={`translate(${shk} ${(1 - inU) * 50 + outU * 40})`}>
      <RoomBase />
      <Lamp x={960} k={0.7} f={fr} spread={1.3} seed="set" />
      {/* 面板（整体放大 PK 倍） */}
      <g transform={`translate(960 ${PN.y}) scale(${PK}) translate(-960 ${-PN.y})`}>
      <rect x={PN.x + 10} y={PN.y + 26} width={PN.w} height={PN.h} rx={44} fill="#000" opacity={0.55} filter="url(#fBlur16)" />
      <clipPath id="n8pn"><rect x={PN.x} y={PN.y} width={PN.w} height={PN.h} rx={44} /></clipPath>
      <g clipPath="url(#n8pn)">
        <rect x={PN.x} y={PN.y} width={PN.w} height={PN.h} fill={C.page} />
        <rect x={PN.x} y={PN.y} width={PN.w} height={110} fill="#1A1D24" />
        <path d={`M ${PN.x + 44} ${PN.y + 40} l -16 16 l 16 16`} fill="none" stroke="#F4F5F8" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
        <Tx x={PN.x + PN.w / 2} y={PN.y + 56} size={52} anchor="middle" weight={700}>群聊设置</Tx>
        <Row y={RY.name} label="群聊名称" dim right={<Tx x={PN.x + PN.w - 40} y={PN.y + RY.name + RH / 2} size={50} anchor="end" fill={C.soft}>班级群</Tx>} />
        <Row y={RY.mute} label="消息免打扰" right={<Toggle x={TOG_X} y={PN.y + RY.mute + RH / 2} on={muteOn} />} />
        {rows > 0 && (
          <g>
            <Row y={RY.fold} label="折叠该聊天" o={rows} dy={-40 * (1 - rows)} right={<Toggle x={TOG_X} y={PN.y + RY.fold + RH / 2} on={foldOn} />} />
            <g opacity={rows} transform={`translate(0 ${-60 * (1 - rows)})`}>
              <rect x={PN.x} y={PN.y + RY.row2} width={PN.w} height={RH} fill={C.row} />
              {row2Label}
            </g>
          </g>
        )}
        <HlBox y={RY.fold} o={hl1 * rows} />
        <HlBox y={RY.row2} o={hl2 * rows} />
        <Slots o={slots} />
        {slots > 0 && (
          <g opacity={slots}>
            {flyAva(t, EV8.adds2[0], '王', 0, fromR.x, fromR.y, 'b0', {o: pre5})}
            {flyAva(t, EV8.adds2[1], '领', 1, fromR.x, fromR.y, 'b1', {o: pre5})}
            {five.slice(0, 4).map((ch, i) => flyAva(t, EV8.five[i], ch, i, fromR.x, fromR.y, `c${i}`))}
          </g>
        )}
        <Tap t={t} at={EV8.tapMute} x={TOG_X} y={PN.y + RY.mute + RH / 2} />
        <Tap t={t} at={EV8.tapFold} x={TOG_X} y={PN.y + RY.fold + RH / 2} />
        <Tap t={t} at={EV8.tapRow2} x={PN.x + PN.w - 120} y={PN.y + RY.row2 + RH / 2} />
        <Tap t={t} at={EV8.tapMuteOff} x={TOG_X} y={PN.y + RY.mute + RH / 2} />
        {sub > 0 && <g transform={`translate(${PN.w * (1 - sub)} 0)`}><SubPage t={t} /></g>}
        <AllBanners t={t} />
      </g>
      {/* 第五个头像挤不进，弹出去 */}
      {t >= EV8.five[4] && t < EV8.tapMuteOff + 0.4 && (() => {
        const u = pr(t, [EV8.five[4], EV8.five[4] + 0.15]);
        const x0 = lerp(fromR.x, SLOT_X(4) - 10, easeOut(u)), y0 = SLOT_Y;
        const x = x0 + 520 * easeOut(bnc), y = y0 - 220 * Math.sin(Math.PI * Math.min(1, bnc * 0.9)) + 60 * bnc;
        return <Ava x={x} y={y} ch="陈" red={pr(t, [EV8.bounce - 0.1, EV8.bounce])} o={1 - pr(t, [EV8.tapMuteOff, EV8.tapMuteOff + 0.4])} />;
      })()}
      </g>
      {/* 面板上方：在哪儿 */}
      <Sticker x={960} y={60} text="   微信群 → 右上角“…”   " size={46} pop={1} tilt={0} />
      {/* 三张小卡：要留的人和 @所有人 */}
      {t >= EV8.chips[0] && chipsO > 0 && chips.map((c, i) => {
        const a = EV8.chips[i];
        if (t < a) return null;
        const u = pr(t, [a, a + 0.3]);
        return <Sticker key={i} x={lerp(2060, 1580, easeOut(u))} y={sy(RY.row2 - 120 + i * 110)} text={c.text} size={52} pop={easeBack(u)} o={chipsO} ring={0.8} />;
      })}
      {/* 贴纸 */}
      {t >= EV8.foldTag && t < EV8.hl2 + 0.2 && (
        <Sticker x={1640} y={sy(RY.fold + RH / 2)} text="开着的关掉" size={52} pop={easeBack(pr(t, [EV8.foldTag, EV8.foldTag + 0.25]))} o={1 - pr(t, [EV8.hl2, EV8.hl2 + 0.2])} />
      )}
      {t >= EV8.noTag && (
        <Sticker x={1650} y={sy(RY.mute + RH / 2)} text="开了的，关掉" size={52} pop={easeBack(pr(t, [EV8.noTag, EV8.noTag + 0.25]))} />
      )}
      <Vignette3 o={0.7} />
    </g>
  );
};

// ================= 顺带 55.4–61 =================
const LockIcon: React.FC<{x: number; y: number; s: number}> = ({x, y, s}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M -14 -4 L -14 -16 Q -14 -32 0 -32 Q 14 -32 14 -16 L 14 -4" fill="none" stroke={C.warm} strokeWidth={6} />
    <rect x={-22} y={-6} width={44} height={36} rx={7} fill={C.warm} />
    <circle cx={0} cy={10} r={5} fill="#3A3320" />
  </g>
);
const Extra: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const inU = po(t, EV8.extraIn);
  const lefts: {name: string; icon: 'flame' | 'bag' | 'chat'}[] = [{name: '游戏', icon: 'flame'}, {name: '资讯', icon: 'flame'}];
  const rights = ['购物', '银行', '外卖', '出行'];
  const rIn = po(t, [SC8.extra[0] + 2.75, SC8.extra[0] + 3.05]);
  return (
    <g opacity={inU}>
      <RoomBase />
      <Lamp x={960} k={0.6} f={fr} spread={1.4} seed="ex" />
      <Tx x={500} y={170} size={64} anchor="middle" weight={800}>可以整个关</Tx>
      {lefts.map((c, i) => {
        const off = pe(t, [EV8.offs[i], EV8.offs[i] + 0.18]);
        const y = 300 + i * 170;
        return (
          <g key={i} opacity={1 - 0.4 * off}>
            <rect x={180} y={y} width={640} height={140} rx={28} fill="#1E222B" stroke="#2E3440" strokeWidth={3} />
            <AppIcon x={250} y={y + 70} size={72} kind={c.icon} />
            <Tx x={310} y={y + 70} size={60} weight={700}>{c.name}</Tx>
            <Toggle x={720} y={y + 70} on={1 - off} />
            <Tap t={t} at={EV8.offs[i]} x={720} y={y + 70} />
          </g>
        );
      })}
      <g opacity={rIn}>
        <Tx x={1400} y={170} size={64} anchor="middle" weight={800} fill={C.warm}>别整个关</Tx>
        {rights.map((name, i) => {
          const x = 1010 + (i % 2) * 400, y = 300 + Math.floor(i / 2) * 170;
          const lk = easeBack(pr(t, [EV8.locks[i], EV8.locks[i] + 0.25]));
          return (
            <g key={i}>
              <rect x={x} y={y} width={370} height={140} rx={28} fill="#1E222B" stroke={t >= EV8.locks[i] ? C.warm : '#2E3440'} strokeWidth={t >= EV8.locks[i] ? 5 : 3} />
              <Tx x={x + 40} y={y + 70} size={60} weight={700}>{name}</Tx>
              {lk > 0 && <LockIcon x={x + 300} y={y + 66} s={1.3 * lk} />}
            </g>
          );
        })}
        <Tx x={1400} y={690} size={50} anchor="middle" fill={C.soft} o={pr(t, [EV8.notes[0], EV8.notes[0] + 0.2])}>会连订单、动账提醒一起关掉</Tx>
        <Tx x={1400} y={780} size={54} anchor="middle" weight={700} fill={C.warm} o={pr(t, [EV8.notes[1], EV8.notes[1] + 0.2])}>私聊、验证码也别关</Tx>
      </g>
      <rect x={958} y={130} width={4} height={700} fill="#2E3440" />
      <Vignette3 o={0.7} />
    </g>
  );
};

// ================= 清单屏 61–66.2 =================
const LIST: {text: string; sub?: boolean; small?: boolean}[] = [
  {text: '① 群聊右上角“…”→ 打开“消息免打扰”'},
  {text: '② 第一行“折叠该聊天”：关着'},
  {text: '③ 第二行是“以下消息仍通知”：'},
  {text: '@我、@所有人、群公告开着，加上老师、领导', sub: true},
  {text: '是“关注的群成员”：加上老师、领导', sub: true},
  {text: '两样都没有，或要紧的人超过 4 个：先别开', sub: true},
  {text: '④ 找群里一个熟人测一下（步骤见简介）'},
  {text: '顺带：游戏、资讯 App 的通知可以整个关；', small: true},
  {text: '购物、银行、外卖、出行、私聊、验证码，别整个关', small: true},
];
const Checklist: React.FC<{t: number}> = ({t}) => {
  const inU = po(t, EV8.listIn);
  const r0 = EV8.listIn[1];
  const groups = [[0], [1], [2, 3, 4, 5], [6], [7, 8]];
  const seg = (SC8.list[1] - r0 - 0.2) / groups.length;
  const gi = Math.floor((t - r0) / seg);
  return (
    <div style={{position: 'absolute', left: 60, top: 92, width: 1800, height: 810, borderRadius: 36, background: '#1C2029', border: '3px solid #2E3440',
      opacity: inU, transform: `translateY(${(1 - inU) * 30}px)`, fontFamily: SANS, color: C.ink, padding: '22px 70px', boxSizing: 'border-box'}}>
      <div style={{fontSize: 64, fontWeight: 800, lineHeight: '80px', marginBottom: 8}}>微信里，<span style={{color: C.warm}}>又吵又要紧的群</span></div>
      {LIST.map((r, i) => {
        const on = t >= r0 && gi >= 0 && gi < groups.length && groups[gi].includes(i);
        return (
          <div key={i} style={{paddingLeft: r.sub ? 96 : 26, borderLeft: `10px solid ${on ? C.warm : 'rgba(255,255,255,0.06)'}`, background: on ? 'rgba(255,201,77,0.08)' : 'transparent',
            fontSize: r.small ? 50 : 54, fontWeight: r.small ? 500 : 600, lineHeight: r.small ? '64px' : '76px', whiteSpace: 'nowrap', color: r.small ? C.soft : C.ink,
            marginTop: r.small && i === 7 ? 14 : 0}}>{r.text}</div>
        );
      })}
    </div>
  );
};

// ================= 结尾 66.2–69.4 =================
const Ending: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const u = po(t, EV8.endIn);
  const cur = Math.floor((t - EV8.endIn[1]) / 0.5) % 2 === 0;
  return (
    <>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <FilmDefs3 />
        <RoomBase />
        <Lamp x={960} k={0.9} f={fr} spread={1.2} seed="end" />
        <Vignette3 o={0.8} />
      </svg>
      <div style={{position: 'absolute', left: 0, width: 1920, top: 280, textAlign: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 132, lineHeight: '160px',
        color: '#FFF8EC', opacity: u, transform: `scale(${lerp(0.9, 1, easeBack(u))})`, textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'}}>评论区报个数</div>
      <div style={{position: 'absolute', left: 0, width: 1920, top: 520, textAlign: 'center', fontFamily: SANS, fontWeight: 700, fontSize: 80, lineHeight: '100px',
        color: CREAM, opacity: pr(t, [EV8.endIn[0] + 0.3, EV8.endIn[0] + 0.5])}}>
        今天收到
        <span style={{display: 'inline-block', width: 220, height: 92, margin: '0 18px', verticalAlign: 'middle', borderRadius: 16, border: `5px solid ${C.warm}`,
          background: 'rgba(0,0,0,0.4)', position: 'relative', top: -6}}>
          <span style={{position: 'absolute', left: 30, top: 14, width: 6, height: 58, background: C.warm, opacity: cur ? 1 : 0}} />
        </span>
        条
      </div>
    </>
  );
};

// ================= 字幕 =================
const SubText: React.FC<{beat: Beat8; t: number}> = ({beat, t}) => {
  if (!beat.sub.length) return null;
  const size = 64;
  const o = pr(t, [beat.t0, beat.t0 + 0.07]);
  return (
    <div style={{position: 'absolute', left: 0, width: 1920, top: 1000 - size * 0.98, height: size * 1.2, display: 'flex', justifyContent: 'center',
      fontFamily: SANS, fontWeight: 600, fontSize: size, lineHeight: `${size * 1.2}px`, color: CREAM, whiteSpace: 'pre', opacity: o, textShadow: SHADOW}}>
      {beat.sub.map((sg: Seg8, i) => (typeof sg === 'string'
        ? <span key={i}>{sg}</span>
        : <span key={i} style={{color: sg[1] === 'warm' ? C.warm : C.gray}}>{sg[0]}</span>))}
    </div>
  );
};
const LowBand: React.FC = () => (
  <div style={{position: 'absolute', left: 0, top: 880, width: 1920, height: 200,
    background: 'linear-gradient(180deg, rgba(8,9,13,0) 0%, rgba(8,9,13,0.8) 40%, rgba(8,9,13,0.92) 100%)'}} />
);

export const Notice8: React.FC<{atFrame?: number}> = ({atFrame}) => {
  const cf = useCurrentFrame();
  const fr = atFrame ?? cf;                       // 封面用：固定画某一帧
  const t = fr / FPS8;
  const b = beatAt8(t);
  const desk = t < SC8.settings[0] || (t >= SC8.settings[1] && t < SC8.extra[0]);
  const settings = t >= SC8.settings[0] && t < SC8.settings[1] + 0.4;
  const extra = t >= SC8.extra[0] && t < SC8.extra[1];
  const list = t >= SC8.list[0] && t < SC8.list[1];
  const end = t >= SC8.end;
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {(desk || settings || extra || list) && (
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <FilmDefs3 />
          {(desk || list) && <DeskScene t={list ? SC8.extra[0] - 0.01 : t} fr={fr} />}
          {settings && <SettingsScene t={t} fr={fr} />}
          {extra && <Extra t={t} fr={fr} />}
          {desk && <Vignette3 o={0.85} />}
          {list && <rect width={1920} height={1080} fill="#0A0B0F" opacity={0.85} />}
        </svg>
      )}
      {desk && t >= SC8.cards[0] && t < SC8.cards[1] && <Cards t={t} />}
      {desk && !(t >= SC8.cards[0] && t < SC8.cards[1]) ? <SubBand3 /> : <LowBand />}
      {desk && <DeskText t={t} />}
      {list && <Checklist t={t} />}
      {end && <Ending t={t} fr={fr} />}
      <SubText beat={b} t={t} />
      <AiBadge />
    </AbsoluteFill>
  );
};
