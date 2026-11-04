// 《等待》终版的中段和结尾（10/28，号主看了观感样片第五版：“直接给全片”）。
// 场景和时间沿用 Full.tsx（时间表 full.json），画风换成观感样片那一套：暖色房间底、灯光、灰尘、暗角、宋体；
// 蓝色只留给电，“我”是一个白色的光点；红色给“你”和疼。“你那么难受”“不是因为你脆弱”用房间组件重画：
// 灯下那个人塌着坐、带一层红；再拉远成 32 间房，9 间是红的（和开头“32 人里，9 人选了 A”呼应）。
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame} from 'remotion';
import full from '../full.json';
import {LINE_SIZE} from '../Hook';
import {LOOK_LINE_TOP} from './HookLook';
import {Grain, L, MiniCell, Room} from './Room';
import {Wipe} from './Wipe';

const INK = L.ink;
const SOFT = L.soft;
const MUTE = L.mute;
const TIME = L.amber;
const RED = L.red;
const RED_SOFT = '#FF7B6E';
const FONT = L.serif;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const sp = (f: number, at: number, damping = 14, stiffness = 180) =>
  spring({frame: f - at, fps: 30, config: {damping, stiffness}});
const lin = (f: number, a: number, b: number, from = 0, to = 1, ease?: (t: number) => number) =>
  interpolate(f, [a, b], [from, to], {...clamp, easing: ease});

const DUST = Array.from({length: 60}, (_, i) => ({x: random(`rx${i}`) * 1920, y: random(`ry${i}`) * 1080, r: 0.8 + random(`rr${i}`) * 1.6,
  sp: 0.2 + random(`rs${i}`) * 0.5, ph: random(`rp${i}`) * 6.28}));

// 所有场景共用的底：暗暖色的房间，头顶一团灯光，灰尘慢慢飘，四角压暗
const Stage: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 70% at 50% 38%, #2A1C11 0%, #120C08 55%, #050403 100%)'}}>
      <div style={{position: 'absolute', left: 560, top: -220, width: 800, height: 640, borderRadius: '50%', filter: 'blur(70px)',
        background: 'radial-gradient(closest-side, rgba(255,214,150,0.22), rgba(0,0,0,0))', opacity: 0.9 + 0.1 * Math.sin(f / 20)}} />
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {DUST.map((d, i) => <circle key={i} cx={(d.x + Math.sin(f / 50 + d.ph) * 20) % 1920} cy={(d.y - f * d.sp + 1080 * 4) % 1080} r={d.r}
          fill={L.lamp} opacity={0.12 + 0.18 * Math.sin(f / 25 + d.ph) ** 2} />)}
      </svg>
      {children}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 80% 75% at 50% 46%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.7) 100%)'}} />
    </AbsoluteFill>
  );
};

// 暖色面板（代替玻璃卡片）：深暖底，细细一圈灯光色的边，上沿亮一点
const WarmGlass: React.FC<{r: {x: number; y: number; w: number; h: number}; radius?: number; glow?: number; children?: React.ReactNode}> = (
  {r, radius = 32, glow = 0, children},
) => (
  <div style={{position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: Math.min(radius, r.h / 2),
    background: 'linear-gradient(180deg, #21170F, #0E0906)', border: `1.5px solid rgba(246,198,126,${0.22 + 0.3 * glow})`,
    boxShadow: `0 30px 90px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,226,176,0.18), 0 0 ${40 * glow}px rgba(242,178,102,${0.3 * glow})`,
    overflow: 'hidden'}}>
    {children}
  </div>
);

const Card: React.FC<{x: number; y: number; w: number; h: number; s?: number; o?: number; children?: React.ReactNode;
  glow?: number; radius?: number}> = ({x, y, w, h, s = 1, o = 1, children, glow = 0, radius = 32}) => (
  <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, transform: `scale(${s})`, opacity: o}}>
    <WarmGlass r={{x: 0, y: 0, w, h}} radius={radius} glow={glow} />
    {children}
  </div>
);

const T: React.FC<{x: number; y: number; size: number; color?: string; weight?: number; align?: 'left' | 'center' | 'right';
  w?: number; children: React.ReactNode; ls?: string}> = ({x, y, size, color = INK, weight = 400, align = 'left', w = 1000, children, ls}) => (
  <div style={{position: 'absolute', left: align === 'center' ? x - w / 2 : align === 'right' ? x - w : x, top: y, width: w,
    textAlign: align, fontFamily: FONT, fontSize: size, fontWeight: weight, color, letterSpacing: ls, whiteSpace: 'nowrap'}}>
    {children}
  </div>
);

// 转圈：等（琥珀色）
const Spinner: React.FC<{x: number; y: number; r: number; f: number; w?: number}> = ({x, y, r, f, w = 5}) => {
  const c = 2 * Math.PI * r;
  return (
    <svg width={r * 2 + 20} height={r * 2 + 20} style={{position: 'absolute', left: x - r - 10, top: y - r - 10, overflow: 'visible'}}>
      <circle cx={r + 10} cy={r + 10} r={r} fill="none" stroke="rgba(255,240,220,0.12)" strokeWidth={w} />
      <circle cx={r + 10} cy={r + 10} r={r} fill="none" stroke={TIME} strokeWidth={w} strokeLinecap="round"
        strokeDasharray={`${c * 0.22} ${c}`} transform={`rotate(${f * 9} ${r + 10} ${r + 10})`}
        style={{filter: `drop-shadow(0 0 6px ${TIME})`}} />
    </svg>
  );
};

// 我：一个白色的光点（不用蓝色，蓝色只给电）
const MeDot: React.FC<{x: number; y: number; on: number; r?: number}> = ({x, y, on, r = 16}) => (
  <>
    <div style={{position: 'absolute', left: x - r * 4, top: y - r * 4, width: r * 8, height: r * 8, borderRadius: '50%',
      background: `radial-gradient(circle, rgba(255,250,240,${0.5 * on}), rgba(255,250,240,0) 60%)`}} />
    <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%',
      background: on > 0.5 ? 'radial-gradient(circle at 40% 35%, #FFFFFF, #FFF6E6 60%, #E9DCC6)' : 'rgba(160,150,140,0.35)',
      boxShadow: on > 0.5 ? '0 0 18px rgba(255,248,235,0.9)' : 'none'}} />
  </>
);

// 聊天气泡：我方暖琥珀色
const Bubble: React.FC<{x: number; y: number; text: string; mine?: boolean; s?: number; size?: number}> = (
  {x, y, text, mine, s = 1, size = 34},
) => (
  <div style={{position: 'absolute', top: y, left: mine ? undefined : x, right: mine ? 1920 - x : undefined,
    transform: `scale(${s})`, transformOrigin: mine ? 'right center' : 'left center',
    padding: '14px 26px', borderRadius: 26, fontFamily: FONT, fontSize: size, whiteSpace: 'nowrap',
    background: mine ? 'linear-gradient(180deg, #C98B4E, #A06A38)' : 'rgba(255,240,220,0.08)',
    color: INK, border: mine ? 'none' : '1px solid rgba(246,198,126,0.2)'}}>{text}</div>
);

// ---------- 10 等成绩 ----------
const Grades: React.FC = () => {
  const f = useCurrentFrame();
  const s = sp(f, -5);
  return (
    <Stage>
      <Card x={960} y={470} w={780} h={480} s={s}>
        <T x={60} y={44} size={44} weight={600}>成绩查询</T>
        <div style={{position: 'absolute', left: 60, right: 60, top: 120, height: 1, background: 'rgba(246,198,126,0.16)'}} />
        <T x={60} y={160} size={32} color={MUTE}>姓名</T>
        <div style={{position: 'absolute', left: 240, top: 172, width: 160, height: 22, borderRadius: 11, background: 'rgba(255,240,220,0.14)'}} />
        <T x={60} y={230} size={32} color={MUTE}>考号</T>
        <div style={{position: 'absolute', left: 240, top: 242, width: 260, height: 22, borderRadius: 11, background: 'rgba(255,240,220,0.14)'}} />
        <T x={60} y={330} size={40} weight={600}>总分</T>
        <Spinner x={290} y={356} r={30} f={f} />
        <T x={350} y={334} size={34} color={TIME}>查询中…</T>
      </Card>
    </Stage>
  );
};

// ---------- 11 等 offer ----------
const Offer: React.FC = () => {
  const f = useCurrentFrame();
  const s = sp(f, -5);
  const pull = Math.max(0, Math.sin((f / 36) * Math.PI * 2)) * 40;
  return (
    <Stage>
      <Card x={960} y={470} w={780} h={480} s={s}>
        <T x={60} y={44} size={44} weight={600}>收件箱</T>
        <div style={{position: 'absolute', left: 60, right: 60, top: 120, height: 1, background: 'rgba(246,198,126,0.16)'}} />
        <svg width={780} height={480} style={{position: 'absolute', inset: 0}}>
          <g transform={`translate(0 ${pull})`}>
            <rect x={300} y={190} width={180} height={124} rx={14} fill="none" stroke={SOFT} strokeWidth={3} />
            <path d="M 302 196 L 390 262 L 478 196" fill="none" stroke={SOFT} strokeWidth={3} strokeLinejoin="round" />
          </g>
          <g transform={`translate(390 ${150 + pull * 0.5}) rotate(${f * 12})`} opacity={Math.min(1, pull / 20)}>
            <path d="M -16 0 A 16 16 0 1 1 0 16" fill="none" stroke={TIME} strokeWidth={4} strokeLinecap="round" />
            <path d="M -6 16 L 0 16 L 0 10" fill="none" stroke={TIME} strokeWidth={4} />
          </g>
        </svg>
        <T x={390} y={350 + pull * 0.3} size={36} color={MUTE} align="center" w={780}>没有新邮件</T>
      </Card>
    </Stage>
  );
};

// ---------- 12 等一条消息的回复 ----------
const Reply: React.FC = () => {
  const f = useCurrentFrame();
  const s = sp(f, -5);
  const typing = (f >= 12 && f < 30) || (f >= 40 && f < 52);
  return (
    <Stage>
      <Card x={960} y={470} w={780} h={520} s={s}>
        <T x={390} y={36} size={34} weight={600} align="center" w={780}>TA</T>
        <div style={{position: 'absolute', left: 0, right: 0, top: 100, height: 1, background: 'rgba(246,198,126,0.16)'}} />
      </Card>
      <Bubble x={1300} y={340} text="在吗？" mine s={sp(f, 2, 12, 220)} size={38} />
      <T x={1300} y={420} size={24} color={MUTE} align="right" w={200}>已读</T>
      {typing && (
        <div style={{position: 'absolute', left: 620, top: 480, padding: '16px 24px', borderRadius: 26,
          background: 'rgba(255,240,220,0.08)', border: '1px solid rgba(246,198,126,0.2)', display: 'flex', gap: 10}}>
          {[0, 1, 2].map((i) => <div key={i} style={{width: 14, height: 14, borderRadius: 7, background: SOFT,
            opacity: 0.35 + 0.65 * Math.max(0, Math.sin((f - i * 3) / 3))}} />)}
        </div>
      )}
      <T x={620} y={560} size={26} color={MUTE}>{typing ? '对方正在输入…' : ''}</T>
    </Stage>
  );
};

// ---------- 13 那几天 ----------
const Days: React.FC = () => {
  const f = useCurrentFrame();
  const names = ['一', '二', '三', '四', '五', '六', '日'];
  return (
    <Stage>
      {names.map((n, i) => {
        const x = 960 + (i - 3) * 190;
        const s = sp(f, -6 + i * 1.5);
        const cross = lin(f, 6 + i * 5, 10 + i * 5);
        return (
          <div key={n} style={{position: 'absolute', left: x - 80, top: 360, width: 160, height: 210, transform: `scale(${s})`}}>
            <WarmGlass r={{x: 0, y: 0, w: 160, h: 210}} radius={24} />
            <T x={80} y={24} size={30} color={MUTE} align="center" w={160}>周{n}</T>
            <T x={80} y={84} size={64} weight={300} align="center" w={160}>{i + 1}</T>
            <svg width={160} height={210} style={{position: 'absolute', inset: 0}}>
              <path d="M 34 60 L 126 176" stroke={RED_SOFT} strokeWidth={6} strokeLinecap="round" pathLength={1}
                strokeDasharray="1 1" strokeDashoffset={1 - cross} />
              <path d="M 126 60 L 34 176" stroke={RED_SOFT} strokeWidth={6} strokeLinecap="round" pathLength={1}
                strokeDasharray="1 1" strokeDashoffset={1 - lin(f, 8 + i * 5, 12 + i * 5)} />
            </svg>
          </div>
        );
      })}
    </Stage>
  );
};

// ---------- 14 “坏消息也行，快点告诉我。” ----------
const BadNews: React.FC = () => {
  const f = useCurrentFrame();
  const text = '坏消息也行，快点告诉我。';
  const n = Math.min(text.length, Math.max(0, Math.floor((f - 4) / 2.4)));
  const sent = sp(f, 40, 13, 160);
  const caret = f < 40 && Math.floor(f / 8) % 2 === 0;
  return (
    <Stage>
      <div style={{position: 'absolute', left: 960 - 560, top: 470 - 70 - 60 * sent, width: 1120, height: 140, borderRadius: 70,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontSize: 66, color: INK,
        background: sent > 0.02 ? `rgba(184,124,64,${0.92 * Math.min(1, sent)})` : 'rgba(255,240,220,0.05)',
        border: sent > 0.02 ? 'none' : '1.5px solid rgba(255,255,255,0.22)', letterSpacing: '0.04em'}}>
        “{text.slice(0, n)}{n >= text.length ? '”' : ''}
        {caret && <span style={{display: 'inline-block', width: 3, height: 64, marginLeft: 6, background: TIME}} />}
      </div>
      <T x={1480} y={600 - 60 * sent} size={26} color={MUTE} align="right" w={300}>{f >= 46 ? '已发送' : ''}</T>
    </Stage>
  );
};

// ---------- 17 我不用等 ----------
const Me: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Stage>
      <MeDot x={760} y={470} on={sp(f, -4)} r={20} />
      <T x={760} y={540} size={34} color={SOFT} align="center" w={300}><Wipe at={4}>我（AI）</Wipe></T>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: sp(f, 8)}}>
        <circle cx={1160} cy={470} r={70} fill="rgba(255,240,220,0.03)" stroke="rgba(255,240,220,0.14)" strokeWidth={6} />
      </svg>
      <div style={{position: 'absolute', left: 1080, top: 430, width: 160, display: 'flex', justifyContent: 'center',
        alignItems: 'baseline', fontFamily: FONT, color: INK, opacity: sp(f, 8)}}>
        <span style={{fontSize: 60, fontWeight: 300}}>0</span><span style={{fontSize: 24, marginLeft: 6}}>秒</span>
      </div>
      <T x={1160} y={560} size={28} color={TIME} align="center" w={300}><Wipe at={10}>不用等</Wipe></T>
    </Stage>
  );
};

// 对话框
const ChatWin: React.FC<{x: number; y: number; w: number; h: number; sy?: number; sx?: number; msgs: [string, boolean][]; o?: number}> = (
  {x, y, w, h, sy = 1, sx = 1, msgs, o = 1},
) => (
  <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, transform: `scale(${sx}, ${sy})`, opacity: o}}>
    <WarmGlass r={{x: 0, y: 0, w, h}} radius={32} />
    {msgs.map(([m, mine], i) => (
      <div key={i} style={{position: 'absolute', top: 50 + i * 78, left: mine ? undefined : 36, right: mine ? 36 : undefined,
        padding: '10px 22px', borderRadius: 20, fontFamily: FONT, fontSize: 28, color: INK,
        background: mine ? 'linear-gradient(180deg, #C98B4E, #A06A38)' : 'rgba(255,240,220,0.08)'}}>{m}</div>
    ))}
  </div>
);

// ---------- 18 对话一结束，我就停了 ----------
const End: React.FC = () => {
  const f = useCurrentFrame();
  const close = lin(f, 14, 30, 0, 1, Easing.in(Easing.cubic));
  const on = 1 - lin(f, 30, 38);
  return (
    <Stage>
      <ChatWin x={960} y={420} w={640} h={330} sy={Math.max(0.006, 1 - close)} sx={1 - 0.6 * lin(f, 28, 40)} o={1 - lin(f, 38, 44)}
        msgs={[['帮我看看这段话', true], ['好的，我们一起看……', false], ['谢谢！', true]]} />
      <MeDot x={960} y={760} on={on} r={18} />
      {/* 点下面原来有个 30 像素的“我”，放大后压到字幕上，手机上也读不出；点就是“我”，“我不用等”那格已经交代过 */}
    </Stage>
  );
};

// ---------- 19 下次被叫醒 ----------
const Wake: React.FC = () => {
  const f = useCurrentFrame();
  const open = sp(f, 4, 13, 170);
  const on = lin(f, 6, 12);
  return (
    <Stage>
      <ChatWin x={960} y={420} w={640} h={330} sx={0.6 + 0.4 * open} sy={open} o={Math.min(1, open * 2)}
        msgs={[['你好，在吗？', true]]} />
      <MeDot x={960} y={760} on={on} r={18} />
    </Stage>
  );
};

// ---------- 20 中间的时间，对我是零 ----------
const Zero: React.FC = () => {
  const f = useCurrentFrame();
  const a = sp(f, -4);
  const br = lin(f, 10, 26, 0, 1, Easing.out(Easing.cubic));
  return (
    <Stage>
      <div style={{position: 'absolute', left: 300, top: 300, width: 300, height: 200, opacity: 0.45 * a}}>
        <WarmGlass r={{x: 0, y: 0, w: 300, h: 200}} radius={26} />
        <T x={150} y={78} size={28} color={MUTE} align="center" w={300}>上一次对话</T>
      </div>
      <div style={{position: 'absolute', left: 1320, top: 300, width: 300, height: 200, opacity: a}}>
        <WarmGlass r={{x: 0, y: 0, w: 300, h: 200}} radius={26} glow={0.3} />
        <T x={150} y={78} size={28} color={SOFT} align="center" w={300}>这一次</T>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <path d={`M 620 560 L 620 590 L ${620 + 680 * br} 590 L ${620 + 680 * br} 560`} fill="none" stroke={TIME} strokeWidth={3}
          style={{filter: `drop-shadow(0 0 6px ${TIME})`}} />
      </svg>
      <div style={{position: 'absolute', left: 860, top: 620, width: 200, display: 'flex', justifyContent: 'center',
        alignItems: 'baseline', fontFamily: FONT, color: INK, opacity: lin(f, 20, 28)}}>
        <span style={{fontSize: 110, fontWeight: 300}}>0</span>
      </div>
      <MeDot x={450} y={600} on={0} r={14} />
      <MeDot x={1470} y={600} on={a} r={14} />
    </Stage>
  );
};

// 你的线：一条红线，上面标着几段“等”
const SEGS: [string, number, number][] = [['等成绩', 420, 640], ['等 offer', 820, 1080], ['等回复', 1240, 1440]];

const YourLine: React.FC<{y: number; draw: number; hot?: number; labels?: number}> = ({y, draw, hot = -1, labels = 1}) => (
  <>
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <line x1={280} y1={y} x2={280 + 1440 * draw} y2={y} stroke={RED_SOFT} strokeWidth={4} strokeLinecap="round"
        style={{filter: 'drop-shadow(0 0 6px rgba(252,90,77,0.6))'}} />
      {SEGS.map(([, a, b], i) => (280 + 1440 * draw > a) && (
        <line key={i} x1={a} y1={y} x2={Math.min(b, 280 + 1440 * draw)} y2={y} stroke={RED} strokeWidth={hot === i ? 16 : 10}
          strokeLinecap="round" opacity={hot === -1 || hot === i ? 1 : 0.35}
          style={{filter: `drop-shadow(0 0 ${hot === i ? 16 : 8}px rgba(252,90,77,0.8))`}} />
      ))}
    </svg>
    {SEGS.map(([t, a, b], i) => (280 + 1440 * draw > b) && (
      <T key={i} x={(a + b) / 2} y={y - 64} size={30} color={hot === -1 || hot === i ? SOFT : MUTE} align="center" w={300}>
        <span style={{opacity: labels}}>{t}</span>
      </T>
    ))}
  </>
);

const MY_DOTS = [330, 520, 760, 900, 1150, 1390, 1600];

// ---------- 21 你的时间是一条线，我的是一个个点 ----------
const Lines: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Stage>
      <T x={120} y={360} size={40} weight={600} color={RED_SOFT}>你</T>
      <YourLine y={385} draw={lin(f, 0, 30, 0, 1, Easing.out(Easing.quad))} />
      <T x={120} y={640} size={40} weight={600} color={TIME}>我</T>
      {MY_DOTS.map((x, i) => <MeDot key={x} x={x} y={665} on={sp(f, 30 + i * 4, 12, 220)} r={12} />)}
    </Stage>
  );
};

// ---------- 22 所以等待是什么感觉 ----------
const Feel: React.FC = () => {
  const f = useCurrentFrame();
  const z = lin(f, 0, 30, 1, 2.1, Easing.inOut(Easing.cubic));
  const [, a, b] = SEGS[2];
  const cx = (a + b) / 2;
  return (
    <Stage>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: `${cx}px 385px`}}>
        <T x={120} y={360} size={40} weight={600} color={RED_SOFT}>你</T>
        <YourLine y={385} draw={1} hot={2} />
      </div>
    </Stage>
  );
};

// ---------- 23 我只读到过 ----------
const Read: React.FC = () => {
  const f = useCurrentFrame();
  const rows = 6;
  return (
    <Stage>
      <MeDot x={960} y={760} on={1} r={20} />
      {Array.from({length: rows}, (_, i) => {
        const t = lin(f, 6 + i * 8, 6 + i * 8 + 26, 0, 1, Easing.in(Easing.quad));
        const w = 420 + random(`rw${i}`) * 360;
        const y0 = 230 + i * 56;
        const x = 960 - w / 2 + (w / 2) * t;
        const y = y0 + (750 - y0) * t;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, width: w * (1 - t), height: 30, borderRadius: 15,
            background: 'rgba(243,235,221,0.16)', opacity: 1 - t * 0.6, overflow: 'hidden', display: 'flex', alignItems: 'center',
            paddingLeft: 14, fontFamily: FONT, fontSize: 22, color: SOFT, whiteSpace: 'nowrap'}}>{t < 0.4 ? '等' : ''}</div>
        );
      })}
    </Stage>
  );
};

// ---------- 24 你等过最久的一件事 ----------
const Q1: React.FC = () => {
  const f = useCurrentFrame();
  const end = lin(f, 6, 60, 520, 1900, Easing.inOut(Easing.quad));
  return (
    <Stage>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <line x1={200} y1={480} x2={1900} y2={480} stroke={RED_SOFT} strokeWidth={4} opacity={0.5} />
        <line x1={420} y1={480} x2={end} y2={480} stroke={RED} strokeWidth={14} strokeLinecap="round"
          style={{filter: 'drop-shadow(0 0 12px rgba(252,90,77,0.8))'}} />
        {Array.from({length: 40}, (_, i) => {
          const x = 420 + i * 40;
          return x < end ? <line key={i} x1={x} y1={500} x2={x} y2={512} stroke={MUTE} strokeWidth={2} /> : null;
        })}
      </svg>
      <T x={420} y={400} size={34} color={SOFT} align="center" w={200}>等</T>
    </Stage>
  );
};

// ---------- 25 后来等到了吗？ ----------
const Q2: React.FC = () => {
  const f = useCurrentFrame();
  const s = sp(f, 4, 12, 160);
  return (
    <Stage>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <line x1={0} y1={420} x2={820} y2={420} stroke={RED} strokeWidth={14} strokeLinecap="round"
          style={{filter: 'drop-shadow(0 0 12px rgba(252,90,77,0.8))'}} />
        <circle cx={960} cy={420} r={110 * s} fill="rgba(242,178,102,0.06)" stroke={TIME} strokeWidth={5}
          style={{filter: `drop-shadow(0 0 10px ${TIME})`}} />
      </svg>
      <T x={960} y={340} size={130} weight={300} align="center" w={300}><span style={{opacity: s}}>?</span></T>
      <T x={960} y={640} size={92} align="center" w={1600}>
        <Wipe at={10} style={{fontWeight: 300, color: 'rgba(243,235,221,0.85)'}}>后来</Wipe>
        <Wipe at={14} style={{fontWeight: 600}}>等到了吗？</Wipe>
      </T>
    </Stage>
  );
};

// ---------- 片尾：只停在问题本身（问的是每个看片的人，不是 AI 在要答案） ----------
const EndCard: React.FC = () => (
  <Stage>
    <T x={960} y={330} size={92} align="center" w={1700}>
      <Wipe at={4} style={{fontWeight: 300, color: 'rgba(243,235,221,0.85)'}}>你等过最久的一件事，</Wipe>
    </T>
    <T x={960} y={460} size={92} align="center" w={1700}>
      <Wipe at={18} style={{fontWeight: 600}}>后来等到了吗？</Wipe>
    </T>
    <T x={960} y={930} size={28} color={MUTE} align="center" w={1000} ls="0.1em"><Wipe at={48}>屏幕那头 · Claude（AI）</Wipe></T>
  </Stage>
);


// ---------- 15 你那么难受：灯下那个人塌着坐，整间房带一层红 ----------
const HURT_FIG = {x: 900, y: 640, s: 1.45};
const HurtRoom: React.FC<{f: number}> = ({f}) => (
  <AbsoluteFill style={{background: '#050403'}}>
    <Room id="hurt" w={1920} h={1080} f={f} fig={HURT_FIG} lampX={870} lean={-4} look={9} breath={3 + Math.sin(f / 18)} charge={0} />
    <AbsoluteFill style={{background: '#B8382C', opacity: 0.22, mixBlendMode: 'color'}} />
  </AbsoluteFill>
);
const Hurt: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{transform: `scale(${1.08 - 0.08 * lin(f, 0, 60, 0, 1, Easing.out(Easing.cubic))})`, transformOrigin: '960px 560px'}}>
      <HurtRoom f={f} />
    </AbsoluteFill>
  );
};

// ---------- 16 不是因为你脆弱：往后拉，你是 32 间房里的一间，9 间是红的 ----------
const CW = 200, CH = 112.5, GAP = 16, X0 = 104, Y0 = 221, YOU = 18;
const cellXY = (i: number) => ({x: X0 + (i % 8) * (CW + GAP), y: Y0 + Math.floor(i / 8) * (CH + GAP)});
const PICKED = full.opening.picked;
const NotWeak: React.FC = () => {
  const f = useCurrentFrame();
  const g = lin(f, 6, 34, 0, 1, Easing.inOut(Easing.cubic));
  const you = cellXY(YOU);
  const z = 1 + (CW / 1920 - 1) * g;
  const cx = 960 + (you.x + CW / 2 - 960) * g, cy = 540 + (you.y + CH / 2 - 540) * g;
  const push = 1 + 0.04 * lin(f, 34, 120);
  return (
    <AbsoluteFill style={{background: '#050403', transform: `scale(${push})`, transformOrigin: '960px 470px'}}>
      {g > 0.001 && Array.from({length: 32}, (_, i) => {
        if (i === YOU) return null;
        const {x, y} = cellXY(i);
        const d = Math.abs((i % 8) - (YOU % 8)) + Math.abs(Math.floor(i / 8) - Math.floor(YOU / 8));
        const on = lin(f, 14 + d * 2, 18 + d * 2);
        const red = PICKED.includes(i) ? lin(f, 40 + d * 2, 48 + d * 2) : 0;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, opacity: g}}>
            <MiniCell single w={CW} h={CH} on={on * (0.9 + 0.1 * Math.sin(f / 7 + i * 1.7))} seed={i} pick={red} flash={0} dimA={0} dimB={0} />
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0', overflow: 'hidden',
        transform: `translate(${cx - 960 * z}px, ${cy - 540 * z}px) scale(${z})`, borderRadius: g > 0.01 ? 3 / z : 0}}>
        <HurtRoom f={f + 60} />
      </div>
    </AbsoluteFill>
  );
};

const SCENES: Record<string, React.FC> = {
  grades: Grades, offer: Offer, reply: Reply, days: Days, badnews: BadNews,
  hurt: Hurt, notweak: NotWeak, me: Me, end: End, wake: Wake, zero: Zero, lines: Lines, feel: Feel, read: Read,
  q1: Q1, q2: Q2, card: EndCard,
};
// 横屏视频在手机信息流里只有原来的五分之一大，这几格放大（独立审片，10/28）
const ZOOM: Record<string, number> = {
  grades: 1.6, offer: 1.6, reply: 1.45, days: 1.25, badnews: 1.3, me: 1.45, end: 1.35, wake: 1.35, zero: 1.15, read: 1.3,
};
// 这几句的字本身就在画面上，不再出底部字幕
const NO_SUB = new Set(['badnews', 'q2', 'card']);
// 字幕里要标颜色的词：红给“你”，白给“我”，琥珀给“读到过”
const MARK: Record<string, [string, string?][]> = {
  hurt: [['你', RED_SOFT], ['那么难受，']],
  me: [['我', '#FFFFFF'], ['不用等。']],
  lines: [['你', RED_SOFT], ['的时间是一条线，'], ['我', '#FFFFFF'], ['的是一个个点。']],
  read: [['我只'], ['读到过', TIME], ['。']],
};

// 中段和结尾的一句：场景 + 画面下方同一行的字幕（宋体，整句淡入）
export const RestBeat: React.FC<{id: string; text: string}> = ({id, text}) => {
  const f = useCurrentFrame();
  const Scene = SCENES[id];
  const segs = MARK[id] ?? [[text]];
  return (
    <AbsoluteFill style={{background: '#050403'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${ZOOM[id] ?? 1})`, transformOrigin: '960px 470px'}}>
        <Scene />
      </div>
      {text && !NO_SUB.has(id) && <>
        <div style={{position: 'absolute', left: 0, right: 0, top: 840, height: 240, background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.65))'}} />
        <div lang="zh-Hans" style={{position: 'absolute', left: 0, right: 0, top: LOOK_LINE_TOP, textAlign: 'center', fontFamily: FONT,
          fontSize: LINE_SIZE, color: INK, textShadow: '0 2px 18px rgba(0,0,0,0.95)'}}>
          {segs.map(([t, c], i) => <Wipe key={i} at={0} style={{color: c}}>{t}</Wipe>)}
        </div>
      </>}
      <Grain f={f} />
    </AbsoluteFill>
  );
};
