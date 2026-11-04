// 第三版（心跳线，号主说看不出字和画面的关联，留作对照）：从内容出发重新剪（分镜见 videos/001_等待/分镜_开头.md，道理见 剪辑认知.md）。
// 母题是一条心跳线，扫描头是红点，就是“正在等的你”。心跳模型和声音都由 videos/001_等待/opening_audio.py 生成，
// 画面读 heart.json 画线，所以心跳声和线上的跳动对得上。
import {AbsoluteFill, Easing, Html5Audio, interpolate, random, staticFile, useCurrentFrame} from 'remotion';
import {Rise} from '../../components/Rise';
import {F as Fonts} from '../../style';
import cues from './cues_v3.json';
import heart from './heart_v3.json';

const SH = cues.shots;
const INK = '#F2EEE6';
const DIM = 'rgba(242,238,230,0.55)';
const RED = '#FF4B3E';
const SONG = Fonts.serif;
const NUM = '"SF Pro Display", system-ui, sans-serif';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// ---------- 心跳线 ----------

const X0 = 100;
const X1 = 1820;
const W = X1 - X0;
const SWEEP = 75;                      // 扫一屏 2.5 秒
const SPEED = W / SWEEP;
const GAP = 7;                         // 扫描头前面擦掉的一小段

const phaseAt = (row: number, t: number) => {
  const arr = heart.phase[row];
  const k = t + heart.pre;
  if (k <= 0) return arr[0] + k * (arr[1] - arr[0]);
  const i = Math.floor(k);
  if (i >= arr.length - 1) return arr[arr.length - 1];
  return arr[i] + (arr[i + 1] - arr[i]) * (k - i);
};

// 一拍的心电波形：P 波、QRS 尖峰、T 波
const ecg = (p: number) => {
  const x = p - Math.floor(p);
  const g = (c: number, w: number, a: number) => a * Math.exp(-((x - c) ** 2) / (2 * w * w));
  return g(0.1, 0.025, 0.12) + g(0.2, 0.008, -0.14) + g(0.22, 0.009, 1) + g(0.245, 0.01, -0.28) + g(0.45, 0.045, 0.26);
};

type Shock = {row: number; f: number; amp: number; dur: number};
const SHOCKS: Shock[] = [
  {row: cues.me, f: cues.aShock, amp: 3.2, dur: 12},
  {row: cues.me, f: cues.bShock, amp: 0.55, dur: 5},
  ...cues.picked.map((row, j) => ({row, f: cues.pickStart + j * cues.pickStep, amp: 1.9, dur: 9})),
];

// since：只算这一帧之后的电击。切到 B 是另一个选项，A 那一下的残影不该留在 B 的线上
const shockAt = (row: number, t: number, since = -Infinity) => {
  let v = 0;
  for (const s of SHOCKS) {
    if (s.row !== row || s.f < since || t < s.f || t > s.f + s.dur) continue;
    v += (random(`sh${row}-${Math.round(t * 4)}`) * 2 - 1) * s.amp * Math.exp(-(t - s.f) / (s.dur / 3));
  }
  return v;
};

const headX = (fe: number) => X0 + (((fe * SPEED) % W) + W) % W;

// 把一条线拆成几段：越旧越淡；扫描头前面留一道空隙
const traceSegments = (row: number, fe: number, cy: number, amp: number, since: number) => {
  const head = headX(fe);
  const pts: {x: number; y: number; age: number}[] = [];
  for (let x = X0; x <= X1; x += 4) {
    const age = (((head - x) % W) + W) % W / SPEED;
    if (age > SWEEP - GAP) continue;
    const t = fe - age;
    pts.push({x, y: cy - (ecg(phaseAt(row, t)) + shockAt(row, t, since)) * amp, age});
  }
  pts.sort((a, b) => a.age - b.age);
  const segs: {d: string; o: number}[] = [];
  let cur: typeof pts = [];
  const flush = () => {
    if (cur.length > 1) {
      const mid = cur[Math.floor(cur.length / 2)].age;
      segs.push({d: cur.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' '), o: 1 - 0.78 * (mid / SWEEP)});
    }
  };
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    const prev = cur[cur.length - 1];
    const bucket = (q: {age: number}) => Math.floor(q.age / 10);
    if (prev && (p.x > prev.x || bucket(p) !== bucket(prev))) {
      const wrapped = p.x > prev.x;
      flush();
      cur = wrapped ? [] : [prev];
    }
    cur.push(p);
  }
  flush();
  return {segs, head, headY: pts.length ? pts[0].y : cy};
};

const Trace: React.FC<{row: number; fe: number; cy: number; amp: number; width: number; color?: string;
  glow?: boolean; dot?: number; opacity?: number; since?: number}> = (
  {row, fe, cy, amp, width, color = INK, glow, dot = 0, opacity = 1, since = -Infinity},
) => {
  const {segs, head, headY} = traceSegments(row, fe, cy, amp, since);
  const lines = (w: number, extra?: number) => segs.map((s, i) => (
    <polyline key={i} points={s.d} fill="none" stroke={color} strokeWidth={w} strokeOpacity={s.o * (extra ?? 1)}
      strokeLinejoin="round" strokeLinecap="round" />
  ));
  return (
    <g opacity={opacity}>
      {glow && <g filter="url(#soft)">{lines(width * 2.4, 0.5)}</g>}
      {lines(width)}
      {dot > 0 && (
        <>
          <circle cx={head} cy={headY} r={dot * 3.2} fill="url(#redGlow)" />
          <circle cx={head} cy={headY} r={dot} fill={RED} />
          <circle cx={head - dot * 0.25} cy={headY - dot * 0.3} r={dot * 0.4} fill="#FFD9D3" />
        </>
      )}
    </g>
  );
};

// ---------- 字 ----------

type Seg = [string, boolean?];
const Line: React.FC<{segs: Seg[]; style?: React.CSSProperties}> = ({segs, style}) => (
  <span style={style}>
    {segs.map(([t, red], i) => <span key={i} style={{color: red ? RED : undefined}}>{t}</span>)}
  </span>
);

// 字幕：底部一行，随镜头硬切
const Subtitle: React.FC<{segs: Seg[]}> = ({segs}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: 930, textAlign: 'center', fontFamily: SONG, fontSize: 44,
    color: INK, letterSpacing: '0.06em', textShadow: '0 2px 16px rgba(0,0,0,0.9)'}}>
    <Line segs={segs} />
  </div>
);

const Question: React.FC = () => (
  <div style={{position: 'absolute', left: 0, right: 0, top: 120, textAlign: 'center', fontFamily: SONG, color: INK}}>
    <div style={{fontSize: 104, letterSpacing: '0.08em'}}>你选哪个？</div>
    <div style={{marginTop: 46, fontSize: 46, lineHeight: 1.7, color: 'rgba(242,238,230,0.86)', letterSpacing: '0.06em'}}>
      <div><b style={{fontWeight: 700, marginRight: 28}}>A</b>马上被电一下，重一点</div>
      <div><b style={{fontWeight: 700, marginRight: 28}}>B</b>等一会儿再电，轻一点</div>
    </div>
  </div>
);

const Channel: React.FC<{letter: string; word: string}> = ({letter, word}) => (
  <div style={{position: 'absolute', left: 120, top: 84, display: 'flex', alignItems: 'baseline', gap: 22,
    fontFamily: SONG, color: INK}}>
    <span style={{fontSize: 72, fontWeight: 700}}>{letter}</span>
    <span style={{fontSize: 34, color: DIM, letterSpacing: '0.1em'}}>{word}</span>
  </div>
);

const Bpm: React.FC<{fe: number}> = ({fe}) => {
  const rate = (phaseAt(cues.me, fe) - phaseAt(cues.me, fe - 15)) * 120;   // 每分钟跳几下，取半秒的平均
  return (
    <div style={{position: 'absolute', right: 120, top: 92, display: 'flex', alignItems: 'baseline', gap: 16,
      fontFamily: NUM, color: INK}}>
      <span style={{fontSize: 40, color: RED}}>♥</span>
      <span style={{fontSize: 64, fontWeight: 300, fontVariantNumeric: 'tabular-nums', minWidth: 110, textAlign: 'right'}}>
        {Math.round(rate)}
      </span>
    </div>
  );
};

// ---------- 32 个人 ----------

const ROW_TOP = 160;
const ROW_H = 24;
const rowY = (i: number) => ROW_TOP + i * ROW_H + ROW_H / 2;

export const OpeningV3: React.FC = () => {
  const frame = useCurrentFrame();
  const fe = Math.min(frame, SH.line);                 // 第 7 场定格
  const shot = frame < SH.a ? 'choice' : frame < SH.b ? 'a' : frame < SH.ask ? 'b'
    : frame < SH.reveal ? 'ask' : frame < SH.pick ? 'reveal' : frame < SH.line ? 'pick' : 'line';

  // 镜头
  let push = 1;
  if (shot === 'a') push = 1.06;
  if (shot === 'b') push = interpolate(frame, [SH.b, cues.bShock], [1.04, 1.26], {...clamp, easing: Easing.in(Easing.quad)});
  if (frame >= SH.reveal) push = interpolate(frame, [SH.reveal, cues.frames], [1, 1.05]);
  const ka = frame - cues.aShock;
  const kb = frame - cues.bShock;
  let shake = 0;
  let flash = 0;
  if (ka >= 0 && ka < 14) { shake += 18 * Math.exp(-ka / 3); flash += [0.85, 0.5, 0.22, 0.08][ka] ?? 0; }
  if (kb >= 0 && kb < 6) { shake += 2.5; flash += kb === 0 ? 0.1 : 0; }
  cues.picked.forEach((_, j) => {
    const k = frame - (cues.pickStart + j * cues.pickStep);
    if (k >= 0 && k < 8) { shake += 3.5 * Math.exp(-k / 2); flash += k === 0 ? 0.03 : 0; }
  });
  const sx = (random(`sx${frame}`) - 0.5) * 2 * shake;
  const sy = (random(`sy${frame}`) - 0.5) * 2 * shake;
  const dark = shot === 'b' ? interpolate(frame, [SH.b, cues.bShock], [0.35, 0.85], clamp) : 0.35;

  // 往后拉：你那一条线上下展开成 32 条
  const u = interpolate(frame, cues.unfold, [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const meY = rowY(cues.me);
  const K = 18.75;                                   // 单条时振幅 150 = 网格里 8 × 18.75
  const k = K + (1 - K) * u;
  const center = 560 + (meY - 560) * u;
  const dimAll = interpolate(frame, [SH.line, SH.line + 10], [1, 0.26], clamp);

  const single = frame < SH.reveal;
  const cy = shot === 'choice' || shot === 'ask' ? 720 : 560;
  const amp = shot === 'choice' || shot === 'ask' ? 110 : 150;

  return (
    <AbsoluteFill style={{background: '#030304', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${push})`, transformOrigin: '960px 560px'}}>
        {/* 很淡的格子，像监护仪的屏 */}
        <AbsoluteFill style={{opacity: single ? 0.5 : 0.35 * dimAll,
          backgroundImage: 'linear-gradient(rgba(242,238,230,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(242,238,230,0.035) 1px, transparent 1px)',
          backgroundSize: '60px 60px', backgroundPosition: '0 20px'}} />

        {/* B：背后很大的倒数 */}
        {shot === 'b' && cues.count.map((f, i) => {
          const next = cues.count[i + 1] ?? cues.bShock;
          if (frame < f || frame >= next) return null;
          const p = interpolate(frame, [f, f + 6], [1.14, 1], {...clamp, easing: Easing.out(Easing.cubic)});
          return (
            <div key={f} style={{position: 'absolute', left: 0, right: 0, top: 250, textAlign: 'center', fontFamily: SONG,
              fontSize: 520, lineHeight: 1, color: 'rgba(242,238,230,0.14)', transform: `scale(${p})`}}>{3 - i}</div>
          );
        })}

        <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
          <defs>
            <filter id="soft" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="5" /></filter>
            <radialGradient id="redGlow">
              <stop offset="0" stopColor="rgba(255,75,62,0.55)" />
              <stop offset="1" stopColor="rgba(255,75,62,0)" />
            </radialGradient>
          </defs>
          {single ? (
            <Trace row={cues.me} fe={fe} cy={cy} amp={amp} width={3} glow dot={9} since={frame >= SH.b ? SH.b : -Infinity} />
          ) : (
            Array.from({length: cues.rows}, (_, i) => {
              const j = cues.picked.indexOf(i);
              const picked = j >= 0 && frame >= cues.pickStart + j * cues.pickStep;
              const y = center + (rowY(i) - meY) * k;
              if (y < -200 || y > 1280) return null;
              return (
                <Trace key={i} row={i} fe={fe} cy={y} amp={8 * k} width={i === cues.me ? 2.4 : 1.6}
                  color={picked ? '#FF8A7C' : INK} glow={i === cues.me && u < 0.5}
                  dot={i === cues.me ? 9 - 5 * u : 3.2 * u} opacity={(i === cues.me ? 1 : u) * dimAll} />
              );
            })
          )}
        </svg>

        {/* 选了 A 的人，右边亮一个红色的 A */}
        {shot !== 'reveal' && !single && cues.picked.map((i, j) => {
          const at = cues.pickStart + j * cues.pickStep;
          if (frame < at) return null;
          const s = interpolate(frame, [at, at + 5], [1.6, 1], {...clamp, easing: Easing.out(Easing.back(2))});
          return (
            <div key={i} style={{position: 'absolute', left: X1 + 26, top: rowY(i) - 13, fontFamily: SONG, fontSize: 22,
              fontWeight: 700, color: RED, opacity: dimAll, transform: `scale(${s})`}}>A</div>
          );
        })}
      </AbsoluteFill>

      {/* 压暗四周：等的时候越压越紧 */}
      <AbsoluteFill style={{background: `radial-gradient(ellipse 75% 70% at 50% 52%, rgba(0,0,0,0) 40%, rgba(0,0,0,${dark}) 100%)`}} />
      {flash > 0 && <AbsoluteFill style={{background: '#EAF2FF', opacity: flash}} />}

      {/* 屏幕上的字（不跟镜头动） */}
      {(shot === 'choice' || shot === 'ask') && <Question />}
      {shot === 'a' && <><Channel letter="A" word="马上" /><Bpm fe={fe} /><Subtitle segs={[['A：'], ['马上', true], ['被电一下，重一点']]} /></>}
      {shot === 'b' && <><Channel letter="B" word="等一会儿" /><Bpm fe={fe} /><Subtitle segs={[['B：'], ['等一会儿', true], ['再电，轻一点']]} /></>}
      {shot === 'ask' && <Subtitle segs={[['先选，再往下看。']]} />}
      {shot === 'reveal' && <Subtitle segs={[['2006 年，埃默里大学做过类似的实验。']]} />}
      {shot === 'pick' && <Subtitle segs={[['近三分之一的人选了 '], ['A', true], ['：']]} />}
      {(shot === 'reveal' || shot === 'pick') && (
        <div style={{position: 'absolute', left: X0, top: 96, fontFamily: SONG, fontSize: 28, color: DIM, letterSpacing: '0.12em'}}>
          <Rise at={cues.unfold[1] - 6}>32 名受试者</Rise>
        </div>
      )}

      {/* 金句：定格、压暗，落在正中 */}
      {shot === 'line' && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontFamily: SONG, fontSize: 124,
          color: INK, letterSpacing: '0.06em', lineHeight: 1.35, textShadow: '0 4px 30px rgba(0,0,0,0.9)'}}>
          <div><Rise at={cues.punch1} perChar={2}>宁可更疼，</Rise></div>
          <div>
            <Rise at={cues.punch2} perChar={2}>也</Rise>
            <Rise at={cues.punch2 + 2} perChar={2} style={{color: RED}}>不想等</Rise>
            <Rise at={cues.punch2 + 8} perChar={2}>。</Rise>
          </div>
        </div>
      )}
      {frame >= cues.source && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 990, textAlign: 'center', fontFamily: SONG, fontSize: 24,
          color: DIM, letterSpacing: '0.08em'}}>
          <Rise at={cues.source}>Berns 等，2006，《科学》｜32 名受试者</Rise>
        </div>
      )}

      <Html5Audio src={staticFile('001/opening.wav')} />
    </AbsoluteFill>
  );
};
