// 003《消息提醒》v11 成片画面（Notice003V11）：第五版，感受到有多烦、影响有多重。秒数、字幕、事件全读 timeline11.ts（照 videos/003_消息提醒/文案.md 最上面一节）。
// ① 中央一句话一直读不完，提醒越盖越密 ② 烦吧？一整天的时间线 ③ 实验 ④ 三个场景（不演手机，不说是提醒造成的）⑤《稀缺》和注意力 ⑥ 观点：光越收越小 ⑦ 简介、问句。
// App 用通用名称，不用真实商标；片里不画设置页、开关、步骤（选题单第五版）。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Chair} from '../../components/people/FlatProps';
import {EXPR, Expr, blink, breath, mixExpr, withBlink} from '../../components/people/face';
import {Look, ME, OTHER} from '../../components/people/look';
import {mixHex} from '../../components/people/geom';
import {Pose, RPose, mixPose, nudge, poseDef, resolve, solve} from '../../components/people/rig';
import {FPerson} from '../002/film/FPerson';
import {AiBadge, AppIcon, CREAM, FilmDefs3, LAMP, Lamp, PhoneBody, RoomBase, SHADOW, Shadow, StatusBar, SubBand3, Vignette3} from './film';
import {Beat11, EV11, FPS11, FRAMES11, SC11, Seg11, beatAt11} from './timeline11';

export const NOTICE11_FRAMES = FRAMES11;

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

// 聊天图标用蓝色：通用的聊天 App，不让人想到某一个具体的 App（号主 11/04：主题不是微信）
const Ic: React.FC<{x: number; y: number; size: number; kind: 'bag' | 'chat' | 'flame'}> = (p) => <AppIcon {...p} tint={p.kind === 'chat' ? '#4C8DF0' : undefined} />;

// ================= ① 一句话一直读不完 =================
type Kind = 'bag' | 'chat' | 'flame';
const NOTES: [string, string, Kind][] = [
  ['外卖', '15 元券快过期', 'bag'], ['游戏', '体力满了', 'flame'], ['王老师', '明早8点前交表', 'chat'], ['热搜', '又上热搜了', 'flame'],
  ['朋友', '在吗？', 'chat'], ['工作', '这个文件你看下', 'chat'], ['快递', '放驿站了', 'bag'], ['领导', '下午三点开会', 'chat'],
  ['直播', '你关注的人开播了', 'flame'], ['新闻', '刚刚发生一件大事', 'flame'], ['购物', '你的订单已发货', 'bag'], ['朋友', '看到回一下', 'chat'],
  ['打车', '优惠券到账', 'bag'], ['游戏', '好友邀请你', 'flame'], ['工作', '方案改好了吗', 'chat'], ['视频', '你可能想看', 'flame'],
];
const SENT = '请读完这句话，就这一句，很短。';
const SENT_X = 300, SENT_Y = 480, SENT_S = 88;
const sentN = (t: number) => (t < 1.3 ? 7 : t < 1.85 ? Math.min(12, 7 + Math.floor((t - 1.3) / 0.09) + 1) : t < 2.7 ? 12 : 13);   // 读到“很”就再也读不到了
const Sentence: React.FC<{t: number; o?: number}> = ({t, o = 1}) => {
  const n = sentN(t);
  const caret = Math.floor(t * 3) % 2 === 0;
  return (
    <g opacity={o}>
      <Tx x={SENT_X} y={SENT_Y} size={SENT_S} weight={700} fill="#FFF8EC">{SENT.slice(0, n)}</Tx>
      {caret && <rect x={SENT_X + n * SENT_S + 4} y={SENT_Y - 48} width={7} height={96} fill={C.warm} />}
    </g>
  );
};
const LEAVE = [1.32, 2.68, 3.72, 4.62];    // 前 4 条会走（走的时候底下那句话露出来），之后堆着不走
const Pile: React.FC<{t: number}> = ({t}) => {
  const P_ = EV11.pops;
  let j = -1;
  P_.forEach((a, i) => { if (t >= a) j = i; });
  const dt = j >= 0 ? t - P_[j] : 1;
  const amp = Math.max(0, 1 - dt / 0.12) * (4 + 12 * j / 31);
  return (
    <g transform={`translate(${amp * (j % 2 ? 1 : -1)} ${amp * 0.6 * (j % 3 === 0 ? 1 : -1)})`}>
      {P_.map((a, i) => {
        if (t < a) return null;
        const lv = i < 4 ? LEAVE[i] : 1e9;
        if (t >= lv + 0.12) return null;
        const early = i < 5;
        const w = early ? 1060 : 760 + 3 * i, h = early ? 176 : 164;
        // 铺满全屏：R2 低差异序列，不会排成一条斜线；最后几条专门压住那句话
        const onSent = i >= P_.length - 4;
        const x = early ? 430 + (i % 2 ? 25 : -25) : onSent ? 180 + (P_.length - 1 - i) * 300 : -30 + ((i * 0.7548777 + 0.31) % 1) * (1920 - w + 60);
        const y = early ? 390 + (i % 2 ? -12 : 14) : onSent ? 400 + (i % 2 ? -30 : 25) : -14 + ((i * 0.5698403 + 0.67) % 1) * (1080 - h + 28);
        const u = easeBack(pr(t, [a, a + 0.13]));
        const dy = -140 * (1 - pr(t, [a, a + 0.1])) - 240 * pr(t, [lv, lv + 0.12]);
        const rot = early ? 0 : ((i * 7) % 5 - 2) * 0.8;
        const [title, msg, ic] = NOTES[i % NOTES.length];
        return (
          <g key={i} opacity={pr(t, [a, a + 0.05]) * (1 - pr(t, [lv + 0.06, lv + 0.12]))} transform={`translate(${x} ${y + dy}) rotate(${rot} ${w / 2} ${h / 2}) translate(${w / 2} ${h / 2}) scale(${lerp(0.92, 1, u)}) translate(${-w / 2} ${-h / 2})`}>
            <rect x={6} y={12} width={w} height={h} rx={30} fill="#000" opacity={0.5} filter="url(#fBlur8)" />
            <rect width={w} height={h} rx={30} fill="#22273A" stroke="#FFFFFF" strokeOpacity={0.16} strokeWidth={2} />
            <Ic x={58} y={h / 2} size={76} kind={ic} />
            <Tx x={112} y={h * 0.31} size={54} weight={700}>{title}</Tx>
            <Tx x={112} y={h * 0.7} size={52} fill="#D6DAE2">{msg}</Tx>
          </g>
        );
      })}
    </g>
  );
};

// ================= ② 一整天的时间线 =================
const DAY_N = 16;
const DayLine: React.FC<{t: number}> = ({t}) => {
  const [a, b] = EV11.bubbles;
  const o = pr(t, [12.5, 12.8]) * (1 - pr(t, [EV11.bubblesOut[0], EV11.bubblesOut[1]]));
  const X0 = 200, X1 = 1720, Y = 560;
  return (
    <g opacity={o}>
      <rect x={X0} y={Y} width={X1 - X0} height={8} rx={4} fill="#6A7080" />
      {[['早上', X0], ['中午', (X0 + X1) / 2], ['晚上', X1]].map(([s_, x]) => <Tx key={s_ as string} x={x as number} y={Y + 70} size={56} anchor="middle" fill="#D6DAE2">{s_ as string}</Tx>)}
      {Array.from({length: DAY_N}).map((_, i) => {
        const at = a + (b - a) * (i / (DAY_N - 1));
        if (t < at) return null;
        const px = X0 + 40 + ((i * 0.618034 + 0.13) % 1) * (X1 - X0 - 80);
        const u = easeBack(pr(t, [at, at + 0.2]));
        const n = NOTES[i % NOTES.length];
        return (
          <g key={i} transform={`translate(${px} ${Y - 62 - 40 * (1 - u)})`} opacity={pr(t, [at, at + 0.08])}>
            <rect x={-2} y={36} width={4} height={26} fill="#6A7080" />
            <Ic x={0} y={0} size={72} kind={n[2]} />
          </g>
        );
      })}
    </g>
  );
};

// ================= 桌前（③ 实验、④ 场景、⑥ 观点共用，手机只在实验那段出现）=================
const shake = (t: number) => {
  const f = Math.round(t * FPS11);
  const on = EV11.rings.some((b) => f >= Math.round(b * FPS11) && f < Math.round(b * FPS11) + 8);
  if (!on) return {dx: 0, rot: 0};
  const k = f % 2 === 0 ? 1 : -1;
  return {dx: 5 * k, rot: 2 * k};
};
const PhoneScreen: React.FC<{t: number}> = ({t}) => (
  <g>
    <clipPath id="n11scr"><rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} rx={52} /></clipPath>
    <g clipPath="url(#n11scr)">
      <rect x={SC_.x} y={SC_.y} width={SC_.w} height={SC_.h} fill="url(#gWall)" />
      <circle cx={SC_.x + 80} cy={SC_.y + 520} r={170} fill="#8C6BC8" opacity={0.35} filter="url(#fBlur28)" />
      <Tx x={SC_.x + SC_.w / 2} y={SC_.y + 118} size={104} anchor="middle" weight={300} fill="#EEF2FA">20:31</Tx>
      {[['来电', '未知号码', 0], ['短信', '一条新短信', 1]].map(([ti, m, i]) => {
        const a = EV11.rings[i as number];
        if (t < a) return null;
        const y = SC_.y + (i === 0 ? 210 : 390);
        return (
          <g key={i as number} opacity={pr(t, [a, a + 0.12])}>
            <rect x={SC_.x + 10} y={y} width={SC_.w - 20} height={166} rx={26} fill="#1E2230" opacity={0.94} />
            <Ic x={SC_.x + 46} y={y + 50} size={52} kind="chat" />
            <Tx x={SC_.x + 82} y={y + 50} size={50}>{ti as string}</Tx>
            <Tx x={SC_.x + 30} y={y + 118} size={50} weight={700}>{m as string}</Tx>
          </g>
        );
      })}
      <StatusBar s={SC_} />
    </g>
  </g>
);
const KID = resolve({yaw: 0.55, pelvis: -2, lean: 1, chest: 1, neck: -3, lN: {hip: 3, knee: 0}, lF: {hip: 10, knee: 10}, ground: true});
const DeskPlain: React.FC<{t: number; fr: number; phone?: boolean; kid?: number; expr?: Expr}> = ({t, fr, phone, kid = 0, expr = E.calm}) => {
  const pose = DESK_UP;
  const deskX = HOOK.x + 30 * HOOK.s;
  const sk0 = shake(t);
  const pc = {x: PB.x + PB.w / 2, y: PB.y + PB.h / 2};
  return (
    <g>
      <RoomBase />
      <g transform={DESK_XF}>
        <Lamp x={940} k={1} f={fr} spread={1.15} floorY={HOOK.G + 6} seed="hook" />
        {kid > 0 && <g opacity={kid}><You fr={fr + 40} look={OTHER} pose={KID} expr={E.calm} x={520} G={HOOK.G} s={1.3} seed="kid" /></g>}
        <Chair x={HOOK.x - 10 * HOOK.s} y={HOOK.G} s={HOOK.s} />
        <rect x={deskX + 14} y={DESK_Y - 9} width={96} height={9} rx={3} fill="#9AA3B2" />
        <path d={`M ${deskX + 102} ${DESK_Y - 6} L ${deskX + 114} ${DESK_Y - 6} L ${deskX + 136} ${DESK_Y - 118} L ${deskX + 124} ${DESK_Y - 118} Z`} fill="#B7C0CE" />
        <You fr={fr} look={ME} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="body" />
        <Shadow x={deskX + 180} y={HOOK.G + 4} rx={220} ry={14} o={0.55} />
        <rect x={deskX} y={DESK_Y} width={360} height={18} rx={4} fill={C.woodTop} />
        <rect x={deskX} y={DESK_Y} width={360} height={5} rx={2.5} fill="#7A6652" />
        <rect x={deskX + 16} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <rect x={deskX + 330} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        {phone && (
          <g transform={`translate(${sk0.dx} 0) rotate(${sk0.rot} ${pc.x} ${pc.y})`}>
            <PhoneBody b={PB} />
            <PhoneScreen t={t} />
          </g>
        )}
        <You fr={fr} look={ME} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="arms" />
      </g>
    </g>
  );
};

// ③ 实验：注意力题 → 错涨了多少（没有数字，示意）
const MARKS: ('ok' | 'no')[] = ['ok', 'ok', 'ok', 'ok', 'ok', 'no', 'ok', 'no', 'no', 'ok'];
const Experiment: React.FC<{t: number}> = ({t}) => {
  const barsOn = pr(t, [18.1, 18.3]);
  const X = 100;
  return (
    <g>
      <Tx x={X} y={120} size={50} fill="#D6DAE2">Stothart 等 2015，实验里是来电和短信</Tx>
      <g opacity={1 - barsOn}>
        <rect x={X} y={190} width={720} height={420} rx={26} fill="#1E2230" stroke="#FFFFFF" strokeOpacity={0.14} strokeWidth={2} />
        <Tx x={X + 40} y={260} size={64} weight={700}>注意力题</Tx>
        {MARKS.map((m, i) => {
          const a = 15.7 + i * 0.22;
          if (t < a) return null;
          const col = i % 5, row = Math.floor(i / 5);
          const cx = X + 90 + col * 130, cy = 380 + row * 130;
          const o = pr(t, [a, a + 0.08]);
          return m === 'ok'
            ? <path key={i} opacity={o} d={`M ${cx - 30} ${cy} l 22 24 l 40 -48`} fill="none" stroke={C.green} strokeWidth={14} strokeLinecap="round" strokeLinejoin="round" />
            : <path key={i} opacity={o} d={`M ${cx - 26} ${cy - 26} l 52 52 M ${cx + 26} ${cy - 26} l -52 52`} fill="none" stroke={C.red} strokeWidth={14} strokeLinecap="round" />;
        })}
      </g>
      <g opacity={barsOn}>
        <Tx x={X} y={210} size={56} weight={700} fill={C.warm}>错涨了多少（示意）</Tx>
        <Tx x={X} y={310} size={56}>手机没响</Tx>
        <rect x={X} y={350} width={40 + 110 * po(t, EV11.barA)} height={56} rx={12} fill="#8A8F99" />
        <Tx x={X} y={480} size={56}>手机响了，没碰</Tx>
        <rect x={X} y={520} width={40 + 650 * pr(t, EV11.barB)} height={56} rx={12} fill={C.warm} />
      </g>
    </g>
  );
};

const Bubble: React.FC<{x: number; y: number; s: string; o: number; tail?: number}> = ({x, y, s: txt, o, tail = 0.5}) => {
  const w = tw(txt, 60) + 70, h = 110;
  return (
    <g opacity={o}>
      <rect x={x} y={y} width={w} height={h} rx={28} fill="#F4F5F8" />
      <path d={`M ${x + w * tail - 16} ${y + h - 2} L ${x + w * tail} ${y + h + 26} L ${x + w * tail + 16} ${y + h - 2} Z`} fill="#F4F5F8" />
      <Tx x={x + 35} y={y + h / 2} size={60} weight={600} fill="#20242E">{txt}</Tx>
    </g>
  );
};

// ④ 三个场景：只演，不演手机
const Life: React.FC<{t: number}> = ({t}) => {
  const [s6, s7, s8, s9] = [21.7, 23.5, 24.8, 26.1];
  const bookO = pr(t, [s7, s7 + 0.12]) * (1 - pr(t, [s8 - 0.1, s8]));
  const page = (t - s7) / ((s8 - s7) / 3);
  const k = Math.min(2, Math.floor(Math.max(0, page)));
  const frac = Math.max(0, page) - k;
  const thinkO = pr(t, [s8, s8 + 0.1]) * (1 - pr(t, [s9 - 0.05, s9 + 0.3]));
  const THINK = '待会儿要先把那个';
  const nThink = Math.min(THINK.length, Math.floor((t - s8) / 0.07));
  const lose = pr(t, [s8 + 0.75, s9 - 0.05]);
  return (
    <g>
      {t >= s6 && t < s7 && <Bubble x={210} y={250} s="你看我画的！" o={pr(t, [s6, s6 + 0.12])} tail={0.75} />}
      {t >= s6 + 1 && t < s7 && <Bubble x={1040} y={150} s="嗯" o={pr(t, [s6 + 1, s6 + 1.08])} tail={0.3} />}
      {bookO > 0 && (
        <g opacity={bookO}>
          <rect x={120} y={200} width={320} height={420} rx={10} fill="#E9E4D6" />
          <rect x={440} y={200} width={320} height={420} rx={10} fill="#F4F0E4" />
          <rect x={436} y={200} width={8} height={420} fill="#B9B2A0" />
          {Array.from({length: 7}).map((_, i) => <rect key={i} x={480} y={240 + i * 52} width={240} height={14} rx={7} fill="#A9A392" />)}
          {Array.from({length: 7}).map((_, i) => <rect key={i} x={160} y={240 + i * 52} width={240} height={14} rx={7} fill="#B7B1A0" />)}
          <rect x={470} y={224 + frac * 320} width={260} height={46} rx={8} fill={C.warm} opacity={0.55} />
          <Tx x={440} y={140} size={60} weight={700} anchor="middle" fill={C.warm}>{`第 ${k + 1} 遍`}</Tx>
        </g>
      )}
      {thinkO > 0 && (
        <g opacity={thinkO}>
          <rect x={120} y={210} width={700} height={170} rx={80} fill="#2A2F40" stroke="#FFFFFF" strokeOpacity={0.2} strokeWidth={3} />
          <circle cx={790} cy={420} r={22} fill="#2A2F40" /><circle cx={840} cy={465} r={14} fill="#2A2F40" />
          <Tx x={190} y={295} size={60} weight={600} fill="#F4F5F8" o={1 - 0.75 * lose}>{THINK.slice(0, Math.max(0, nThink))}</Tx>
        </g>
      )}
    </g>
  );
};

// 注意力：一团暖光，被一点点吸走
const orbR = (t: number) => {
  let r = 230;
  r -= 35 * pr(t, [28, 29.5]);
  EV11.bites.forEach((b) => { r -= 19 * easeOut(pr(t, [b, b + 0.2])); });
  r -= 30 * pr(t, [34.7, 36.3]);
  r -= 45 * pr(t, [36.4, 38.6]);
  return Math.max(26, r);
};
const Orb: React.FC<{cx: number; cy: number; r: number; size?: number; o?: number; label?: boolean}> = ({cx, cy, r, size = 72, o = 1, label = true}) => (
  <g opacity={o}>
    <circle cx={cx} cy={cy} r={r * 1.5} fill={C.warm} opacity={0.14} filter="url(#fBlur28)" />
    <circle cx={cx} cy={cy} r={r} fill={C.warm} />
    <circle cx={cx - r * 0.25} cy={cy - r * 0.3} r={r * 0.5} fill="#FFE7A6" opacity={0.6} filter="url(#fBlur8)" />
    {label && (r > 110
      ? <Tx x={cx} y={cy} size={size} weight={800} anchor="middle" fill="#3A2C0A">注意力</Tx>
      : <Tx x={cx} y={cy - r - 54} size={60} weight={700} anchor="middle" fill={C.warm}>注意力</Tx>)}
  </g>
);
const Biters: React.FC<{t: number; cx: number; cy: number; r: number; times: number[]}> = ({t, cx, cy, r, times}) => (
  <g>
    {times.map((b, i) => {
      if (t < b - 0.25 || t > b + 0.4) return null;
      const ang = 2.2 + i * 1.7;
      const fx = cx + Math.cos(ang) * 620, fy = cy + Math.sin(ang) * 420;
      const u = po(t, [b - 0.25, b]);
      const x = lerp(fx, cx + Math.cos(ang) * (r + 40), u), y = lerp(fy, cy + Math.sin(ang) * (r + 40), u);
      const back = pr(t, [b + 0.05, b + 0.4]);
      const n = NOTES[(i * 3 + 1) % NOTES.length];
      return (
        <g key={i} opacity={1 - back}>
          <g transform={`translate(${lerp(x, fx, back)} ${lerp(y, fy, back)})`}><Ic x={0} y={0} size={84} kind={n[2]} /></g>
          {back > 0 && <circle cx={lerp(x, fx, back)} cy={lerp(y, fy, back) + 56} r={16} fill={C.warm} />}
        </g>
      );
    })}
  </g>
);

// ⑤《稀缺》：书讲的是钱和时间，这里是借用（小字留到“一条吸走一点”说完）
const Scarcity: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const u = po(t, [26.5, 26.85]);
  const holeO = pr(t, [27.7, 28]) * (1 - pr(t, [29.3, 29.6]));
  const cx = 1330, cy = 440;
  const r = orbR(t);
  return (
    <g>
      <RoomBase />
      <Lamp x={960} k={0.9} f={fr} spread={1.2} seed="end" />
      <g transform={`translate(${-40 * (1 - u)} 0)`} opacity={u}>
        <rect x={150} y={170} width={360} height={480} rx={14} fill="#7C3B38" />
        <rect x={150} y={170} width={28} height={480} rx={8} fill="#5E2B29" />
        <Tx x={345} y={400} size={110} weight={800} anchor="middle" fill="#F6EBD8">稀缺</Tx>
      </g>
      <Tx x={100} y={740} size={50} fill="#D6DAE2" o={u}>书讲的是钱和时间，这里是借用</Tx>
      <Orb cx={cx} cy={cy} r={r} o={pr(t, [26.9, 27.3])} />
      {holeO > 0 && (
        <g opacity={holeO}>
          <circle cx={800} cy={440} r={74} fill="#05060A" stroke="#FFFFFF" strokeOpacity={0.25} strokeWidth={3} />
          <Tx x={800} y={570} size={50} anchor="middle" fill="#D6DAE2">缺的东西</Tx>
          {Array.from({length: 14}).map((_, i) => {
            const ph = ((t - 27.7) * 0.9 + i / 14) % 1;
            const sx = cx - r * 0.9, x = lerp(sx, 800, ph), y = cy + Math.sin(i * 2.1) * 90 * (1 - ph);
            return <circle key={i} cx={x} cy={y} r={lerp(13, 5, ph)} fill={C.warm} opacity={0.9 * Math.sin(Math.PI * ph)} />;
          })}
        </g>
      )}
      <Biters t={t} cx={cx} cy={cy} r={r} times={EV11.bites} />
    </g>
  );
};

// ⑥ 观点：眼前的人和事，光越收越小；注意力越来越少
const Opinion: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const cx = 1500, cy = 330;
  const r = orbR(t);
  const spot = pr(t, EV11.spot);
  const R_ = lerp(1500, 470, ease(spot));
  return (
    <g>
      <DeskPlain t={t} fr={fr} kid={1} expr={t > 35 ? E.blank : E.calm} />
      <defs>
        <radialGradient id="n11spot" gradientUnits="userSpaceOnUse" cx={800} cy={600} r={R_}>
          <stop offset="0.6" stopColor="#05060A" stopOpacity={0} />
          <stop offset="1" stopColor="#05060A" stopOpacity={0.97} />
        </radialGradient>
      </defs>
      <rect width={1920} height={1080} fill="url(#n11spot)" />
      <Orb cx={cx} cy={cy} r={r} size={56} o={1} />
      <Biters t={t} cx={cx} cy={cy} r={r} times={[33, 34, 35.2, 35.9]} />
      <Bubble x={140} y={270} s="你看我画的！" o={pr(t, [32.4, 32.6]) * (1 - 0.65 * spot)} tail={0.75} />
    </g>
  );
};

const BIG: React.CSSProperties = {position: 'absolute', fontFamily: SANS, fontWeight: 800, textAlign: 'center', whiteSpace: 'nowrap', textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'};

// 办法放在简介
const Hint: React.FC<{t: number}> = ({t}) => {
  const u = po(t, EV11.hintIn);
  const bob = 20 * Math.sin((t - EV11.hintIn[0]) * 5);
  const push = 1 + 0.1 * pr(t, [EV11.hintIn[1], SC11.end]);       // 慢慢推近，不让整幅停住
  return (
    <>
      <div style={{...BIG, left: 0, width: 1920, top: 330, fontSize: 104, lineHeight: '130px', color: '#FFF8EC', opacity: u, transform: `translateY(${(1 - u) * 24}px) scale(${push})`}}>办法放在简介</div>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', opacity: u}}>
        <path d={`M 960 ${500 + bob} v 90 m -40 -40 l 40 40 l 40 -40`} fill="none" stroke={C.warm} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </>
  );
};

// 结尾：问句，空框里轮流闪过几个类别
const GUESS = ['外卖', '工作', '游戏'];
const Ending: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const u = po(t, EV11.endIn);
  const cur = Math.floor((t - EV11.endIn[1]) / 0.5) % 2 === 0;
  return (
    <>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <FilmDefs3 />
        <RoomBase />
        <Lamp x={960} k={0.9} f={fr} spread={1.2} seed="end" />
        <Vignette3 o={0.8} />
      </svg>
      <div style={{...BIG, left: 0, width: 1920, top: 190, fontSize: 112, lineHeight: '140px', color: '#FFF8EC', opacity: u, transform: `scale(${lerp(0.9, 1, easeBack(u))})`}}>你手机上来得最多的，<br />是哪个 App？</div>
      <div style={{position: 'absolute', left: 660, top: 520, width: 600, height: 150, borderRadius: 24, border: `6px solid ${C.warm}`, background: 'rgba(0,0,0,0.4)', opacity: pr(t, [EV11.endIn[0] + 0.3, EV11.endIn[0] + 0.5])}}>
        <div style={{position: 'absolute', left: 40, top: 26, width: 8, height: 90, background: C.warm, opacity: cur ? 1 : 0}} />
        {EV11.guess.map((a, i) => {
          const b = a + 0.62;
          if (t < a || t >= b) return null;
          return <div key={i} style={{position: 'absolute', left: 70, top: 26, fontFamily: SANS, fontWeight: 600, fontSize: 80, lineHeight: '96px', color: C.soft, opacity: pr(t, [a, a + 0.1]) * (1 - pr(t, [b - 0.1, b]))}}>{GUESS[i]}</div>;
        })}
      </div>
    </>
  );
};

// ================= 字幕 =================
const SubText: React.FC<{beat: Beat11; t: number}> = ({beat, t}) => {
  if (!beat.sub.length) return null;
  const size = 64;
  const o = pr(t, [beat.t0, beat.t0 + 0.07]);
  return (
    <div style={{position: 'absolute', left: 0, width: 1920, top: 1000 - size * 0.98, height: size * 1.2, display: 'flex', justifyContent: 'center',
      fontFamily: SANS, fontWeight: 600, fontSize: size, lineHeight: `${size * 1.2}px`, color: CREAM, whiteSpace: 'pre', opacity: o, textShadow: SHADOW}}>
      {beat.sub.map((sg: Seg11, i) => (typeof sg === 'string'
        ? <span key={i}>{sg}</span>
        : <span key={i} style={{color: sg[1] === 'warm' ? C.warm : C.gray}}>{sg[0]}</span>))}
    </div>
  );
};
const LowBand: React.FC = () => (
  <div style={{position: 'absolute', left: 0, top: 880, width: 1920, height: 200,
    background: 'linear-gradient(180deg, rgba(8,9,13,0) 0%, rgba(8,9,13,0.8) 40%, rgba(8,9,13,0.92) 100%)'}} />
);

export const Notice11: React.FC<{atFrame?: number}> = ({atFrame}) => {
  const cf = useCurrentFrame();
  const fr = atFrame ?? cf;                       // 封面用：固定画某一帧
  const t = fr / FPS11;
  const b = beatAt11(t);
  const S = EV11.stop;
  const part1 = t < 12.9;
  const exp = t >= 15.1 && t < 21.7;
  const life = t >= 21.3 && t < 26.3;
  const sc = t >= 26.3 && t < 32.3;
  const op = t >= 32.1 && t < SC11.end;
  const hint = t >= SC11.hint[0] && t < SC11.end;
  const end = t >= SC11.end;
  const dim = 0.86 * pr(t, EV11.fadeOut);
  const push = 1 + 0.05 * clamp(t / S);          // 被打断那段慢慢推近
  // 场景之间很短的压暗，不跳
  const cross = Math.max(
    bump(t, 15.3, 0.25), bump(t, 21.5, 0.25), bump(t, 26.3, 0.25), bump(t, 32.1, 0.25),
  );
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {!end && (
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <FilmDefs3 />
          {t < 15.3 && (
            <g>
              <RoomBase />
              <Lamp x={960} k={0.85} f={fr} spread={1.3} seed="end" />
              <g transform={`translate(960 540) scale(${t < S ? push : 1}) translate(-960 -540)`}>
                {part1 && <Sentence t={t} o={t < 11.5 ? 1 : 1 - pr(t, [12.5, 12.85])} />}
                {t < S && <Pile t={t} />}
              </g>
              <DayLine t={t} />
            </g>
          )}
          {exp && t >= 15.3 && <g><DeskPlain t={t} fr={fr} phone expr={t > 18 ? E.blank : E.calm} /><Experiment t={t} /></g>}
          {life && t >= 21.5 && !exp && <g><DeskPlain t={t} fr={fr} kid={t < 23.5 ? 1 : 1 - pr(t, [23.5, 23.7])} expr={t < 23.5 ? E.blank : E.sighing} /><Life t={t} /></g>}
          {sc && t >= 26.3 && <Scarcity t={t} fr={fr} />}
          {op && t >= 32.1 && <Opinion t={t} fr={fr} />}
          <Vignette3 o={t < S ? 0.6 : 0.85} />
          {cross > 0 && <rect width={1920} height={1080} fill="#0A0B0F" opacity={0.75 * cross} />}
          {dim > 0 && <rect width={1920} height={1080} fill="#0A0B0F" opacity={dim} />}
        </svg>
      )}
      {!hint && !end && t >= S ? <SubBand3 /> : hint || end ? <LowBand /> : null}
      {hint && <Hint t={t} />}
      {end && <Ending t={t} fr={fr} />}
      <SubText beat={b} t={t} />
      <AiBadge />
    </AbsoluteFill>
  );
};
