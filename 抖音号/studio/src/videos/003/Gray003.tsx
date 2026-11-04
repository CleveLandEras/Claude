// 003《消息提醒》画面：灰框（Notice003Gray）和成片（Notice003Film，Film003.tsx）共用这一套时间和动作，画法由 mode.ts 的开关切换。
// 秒数、字幕、事件时刻全读 timeline.ts（照 videos/003_消息提醒/分镜.md；节奏从 v2 起锁定）。
// v2：手机一开始就亮着放大、横幅 52；探身按屏上开关；卡片压头；分类一次只放大一类；清单屏整屏一起出、每行 ≥60。
// v3（分镜“灰框 v2 遮字幕测试”采纳的 1–6 条）：全关的你自己拿起手机看一眼（45→46）、小钟标 14:40→15:40、交表那条 15:40 才弹出；
//   红心一个个飞进盒子、9/15/21 点各开一次；右边的你翻开一本书（不画气泡）；“先别关”下加一行；读数上移；不讲的栏不变暗、改用聚光；
//   第 3 秒手机里旧通知不留残影（群聊整页从右边盖进来）。
// 成片画法（mode.film）：暗房间、头顶暖灯、真手机、成片小人（002 的 FPerson）；字幕带、字幕、“AI 生成”标照第二条成片（mode.text）。
import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {FlatPerson} from '../../components/people/FlatPerson';
import {Chair} from '../../components/people/FlatProps';
import {EXPR, Expr, blink, breath, mixExpr, withBlink} from '../../components/people/face';
import {ME} from '../../components/people/look';
import {mixHex} from '../../components/people/geom';
import {Pose, RPose, mixPose, nudge, poseDef, resolve, solve} from '../../components/people/rig';
import {FPerson} from '../002/film/FPerson';
import {Beat, EV, FPS, FRAMES, READ, Seg, beatAt} from './timeline';
import {ModeCtx, useMode} from './mode';
import {AiBadge, AppIcon, CREAM, FilmDefs3, LAMP, Lamp, PhoneBody, RoomBase, SHADOW, Shadow, Sticker, StatusBar, SubBand3, Vignette3} from './film';

export const GRAY003_FRAMES = FRAMES;

const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
const C = {
  bg: '#101219', ink: '#F4F5F8', soft: '#B9BEC9', bright: '#E4E7ED', gray: '#8A8F99', warm: '#FFC94D', warmBg: '#4A3D1C',
  card: '#2B3140', cardHi: '#3F4A60', edge: '#4A5263', red: '#FF4B3E', phone: '#1B1D24', back: '#30333C',
  screen: '#141821', wood: '#3F352D', woodTop: '#5A4B3E', green: '#4CC38A', tag: '#2E3442',
};
const DIM = 0.6;   // 分类标签里没讲到的那几个：只降到六成不透明
const DIMTXT = '#A9AEB8';

// —— 小工具 ——
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

const BOARD = poseDef('board');
const SITD = poseDef('sit');
const P = (base: Pose, o: Pose) => resolve({...base, ...o});
const DESK = P(BOARD, {neck: 4, pitch: 0.3, yaw: 0.45, gaze: {x: 1, y: 0.5}});
const DESK_UP = P(BOARD, {lean: 3, neck: -6, pitch: -0.05, yaw: 0.5, gaze: {x: 1, y: -0.15}});
const DESK_READ = P(BOARD, {lean: 9, chest: 4, neck: -2, pitch: 0.05, yaw: 0.5, gaze: {x: 1, y: 0}});
const DESK_REACH = P(BOARD, {pelvis: 8, lean: 24, chest: 10, neck: -12, pitch: -0.05, yaw: 0.5, gaze: {x: 1, y: 0.1},
  aN: {to: {x: 128, y: -42}, wr: -4}, hN: 'open'});
// 样片 v2：先往前探一下（上身再压低一点，手往前约 15 像素），再往后撤约 140 像素、握拳（按 rig 解算量过）
const DESK_POKE = P(BOARD, {pelvis: 15, lean: 36, chest: 10, neck: -12, pitch: -0.05, yaw: 0.5, gaze: {x: 1, y: 0.1},
  aN: {to: {x: 140, y: -42}, wr: -4}, hN: 'open'});
const DESK_PULL = P(BOARD, {pelvis: 2, lean: 8, chest: 6, neck: -4, pitch: 0.05, yaw: 0.5, gaze: {x: 1, y: 0},
  aN: {to: {x: 54, y: -48}, wr: 20}, hN: 'fist'});
const DESK_SLUMP = P(BOARD, {lean: 6, chest: 9, neck: 6, shrug: -0.8, pitch: 0.2, yaw: 0.5, gaze: {x: 1, y: 0}});
const SIT = P(SITD, {});
const SIT_LOOK = P(SITD, {neck: 12, pitch: 0.5, yaw: 0.6, gaze: {x: 1, y: 0.75}});
// v3：伸手拿桌上的手机、双手捧着看
const SIT_GRAB = P(SITD, {lean: 14, chest: 4, neck: 4, pitch: 0.3, yaw: 0.6, gaze: {x: 1, y: 0.6}, aN: {to: {x: 95, y: -30}, wr: -10}, hN: 'open'});
const SIT_HOLD = P(SITD, {lean: 8, chest: 12, neck: 16, pitch: 0.7, yaw: 0.55, gaze: {x: 0.6, y: 0.95},
  aN: {to: {x: 50, y: -28}, wr: 20}, aF: {to: {x: 44, y: -26}, wr: 30}, hN: 'hold', hF: 'hold'});
const SIT_STARTLE = P(SITD, {lean: -8, neck: -8, shrug: 0.9, aN: {sh: 40, el: 75}, aF: {sh: 30, el: 75}, hN: 'open', hF: 'open', gaze: {x: 1, y: 0.4}});
const SIT_PRESSED = P(SITD, {lean: 12, chest: 12, neck: 24, duck: 0.9, shrug: 0.7, pitch: 0.75, gaze: {x: 0.5, y: 0.9}});
const SIT_PRESSED_LOOK = P(SITD, {lean: 12, chest: 12, neck: 26, duck: 0.9, shrug: 0.7, pitch: 0.8, yaw: 0.62, gaze: {x: 1, y: 1}});
const SIT_FWD = P(SITD, {lean: 4, neck: 0, gaze: {x: 1, y: 0.1}});
// v3：捧着书读
const SIT_READ = P(SITD, {lean: 7, chest: 10, neck: 18, pitch: 0.75, yaw: 0.55, gaze: {x: 0.5, y: 1},
  aN: {to: {x: 52, y: -30}, wr: 25}, aF: {to: {x: 44, y: -28}, wr: 30}, hN: 'hold', hF: 'hold'});

const E = EXPR;
const SMILE: Expr = {...E.calm, smile: 0.6, lid: 0.2, blush: 0.7};
const READING: Expr = {...E.calm, smile: 0.45, lid: 0.35, blush: 0.6};

type Glow = {at: {x: number; y: number}; color: string; amount: number; r?: number};
// 一个“你”：带呼吸和眨眼；成片画法用 002 的 FPerson（手更细、带灯光颜色）
const You: React.FC<{fr: number; pose: RPose; expr: Expr; x: number; G: number; s: number; seed: string; part?: 'all' | 'body' | 'arms'; dy?: number; glow?: Glow}> = (
  {fr, pose, expr, x, G, s, seed, part, dy = 0, glow},
) => {
  const {film} = useMode();
  const b = breath(fr);
  const r = nudge(pose, {shrug: 0.08 * b, chest: -0.7 * b, y: dy});
  const e = withBlink(expr, blink(fr, seed));
  if (film) {
    return <FPerson pose={r} expr={e} look={ME} x={x} y={G} s={s} facing={1} night="#0B0D12" light={{x: -0.25, y: -1}} part={part}
      tint={{color: LAMP, amount: 0.07}} glow={glow} />;
  }
  return <FlatPerson pose={r} expr={e} look={ME} x={x} y={G} s={s} facing={1} night="#0B0D12" light={{x: -0.35, y: -1}} part={part} />;
};
const headAt = (pose: RPose, x: number, G: number, s: number) => {
  const sk = solve(pose);
  return {x: x + sk.head.x * s, y: G + sk.head.y * s, top: G + (sk.head.y - 52) * s};
};
const handsAt = (pose: RPose, x: number, G: number, s: number) => {
  const sk = solve(pose);
  return {x: x + ((sk.wN.x + sk.wF.x) / 2) * s, y: G + ((sk.wN.y + sk.wF.y) / 2) * s};
};

const Tx: React.FC<{x: number; y: number; size: number; fill?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number; o?: number; children: React.ReactNode}> = (
  {x, y, size, fill = C.ink, anchor = 'start', weight = 600, o = 1, children},
) => (
  <text x={x} y={y} fontSize={size} fontFamily={SANS} fontWeight={weight} fill={fill} textAnchor={anchor} dominantBaseline="central" opacity={o}>{children}</text>
);
const Tag: React.FC<{x: number; y: number; text: string; size: number; bg?: string; fg?: string; o?: number; sc?: number; stroke?: string}> = (
  {x, y, text, size, bg = C.tag, fg = C.ink, o = 1, sc = 1, stroke},
) => {
  const w = tw(text, size);
  return (
    <g opacity={o} transform={`translate(${x} ${y}) scale(${sc})`}>
      <rect x={-w / 2 - size * 0.35} y={-size * 0.66} width={w + size * 0.7} height={size * 1.32} rx={size * 0.3} fill={bg} stroke={stroke ?? 'none'} strokeWidth={stroke ? 4 : 0} />
      <Tx x={0} y={0} size={size} fill={fg} anchor="middle">{text}</Tx>
    </g>
  );
};

const Defs: React.FC = () => (
  <>
    <defs>
      <radialGradient id="g3warm"><stop offset="0" stopColor="#FFF6DD" stopOpacity={0.95} /><stop offset="0.5" stopColor="#FFD98A" stopOpacity={0.45} /><stop offset="1" stopColor="#FFD98A" stopOpacity={0} /></radialGradient>
      <radialGradient id="g3blue"><stop offset="0" stopColor="#D6E6FF" stopOpacity={0.9} /><stop offset="1" stopColor="#D6E6FF" stopOpacity={0} /></radialGradient>
    </defs>
    <FilmDefs3 />
  </>
);

const Heart: React.FC<{x: number; y: number; r: number; fill?: string; o?: number}> = ({x, y, r, fill = C.red, o = 1}) => (
  <path opacity={o} fill={fill} d={`M ${x} ${y + r * 0.9} C ${x - r * 1.6} ${y - r * 0.2} ${x - r * 0.8} ${y - r * 1.4} ${x} ${y - r * 0.5} C ${x + r * 0.8} ${y - r * 1.4} ${x + r * 1.6} ${y - r * 0.2} ${x} ${y + r * 0.9} Z`} />
);

// ================= 钩子段 0–10.4 秒 =================
const HOOK = {x: 880, G: 900, s: 1.9};
const DESK_Y = HOOK.G - 88 * HOOK.s;
const PB = {x: 1080, y: 180, w: 420, h: 720};
const SC = {x: PB.x + 14, y: PB.y + 14, w: PB.w - 28, h: PB.h - 28};
const SHEET_Y = 640;
const TOGGLE = {x: SC.x + 26, y: 716, w: 100, h: 56};

const hookPose = (t: number) => ptrack(t, [
  [0, DESK], [EV.turn[0], DESK_UP, 0.3], [4.8, DESK_READ, 0.5], [EV.reach[0], DESK_REACH, 0.55],
  [EV.poke[0], DESK_POKE, EV.poke[1] - EV.poke[0]], [EV.retract[0], DESK_PULL, EV.retract[1] - EV.retract[0], easeOut],
  [EV.resit[0], DESK_UP, EV.resit[1] - EV.resit[0]], [9.0, DESK_SLUMP, 0.8],
]);
const hookExpr = (t: number) => etrack(t, [
  [0, E.calm], [EV.buzz[0], {...E.surprise, open: 0.3}, 0.15], [0.9, E.calm, 0.4], [EV.preview[0], E.worry, 0.4], [3.0, E.calm, 0.3],
  [EV.highlight[0], E.worry, 0.3], [9.2, E.sad, 0.5],
]);

// 横幅：film 里用半角括号，好和 App 图标排进一行
const NOTI: {text: string; filmText: string; at: number; dot: string; icon: 'bag' | 'chat' | 'flame'; preview?: string}[] = [
  {text: '拼单立减', filmText: '拼单立减', at: EV.buzz[0], dot: '#F06A3C', icon: 'bag'},
  {text: '工作群(37)', filmText: '工作群(37)', at: EV.buzz[1], dot: C.green, icon: 'chat', preview: '明早8点前交表'},
  {text: '热榜第一', filmText: '热榜第一', at: EV.buzz[2], dot: '#E8487A', icon: 'flame'},
];
const CHAT = ['收到', '+1', '好的', '[图片]', '收到', '哈哈哈', '好', '1', '[文件]', '收到', '谢谢', '+1', '收到', '[图片]', '好的', '1',
  '哈哈', '收到', '+1', '[表情]', '好的', '收到', '明早8点前交表', '收到', '+1', '好的', '[图片]', '收到', '1', '谢谢'];
const KEY_MSG = 22;
const CHAT_Y0 = SC.y + 104, CHAT_STEP = 86;          // 样片 v2：群消息 52 像素
const BUB_H = 72;
const SCROLL = CHAT_Y0 + KEY_MSG * CHAT_STEP + BUB_H / 2 - 500;
const BANNER_Y = SC.y + 200;

const screenFlash = (t: number) => {
  let v = 0;
  for (const a of [...EV.buzz, EV.buzzAgain]) v = Math.max(v, bump(t, a, 0.35));
  if (t >= EV.count[0] && t < EV.count[1] + 0.3) v = Math.max(v, 0.6 * Math.abs(Math.sin(t * 38)));
  return v;
};
// 样片 v2：每次震动，手机左右 ±6 像素（画面放大 1.2 倍后）、转 ±2°，一帧一换方向，抖 8 帧；计数狂涨时一直抖
const shake = (t: number) => {
  const f = Math.round(t * FPS);
  const on = [...EV.buzz, EV.buzzAgain].some((b) => f >= Math.round(b * FPS) && f < Math.round(b * FPS) + 8)
    || (t >= EV.count[0] && t < EV.count[1]);
  if (!on) return {dx: 0, rot: 0};
  const k = f % 2 === 0 ? 1 : -1;
  return {dx: 5 * k, rot: 2 * k};
};

const PhoneScreen: React.FC<{t: number; near: number}> = ({t, near}) => {
  const {film} = useMode();
  // v3：群聊整页带底色从右边盖进来，盖满以后锁屏不再画（不留旧通知的残影）
  const slide = po(t, EV.openChat);
  const chatOn = t >= EV.openChat[0];
  const lockOn = slide < 1;
  const hl = pe(t, EV.highlight);
  const scroll = SCROLL * easeOut(pr(t, EV.scroll));
  const pv = po(t, EV.preview);
  const kl = pr(t, EV.keyLight);
  const BH = film ? 100 : 92;
  const hgt = (i: number) => (NOTI[i].preview ? BH + 64 * pv : BH);
  const sheet = po(t, EV.sheetIn) * (1 - pe(t, EV.sheetOut));
  const chatX = SC.w * (1 - slide);
  return (
    <g>
      <clipPath id="g3scr"><rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} rx={film ? 52 : 32} /></clipPath>
      <g clipPath="url(#g3scr)">
        {lockOn && (
          <g>
            {film ? (
              <>
                <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill="url(#gWall)" />
                <circle cx={SC.x + 80} cy={SC.y + 520} r={170} fill="#8C6BC8" opacity={0.35} filter="url(#fBlur28)" />
                <circle cx={SC.x + 330} cy={SC.y + 260} r={140} fill="#5FA3D9" opacity={0.3} filter="url(#fBlur28)" />
              </>
            ) : (
              <>
                <linearGradient id="g3wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#4A6290" /><stop offset="1" stopColor="#27344F" /></linearGradient>
                <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill="url(#g3wall)" />
              </>
            )}
            <Tx x={SC.x + SC.w / 2} y={SC.y + 118} size={film ? 104 : 80} anchor="middle" weight={film ? 300 : 500} fill="#EEF2FA">09:02</Tx>
            {NOTI.map((n, i) => {
              if (t < n.at) return null;
              const below = NOTI.reduce((s, m, j) => (j > i && t >= m.at ? s + (hgt(j) + 14) * po(t, [m.at, m.at + 0.25]) : s), 0);
              const y = BANNER_Y + below - 70 * (1 - po(t, [n.at, n.at + 0.25]));
              const o = pr(t, [n.at, n.at + 0.12]);
              const h = hgt(i);
              return (
                <g key={i} opacity={o}>
                  {film ? (
                    <>
                      <rect x={SC.x + 10} y={y + 6} width={SC.w - 20} height={h} rx={26} fill="#000" opacity={0.3} filter="url(#fBlur8)" />
                      <rect x={SC.x + 10} y={y} width={SC.w - 20} height={h} rx={26} fill="#1E2230" opacity={0.88} />
                      <rect x={SC.x + 10} y={y} width={SC.w - 20} height={h} rx={26} fill="none" stroke="#FFFFFF" strokeOpacity={0.08} strokeWidth={2} />
                      <AppIcon x={SC.x + 46} y={y + 50} size={52} kind={n.icon} />
                      <Tx x={SC.x + 82} y={y + 50} size={56} weight={600} fill="#F4F5F8">{n.filmText}</Tx>
                    </>
                  ) : (
                    <>
                      <rect x={SC.x + 10} y={y} width={SC.w - 20} height={h} rx={18} fill="#46536B" />
                      <circle cx={SC.x + 30} cy={y + 46} r={8} fill={n.dot} />
                      <Tx x={SC.x + 46} y={y + 46} size={56}>{n.text}</Tx>
                    </>
                  )}
                  {n.preview && pv > 0 && kl > 0 && <rect x={SC.x + 16} y={y + BH - 6} width={SC.w - 32} height={62} rx={12} fill={C.warmBg} stroke={C.warm} strokeWidth={4} opacity={kl} />}
                  {n.preview && pv > 0 && <Tx x={SC.x + 26} y={y + BH + 25} size={52} fill={mixHex('#E4E7ED', C.warm, kl)} o={pv}>{n.preview}</Tx>}
                </g>
              );
            })}
          </g>
        )}
        {chatOn && (
          <g transform={`translate(${chatX} 0)`}>
            <rect x={SC.x - 20} y={SC.y} width={SC.w + 20} height={SC.h} fill={film ? '#111318' : '#1F2838'} />
            {film && <rect x={SC.x - 30} y={SC.y} width={10} height={SC.h} fill="#000" opacity={0.4} filter="url(#fBlur8)" />}
            {CHAT.map((m, i) => {
              const y = CHAT_Y0 + i * CHAT_STEP - scroll;
              if (y < SC.y - 80 || y > SC.y + SC.h + 10) return null;
              const key = i === KEY_MSG;
              const w = tw(m, 52) + 28;
              // 样片 v2：别的消息变灰只换字色（#A9AEB8，对气泡底色约 6:1），不降透明度
              return (
                <g key={i}>
                  {key && <rect x={SC.x + 1} y={y - 8} width={w + 16} height={BUB_H + 16} rx={20} fill={C.warm} opacity={0.12 + hl * (0.1 + 0.14 * Math.sin((t - EV.highlight[1]) * 6))} />}
                  <rect x={SC.x + 9} y={y} width={w} height={BUB_H} rx={14} fill={key ? C.warmBg : film ? '#2A2E37' : C.card} stroke={C.warm} strokeWidth={key ? 5 : 0} />
                  <Tx x={SC.x + 23} y={y + BUB_H / 2} size={52} fill={key ? C.warm : mixHex(C.ink, DIMTXT, hl)}>{m}</Tx>
                </g>
              );
            })}
            <rect x={SC.x} y={SC.y} width={SC.w} height={film ? 116 : 82} fill={film ? '#1C1F26' : '#2A3346'} />
            {film && <path d={`M ${SC.x + 32} ${SC.y + 66} l -13 13 l 13 13`} fill="none" stroke="#F4F5F8" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />}
            <Tx x={SC.x + SC.w / 2 + (film ? 10 : 0)} y={SC.y + (film ? 80 : 42)} size={56} anchor="middle">工作群(37)</Tx>
          </g>
        )}
        {sheet > 0 && (
          <g transform={`translate(0 ${(1 - sheet) * (SC.y + SC.h - SHEET_Y)})`}>
            {film && <rect x={SC.x} y={SHEET_Y - 10} width={SC.w} height={40} fill="#000" opacity={0.35} filter="url(#fBlur8)" />}
            <rect x={SC.x} y={SHEET_Y} width={SC.w} height={SC.y + SC.h - SHEET_Y + 20} rx={28} fill={film ? '#23262E' : '#323B4E'} />
            {film && <rect x={SC.x + SC.w / 2 - 30} y={SHEET_Y + 12} width={60} height={7} rx={3.5} fill="#6A6F7A" />}
            <rect x={TOGGLE.x} y={TOGGLE.y - TOGGLE.h / 2} width={TOGGLE.w} height={TOGGLE.h} rx={TOGGLE.h / 2} fill={film ? '#4A4F5A' : '#596276'} />
            <circle cx={TOGGLE.x + TOGGLE.h / 2} cy={TOGGLE.y} r={TOGGLE.h / 2 - 5} fill="#F4F5F8" />
            <Tx x={TOGGLE.x + TOGGLE.w + 22} y={TOGGLE.y} size={56}>关闭通知</Tx>
            {/* 开关外面那圈暖黄框画在面板里，跟着面板走；手往回撤时就没了（样片 v2 第 8 条） */}
            {near > 0 && <rect x={TOGGLE.x - 8} y={TOGGLE.y - TOGGLE.h / 2 - 8} width={TOGGLE.w + 16} height={TOGGLE.h + 16} rx={TOGGLE.h / 2 + 8}
              fill="none" stroke={C.warm} strokeWidth={4} opacity={near} />}
          </g>
        )}
        <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill="#FFFFFF" opacity={(film ? 0.14 : 0.2) * screenFlash(t)} />
        {film && <StatusBar s={SC} />}
      </g>
    </g>
  );
};

// 第一段画面的摆法（样片 v2 第二轮）：放大 1.04 倍（v2 的 1.2 倍再缩到约 0.87），手机顶在 y≈141（不碰大标题）、底在 y≈890（离字幕上缘约 47）；
// 计数、你、手机三样从左到右居中排开：计数 x≈303–819，你 x≈863 起，手机 x≈1174–1616，左右留白都约 303。
// 8.2–9.4 秒镜头再推到 1.15 倍（以你胸口为准）
const HS = 1.04, HX = 50.8, HY = -46.2;          // 画面 X = HS·x + HX，Y = HS·y + HY
const PUSH_C = {x: 987, y: 680};
const pushK = (t: number) => 1 + 0.15 * pe(t, EV.camPush) * (1 - pe(t, EV.camBack));
const hookXf = (t: number) => {
  const k = pushK(t);
  return `translate(${PUSH_C.x} ${PUSH_C.y}) scale(${k}) translate(${-PUSH_C.x} ${-PUSH_C.y}) translate(${HX} ${HY}) scale(${HS})`;
};
// 画面坐标里的一点跟着推镜头走（计数用）
const pushMap = (t: number, X: number, Y: number) => {
  const k = pushK(t);
  return {x: (X - PUSH_C.x) * k + PUSH_C.x, y: (Y - PUSH_C.y) * k + PUSH_C.y, k};
};
const COUNTER_AT = {x: 303, y: 514};

// 样片 v2：8.2–9.15 秒 27 条横幅从手机里一条条喷出来，铺满画面，从下往上把你埋到肩膀（头露在外面）；9.4 秒 3 帧内全部震散
const BURST_NAMES = ['拼单立减', '热榜第一', '工作群(37)', '限时秒杀', '家长群(12)', '快递已签收', '直播开始了', '红包到账', '新闻快讯',
  '小区群(99+)', '你有新消息', '优惠券到期', '同学群(8)', '热搜爆了', '会员续费', '亲戚群(5)', '好友点赞', '外卖已送达', '步数排行',
  '新品上架', '视频更新', '账单提醒', '系统更新', '天气预警', '评论回复', '体力满了', '签到提醒'];
const BURST_ICON: ('bag' | 'chat' | 'flame')[] = ['bag', 'flame', 'chat'];
const HEAD_BOX = {x0: 850, x1: 1100, y0: 400, y1: 660};       // 头露出来的地方（画面坐标，推镜头以后）
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
const BURST_FROM = {x: 1440, y: 500};
const Burst: React.FC<{t: number}> = ({t}) => {
  if (t < EV.burst[0] || t >= EV.shatter[1]) return null;
  const sh = pr(t, EV.shatter);
  return (
    <g>
      {BURST.map((b, i) => {
        const s0 = EV.burstTimes[i];
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

const Hook: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const {film} = useMode();
  const pose = hookPose(t);
  const expr = hookExpr(t);
  const sk0 = shake(t);
  const near = t >= EV.reach[0] && t < EV.poke[1] + 0.1 ? pe(t, [EV.reach[0] + 0.2, EV.stop[0]]) * (1 - pr(t, [EV.poke[1], EV.poke[1] + 0.1])) : 0;
  const deskX = HOOK.x + 30 * HOOK.s;
  const fl = screenFlash(t);
  const sk = solve(pose);
  const glow: Glow | undefined = film ? {at: {x: sk.head.x + 45, y: sk.head.y + 5}, color: '#BFD4FF', amount: 0.16 + 0.24 * fl, r: 110} : undefined;
  const pc = {x: PB.x + PB.w / 2, y: PB.y + PB.h / 2};
  return (
    <g>
      {film && <RoomBase />}
      <g transform={hookXf(t)}>
        {film && (
          <g>
            <Lamp x={940} k={1} f={fr} spread={1.15} floorY={HOOK.G + 6} seed="hook" />
            <ellipse cx={pc.x} cy={pc.y} rx={520} ry={560} fill="url(#gScreenLight)" opacity={0.35 + 0.4 * fl} style={{mixBlendMode: 'screen'}} />
          </g>
        )}
        <Chair x={HOOK.x - 10 * HOOK.s} y={HOOK.G} s={HOOK.s} />
        <rect x={deskX + 14} y={DESK_Y - 9} width={96} height={9} rx={3} fill="#9AA3B2" />
        <path d={`M ${deskX + 102} ${DESK_Y - 6} L ${deskX + 114} ${DESK_Y - 6} L ${deskX + 136} ${DESK_Y - 118} L ${deskX + 124} ${DESK_Y - 118} Z`} fill="#B7C0CE" />
        {film && <path d={`M ${deskX + 100} ${DESK_Y - 8} L ${deskX + 122} ${DESK_Y - 116}`} stroke="#DCE7FF" strokeWidth={3} opacity={0.6} />}
        <You fr={fr} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="body" glow={glow} />
        {film && <Shadow x={deskX + 180} y={HOOK.G + 4} rx={220} ry={14} o={0.55} />}
        <rect x={deskX} y={DESK_Y} width={360} height={18} rx={4} fill={C.woodTop} />
        {film && <rect x={deskX} y={DESK_Y} width={360} height={5} rx={2.5} fill="#7A6652" />}
        <rect x={deskX + 16} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <rect x={deskX + 330} y={DESK_Y + 18} width={14} height={HOOK.G - DESK_Y - 18} fill={C.wood} />
        <g transform={`translate(${sk0.dx} 0) rotate(${sk0.rot} ${pc.x} ${pc.y})`}>
          {film ? <PhoneBody b={PB} /> : (
            <>
              <ellipse cx={pc.x} cy={pc.y} rx={300} ry={430} fill="url(#g3blue)" opacity={0.16 + 0.3 * fl} />
              <rect x={PB.x} y={PB.y} width={PB.w} height={PB.h} rx={46} fill={C.phone} stroke="#3A3F4C" strokeWidth={4} />
            </>
          )}
          <PhoneScreen t={t} near={near} />
        </g>
        <You fr={fr} pose={pose} expr={expr} x={HOOK.x} G={HOOK.G} s={HOOK.s} seed="hook" part="arms" glow={glow} />
      </g>
      <Burst t={t} />
    </g>
  );
};

const hookCount = (t: number) => {
  let n = 0;
  if (t >= EV.buzz[0]) n = 1;
  if (t >= EV.buzz[1]) n = 2;
  if (t >= EV.buzz[2]) n = 3;
  if (t >= EV.buzzAgain) n = 4;
  if (t >= EV.count[0]) n = Math.round(4 + 116 * Math.pow(pr(t, EV.count), 1.25));
  return n;
};
const HookText: React.FC<{t: number}> = ({t}) => {
  const {film} = useMode();
  const out = 1 - pr(t, EV.titleOut);
  if (out <= 0) return null;
  const s = pe(t, EV.shrinkTitle);
  const size = lerp(96, 64, s);                 // 样片 v2：缩到左上角后 64 像素
  const title = '手机通知：全开？全关？';
  const bigW = tw(title, 96);
  const left = lerp(960 - bigW / 2, 24, s);
  const top = lerp(22, 88, s);                  // 缩到左上角，在“AI 生成”标下面
  const n = hookCount(t);
  const cp = pushMap(t, COUNTER_AT.x, COUNTER_AT.y);   // 计数在你左边，跟着推镜头走
  const inBurst = t >= EV.burst[0] && t < EV.camBack[1];
  let pop = 0;
  for (const a of [...EV.buzz, EV.buzzAgain]) pop = Math.max(pop, bump(t, a, 0.25));
  const fl = t >= EV.countFlash[0] ? Math.max(bump(t, EV.countFlash[0], 0.2), bump(t, EV.countFlash[0] + 0.2, 0.2)) : 0;
  const titleStyle: React.CSSProperties = film
    ? {color: '#FFF8EC', textShadow: s < 0.5 ? '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)' : '0 3px 14px rgba(0,0,0,0.5)', opacity: out * lerp(1, 0.8, s)}
    : {color: '#FFFFFF', textShadow: '0 4px 20px rgba(0,0,0,0.5)', opacity: out};
  return (
    <>
      <div style={{position: 'absolute', left, top, fontFamily: SANS, fontWeight: 700, fontSize: size, whiteSpace: 'nowrap', lineHeight: `${size * 1.2}px`, ...titleStyle}}>{title}</div>
      <div style={{position: 'absolute', left: cp.x, top: cp.y, fontFamily: SANS, fontWeight: 600, fontSize: 60, color: fl > 0 ? C.warm : film ? CREAM : '#FFFFFF',
        whiteSpace: 'nowrap', lineHeight: '72px', opacity: out, transformOrigin: 'center center', transform: `scale(${1 + 0.1 * pop + 0.08 * fl})`,
        background: film && !inBurst ? 'transparent' : 'rgba(10,11,16,0.92)', borderRadius: 16, padding: '0 14px', textShadow: film ? SHADOW : undefined,
        boxShadow: inBurst ? '0 8px 30px rgba(0,0,0,0.6)' : undefined}}>
        今天被打断<span style={{fontVariantNumeric: 'tabular-nums', display: 'inline-block', minWidth: 120, textAlign: 'center',
          ...(film ? {background: 'rgba(0,0,0,0.45)', borderRadius: 14, margin: '0 10px', minWidth: 110} : {})}}>{n}</span>次
      </div>
    </>
  );
};

// ================= 三栏 10.4–39.6 秒 =================
const COLX = [320, 960, 1600];
const LABEL_Y = 180;
const CG = 640, CS = 1.35;              // 样片 v2：读数数字改 96 像素，三栏整体再上移 80，读数离字幕仍至少 60 像素
const RD_Y = [706, 800];
const LABELS = ['全开', '全关', '先分开'];
// 推镜头时地面去 y=720（三栏地面上移以后，先分开的标签才不压到上面那排分类标签）
const FOCUS: [number, number, number][] = [[110, 720, 0.35], [300, 720, 0.35], [612, 720, 1.2]];
const ACTIVE: [number, number | null][] = [[10.4, null], [11.8, 0], [13.4, 1], [21.6, 2], [34.6, 1], [36.6, 2]];
// v3：不讲的栏不变暗；聚光（灰框是一圈暖黄框 + 地上一块光，成片是头顶那盏灯）跟着正在讲的那一栏走
const spotAt = (t: number) => {
  let x = COLX[0], prevX = COLX[0], ts = -9, on = false;
  for (const [tk, a] of ACTIVE) {
    if (t < tk) break;
    if (a !== null) { prevX = on ? x : COLX[a]; x = COLX[a]; on = true; ts = tk; } else on = false;
  }
  return {x: lerp(prevX, x, ease((t - ts) / 0.3)), k: on ? clamp((t - EV.leftFlash) / 0.25) : 0};
};
const activeOf = (t: number) => {
  let a: number | null = null;
  for (const [tk, c] of ACTIVE) if (t >= tk) a = c;
  return a;
};
const focusU = (t: number) => pe(t, EV.push) * (1 - pe(t, EV.pull));
const textO = (t: number) => clamp(1 - pr(t, EV.textOut) + pr(t, EV.textIn));
const leftFlick = (t: number) => (t < EV.leftFlash ? 0 : Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 2.6)), 2));

const colPose = (c: number, t: number): RPose => {
  if (c === 0) return nudge(SIT_LOOK, {neck: 4 * leftFlick(t)});
  if (c === 1) {
    return ptrack(t, [
      [0, SIT], [EV.pickUp[0], SIT_GRAB, 0.22], [EV.pickUp[0] + 0.24, SIT_HOLD, 0.3], [EV.putDown[0], SIT_GRAB, 0.22], [EV.putDown[0] + 0.24, SIT, 0.3],
      [EV.startle[0], SIT_STARTLE, 0.15], [EV.startle[1] + 0.05, SIT_LOOK, 0.3], [EV.press[0], SIT_PRESSED, 0.3],
      [EV.glances[0], SIT_PRESSED_LOOK, 0.25], [35.25, SIT_PRESSED, 0.3], [EV.glances[1], SIT_PRESSED_LOOK, 0.25], [36.35, SIT_PRESSED, 0.3],
    ]);
  }
  return ptrack(t, [[0, SIT], [EV.deal[0] - 0.4, SIT_FWD, 0.3], [EV.pull[0], SIT, 0.4], [EV.bookTake[0], SIT_READ, 0.4]]);
};
const colExpr = (c: number, t: number): Expr => {
  if (c === 0) return etrack(t, [[0, E.calm], [EV.leftFlash, E.worry, 0.3]]);
  if (c === 1) return etrack(t, [[0, E.calm], [EV.pickUp[0], E.blank, 0.3], [EV.putDown[1], E.calm, 0.3], [EV.startle[0], E.surprise, 0.12], [18.6, E.worry, 0.3], [EV.press[0], E.sad, 0.2]]);
  return etrack(t, [[0, E.calm], [EV.bookOpen[0], READING, 0.4], [EV.glowPulse, SMILE, 0.3], [37.8, READING, 0.4]]);
};

const MiniPhone: React.FC<{cx: number; cy: number; a: 'front' | 'back'; b?: 'front' | 'back'; flip?: number; lit?: number; warm?: number; bars?: number; o?: number; sc?: number}> = (
  {cx, cy, a, b, flip = 0, lit = 0, warm = 0, bars = 0, o = 1, sc = 1},
) => {
  const {film} = useMode();
  const w = 92, h = 160;
  const face = flip > 0.5 && b ? b : a;
  const sx = Math.max(0.04, Math.abs(Math.cos(Math.PI * flip)));
  return (
    <g opacity={o} transform={`translate(${cx} ${cy}) scale(${sx * sc} ${sc})`}>
      {lit > 0 && face === 'front' && <ellipse cx={0} cy={0} rx={120} ry={130} fill="url(#g3blue)" opacity={0.55 * lit} />}
      {warm > 0 && face === 'front' && <ellipse cx={0} cy={0} rx={130} ry={140} fill="url(#g3warm)" opacity={0.6 * warm} />}
      {film && <rect x={-w / 2 + 6} y={-h / 2 + 10} width={w} height={h} rx={16} fill="#000" opacity={0.45} filter="url(#fBlur4)" />}
      <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={film ? 16 : 14} fill={face === 'front' ? (film ? '#5D626D' : C.phone) : (film ? '#5D626D' : C.back)} stroke={film ? 'none' : '#454B58'} strokeWidth={3} />
      {film && <rect x={-w / 2 + 3} y={-h / 2 + 3} width={w - 6} height={h - 6} rx={13} fill={face === 'front' ? '#06070A' : '#3A3E48'} />}
      {face === 'front' ? (
        <>
          <rect x={-w / 2 + 6} y={-h / 2 + 6} width={w - 12} height={h - 12} rx={9} fill={mixHex(film ? '#1D2133' : C.screen, '#5E7FB8', lit)} />
          {film && <rect x={-12} y={-h / 2 + 10} width={24} height={7} rx={3.5} fill="#000" />}
          {[0, 1, 2].map((i) => i < bars && <rect key={i} x={-w / 2 + 12} y={-h / 2 + 22 + i * 26} width={w - 24} height={18} rx={5} fill="#FFFFFF" opacity={0.75} />)}
          {warm > 0 && <rect x={-w / 2 + 10} y={-14} width={w - 20} height={28} rx={6} fill={C.warm} opacity={warm} />}
        </>
      ) : (
        <>
          <rect x={-w / 2 + 8} y={-h / 2 + 8} width={34} height={34} rx={9} fill="#24272E" />
          <circle cx={-w / 2 + 18} cy={-h / 2 + 18} r={6} fill="#0E0F12" />
          <circle cx={-w / 2 + 32} cy={-h / 2 + 32} r={6} fill="#0E0F12" />
          <circle cx={0} cy={8} r={9} fill="#4A4E58" />
        </>
      )}
    </g>
  );
};

const Clock: React.FC<{x: number; y: number; u: number; o: number}> = ({x, y, u, o}) => {
  const {film} = useMode();
  const r = 42;
  const a = -Math.PI / 2 + Math.PI * 2 * u;
  const ha = -Math.PI / 2 + Math.PI / 3 + (Math.PI / 6) * u;
  const large = u > 0.5 ? 1 : 0;
  const ex = x + r * 0.92 * Math.cos(a), ey = y + r * 0.92 * Math.sin(a);
  // v3：钟旁边标时刻 14:40 → 15:40
  const mins = 14 * 60 + 40 + Math.round(60 * u);
  const label = `${Math.floor(mins / 60)}:${String(mins % 60).padStart(2, '0')}`;
  return (
    <g opacity={o}>
      <circle cx={x} cy={y} r={r} fill="#1E222B" stroke="#C9CED8" strokeWidth={5} />
      {u > 0.001 && u < 0.999 && <path d={`M ${x} ${y} L ${x} ${y - r * 0.92} A ${r * 0.92} ${r * 0.92} 0 ${large} 1 ${ex} ${ey} Z`} fill={C.warm} opacity={0.35} />}
      {u >= 0.999 && <circle cx={x} cy={y} r={r * 0.92} fill={C.warm} opacity={0.35} />}
      {[0, 1, 2, 3].map((i) => <line key={i} x1={x + Math.cos((i * Math.PI) / 2) * r * 0.72} y1={y + Math.sin((i * Math.PI) / 2) * r * 0.72}
        x2={x + Math.cos((i * Math.PI) / 2) * r * 0.86} y2={y + Math.sin((i * Math.PI) / 2) * r * 0.86} stroke="#C9CED8" strokeWidth={4} />)}
      <line x1={x} y1={y} x2={x + Math.cos(ha) * r * 0.5} y2={y + Math.sin(ha) * r * 0.5} stroke="#FFFFFF" strokeWidth={6} strokeLinecap="round" />
      <line x1={x} y1={y} x2={x + Math.cos(a) * r * 0.78} y2={y + Math.sin(a) * r * 0.78} stroke="#FFFFFF" strokeWidth={4} strokeLinecap="round" />
      <circle cx={x} cy={y} r={5} fill="#FFFFFF" />
      <Tx x={x} y={y - r - 36} size={48} anchor="middle" fill={u >= 0.999 ? C.warm : film ? CREAM : C.bright} weight={700}>{label}</Tx>
    </g>
  );
};

const MSG = '明早 8 点前交表';
const MSG_W = tw(MSG, 56) + 52;
const MsgCard: React.FC<{cx: number; cy: number; head?: string; tone: 'gray' | 'warm'; sc?: number; sy?: number; o?: number; heavy?: boolean}> = (
  {cx, cy, head, tone, sc = 1, sy = 1, o = 1, heavy},
) => {
  const w = MSG_W;
  const h = head ? 160 : 92;
  const warm = tone === 'warm';
  return (
    <g opacity={o} transform={`translate(${cx} ${cy}) scale(${sc * (2 - sy)} ${sc * sy})`}>
      {warm && <ellipse cx={0} cy={0} rx={w * 0.72} ry={h * 1.05} fill="url(#g3warm)" opacity={0.5} />}
      {heavy && <rect x={-w / 2 + 6} y={-h / 2 + 22} width={w} height={h} rx={16} fill="#000000" opacity={0.45} />}
      {heavy && <rect x={-w / 2} y={-h / 2 + 16} width={w} height={h} rx={16} fill="#1A1D24" stroke="#3A3F4B" strokeWidth={3} />}
      <rect x={-w / 2} y={-h / 2} width={w} height={h} rx={16} fill={warm ? C.warmBg : heavy ? '#3A3F4B' : '#262A33'} stroke={warm ? C.warm : '#5A6070'} strokeWidth={warm ? 5 : 3} />
      {head && <Tx x={-w / 2 + 26} y={-h / 2 + 42} size={56} fill={C.bright}>{head}</Tx>}
      <Tx x={-w / 2 + 26} y={head ? h / 2 - 42 : 0} size={56} fill={warm ? C.warm : heavy ? '#D3D7DF' : '#A3A9B4'}>{MSG}</Tx>
    </g>
  );
};

// v3：一本书。open 0 = 合着（看得见封面），1 = 摊开；turn：翻一页（0..1）
const Book: React.FC<{x: number; y: number; open: number; turn?: number; sc?: number; flat?: boolean}> = ({x, y, open, turn = 0, sc = 1, flat}) => {
  if (flat) {
    return (
      <g transform={`translate(${x} ${y})`}>
        <rect x={-60} y={-16} width={120} height={16} rx={3} fill="#B65A3C" />
        <rect x={-56} y={-12} width={112} height={6} rx={2} fill="#F2E6D0" />
      </g>
    );
  }
  const pw = 70 * open + 4, ph = 92;
  const lines = (dir: 1 | -1) => [0, 1, 2, 3, 4, 5].map((i) => (
    <line key={i} x1={dir * 12} y1={-ph / 2 + 18 + i * 12} x2={dir * (pw - 10)} y2={-ph / 2 + 18 + i * 12} stroke="#B9B2A3" strokeWidth={3} strokeLinecap="round" opacity={open} />
  ));
  const tp = clamp(turn);
  return (
    <g transform={`translate(${x} ${y}) scale(${sc})`}>
      <rect x={-pw - 6} y={-ph / 2 - 4} width={pw * 2 + 12} height={ph + 10} rx={6} fill="#B65A3C" />
      <path d={`M 0 ${-ph / 2} L ${-pw} ${-ph / 2 + 4} L ${-pw} ${ph / 2} L 0 ${ph / 2 - 2} Z`} fill="#F4EBDA" />
      <path d={`M 0 ${-ph / 2} L ${pw} ${-ph / 2 + 4} L ${pw} ${ph / 2} L 0 ${ph / 2 - 2} Z`} fill="#FBF4E6" />
      {lines(-1)}{lines(1)}
      <line x1={0} y1={-ph / 2} x2={0} y2={ph / 2 - 2} stroke="#D9CDB6" strokeWidth={3} />
      {tp > 0 && tp < 1 && <path d={`M 0 ${-ph / 2} L ${pw * Math.cos(Math.PI * tp)} ${-ph / 2 + 4 - 10 * Math.sin(Math.PI * tp)} L ${pw * Math.cos(Math.PI * tp)} ${ph / 2 - 10 * Math.sin(Math.PI * tp)} L 0 ${ph / 2 - 2} Z`}
        fill="#FFFDF6" stroke="#D9CDB6" strokeWidth={2} />}
    </g>
  );
};

const Column: React.FC<{c: number; t: number; fr: number}> = ({c, t, fr}) => {
  const {film} = useMode();
  const X = COLX[c];
  let px = X - 110, G = CG, s = CS;
  let pose = colPose(c, t);
  let expr = colExpr(c, t);
  const propO = pr(t, EV.propsIn) * (c === 2 ? clamp(1 - pr(t, [22.2, 22.6]) + pr(t, [31.3, 31.7])) : 1);
  const txO = c === 2 ? 1 : textO(t);
  const dy = c === 1 ? -10 * bump(t, EV.startle[0], 0.35) : c === 2 ? 5 * bump(t, EV.settle[0], 0.4) : 0;
  const hd = headAt(pose, px, G, s);
  const top = G - 88 * s;
  const phoneC = {x: X + 110, y: top - 80};
  let phone: React.ReactNode = null;
  if (c === 0) {
    const fl = leftFlick(t);
    phone = <MiniPhone cx={phoneC.x} cy={phoneC.y} a="front" lit={t < EV.leftFlash ? 0.15 : 0.25 + 0.75 * fl} bars={t < EV.leftFlash ? 0 : 1 + (Math.floor(t * 5.2) % 3)} o={propO} />;
  } else if (c === 1) {
    // v3：14.1 秒伸手拿起扣着的手机，看一眼（没有新消息），15.15 秒放回去、扣好
    const hand = handsAt(pose, px, G, s);
    const up = pe(t, EV.pickUp), dn = pe(t, EV.putDown);
    const inHand = t >= EV.pickUp[0] && t < EV.putDown[1];
    if (inHand) {
      const k = t < EV.putDown[0] ? up : 1 - dn;
      const x = lerp(phoneC.x, hand.x + 18, k), y = lerp(phoneC.y, hand.y + 18, k);
      const faceFront = k > 0.5;
      phone = <MiniPhone cx={x} cy={y} a={faceFront ? 'front' : 'back'} lit={faceFront ? 0.55 : 0} sc={lerp(1, 0.6, k)} o={propO} />;
    } else {
      const f1 = pe(t, EV.flip), f2 = pe(t, EV.flipBack);
      phone = t < EV.flipBack[0]
        ? <MiniPhone cx={phoneC.x} cy={phoneC.y} a="back" b="front" flip={f1} lit={0.5} warm={f1 > 0.5 ? 0.8 : 0} o={propO} />
        : <MiniPhone cx={phoneC.x} cy={phoneC.y} a="front" b="back" flip={f2} lit={0.5} warm={0.8} o={propO} />;
    }
  } else {
    const w = pr(t, [EV.rightCard, EV.rightCard + 0.15]) * (1 - pr(t, [EV.cardIntoPhone[1], EV.cardIntoPhone[1] + 0.4]));
    phone = <MiniPhone cx={phoneC.x} cy={phoneC.y} a="front" lit={0.2 + 0.5 * w} warm={w} bars={t >= EV.rightCard ? 1 : 0} o={propO} />;
  }
  const la = EV.labels[c];
  // 样片 v2：全开、先分开从上面落下；全关从右边滑进来（不穿过标题）。右栏那张卡片亮着时，先分开的标签往上让 40
  const lift = c === 2 ? -40 * pe(t, [EV.rightCard - 0.2, EV.rightCard]) * (1 - pe(t, [EV.cardIntoPhone[1], EV.cardIntoPhone[1] + 0.3])) : 0;
  const ly = c === 1 ? LABEL_Y : lerp(-80, LABEL_Y, easeBack(pr(t, [la, la + 0.3]))) + lift;
  const lx = c === 1 ? lerp(2150, X, easeOut(pr(t, [la, la + 0.32]))) : X;
  const isActive = activeOf(t) === c && focusU(t) < 0.05;
  // 右栏的书：先平放在桌上，33.7 秒拿到手里，34.1 秒翻开，37.0 秒翻一页
  const bookIn = c === 2 && t >= EV.bookTake[0];
  const bk = pe(t, EV.bookTake);
  const bh = handsAt(pose, px, G, s);
  const bookFlat = {x: X + 110, y: top};
  return (
    <g>
      {film && <Shadow x={px + 10} y={G + 4} rx={95} ry={12} o={0.5 * pr(t, EV.propsIn)} />}
      <g opacity={pr(t, EV.propsIn)}><Chair x={px - 10 * s} y={G} s={s} /></g>
      <You fr={fr} pose={pose} expr={expr} x={px} G={G} s={s} seed={`col${c}`} dy={dy}
        glow={film && c === 0 && t >= EV.leftFlash ? {at: {x: solve(pose).head.x + 40, y: solve(pose).head.y}, color: '#BFD4FF', amount: 0.25 + 0.35 * leftFlick(t), r: 90} : undefined} />
      <g opacity={propO}>
        {film && <Shadow x={X + 110} y={G + 4} rx={100} ry={10} o={0.5} />}
        <rect x={X + 20} y={top} width={180} height={12} rx={4} fill={C.woodTop} />
        {film && <rect x={X + 20} y={top} width={180} height={4} rx={2} fill="#7A6652" />}
        <rect x={X + 34} y={top + 12} width={10} height={G - top - 12} fill={C.wood} />
        <rect x={X + 176} y={top + 12} width={10} height={G - top - 12} fill={C.wood} />
      </g>
      {phone}
      {c === 2 && !bookIn && <g opacity={propO}><Book x={bookFlat.x} y={bookFlat.y} open={0} flat /></g>}
      {bookIn && (
        <g>
          {bk < 1 && <g opacity={1 - bk}><Book x={lerp(bookFlat.x, bh.x, bk)} y={lerp(bookFlat.y, bh.y, bk)} open={0} flat /></g>}
          {bk > 0.3 && <Book x={bh.x + 14} y={bh.y + 6} open={pe(t, EV.bookOpen)} turn={pr(t, [EV.glowPulse, EV.glowPulse + 0.45])} sc={lerp(0.55, 0.78, bk)} />}
          {t >= EV.bookOpen[1] && <ellipse cx={bh.x + 14} cy={bh.y + 6} rx={150} ry={110} fill="url(#g3warm)" opacity={0.18 + 0.3 * bump(t, EV.glowPulse, 0.6)} />}
        </g>
      )}
      {c === 0 && t >= EV.leftFlash && [-1, 1].map((d) => (
        <path key={d} d={`M ${phoneC.x + d * 64} ${phoneC.y - 26} q ${d * 12} 26 0 52`} fill="none" stroke="#D6E6FF" strokeWidth={5} strokeLinecap="round" opacity={leftFlick(t)} />
      ))}
      {/* 中栏：自己拿起来那一下冒个 +1；小钟 14:40→15:40；交表那条 15:40 才弹出来；19 秒起砸到头上 */}
      {c === 1 && t >= EV.midSelf && t < EV.midSelf + 0.9 && (
        <Tx x={bh.x + 90} y={bh.y - 110 - 60 * pr(t, [EV.midSelf, EV.midSelf + 0.9])} size={56} anchor="middle" weight={800} fill={C.warm}
          o={txO * (1 - pr(t, [EV.midSelf + 0.6, EV.midSelf + 0.9]))}>+1</Tx>
      )}
      {c === 1 && t >= EV.clockIn[0] && <Clock x={X + 262} y={460} u={pe(t, EV.clockTurn)} o={pr(t, EV.clockIn) * (1 - pr(t, EV.clockOut)) * txO} />}
      {c === 1 && t >= EV.cardIn[0] && (() => {
        const A = {x: X + 60, y: 272};
        const restY = hd.top - 92 / 2 - 14;
        const lift = pe(t, EV.cardLift), drop = easeIn(pr(t, EV.cardDrop));
        const land = bump(t, EV.cardDrop[1], 0.28);
        const pressed = t >= EV.cardDrop[1];
        let cx = lerp(A.x, hd.x, lift);
        let cy = lerp(lerp(phoneC.y - 40, A.y, po(t, EV.cardIn)), restY - 120, lift);
        cy = lerp(cy, restY, drop);
        if (pressed) { cx = hd.x; cy = restY + 6 * land; }
        const heavy = t >= EV.cardLift[0];
        return (
          <g>
            {pressed && [-1, 1].map((d) => (
              <path key={d} d={`M ${hd.x + d * (MSG_W / 2 + 6)} ${restY + 30} q ${d * 22} -6 ${d * 36} -22`} fill="none" stroke="#9AA0AC" strokeWidth={4}
                strokeLinecap="round" opacity={land * txO} />
            ))}
            <MsgCard cx={cx} cy={cy} tone="gray" heavy={heavy} sy={1 - 0.1 * land} sc={easeBack(pr(t, EV.cardIn))} o={clamp(pr(t, EV.cardIn) * 3) * txO} />
          </g>
        );
      })()}
      {c === 2 && t >= EV.rightCard && t < EV.cardIntoPhone[1] && (() => {
        const into = pe(t, EV.cardIntoPhone);
        return (
          <MsgCard cx={lerp(X + 60, phoneC.x, into)} cy={lerp(262, phoneC.y, into)} head="工作群" tone="warm"
            sc={lerp(easeBack(pr(t, [EV.rightCard, EV.rightCard + 0.2])), 0.15, into)} o={1 - pr(t, [EV.cardIntoPhone[1] - 0.1, EV.cardIntoPhone[1]])} />
        );
      })()}
      {film
        ? <Sticker x={lx} y={ly} text={LABELS[c]} size={64} o={txO * (t >= la ? 1 : 0)} pop={c === 1 ? 1 : easeBack(pr(t, [la, la + 0.3]))} ring={isActive ? 1 : 0} />
        : <Tag x={lx} y={ly} text={LABELS[c]} size={64} o={txO * (t >= la ? 1 : 0)} stroke={isActive ? C.warm : undefined} />}
    </g>
  );
};

// 样片 v2：数字 96 像素、等宽、右对齐；“被打断”“要紧的晚看到”52 像素。同一栏两行的数字右边对齐成一列
const NUM = 96, LAB = 52;
const NUM_R = (cx: number) => cx + 214;          // 数字右边缘
const Readout: React.FC<{cx: number; cy: number; pre: string; suf: string; n: number; color: string; pop: number}> = ({cx, cy, pre, suf, n, color, pop}) => {
  const {film} = useMode();
  const nr = NUM_R(cx);
  const slotW = 3 * 0.62 * NUM;
  const row = (fill: string, dx = 0, dy = 0) => (
    <g transform={`translate(${dx} ${dy})`}>
      <Tx x={nr - slotW - 16} y={cy + 6} size={LAB} fill={fill} anchor="end">{pre}</Tx>
      <g transform={`translate(${nr} ${cy}) scale(${1 + 0.18 * pop})`}>
        <text x={0} y={0} fontSize={NUM} fontFamily={SANS} fontWeight={700} fill={fill} textAnchor="end" dominantBaseline="central"
          style={{fontVariantNumeric: 'tabular-nums'}}>{n}</text>
      </g>
      <Tx x={nr + 14} y={cy + 6} size={LAB} fill={fill}>{suf}</Tx>
    </g>
  );
  return (
    <g>
      {film && <g filter="url(#fBlur4)" opacity={0.7}>{row('#000000', 2, 5)}</g>}
      {row(film && color === C.ink ? CREAM : color)}
    </g>
  );
};

// 读数：一开始就是“0”。v3：上移到 760、822，画在字幕带上面
const Readouts: React.FC<{t: number}> = ({t}) => {
  const o = textO(t) * pr(t, EV.readoutsIn);
  if (t < EV.readoutsIn[0] || o <= 0) return null;
  const rolls = [EV.leftRoll, EV.midRoll, EV.rightRoll];
  const lates = [EV.leftLate, EV.midLate, EV.rightLate];
  return (
    <g opacity={o}>
      {[0, 1, 2].map((c) => {
        // v3：全关先滚到 45，自己拿起手机那一下加到 46
        const n1 = c === 1 ? (t >= EV.midSelf ? 46 : Math.round(45 * pe(t, rolls[1]))) : Math.round(READ[c][0] * pe(t, rolls[c]));
        const n2 = t < lates[c] ? 0 : READ[c][1];
        const warm = c === 1 && t >= EV.midLate;
        const pop1 = c === 1 ? Math.max(bump(t, rolls[1][1], 0.3), bump(t, EV.midSelf, 0.35)) : bump(t, rolls[c][1], 0.3);
        return (
          <g key={c}>
            <Readout cx={COLX[c]} cy={RD_Y[0]} pre="被打断" suf="次" n={n1} color={C.ink} pop={pop1} />
            <Readout cx={COLX[c]} cy={RD_Y[1]} pre="要紧的晚看到" suf="件" n={n2} color={warm ? C.warm : C.ink} pop={READ[c][1] ? bump(t, lates[c], 0.3) : 0} />
          </g>
        );
      })}
    </g>
  );
};

// 背景：灰框是平的深色底 + 聚光框；成片是暗房间，每栏头顶一盏灯，讲到哪栏哪盏亮
const ColBackdrop: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const {film} = useMode();
  const u = focusU(t);
  const sp = spotAt(t);
  const showSpot = (1 - clamp(u * 5)) * sp.k;
  if (film) {
    const inO = 1;
    const a = activeOf(t);
    return (
      <g opacity={inO}>
        <RoomBase />
        {[0, 1, 2].map((c) => {
          const kOn = a === null ? 0.6 : a === c ? 1 : 0.3;
          return <Lamp key={c} x={COLX[c]} k={kOn * (1 - u)} f={fr} spread={0.62} cy={350} floorY={CG + 6} seed={`c${c}`} />;
        })}
      </g>
    );
  }
  if (showSpot <= 0.001 || t >= 39.6) return null;
  return (
    <g opacity={showSpot}>
      <ellipse cx={sp.x - 20} cy={CG + 4} rx={260} ry={40} fill="url(#g3warm)" opacity={0.35} />
      <rect x={sp.x - 304} y={124} width={608} height={740} rx={30} fill="#FFC94D" opacity={0.04} />
      <rect x={sp.x - 304} y={124} width={608} height={740} rx={30} fill="none" stroke={C.warm} strokeWidth={4} opacity={0.85} />
    </g>
  );
};

const Columns: React.FC<{t: number; fr: number}> = ({t, fr}) => {
  const u = focusU(t);
  return (
    <g>
      {[0, 2, 1].map((c) => {
        const X = COLX[c];
        const [fx, fy, K] = FOCUS[c];
        const k = lerp(1, K, u), tx = lerp(X, fx, u), ty = lerp(CG, fy, u);
        // 样片 v2：10.4 秒三个你连椅子、小桌一起从中间滑开
        const slide = c === 1 ? 0 : (COLX[1] - X) * (1 - pe(t, EV.split));
        return (
          <g key={c} transform={`translate(${slide} 0) translate(${tx} ${ty}) scale(${k}) translate(${-X} ${-CG})`}>
            <Column c={c} t={t} fr={fr} />
          </g>
        );
      })}
    </g>
  );
};

// ================= 先分开 22.6–31.3 秒：一次只放大一类，放在画面中间 =================
const STAGE_C = 1080;
const CHIP_Y = 270;
const CHIPS = ['广告推送', '群', '点赞', '私聊'];
const CHIP_W = CHIPS.map((l) => tw(l, 64) + 64 * 0.7);
const CHIP_X = (() => {
  const gap = 28, total = CHIP_W.reduce((a, b) => a + b, 0) + gap * (CHIPS.length - 1);
  let x = STAGE_C - total / 2;
  return CHIP_W.map((w) => { const c = x + w / 2; x += w + gap; return c; });
})();
const BW = 380, BH = 84;
const GROUP = ['同学群', '工作群', '小区群', '老师群', '购物群'];
const GROUP_SLOT = [2, 0, 3, 1, 4];
const GROUP_TOP = [false, true, false, true, false];
const DEAL_FROM = {x: 540, y: 626};
const TICKS = [{x: 780, label: '9点'}, {x: 1080, label: '15点'}, {x: 1380, label: '21点'}];
const LINE_Y = 740;
const BOX_START = {x: 640, y: LINE_Y - 52};
const chipActive = (t: number) => (t < EV.adOpen[0] ? -1 : t < EV.groupOpen[0] ? 0 : t < EV.likeOpen[0] ? 1 : t < EV.dmOpen[0] ? 2 : 3);

const Bell: React.FC<{x: number; y: number; sc: number}> = ({x, y, sc}) => (
  <g transform={`translate(${x} ${y}) scale(${sc})`}>
    <path d="M -15 9 Q -15 -15 0 -17 Q 15 -15 15 9 L 19 13 L -19 13 Z" fill="#C9CED8" />
    <circle cx={0} cy={17} r={4.5} fill="#C9CED8" />
    <line x1={-20} y1={-17} x2={20} y2={21} stroke={C.red} strokeWidth={5} strokeLinecap="round" />
  </g>
);
const Pin: React.FC<{x: number; y: number; o: number}> = ({x, y, o}) => (
  <g opacity={o}>
    <line x1={x} y1={y} x2={x + 12} y2={y + 34} stroke="#D8DCE4" strokeWidth={5} strokeLinecap="round" />
    <circle cx={x} cy={y} r={18} fill={C.red} />
    <circle cx={x - 6} cy={y - 6} r={5} fill="#FFFFFF" opacity={0.6} />
  </g>
);
const BigCard: React.FC<{x: number; y: number; text: string; sc?: number; o?: number; fill?: string; fg?: string; glow?: number}> = (
  {x, y, text, sc = 1, o = 1, fill = C.card, fg = C.ink, glow = 0},
) => (
  <g opacity={o} transform={`translate(${x} ${y}) scale(${sc})`}>
    {glow > 0 && <rect x={-BW / 2 - 12} y={-BH / 2 - 12} width={BW + 24} height={BH + 24} rx={24} fill="#9FC2FF" opacity={0.35 * glow} />}
    <rect x={-BW / 2} y={-BH / 2} width={BW} height={BH} rx={16} fill={fill} stroke={C.edge} strokeWidth={2} />
    <Tx x={-BW / 2 + 28} y={0} size={56} fill={fg}>{text}</Tx>
  </g>
);
const fromChip = (i: number, dest: {x: number; y: number}, u: number) => ({
  x: lerp(CHIP_X[i], dest.x, u), y: lerp(CHIP_Y, dest.y, u), sc: lerp(0.25, 1, u), o: clamp(u * 4),
});
// v3：盒子沿时间轴走；红心一个个飞进去，到 9、15、21 点各开一次盖，攒着的一次看完
const boxAt = (t: number) => {
  let b = {...BOX_START};
  EV.stops.forEach(([s0, s1], i) => {
    const prev = i === 0 ? BOX_START : {x: TICKS[i - 1].x, y: LINE_Y - 52};
    if (t >= s0) b = {x: lerp(prev.x, TICKS[i].x, pe(t, [s0, s1])), y: LINE_Y - 52};
  });
  return b;
};
const HEART_N = 12;
const heartAt = (k: number) => EV.hearts[0] + (k * (EV.hearts[1] - EV.hearts[0])) / (HEART_N - 1);   // 第 k 颗出发的时刻
const HEART_FLY = 0.32;

const Stage: React.FC<{t: number}> = ({t}) => {
  const out = 1 - pr(t, EV.pilesOut);
  const act = chipActive(t);
  const adG = pr(t, EV.adGray), adX = pe(t, EV.adGone);
  const nodes: React.ReactNode[] = [];
  for (let k = 0; k < 12; k++) {
    const d = EV.deal[0] + 0.022 * k;
    const u = po(t, [d, d + 0.28]);
    if (u <= 0 || u >= 1) continue;
    const i = k % 4;
    nodes.push(<rect key={`d${k}`} x={lerp(DEAL_FROM.x, CHIP_X[i], u) - 30} y={lerp(DEAL_FROM.y, CHIP_Y, u) - 16} width={60} height={32} rx={6}
      fill={C.card} stroke={C.edge} strokeWidth={2} opacity={1 - u * 0.5} />);
  }
  if (t >= EV.adOpen[0] && t < EV.adGone[1]) {
    ['拼单立减', '热榜第一', '领红包'].forEach((txt, j) => {
      const u = po(t, [EV.adOpen[0] + 0.05 * j, EV.adOpen[1] + 0.05 * j]);
      const f = fromChip(0, {x: STAGE_C, y: 420 + j * 104}, u);
      nodes.push(<BigCard key={`a${j}`} x={f.x} y={f.y} sc={f.sc * (1 - adX)} o={f.o * (1 - adX)} text={txt}
        fill={mixHex(C.card, '#3A3D44', adG)} fg={mixHex(C.ink, C.gray, adG)} />);
    });
  }
  if (t >= EV.groupOpen[0] && t < EV.groupClose[1]) {
    const rise = pe(t, EV.rise);
    const close = pe(t, EV.groupClose);
    [0, 2, 4, 1, 3].forEach((i) => {
      const slot = lerp(i, GROUP_SLOT[i], rise);
      const u = po(t, [EV.groupOpen[0] + 0.04 * i, EV.groupOpen[1] + 0.04 * i]) * (1 - close);
      const f = fromChip(1, {x: STAGE_C, y: 380 + slot * 92}, u);
      const top = GROUP_TOP[i];
      const bi = [0, 2, 4].indexOf(i);
      const bellAt = bi >= 0 ? EV.bells[bi] : 99;
      const muted = pr(t, [bellAt, bellAt + 0.2]);
      const lit = top ? pr(t, EV.rise) : 0;
      const ping = top ? bump(t, EV.groupPing[i === 1 ? 0 : 1], 0.4) : 0;
      nodes.push(<BigCard key={`g${i}`} x={f.x} y={f.y} sc={f.sc} o={f.o} text={GROUP[i]} fill={top ? mixHex(C.card, C.cardHi, lit) : C.card}
        fg={mixHex(C.ink, C.gray, muted)} glow={top ? lit * (0.5 + 0.3 * Math.sin(t * 5)) + ping : 0} />);
      if (u < 0.95) return;
      const ph = (t * 1.1 + i * 0.37) % 1;
      const pop = top ? ping : (1 - muted) * Math.sin(Math.PI * clamp(ph / 0.35));
      nodes.push(<circle key={`gd${i}`} cx={f.x + BW / 2 - 10} cy={f.y - BH / 2 + 6} r={14 * (1 + 0.45 * pop)} fill={C.red} opacity={f.o * (1 - muted)} />);
      if (muted > 0) nodes.push(<Bell key={`gb${i}`} x={f.x + BW / 2 - 44} y={f.y} sc={1.25 * easeBack(muted)} />);
      if (top && t >= EV.pins[0]) {
        const pu = easeBack(pr(t, EV.pins));
        nodes.push(<Pin key={`gp${i}`} x={f.x - BW / 2 + 8} y={f.y - BH / 2 - 4 - 50 * (1 - pu)} o={pr(t, [EV.pins[0], EV.pins[0] + 0.1])} />);
      }
    });
  }
  // 点赞：盒子 + 时间轴；红心一个个从“点赞”标签飞进盒子；到点开盖，攒着的红心一次冒出来
  if (t >= EV.likeOpen[0] && t < EV.dmOpen[1]) {
    const lo = 1 - pr(t, EV.dmOpen);
    const lineO = pr(t, EV.line) * lo;
    nodes.push(
      <g key="line" opacity={lineO}>
        <line x1={600} y1={LINE_Y} x2={1520} y2={LINE_Y} stroke="#6B7282" strokeWidth={6} strokeLinecap="round" />
        {TICKS.map((k2, i) => (
          <g key={i}>
            <circle cx={k2.x} cy={LINE_Y} r={12} fill={t >= EV.stops[i][1] ? C.warm : '#8A90A0'} />
            <Tx x={k2.x} y={LINE_Y + 50} size={56} anchor="middle" fill={C.bright}>{k2.label}</Tx>
          </g>
        ))}
      </g>,
    );
    const box = boxAt(t);
    // 正在飞的红心
    for (let k = 0; k < HEART_N; k++) {
      const s0 = heartAt(k);
      const u = pr(t, [s0, s0 + HEART_FLY]);
      if (u <= 0 || u >= 1) continue;
      const tgt = boxAt(s0 + HEART_FLY);
      const x = lerp(CHIP_X[2], tgt.x, easeOut(u)), y = lerp(CHIP_Y + 40, tgt.y - 20, easeIn(u)) - 90 * Math.sin(Math.PI * u);
      nodes.push(<Heart key={`h${k}`} x={x} y={y} r={22 * lerp(1, 0.7, u)} o={lo} />);
    }
    // 开盖：从上次开盖以后进盒子的红心一次冒出来
    let lid = 0;
    const bursts: React.ReactNode[] = [];
    EV.stops.forEach(([, s1, s2], i) => {
      if (t >= s1 && t < s2 + 0.1) lid = bump(t, s1, s2 - s1 + 0.1);
      if (t < s1 || t > s2 + 0.15) return;
      const prevOpen = i === 0 ? -1 : EV.stops[i - 1][1];
      const n = Array.from({length: HEART_N}, (_, k) => heartAt(k) + HEART_FLY).filter((a) => a > prevOpen && a <= s1).length;
      const q = pr(t, [s1, s2 + 0.1]);
      for (let j = 0; j < n; j++) {
        const ang = -Math.PI / 2 + (j - (n - 1) / 2) * 0.32;
        bursts.push(<Heart key={`b${i}-${j}`} x={box.x + Math.cos(ang) * 110 * easeOut(q)} y={box.y - 30 + Math.sin(ang) * 120 * easeOut(q)} r={17} o={(1 - q) * lo} />);
      }
    });
    const boxShow = pr(t, EV.boxIn) * lo;
    if (boxShow > 0) {
      nodes.push(
        <g key="box" opacity={boxShow} transform={`translate(${box.x} ${box.y}) scale(${easeBack(boxShow)})`}>
          <rect x={-65} y={-42} width={130} height={84} rx={10} fill="#7A6447" />
          <rect x={-65} y={-8} width={130} height={10} fill="#5E4C36" />
          <g transform={`translate(-68 -42) rotate(${-75 * lid})`}><rect x={0} y={-20} width={136} height={22} rx={6} fill="#957A57" /></g>
        </g>,
      );
    }
    nodes.push(<g key="bursts">{bursts}</g>);
  }
  if (t >= EV.dmOpen[0]) {
    ['妈妈', '同事'].forEach((txt, j) => {
      const u = po(t, [EV.dmOpen[0] + 0.05 * j, EV.dmOpen[1] + 0.05 * j]);
      const f = fromChip(3, {x: STAGE_C, y: 440 + j * 104}, u);
      const ping = bump(t, EV.dmPing[2], 0.35);
      nodes.push(<BigCard key={`m${j}`} x={f.x} y={f.y} sc={f.sc} o={f.o} text={txt} fill={C.cardHi} glow={0.6 + 0.4 * ping} />);
      if (u > 0.95) nodes.push(<circle key={`md${j}`} cx={f.x + BW / 2 - 10} cy={f.y - BH / 2 + 6} r={14 * (1 + 0.4 * ping)} fill={C.red} />);
    });
  }
  const chips = CHIPS.map((l, i) => {
    const a = EV.chipsIn[0] + 0.06 * i;
    const done0 = i === 0 ? adX : 0;
    const o = pr(t, [a, a + 0.1]) * (act === i ? 1 : DIM);
    const dmPing = i === 3 ? Math.max(bump(t, EV.dmPing[0], 0.35), bump(t, EV.dmPing[1], 0.35)) : 0;
    return (
      <g key={`c${i}`}>
        <Tag x={CHIP_X[i]} y={CHIP_Y} text={l} size={64} sc={easeBack(pr(t, [a, a + 0.25]))} o={o}
          bg={i === 0 ? mixHex(C.tag, '#3A3D44', adG) : C.tag} fg={i === 0 ? mixHex(C.ink, C.gray, adG) : C.ink} stroke={act === i ? C.warm : undefined} />
        {done0 > 0 && <line x1={CHIP_X[0] - CHIP_W[0] / 2 + 10} y1={CHIP_Y} x2={CHIP_X[0] - CHIP_W[0] / 2 + 10 + (CHIP_W[0] - 20) * done0} y2={CHIP_Y}
          stroke={C.gray} strokeWidth={6} strokeLinecap="round" />}
        {i === 3 && t >= EV.chipsIn[1] && (
          <g>
            <rect x={CHIP_X[3] - CHIP_W[3] / 2 - 10} y={CHIP_Y - 52} width={CHIP_W[3] + 20} height={104} rx={26} fill="#9FC2FF" opacity={0.18 + 0.12 * Math.sin(t * 6)} />
            <circle cx={CHIP_X[3] + CHIP_W[3] / 2 - 6} cy={CHIP_Y - 38} r={13 * (1 + 0.5 * dmPing)} fill={C.red} />
          </g>
        )}
      </g>
    );
  });
  return <g opacity={out}>{chips}{nodes}</g>;
};

// ================= 清单屏 39.6–58.2 秒 =================
type Row = {text: string};
const LISTS: {t0: number; t1: number; title: string; icon: 'wechat' | 'iphone' | 'android'; rows: Row[]; small?: string}[] = [
  {t0: 42.2, t1: 47.2, title: '微信群', icon: 'wechat', rows: [
    {text: '普通群 → 右上角“…” → 消息免打扰'},
    {text: '老师、工作的群：不静音，置顶聊天'},
    {text: '被 @ 会标红“有人@我”'},
  ]},
  {t0: 47.2, t1: 52.2, title: 'iPhone', icon: 'iphone', rows: [
    {text: '① 广告、资讯 App → 关“允许通知”'},
    {text: '② 通知 → 定时推送摘要：9、15、21 点'},
    {text: '③ 专注模式 → 只留家人'},
  ]},
  {t0: 52.2, t1: 58.2, title: '安卓', icon: 'android', rows: [
    {text: '① 设置里搜“通知”，广告、资讯 App 关掉'},
    {text: '② 每天定三个时间自己看'},
    {text: '③ 设置里搜“免打扰”，加家人'},
  ], small: '各品牌路径见简介'},
];

const ListIcon: React.FC<{kind: string}> = ({kind}) => (
  <svg width={200} height={200} viewBox="-90 -90 180 180">
    <circle r={86} fill="#2F3A4F" />
    {kind === 'wechat' && (
      <g fill="#7FD49B">
        <ellipse cx={-14} cy={-10} rx={42} ry={34} /><path d="M -40 14 L -46 34 L -22 20 Z" />
        <ellipse cx={26} cy={22} rx={34} ry={28} fill="#B9F0C9" /><path d="M 44 40 L 50 56 L 30 46 Z" fill="#B9F0C9" />
      </g>
    )}
    {(kind === 'iphone' || kind === 'android') && (
      <g>
        <rect x={-32} y={-56} width={64} height={112} rx={12} fill="none" stroke="#DDE3EE" strokeWidth={7} />
        {kind === 'iphone' ? <rect x={-12} y={-48} width={24} height={7} rx={3.5} fill="#DDE3EE" /> : <circle cx={0} cy={-46} r={4} fill="#DDE3EE" />}
        <path d="M -14 4 Q -14 -16 0 -18 Q 14 -16 14 4 L 18 8 L -18 8 Z" fill="#DDE3EE" /><circle cx={0} cy={13} r={4} fill="#DDE3EE" />
      </g>
    )}
  </svg>
);

const Screen1: React.FC<{t: number}> = ({t}) => {
  const t0 = 39.6;
  const inU = po(t, [t0, t0 + 0.3]);
  const items = [
    {label: '私聊', icon: (
      <g fill="#DDE3EE"><rect x={-56} y={-42} width={112} height={74} rx={22} /><path d="M -30 28 L -40 54 L -6 30 Z" /></g>)},
    {label: '电话短信（验证码）', icon: (
      <g><rect x={-34} y={-58} width={68} height={116} rx={12} fill="none" stroke="#DDE3EE" strokeWidth={7} />
        <rect x={-22} y={-20} width={44} height={30} rx={4} fill="#DDE3EE" /><path d="M -22 -20 L 0 0 L 22 -20" fill="none" stroke="#2F3A4F" strokeWidth={5} /></g>)},
    {label: '银行和支付', icon: (
      <g><rect x={-60} y={-38} width={120} height={78} rx={12} fill="#DDE3EE" /><rect x={-60} y={-20} width={120} height={16} fill="#2F3A4F" />
        <rect x={-44} y={14} width={34} height={10} rx={3} fill="#2F3A4F" /></g>)},
  ];
  const seg = (42.2 - (t0 + 0.5)) / 3;
  return (
    <div style={{position: 'absolute', left: 80, top: 50, width: 1760, height: 830, borderRadius: 40, background: '#1C2029', border: '3px solid #2E3440',
      opacity: inU, transform: `translateY(${(1 - inU) * 40}px)`, fontFamily: SANS, color: C.ink}}>
      <div style={{position: 'absolute', left: 80, top: 40, fontSize: 72, fontWeight: 700, lineHeight: '90px'}}>先别关</div>
      {/* v3：标题下加一行 */}
      <div style={{position: 'absolute', left: 80, top: 136, fontSize: 60, fontWeight: 600, lineHeight: '76px', color: C.warm}}>这几样关了会出事</div>
      {items.map((it, i) => {
        const on = t >= t0 + 0.5 + i * seg && t < t0 + 0.5 + (i + 1) * seg;
        return (
          <div key={i} style={{position: 'absolute', left: 20 + i * 580, top: 250, width: 560, height: 520, textAlign: 'center',
            borderRadius: 32, border: `6px solid ${on ? C.warm : 'transparent'}`}}>
            <svg width={240} height={240} viewBox="-130 -130 260 260" style={{marginTop: 24}}>
              <circle r={124} fill="#2F4A3F" stroke={C.green} strokeWidth={8} />
              <circle r={124} fill={C.green} opacity={0.18} />
              {it.icon}
            </svg>
            <div style={{fontSize: 60, fontWeight: 700, lineHeight: '76px', marginTop: 34, whiteSpace: 'nowrap'}}>{it.label}</div>
          </div>
        );
      })}
    </div>
  );
};

const ListScreen: React.FC<{t: number; L: (typeof LISTS)[number]}> = ({t, L}) => {
  const inU = po(t, [L.t0, L.t0 + 0.3]);
  const n = L.rows.length;
  const r0 = L.t0 + 0.5;
  const seg = (L.t1 - r0 - 0.2) / n;
  return (
    <div style={{position: 'absolute', left: 80, top: 50, width: 1760, height: 980, borderRadius: 40, background: '#1C2029', border: '3px solid #2E3440',
      opacity: inU, transform: `translateX(${(1 - inU) * 60}px)`, fontFamily: SANS, color: C.ink}}>
      <div style={{position: 'absolute', left: 80, top: 60, fontSize: 72, fontWeight: 700, lineHeight: '90px'}}>{L.title}</div>
      <div style={{position: 'absolute', left: 50, top: 270}}><ListIcon kind={L.icon} /></div>
      <div style={{position: 'absolute', left: 290, top: 230, width: 1420}}>
        {L.rows.map((r, i) => {
          const on = t >= r0 + i * seg && t < r0 + (i + 1) * seg;
          return (
            <div key={i} style={{marginBottom: 64, paddingLeft: 34, borderLeft: `10px solid ${on ? C.warm : 'rgba(255,255,255,0.08)'}`,
              background: on ? 'rgba(255,201,77,0.08)' : 'transparent', borderRadius: 8}}>
              <div style={{fontSize: 64, fontWeight: 600, lineHeight: '104px', whiteSpace: 'nowrap'}}>{r.text}</div>
            </div>
          );
        })}
        {L.small && <div style={{fontSize: 56, fontWeight: 500, lineHeight: '72px', color: C.soft, paddingLeft: 44, whiteSpace: 'nowrap'}}>{L.small}</div>}
      </div>
    </div>
  );
};

const Checklist: React.FC<{t: number}> = ({t}) => {
  const L = LISTS.filter((l) => t >= l.t0).pop();
  return (
    <>
      {t < 42.2 + 0.3 && <Screen1 t={t} />}
      {L && <ListScreen t={t} L={L} />}
      <div style={{position: 'absolute', inset: 0, background: '#FFFFFF', opacity: 0.55 * bump(t, EV.shot, 0.25)}} />
    </>
  );
};

// ================= 结尾 58.2–61.2 秒 =================
const BTN: [string, number, number][] = [['工作群', 660, 400], ['家长群', 1260, 400], ['班级群', 660, 610], ['亲戚群', 1260, 610]];
const Ending: React.FC<{t: number}> = ({t}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
    {BTN.map(([text, x, y], i) => {
      const a = EV.buttons[i];
      if (t < a) return null;
      const sc = easeBack(pr(t, [a, a + 0.25]));
      const idle = t - (EV.buttons[3] + 0.3);
      const hl = idle > 0 ? Math.max(0, Math.cos(((idle / 0.5) % 4 - i) * Math.PI / 2)) ** 6 * (Math.floor(idle / 0.5) % 4 === i ? 1 : 0.6) : 0;
      const fy = 4 * Math.sin((t * 0.9 + i * 0.25) * Math.PI * 2);
      return (
        <g key={i} transform={`translate(${x} ${y + fy}) scale(${sc})`}>
          <rect x={-260} y={-80} width={520} height={160} rx={40} fill="#2E3442" stroke={mixHex('#5A6478', C.warm, hl)} strokeWidth={5} />
          <Tx x={0} y={0} size={72} anchor="middle" weight={700}>{text}</Tx>
        </g>
      );
    })}
  </svg>
);

// ================= 字：字幕、右上小字、标题卡大字 =================
const SubText: React.FC<{beat: Beat; t: number}> = ({beat, t}) => {
  const {text} = useMode();
  if (!beat.sub.length || beat.card) return null;
  const size = beat.size ?? 64;
  const o = pr(t, [beat.t0, beat.t0 + 0.07]);
  return (
    <div style={{position: 'absolute', left: 0, width: 1920, top: 1000 - size * 0.98, height: size * 1.2, display: 'flex', justifyContent: 'center',
      fontFamily: SANS, fontWeight: 600, fontSize: size, lineHeight: `${size * 1.2}px`, color: text ? CREAM : C.ink, whiteSpace: 'nowrap', opacity: o,
      textShadow: text ? SHADOW : '0 4px 18px rgba(0,0,0,0.7)'}}>
      {beat.sub.map((sg: Seg, i) => {
        if (typeof sg === 'string') return <span key={i}>{sg}</span>;
        if (sg[1] === 'late') {
          // 先占着位置不显示，到 lateAt 再出（一下弹出来、亮一下）
          const at = beat.lateAt ?? beat.t0;
          const lo = pr(t, [at, at + 0.07]);
          const g = bump(t, at, 0.5);
          return <span key={i} style={{opacity: lo, color: g > 0.05 ? mixHex(text ? CREAM : C.ink, C.warm, g) : undefined,
            display: 'inline-block', transform: `scale(${1 + 0.12 * g})`, transformOrigin: 'left center'}}>{sg[0].replace(/^ /, '\u00A0')}</span>;
        }
        return <span key={i} style={{color: sg[1] === 'warm' ? C.warm : C.gray}}>{sg[0]}</span>;
      })}
    </div>
  );
};

const SOURCES: [number[], string][] = [
  [EV.src1, '按 278 人的手机记录推算，出处见简介'],
  [EV.src2, '做过实验：全关的人更焦虑（出处见简介）'],
  [EV.src3, '《稀缺》这本书把这叫‘余闲’'],
];
const SourceText: React.FC<{t: number}> = ({t}) => {
  const s = SOURCES.find(([ab]) => t >= ab[0] && t < ab[1]);
  if (!s) return null;
  const o = pr(t, [s[0][0], s[0][0] + 0.2]) * (1 - pr(t, [s[0][1] - 0.15, s[0][1]]));
  return (
    <div style={{position: 'absolute', right: 36, top: 24, fontFamily: SANS, fontWeight: 600, fontSize: 56, lineHeight: '74px', color: C.bright,
      whiteSpace: 'nowrap', opacity: o, background: 'rgba(16,18,25,0.8)', borderRadius: 14, padding: '0 18px'}}>{s[1]}</div>
  );
};

const BigText: React.FC<{t: number}> = ({t}) => {
  const {film} = useMode();
  // 样片 v2：6 帧落下（越过 14 像素）+ 2 帧弹回，不淡入
  const [a, b] = EV.bigText;
  const [d0, d1, d2] = EV.titleDrop;
  if (t < a) return null;
  const o = 1 - pr(t, [b, b + 0.25]);
  if (o <= 0) return null;
  const top = t < d1 ? lerp(-140, 48, easeIn(pr(t, [d0, d1])) ) : lerp(48, 34, pe(t, [d1, d2]));
  return (
    <div style={{position: 'absolute', left: 0, width: 1920, top, textAlign: 'center', fontFamily: SANS, fontWeight: 700, fontSize: 88,
      lineHeight: '106px', color: film ? '#FFF8EC' : '#FFFFFF', opacity: o,
      textShadow: film ? '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)' : '0 4px 20px rgba(0,0,0,0.5)'}}>同一天，三种设法</div>
  );
};

const Band: React.FC = () => (
  <div style={{position: 'absolute', left: 0, top: 880, width: 1920, height: 200,
    background: 'linear-gradient(180deg, rgba(10,11,15,0) 0%, rgba(10,11,15,0.8) 35%, rgba(10,11,15,0.9) 100%)'}} />
);

// 整条画面（灰框、成片共用）；画法由外面的 ModeCtx 决定
export const NoticeBody: React.FC = () => {
  const {film, text} = useMode();
  const fr = useCurrentFrame();
  const t = fr / FPS;
  const frozen = t >= EV.freeze[0] && t < EV.freeze[1];
  const tv = frozen ? EV.freeze[0] - 1 / FPS : t;
  const fv = Math.round(tv * FPS);
  const b = beatAt(t);
  const bandOn = t < 39.6 || t >= 58.2;
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {t < 39.6 && (
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <Defs />
          {tv >= EV.hookOut[0] && <ColBackdrop t={tv} fr={fv} />}
          {tv < EV.hookOut[0] && <Hook t={tv} fr={fv} />}
          {tv >= EV.hookOut[0] && <Columns t={tv} fr={fv} />}
          {tv >= EV.deal[0] && tv < EV.pilesOut[1] && <Stage t={tv} />}
          {film && <Vignette3 o={0.85} />}
        </svg>
      )}
      {bandOn && (text ? <SubBand3 /> : <Band />)}
      {t < 39.6 && tv >= EV.readoutsIn[0] && (
        <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
          <Defs />
          <Readouts t={tv} />
        </svg>
      )}
      {t < 39.6 && <HookText t={tv} />}
      {t < 39.6 && <BigText t={tv} />}
      {t >= 39.6 && t < 58.2 && <Checklist t={t} />}
      {t >= 58.2 && <Ending t={t} />}
      <SourceText t={t} />
      <SubText beat={b} t={t} />
      {text && <AiBadge />}
    </AbsoluteFill>
  );
};

export const Gray003: React.FC = () => (
  <ModeCtx.Provider value={{film: false, text: false}}>
    <NoticeBody />
  </ModeCtx.Provider>
);
