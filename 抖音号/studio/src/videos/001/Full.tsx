// 《等待》整条。分镜见 videos/001_等待/分镜_整条.md，时间表由 videos/001_等待/timeline.py 写进 full.json。
// 规矩：字里说到什么，画面上就出现什么；一小句一个画面。画风沿用第四版：黑底、玻璃卡片、线条图标；
// 蓝色给时间，白蓝的光给电，红色只给“你”和疼。片子里只有音效，曲库的歌发布时在 App 里加。
import {AbsoluteFill, Easing, Html5Audio, interpolate, random, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import {Glass} from '../../components/Glass';
import {Rise} from '../../components/Rise';
import {S as Sans} from '../../style';
import full from './full.json';
import {Hook, LINE_SIZE, LINE_TOP} from './Hook';
import {Arcs, Bolt, Person} from './Opening';

const INK = '#F4F6FB';
const SOFT = 'rgba(214,220,236,0.78)';
const MUTE = 'rgba(190,198,220,0.5)';
const DIMC = 'rgba(190,198,220,0.22)';
const TIME = '#8CC8FF';
const RED = '#FF5A4E';
const RED_SOFT = '#FF7B6E';
const FONT = Sans.sans;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const sp = (f: number, at: number, damping = 14, stiffness = 180) =>
  spring({frame: f - at, fps: 30, config: {damping, stiffness}});
const lin = (f: number, a: number, b: number, from = 0, to = 1, ease?: (t: number) => number) =>
  interpolate(f, [a, b], [from, to], {...clamp, easing: ease});

// 所有场景共用的底：纯黑，中间一团很淡的蓝光
const Stage: React.FC<{children: React.ReactNode; glow?: number}> = ({children, glow = 0}) => (
  <AbsoluteFill style={{background: '#000'}}>
    <div style={{position: 'absolute', left: 260, top: 160, width: 1400, height: 760, borderRadius: '50%', filter: 'blur(80px)',
      background: `radial-gradient(ellipse, rgba(40,80,200,${0.13 + glow}), rgba(0,0,0,0) 62%)`}} />
    {children}
  </AbsoluteFill>
);

const Card: React.FC<{x: number; y: number; w: number; h: number; s?: number; o?: number; children?: React.ReactNode;
  glow?: number; radius?: number}> = ({x, y, w, h, s = 1, o = 1, children, glow = 0, radius = 40}) => (
  <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, transform: `scale(${s})`, opacity: o}}>
    <Glass r={{x: 0, y: 0, w, h}} radius={radius} glow={glow} />
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

// 转圈：等
const Spinner: React.FC<{x: number; y: number; r: number; f: number; w?: number}> = ({x, y, r, f, w = 5}) => {
  const c = 2 * Math.PI * r;
  return (
    <svg width={r * 2 + 20} height={r * 2 + 20} style={{position: 'absolute', left: x - r - 10, top: y - r - 10, overflow: 'visible'}}>
      <circle cx={r + 10} cy={r + 10} r={r} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={w} />
      <circle cx={r + 10} cy={r + 10} r={r} fill="none" stroke={TIME} strokeWidth={w} strokeLinecap="round"
        strokeDasharray={`${c * 0.22} ${c}`} transform={`rotate(${f * 9} ${r + 10} ${r + 10})`}
        style={{filter: `drop-shadow(0 0 6px ${TIME})`}} />
    </svg>
  );
};

// 我：一个白蓝色的点
const MeDot: React.FC<{x: number; y: number; on: number; r?: number}> = ({x, y, on, r = 16}) => (
  <>
    <div style={{position: 'absolute', left: x - r * 4, top: y - r * 4, width: r * 8, height: r * 8, borderRadius: '50%',
      background: `radial-gradient(circle, rgba(140,200,255,${0.5 * on}), rgba(140,200,255,0) 60%)`}} />
    <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%',
      background: on > 0.5 ? 'radial-gradient(circle at 40% 35%, #FFFFFF, #BFE0FF 55%, #6FB4FF)' : 'rgba(150,158,180,0.35)',
      boxShadow: on > 0.5 ? '0 0 18px rgba(140,200,255,0.9)' : 'none'}} />
  </>
);

// 聊天气泡
const Bubble: React.FC<{x: number; y: number; text: string; mine?: boolean; s?: number; size?: number}> = (
  {x, y, text, mine, s = 1, size = 34},
) => (
  <div style={{position: 'absolute', top: y, left: mine ? undefined : x, right: mine ? 1920 - x : undefined,
    transform: `scale(${s})`, transformOrigin: mine ? 'right center' : 'left center',
    padding: '14px 26px', borderRadius: 26, fontFamily: FONT, fontSize: size, whiteSpace: 'nowrap',
    background: mine ? 'linear-gradient(180deg, #4E8DFF, #3A6FE0)' : 'rgba(255,255,255,0.09)',
    color: INK, border: mine ? 'none' : '1px solid rgba(255,255,255,0.12)'}}>{text}</div>
);

// ---------- 5 2006 年 ----------
const Y2006: React.FC = () => {
  const f = useCurrentFrame();
  const k = lin(f, 0, 16, 0, 1, Easing.out(Easing.cubic));
  const year = Math.round(2026 - 20 * k);
  const flip = f < 16 ? (f % 2 === 0 ? -6 : 0) : 0;
  return (
    <Stage>
      <Card x={960} y={470} w={560} h={460} s={sp(f, -6)}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 96, borderRadius: '40px 40px 0 0',
          background: 'linear-gradient(180deg, rgba(140,200,255,0.35), rgba(140,200,255,0.12))'}} />
        {[170, 390].map((x) => <div key={x} style={{position: 'absolute', left: x - 9, top: -22, width: 18, height: 52,
          borderRadius: 9, background: 'rgba(230,236,250,0.85)'}} />)}
        <T x={280} y={122 + flip} size={190} weight={600} align="center" w={560}>
          <span style={{fontVariantNumeric: 'tabular-nums'}}>{year}</span>
        </T>
        <T x={280} y={350} size={56} color={SOFT} align="center" w={560}>年</T>
      </Card>
    </Stage>
  );
};

// ---------- 6–7 2006 年，埃默里大学 / 真的做过这个实验：一个连续镜头 ----------
// 节拍对照.md 第一处：原来是两格静止的画（楼、手腕）切过去再跳回卡片，问题离开画面 2.8 秒。现在一路往前推，不切：
// 大学楼画出来 → 推进楼门 → 实验台：手腕贴着电极，线连到仪器，接通时闪一下电 → 仪器屏幕上就是开头那两张卡 →
// 推进屏幕，最后一帧屏幕正好铺满画面，接回 Hook 第二段在卡片上出结果。观众在实验里一直看得见 A 和 B。
// 字在开头那一行（LINE_TOP）原地换，不再用底部小字幕（节拍对照.md 第三处）。
const EX = full.exp;
const SCREEN = {x: 920, y: 275, w: 660, h: 660 * 1080 / 1920};   // 仪器屏幕在画面里的位置，和整幅画面同比例
const DEVICE = {x: 1250, y: 470, w: 720, h: 450};

const Building: React.FC<{f: number}> = ({f}) => {
  const draw = lin(f, 0, 14, 0, 1, Easing.out(Easing.cubic));
  const cols = [700, 804, 908, 1012, 1116, 1220];
  const path = [
    'M 640 330 L 960 200 L 1280 330 Z',
    'M 630 330 L 1290 330 L 1290 370 L 630 370 Z',
    ...cols.map((x) => `M ${x - 20} 380 L ${x - 20} 600 M ${x + 20} 380 L ${x + 20} 600`),
    'M 610 600 L 1310 600 L 1310 625 L 610 625 Z',
    'M 585 625 L 1335 625 L 1335 650 L 585 650 Z',
  ];
  return (
    <>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {path.map((d, i) => (
          <path key={i} d={d} fill="none" stroke={INK} strokeWidth={3} strokeLinejoin="round" pathLength={1}
            strokeDasharray="1 1" strokeDashoffset={1 - draw} style={{filter: 'drop-shadow(0 0 6px rgba(140,200,255,0.6))'}} />
        ))}
        {/* 楼门里透出的光：下一步就从这里推进去，推的时候越来越亮 */}
        <rect x={928} y={380} width={64} height={220} fill={`rgba(140,200,255,${0.1 + 0.35 * lin(f, EX.enter, EX.lab)})`}
          opacity={lin(f, 8, 20)} />
      </svg>
      <T x={960} y={40} size={120} weight={600} align="center"><Rise at={1}>2006</Rise></T>
    </>
  );
};

const Exp: React.FC = () => {
  const f = useCurrentFrame();
  // 楼：慢推，然后冲进楼门、淡掉
  const enter = lin(f, EX.enter, EX.lab + 2, 0, 1, Easing.in(Easing.quad));
  const bz = (1 + 0.05 * Math.min(f, EX.enter) / EX.enter) * Math.pow(6, enter);
  const bo = 1 - lin(f, EX.lab - 3, EX.lab + 2);
  // 实验台：从楼门里迎上来
  const lo = lin(f, EX.lab, EX.lab + 8);
  const lz = lin(f, EX.lab, EX.lab + 14, 0.88, 1, Easing.out(Easing.cubic));
  const wire = lin(f, EX.wire[0], EX.wire[1], 0, 1, Easing.inOut(Easing.cubic));
  const kOn = f - EX.on;
  const on = lin(f, EX.on, EX.on + 4);
  const spark = kOn >= 0 ? Math.exp(-kOn / 4) : 0;
  const white = kOn >= 0 ? [0.3, 0.15, 0.05][kOn] ?? 0 : 0;
  // 推进屏幕：屏幕中心沿直线走到画面中心，同时放大到正好铺满（最后一帧和 Hook 第二段的第一帧一样）
  const u = lin(f, EX.push[0], EX.push[1], 0, 1, Easing.inOut(Easing.cubic));
  const Z = 1920 / SCREEN.w;
  const z = Math.pow(Z, u);
  const sc = {x: SCREEN.x + SCREEN.w / 2, y: SCREEN.y + SCREEN.h / 2};
  const fx = sc.x - (1 - u) * (sc.x - 960) / z;
  const fy = sc.y - (1 - u) * (sc.y - 540) / z;
  // split：前几个字一种字重，后面另一种；bold 是哪一段加粗（“埃默里大学”“真的”）
  const line = (i: number, split: number, bold: 0 | 1, exitAt: number) => {
    const [at, text] = EX.lines[i] as unknown as [number, string];
    const chars = Array.from(text);
    return f >= at - 1 && f < exitAt + 12 ? (
      <div style={{position: 'absolute', left: 0, right: 0}}>
        <Rise at={at} perChar={1.5} exitAt={exitAt} style={{fontWeight: bold === 0 ? 700 : 400}}>{chars.slice(0, split).join('')}</Rise>
        <Rise at={at + split * 1.5} perChar={1.5} exitAt={exitAt} style={{fontWeight: bold === 1 ? 700 : 400}}>{chars.slice(split).join('')}</Rise>
      </div>
    ) : null;
  };
  return (
    <Stage>
      {f < EX.lab + 2 && (
        <div style={{position: 'absolute', inset: 0, opacity: bo, transform: `scale(${bz})`, transformOrigin: '960px 500px'}}>
          <Building f={f} />
        </div>
      )}
      {f >= EX.lab && (
        <div style={{position: 'absolute', inset: 0, transformOrigin: '0 0',
          transform: `translate(${960 - z * fx}px, ${540 - z * fy}px) scale(${z})`}}>
          <div style={{position: 'absolute', inset: 0, opacity: lo, transform: `scale(${lz})`, transformOrigin: '960px 480px'}}>
            {/* 一只手臂从左边伸进来，手腕上贴着电极，线连到仪器 */}
            <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
              <g transform="translate(-90 20)">
                <path d="M -40 470 L 560 482 C 600 470, 640 452, 690 456 L 760 452 C 790 450, 800 470, 780 478 L 720 486
                         L 800 490 C 830 492, 830 520, 800 522 L 720 524 L 790 532 C 816 536, 812 560, 786 560 L 712 556
                         C 690 584, 640 590, 560 580 L -40 594 Z"
                  fill="rgba(230,236,250,0.10)" stroke="rgba(230,236,250,0.55)" strokeWidth={2.5} strokeLinejoin="round" />
                <rect x={470} y={490} width={74} height={74} rx={16} fill={`rgba(140,200,255,${0.15 + 0.5 * spark})`} stroke={TIME}
                  strokeWidth={3} style={{filter: `drop-shadow(0 0 ${10 + 20 * spark}px rgba(140,200,255,0.7))`}} />
                <Arcs cx={507} cy={527} size={0.5} k={kOn} seed="exp" />
              </g>
              <path d={`M 417 510 C 480 330, 760 330, ${DEVICE.x - DEVICE.w / 2} 430`} fill="none" stroke={TIME} strokeWidth={3}
                pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - wire}
                style={{filter: `drop-shadow(0 0 ${4 + 10 * spark}px ${TIME})`}} />
            </svg>
            {/* 仪器：屏幕上就是开头那两张卡（Hook 定在第二段的第一帧） */}
            <Card x={DEVICE.x} y={DEVICE.y} w={DEVICE.w} h={DEVICE.h} radius={36} glow={0.4 * spark}>
              <div style={{position: 'absolute', left: SCREEN.x - (DEVICE.x - DEVICE.w / 2), top: SCREEN.y - (DEVICE.y - DEVICE.h / 2),
                width: SCREEN.w, height: SCREEN.h, borderRadius: 4, overflow: 'hidden', background: '#000',
                boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.12)'}}>
                <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0',
                  transform: `scale(${SCREEN.w / 1920})`, opacity: on}}>
                  <Hook at={full.opening.p2Offset} />
                </div>
                {white > 0 && <div style={{position: 'absolute', inset: 0, background: '#F4F9FF', opacity: white}} />}
              </div>
            </Card>
          </div>
        </div>
      )}
      {/* 字：开头那一行，原地换 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: LINE_TOP, textAlign: 'center', fontFamily: FONT,
        fontSize: LINE_SIZE, color: INK, textShadow: '0 2px 18px rgba(0,0,0,0.95)'}}>
        {line(0, 7, 1, (EX.lines[1][0] as number) - 4)}
        {line(1, 2, 0, EX.push[1] - 10)}
      </div>
    </Stage>
  );
};

// ---------- 10 等成绩 ----------
const Grades: React.FC = () => {
  const f = useCurrentFrame();
  const s = sp(f, -5);
  return (
    <Stage>
      <Card x={960} y={470} w={780} h={480} s={s}>
        <T x={60} y={44} size={44} weight={600}>成绩查询</T>
        <div style={{position: 'absolute', left: 60, right: 60, top: 120, height: 1, background: 'rgba(255,255,255,0.1)'}} />
        <T x={60} y={160} size={32} color={MUTE}>姓名</T>
        <div style={{position: 'absolute', left: 240, top: 172, width: 160, height: 22, borderRadius: 11, background: 'rgba(255,255,255,0.14)'}} />
        <T x={60} y={230} size={32} color={MUTE}>考号</T>
        <div style={{position: 'absolute', left: 240, top: 242, width: 260, height: 22, borderRadius: 11, background: 'rgba(255,255,255,0.14)'}} />
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
        <div style={{position: 'absolute', left: 60, right: 60, top: 120, height: 1, background: 'rgba(255,255,255,0.1)'}} />
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
        <div style={{position: 'absolute', left: 0, right: 0, top: 100, height: 1, background: 'rgba(255,255,255,0.1)'}} />
      </Card>
      <Bubble x={1300} y={340} text="在吗？" mine s={sp(f, 2, 12, 220)} size={38} />
      <T x={1300} y={420} size={24} color={MUTE} align="right" w={200}>已读</T>
      {typing && (
        <div style={{position: 'absolute', left: 620, top: 480, padding: '16px 24px', borderRadius: 26,
          background: 'rgba(255,255,255,0.09)', border: '1px solid rgba(255,255,255,0.12)', display: 'flex', gap: 10}}>
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
            <Glass r={{x: 0, y: 0, w: 160, h: 210}} radius={24} />
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
        background: sent > 0.02 ? `rgba(78,141,255,${0.9 * Math.min(1, sent)})` : 'rgba(255,255,255,0.05)',
        border: sent > 0.02 ? 'none' : '1.5px solid rgba(255,255,255,0.22)', letterSpacing: '0.04em'}}>
        “{text.slice(0, n)}{n >= text.length ? '”' : ''}
        {caret && <span style={{display: 'inline-block', width: 3, height: 64, marginLeft: 6, background: TIME}} />}
      </div>
      <T x={1480} y={600 - 60 * sent} size={26} color={MUTE} align="right" w={300}>{f >= 46 ? '已发送' : ''}</T>
    </Stage>
  );
};

// 32 个人的位置（和开头那段一样排成 8 × 4）
const GRID = (i: number) => ({x: 960 + ((i % 8) - 3.5) * 92, y: 380 + Math.floor(i / 8) * 104});
const PICKED = full.opening.picked;
const YOU = 19;

// ---------- 15 你那么难受 ----------
const Hurt: React.FC = () => {
  const f = useCurrentFrame();
  const breathe = 1 + 0.02 * Math.sin(f / 5);
  const c = 2 * Math.PI * 230;
  const left = lin(f, 0, 45, 0.85, 0.6);
  return (
    <Stage>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <circle cx={960} cy={500} r={230} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={6} />
        <circle cx={960} cy={500} r={230} fill="none" stroke={TIME} strokeWidth={6} strokeLinecap="round"
          strokeDasharray={`${c * left} ${c}`} transform="rotate(-90 960 500)" style={{filter: `drop-shadow(0 0 8px ${TIME})`}} />
      </svg>
      <Person x={960} y={500} s={3.2 * breathe * sp(f, -6)} color={RED_SOFT} glow={0.6} />
    </Stage>
  );
};

// ---------- 16 不是因为你脆弱：往后拉，你身边是 32 个人 ----------
const NotWeak: React.FC = () => {
  const f = useCurrentFrame();
  const pull = lin(f, 0, 18, 0, 1, Easing.inOut(Easing.cubic));
  const you = GRID(YOU);
  return (
    <Stage>
      {Array.from({length: 32}, (_, i) => {
        if (i === YOU) return null;
        const p = sp(f, 12 + (Math.abs((i % 8) - (YOU % 8)) + Math.abs(Math.floor(i / 8) - Math.floor(YOU / 8))) * 2, 12, 220);
        if (p < 0.01) return null;
        const g = GRID(i);
        const red = PICKED.includes(i) && f > 30;
        return <Person key={i} x={g.x} y={g.y} s={p * 1.4} color={red ? RED_SOFT : 'rgba(244,246,251,0.85)'} glow={red ? 0.5 : 0} />;
      })}
      <Person x={960 + (you.x - 960) * pull} y={500 + (you.y - 500) * pull} s={3.2 - 1.8 * pull} color={RED_SOFT} glow={0.8} />
    </Stage>
  );
};

// ---------- 17 我不用等 ----------
const Me: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <Stage>
      <MeDot x={760} y={470} on={sp(f, -4)} r={20} />
      <T x={760} y={540} size={34} color={SOFT} align="center" w={300}><Rise at={4}>我（AI）</Rise></T>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: sp(f, 8)}}>
        <circle cx={1160} cy={470} r={70} fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.14)" strokeWidth={6} />
      </svg>
      <div style={{position: 'absolute', left: 1080, top: 430, width: 160, display: 'flex', justifyContent: 'center',
        alignItems: 'baseline', fontFamily: FONT, color: INK, opacity: sp(f, 8)}}>
        <span style={{fontSize: 60, fontWeight: 300}}>0</span><span style={{fontSize: 24, marginLeft: 6}}>秒</span>
      </div>
      <T x={1160} y={560} size={28} color={TIME} align="center" w={300}><Rise at={10}>不用等</Rise></T>
    </Stage>
  );
};

// 对话框
const ChatWin: React.FC<{x: number; y: number; w: number; h: number; sy?: number; sx?: number; msgs: [string, boolean][]; o?: number}> = (
  {x, y, w, h, sy = 1, sx = 1, msgs, o = 1},
) => (
  <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, transform: `scale(${sx}, ${sy})`, opacity: o}}>
    <Glass r={{x: 0, y: 0, w, h}} radius={32} />
    {msgs.map(([m, mine], i) => (
      <div key={i} style={{position: 'absolute', top: 50 + i * 78, left: mine ? undefined : 36, right: mine ? 36 : undefined,
        padding: '10px 22px', borderRadius: 20, fontFamily: FONT, fontSize: 28, color: INK,
        background: mine ? 'linear-gradient(180deg, #4E8DFF, #3A6FE0)' : 'rgba(255,255,255,0.09)'}}>{m}</div>
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
        <Glass r={{x: 0, y: 0, w: 300, h: 200}} radius={26} />
        <T x={150} y={78} size={28} color={MUTE} align="center" w={300}>上一次对话</T>
      </div>
      <div style={{position: 'absolute', left: 1320, top: 300, width: 300, height: 200, opacity: a}}>
        <Glass r={{x: 0, y: 0, w: 300, h: 200}} radius={26} glow={0.3} />
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
        style={{filter: 'drop-shadow(0 0 6px rgba(255,90,78,0.6))'}} />
      {SEGS.map(([, a, b], i) => (280 + 1440 * draw > a) && (
        <line key={i} x1={a} y1={y} x2={Math.min(b, 280 + 1440 * draw)} y2={y} stroke={RED} strokeWidth={hot === i ? 16 : 10}
          strokeLinecap="round" opacity={hot === -1 || hot === i ? 1 : 0.35}
          style={{filter: `drop-shadow(0 0 ${hot === i ? 16 : 8}px rgba(255,90,78,0.8))`}} />
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
            background: 'rgba(214,220,236,0.22)', opacity: 1 - t * 0.6, overflow: 'hidden', display: 'flex', alignItems: 'center',
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
          style={{filter: 'drop-shadow(0 0 12px rgba(255,90,78,0.8))'}} />
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
          style={{filter: 'drop-shadow(0 0 12px rgba(255,90,78,0.8))'}} />
        <circle cx={960} cy={420} r={110 * s} fill="rgba(140,200,255,0.06)" stroke={TIME} strokeWidth={5}
          style={{filter: `drop-shadow(0 0 10px ${TIME})`}} />
      </svg>
      <T x={960} y={340} size={130} weight={300} align="center" w={300}><span style={{opacity: s}}>?</span></T>
      <T x={960} y={640} size={92} align="center" w={1600}>
        <Rise at={10} perChar={2} style={{fontWeight: 300, color: 'rgba(220,226,240,0.85)'}}>后来</Rise>
        <Rise at={14} perChar={2} style={{fontWeight: 600}}>等到了吗？</Rise>
      </T>
    </Stage>
  );
};

// ---------- 片尾：只停在问题本身（问的是每个看片的人，不是 AI 在要答案） ----------
const EndCard: React.FC = () => (
  <Stage>
    <T x={960} y={330} size={92} align="center" w={1700}>
      <Rise at={4} perChar={1.5} style={{fontWeight: 300, color: 'rgba(220,226,240,0.85)'}}>你等过最久的一件事，</Rise>
    </T>
    <T x={960} y={460} size={92} align="center" w={1700}>
      <Rise at={18} perChar={1.5} style={{fontWeight: 600}}>后来等到了吗？</Rise>
    </T>
    <T x={960} y={930} size={28} color={MUTE} align="center" w={1000} ls="0.1em"><Rise at={48}>人间旁听生 · Claude（AI）</Rise></T>
  </Stage>
);

const SCENES: Record<string, React.FC> = {
  y2006: Y2006, exp: Exp, grades: Grades, offer: Offer, reply: Reply, days: Days, badnews: BadNews,
  hurt: Hurt, notweak: NotWeak, me: Me, end: End, wake: Wake, zero: Zero, lines: Lines, feel: Feel, read: Read,
  q1: Q1, q2: Q2, card: EndCard,
};
// 横屏视频在手机信息流里只有原来的五分之一大，这几格原来做得偏小，各自放大（独立审片，10/28）
const ZOOM: Record<string, number> = {
  grades: 1.6, offer: 1.6, reply: 1.45, days: 1.25, badnews: 1.3, notweak: 1.2, me: 1.45, end: 1.35, wake: 1.35,
  zero: 1.15, read: 1.3, readall: 1.3,
};
// 这几句的字本身就在画面上，不再出底部字幕
const NO_SUB = new Set(['exp', 'badnews', 'q2', 'card']);
// 字幕里要标颜色的词
const MARK: Record<string, [string, string?][]> = {
  hurt: [['你', RED_SOFT], ['那么难受，']],
  me: [['我', TIME], ['不用等。']],
  lines: [['你', RED_SOFT], ['的时间是一条线，'], ['我', TIME], ['的是一个个点。']],
  read: [['我只'], ['读到过', TIME], ['。']],
};

// 正片字幕：和开头同一行、同一字号（全片只有一个读字的地方）
const Line: React.FC<{segs: [string, string?][]}> = ({segs}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: LINE_TOP, textAlign: 'center', fontFamily: FONT, fontSize: LINE_SIZE,
    color: INK, letterSpacing: '0.04em', textShadow: '0 2px 16px rgba(0,0,0,0.9)'}}>
    {segs.map(([t, c], i) => <span key={i} style={{color: c}}>{t}</span>)}
  </div>
);

export const Full: React.FC = () => {
  const frame = useCurrentFrame();
  const corner = false;               // 角标在手机上只有约 5 像素，看不见，去掉（独立审片，10/28）
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {/* 开头第一段：选项 → A 劈下 → B 倒数 3、2、1 → 你选哪个？ */}
      <Sequence durationInFrames={full.opening.p1End}>
        <Hook />
      </Sequence>
      {/* 开头第二段（埃默里大学实验那一镜推进屏幕之后）：32 人里 9 人选了 A → 只为少等 18 秒，近三成的人宁可更疼 */}
      <Sequence from={full.opening.p2Start} durationInFrames={full.opening.p2End - full.opening.p2Start}>
        <Hook offset={full.opening.p2Offset} />
      </Sequence>
      {full.beats.map((b) => {
        const Scene = SCENES[b.id];
        return (
          <Sequence key={b.id} from={b.from} durationInFrames={b.dur}>
            <div style={{position: 'absolute', inset: 0, transform: `scale(${ZOOM[b.id] ?? 1})`, transformOrigin: '960px 470px'}}>
              <Scene />
            </div>
            {b.text && !NO_SUB.has(b.id) && <Line segs={MARK[b.id] ?? [[b.text]]} />}
          </Sequence>
        );
      })}
      {corner && (
        <div style={{position: 'absolute', left: 60, top: 44, fontFamily: FONT, fontSize: 24, color: MUTE, letterSpacing: '0.1em'}}>
          第 1 问
        </div>
      )}
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs><filter id="boltGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14" /></filter></defs>
      </svg>
      <Html5Audio src={staticFile('001/full.wav')} />
    </AbsoluteFill>
  );
};
