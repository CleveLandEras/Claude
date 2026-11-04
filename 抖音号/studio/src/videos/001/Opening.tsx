// 笔记 001《等待》开头样片，第四版：字里说到什么，画面上就出现什么。分镜见 videos/001_等待/分镜_开头.md。
//   电 = 闪电；重 / 轻 = 大闪电 / 小闪电；马上 = 计时圈里的“0 秒”；等一会儿 = 计时圈在倒数；
//   你选哪个 = 两张选项卡；32 名受试者 = 32 个人形；三分之一选了 A = 10 个人走到 A 下面。
// 颜色也对应字：蓝色是时间（计时圈和“马上”“等一会儿”），白蓝的光是电，红色只给“不想等”和选了 A 的人。
import {AbsoluteFill, Easing, Html5Audio, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Glass} from '../../components/Glass';
import {Rise} from '../../components/Rise';
import {S as Sans} from '../../style';
import cuesV4 from './cues_v4.json';

// 节拍表：单独渲第四版样片用 cues_v4.json；整条（Full.tsx）传入 full.json 里的 opening
export type Cues = typeof cuesV4;

const INK = '#F4F6FB';
const SOFT = 'rgba(214,220,236,0.75)';
const MUTE = 'rgba(190,198,220,0.5)';
const TIME = '#8CC8FF';
const RED = '#FF5A4E';
const FONT = Sans.sans;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const CW = 600;
const ASK_AT = 18;                  // “你选哪个？”在第几帧浮出来
const CH = 490;
const A_X = 600;
const B_X = 1320;
const CARD_Y = 540;
// 卡片里的两个图标位置（卡片自己的坐标）
const RING = {x: 170, y: 300, r: 76};
const BOLT = {x: 430, y: 294};

// ---------- 闪电 ----------

const BOLT_PTS = [[0.62, 0], [0.1, 0.57], [0.45, 0.57], [0.32, 1], [0.9, 0.39], [0.55, 0.39], [0.72, 0]];

export const Bolt: React.FC<{cx: number; cy: number; h: number; flash: number; id: string}> = ({cx, cy, h, flash, id}) => {
  const w = h * 0.6;
  const pts = BOLT_PTS.map(([x, y]) => `${(cx - w / 2 + x * w).toFixed(1)},${(cy - h / 2 + y * h).toFixed(1)}`).join(' ');
  const s = 1 + 0.12 * flash;
  return (
    <g transform={`translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})`}>
      <defs>
        <linearGradient id={`bg${id}`} x1="0" y1="0" x2="0.3" y2="1">
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="1" stopColor={flash > 0.3 ? '#FFFFFF' : '#9CCBFF'} />
        </linearGradient>
      </defs>
      <polygon points={pts} fill="#5AA8FF" opacity={0.35 + 0.6 * flash} filter="url(#boltGlow)" />
      <polygon points={pts} fill={`url(#bg${id})`} stroke="rgba(255,255,255,0.9)" strokeWidth={1.5} strokeLinejoin="round" />
    </g>
  );
};

// 电弧：电下去那几帧，从闪电四周炸开的几道折线
export const Arcs: React.FC<{cx: number; cy: number; size: number; k: number; seed: string}> = ({cx, cy, size, k, seed}) => {
  if (k < 0 || ![0, 1, 2, 4].includes(k)) return null;
  const n = Math.round(4 + size * 3);
  return (
    <g>
      {Array.from({length: n}, (_, i) => {
        const ang = (i / n) * Math.PI * 2 + random(`${seed}a${k}${i}`) * 0.8;
        const len = (60 + random(`${seed}l${k}${i}`) * 80) * size;
        const pts = Array.from({length: 7}, (_, j) => {
          const t = j / 6;
          const off = j === 0 ? 0 : (random(`${seed}o${k}${i}${j}`) - 0.5) * 22 * size;
          const r0 = 40 * size;
          return `${(cx + Math.cos(ang) * (r0 + len * t) - Math.sin(ang) * off).toFixed(1)},${(cy + Math.sin(ang) * (r0 + len * t) + Math.cos(ang) * off).toFixed(1)}`;
        }).join(' ');
        return (
          <g key={i}>
            <polyline points={pts} fill="none" stroke="#BFE0FF" strokeOpacity={0.25} strokeWidth={8 * size + 2} />
            <polyline points={pts} fill="none" stroke="#FFFFFF" strokeWidth={1.6 + size} strokeLinejoin="round" />
          </g>
        );
      })}
    </g>
  );
};

// ---------- 计时圈 ----------

const Ring: React.FC<{frac: number; spin?: number; children: React.ReactNode}> = ({frac, spin, children}) => {
  const c = 2 * Math.PI * RING.r;
  return (
    <>
      <svg width={CW} height={CH} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <circle cx={RING.x} cy={RING.y} r={RING.r} fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.12)" strokeWidth={6} />
        {spin !== undefined ? (
          <circle cx={RING.x} cy={RING.y} r={RING.r} fill="none" stroke={TIME} strokeWidth={6} strokeLinecap="round"
            strokeDasharray={`${c * 0.18} ${c}`} transform={`rotate(${spin} ${RING.x} ${RING.y})`}
            style={{filter: `drop-shadow(0 0 8px ${TIME})`}} />
        ) : frac > 0 && (
          <circle cx={RING.x} cy={RING.y} r={RING.r} fill="none" stroke={TIME} strokeWidth={6} strokeLinecap="round"
            strokeDasharray={`${c * frac} ${c}`} transform={`rotate(-90 ${RING.x} ${RING.y})`}
            style={{filter: `drop-shadow(0 0 8px ${TIME})`}} />
        )}
      </svg>
      <div style={{position: 'absolute', left: RING.x - 80, top: RING.y - 40, width: 160, height: 80, display: 'flex',
        alignItems: 'baseline', justifyContent: 'center', fontFamily: FONT, color: INK, fontVariantNumeric: 'tabular-nums'}}>
        {children}
      </div>
    </>
  );
};

// ---------- 选项卡 ----------

const Card: React.FC<{letter: 'A' | 'B'; cx: number; cy: number; scale: number; opacity: number; blur: number;
  ring: React.ReactNode; boltH: number; flash: number; arcK: number; time: string; size: string; tail: string}> = (
  {letter, cx, cy, scale, opacity, blur, ring, boltH, flash, arcK, time, size, tail},
) => (
  <div style={{position: 'absolute', left: cx - CW / 2, top: cy - CH / 2, width: CW, height: CH, opacity,
    filter: blur > 0.1 ? `blur(${blur}px)` : undefined, transform: `scale(${scale})`, transformOrigin: 'center'}}>
    <Glass r={{x: 0, y: 0, w: CW, h: CH}} radius={40} glow={flash * 0.9} />
    {/* 选项写在 A、B 字母旁边：观众第一眼先认这一行，再看下面的图（号主，10/28） */}
    <div style={{position: 'absolute', left: 44, top: 26, display: 'flex', alignItems: 'flex-start', gap: 24, fontFamily: FONT,
      whiteSpace: 'nowrap'}}>
      <span style={{fontSize: 72, fontWeight: 600, color: INK, lineHeight: 1}}>{letter}</span>
      {/* 横屏视频在竖着刷的信息流里只有手机宽度那么大，字要够大：选项分两行，52 像素 */}
      <span style={{fontSize: 52, color: SOFT, lineHeight: 1.22, letterSpacing: '0.02em', marginTop: 2}}>
        <span style={{color: TIME}}>{time}</span>{tail.split('|')[0]}<br />
        <span style={{color: INK, fontWeight: 600}}>{tail.split('|')[1]}</span>
      </span>
    </div>
    <div style={{position: 'absolute', left: 44, right: 44, top: 170, height: 1, background: 'rgba(255,255,255,0.1)'}} />
    {ring}
    <svg width={CW} height={CH} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <Arcs cx={BOLT.x} cy={BOLT.y} size={boltH / 220} k={arcK} seed={letter} />
      <Bolt cx={BOLT.x} cy={BOLT.y} h={boltH} flash={flash} id={letter} />
    </svg>
    <div style={{position: 'absolute', left: RING.x - 100, width: 200, top: RING.y + RING.r + 22, textAlign: 'center',
      fontFamily: FONT, fontSize: 28, color: TIME}}>{time}</div>
    <div style={{position: 'absolute', left: BOLT.x - 100, width: 200, top: RING.y + RING.r + 22, textAlign: 'center',
      fontFamily: FONT, fontSize: 28, fontWeight: 600, color: INK}}>{size}</div>
  </div>
);

// ---------- 人 ----------

export const Person: React.FC<{x: number; y: number; s: number; color: string; glow?: number}> = ({x, y, s, color, glow = 0}) => (
  <svg width={44} height={52} style={{position: 'absolute', left: x - 22, top: y - 26, overflow: 'visible',
    transform: `scale(${s})`, filter: glow > 0.01 ? `drop-shadow(0 0 ${10 * glow}px rgba(255,90,78,${0.8 * glow}))` : undefined}}>
    <circle cx={22} cy={13} r={11} fill={color} />
    <path d="M3 52 C3 35 12 28.5 22 28.5 C32 28.5 41 35 41 52 Z" fill={color} />
  </svg>
);

const GRID = (i: number) => ({x: 960 + ((i % 8) - 3.5) * 70, y: 480 + Math.floor(i / 8) * 82});
const SLOT_A = (j: number) => ({x: A_X + ((j % 5) - 2) * 70, y: 480 + Math.floor(j / 5) * 82});
const SLOT_B = (j: number) => ({x: B_X + ((j % 6) - 2.5) * 70, y: 480 + Math.floor(j / 6) * 82});

export const Subtitle: React.FC<{segs: [string, string?][]}> = ({segs}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: 918, textAlign: 'center', fontFamily: FONT, fontSize: 54,
    color: INK, letterSpacing: '0.04em', textShadow: '0 2px 16px rgba(0,0,0,0.9)'}}>
    {segs.map(([t, c], i) => <span key={i} style={{color: c}}>{t}</span>)}
  </div>
);

export const Opening: React.FC<{c?: Cues; audio?: boolean}> = ({c = cuesV4, audio = true}) => {
  const cues = c;
  const SH = cues.shots;
  // 整条里，“先选”之后插了三句（2006 年 / 埃默里大学 / 实验），32 个人那段的字幕合成一句
  const merged = 'gap' in SH;
  const askEnd = merged ? (SH as {gap: number}).gap : SH.exp;
  const askAt = (cues as {askAt?: number}).askAt ?? ASK_AT;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sp = (at: number, damping = 20, stiffness = 140) => spring({frame: frame - at, fps, config: {damping, stiffness}});

  // 镜头：全景 → 推到 A → 移到 B（越等推得越近）→ 拉回全景
  // inPlace：A、B 不推近，就在原地按阅读顺序演（整条用；第四版样片仍是推近）
  const inPlace = Boolean((cues as {inPlace?: boolean}).inPlace);
  // startOnA：一开头就在 A 上（每一刻只给一个大主体），不先给全景；wide：什么时候拉回全景（默认和“先选”同时）
  const startOnA = Boolean((cues as {startOnA?: boolean}).startOnA);
  const ZA = startOnA ? 1.45 : 1.32;
  const pA = inPlace ? 0 : startOnA ? 1 : sp(SH.a, 18, 170);
  const pB = inPlace ? 0 : sp(SH.b, 22, 120);
  const pW = inPlace ? 0 : sp((cues as {wide?: number}).wide ?? SH.ask, 22, 140);
  const bPush = interpolate(frame, [SH.b, cues.bStrike], [ZA, ZA + 0.12], {...clamp, easing: Easing.in(Easing.quad)});
  const mix = (a: number, b: number, t: number) => a + (b - a) * t;
  let cx = mix(960, A_X, pA);
  let cy = mix(540, CARD_Y, pA);
  // 第一场也不能停着：读题的这一秒多里，镜头慢慢往里推
  let cs = mix(1 + 0.035 * Math.min(1, frame / Math.max(1, SH.a)), ZA, pA);
  cx = mix(cx, B_X, pB); cy = mix(cy, CARD_Y, pB); cs = mix(cs, bPush, pB);
  cx = mix(cx, 960, pW); cy = mix(cy, 540, pW); cs = mix(cs, 1, pW);
  const focusA = pA * (1 - pB);
  const focusB = pB * (1 - pW);

  // 电
  const kA = frame - cues.aStrike;
  const kB = frame - cues.bStrike;
  const flashA = kA >= 0 ? Math.exp(-kA / 4) : 0;
  const flashB = kB >= 0 ? 0.6 * Math.exp(-kB / 3) : 0;
  const arrivals = cues.picked.map((_, j) => cues.moveA.start + j * cues.moveA.step + cues.travel);
  const kArr = Math.min(...arrivals.map((a) => (frame >= a ? frame - a : 99)));
  const flashHead = kArr < 10 ? 0.8 * Math.exp(-kArr / 2.5) : 0;
  let shake = 0;
  let screen = 0;
  if (kA >= 0 && kA < 14) {
    shake += (inPlace ? 7 : 16) * Math.exp(-kA / 3);
    screen += (inPlace ? [0.4, 0.2, 0.08] : [0.8, 0.45, 0.2, 0.08])[kA] ?? 0;
  }
  if (kB >= 0 && kB < 5) { shake += 1.5; screen += kB === 0 ? 0.06 : 0; }
  if (kArr < 6) shake += 2 * Math.exp(-kArr / 2);
  const sx = (random(`x${frame}`) - 0.5) * 2 * shake;
  const sy = (random(`y${frame}`) - 0.5) * 2 * shake;

  // 卡片缩上去当表头
  const pH = sp(SH.exp, 18, 120);
  // 第 0 秒两张卡带着字一起轻轻落定（同时、对称，不分两处）
  const settle = inPlace ? 0.96 + 0.04 * sp(-2, 20, 200) : 1;
  const cardS = mix(settle, 0.46, pH);
  const cardY = mix(CARD_Y, 250, pH);
  const dark = !inPlace && frame >= SH.b && frame < ((cues as {wide?: number}).wide ?? SH.ask) + 12 ? interpolate(frame, [SH.b, cues.bStrike], [0.3, 0.8], clamp) * (1 - pW) : 0.3;
  const lineDim = interpolate(frame, [SH.line, SH.line + 10], [1, 0.4], clamp);

  // B 的计时圈：平时转着等；轮到它时从满圈倒数到空
  const bCount = cues.count.findIndex((f, i) => frame >= f && frame < (cues.count[i + 1] ?? cues.bStrike));
  const counting = frame >= cues.count[0] && frame < cues.bStrike;
  const bFrac = interpolate(frame, [cues.count[0], cues.bStrike], [1, 0], clamp);
  const bRing = counting
    ? <Ring frac={bFrac}><span style={{fontSize: 64, fontWeight: 300}}>{3 - bCount}</span><span style={{fontSize: 26, marginLeft: 6}}>秒</span></Ring>
    : frame >= cues.bStrike && frame < SH.ask
      ? <Ring frac={0}><span style={{fontSize: 64, fontWeight: 300}}>0</span><span style={{fontSize: 26, marginLeft: 6}}>秒</span></Ring>
      : <Ring frac={0} spin={-60}><span style={{fontSize: 40, fontWeight: 300, letterSpacing: '0.1em', color: MUTE}}>···</span></Ring>;
  const aRing = <Ring frac={0}><span style={{fontSize: 64, fontWeight: 300}}>0</span><span style={{fontSize: 26, marginLeft: 6}}>秒</span></Ring>;

  return (
    <AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 260, top: 200, width: 1400, height: 760, borderRadius: '50%', filter: 'blur(80px)',
        background: `radial-gradient(ellipse, rgba(40,80,200,${0.14 + 0.25 * flashA + 0.1 * flashHead}), rgba(0,0,0,0) 62%)`}} />

      <AbsoluteFill style={{transformOrigin: '0 0',
        transform: `translate(${960 - cx * cs + sx}px, ${540 - cy * cs + sy}px) scale(${cs})`}}>
        {/* 视线只走一条路：先读左边 A、再读右边 B，读完往下，问题就在卡片正下方浮出来；
            回到两张卡时，同一个位置原地变成“先选，再往下看。”（号主，10/28：一会这里闪、一会那里跳字，顺序乱） */}
        <div style={{position: 'absolute', left: 0, right: 0, top: CARD_Y + CH / 2 + 34, textAlign: 'center', fontFamily: FONT,
          fontSize: 84}}>
          <div style={{position: 'absolute', left: 0, right: 0}}>
            <Rise at={askAt} perChar={2} exitAt={SH.ask - 4} style={{fontWeight: 300, color: 'rgba(200,206,222,0.7)'}}>你选</Rise>
            <Rise at={askAt + 4} perChar={2} exitAt={SH.ask - 4} style={{fontWeight: 600, color: INK}}>哪个？</Rise>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0}}>
            <Rise at={SH.ask + 2} perChar={1.5} exitAt={askEnd - 4} style={{fontWeight: 400, color: INK, fontSize: 64}}>先选，再往下看。</Rise>
          </div>
        </div>

        <Card letter="A" cx={A_X} cy={cardY} scale={cardS} opacity={(1 - 0.72 * focusB) * (frame >= SH.line ? 1 : 1)} blur={4 * focusB}
          ring={aRing} boltH={196} flash={Math.max(flashA, flashHead)} arcK={kArr < 10 ? kArr : kA}
          time="马上" size="重" tail="被电一下，|重一点" />
        <Card letter="B" cx={B_X} cy={cardY} scale={cardS} opacity={(1 - 0.72 * focusA) * (frame >= SH.line ? 0.45 : 1)}
          blur={4 * focusA} ring={bRing} boltH={92} flash={flashB} arcK={kB} time="等一会儿" size="轻" tail="再电，|轻一点" />

        {/* 32 名受试者 */}
        {frame >= SH.exp && (
          <>
            <div style={{position: 'absolute', left: 0, right: 0, top: 400, textAlign: 'center', fontFamily: FONT, fontSize: 28,
              color: MUTE, letterSpacing: '0.1em'}}>
              <Rise at={cues.people.start - 4}>32 名受试者</Rise>
            </div>
            {Array.from({length: cues.people.n}, (_, i) => {
              const pop = sp(cues.people.start + i * cues.people.step, 12, 220);
              if (pop < 0.001) return null;
              const j = cues.picked.indexOf(i);
              const toA = j >= 0;
              const order = toA ? j : Array.from({length: i}, (_, q) => q).filter((q) => !cues.picked.includes(q)).length;
              const start = toA ? cues.moveA.start + j * cues.moveA.step : cues.moveB.start + order * cues.moveB.step;
              const m = spring({frame: frame - start, fps, durationInFrames: cues.travel, config: {damping: 16, stiffness: 150}});
              const from = GRID(i);
              const to = toA ? SLOT_A(j) : SLOT_B(order);
              const x = mix(from.x, to.x, m);
              const y = mix(from.y, to.y, m) - 36 * Math.sin(Math.PI * Math.min(1, m));
              const arrived = frame >= start + cues.travel;
              const lit = toA && frame >= SH.line ? interpolate(frame, [SH.line, SH.line + 8], [0, 1], clamp) : 0;
              const color = toA && arrived ? (lit > 0 ? '#FF7B6E' : 'rgba(244,246,251,0.95)') : 'rgba(244,246,251,0.8)';
              return <Person key={i} x={x} y={y} s={pop} color={color} glow={lit}
                />;
            })}
            {/* 人数放在两张小卡旁边，读起来像一张表 */}
            {frame >= Math.min(cues.counts, (cues as {countA?: number}).countA ?? cues.counts) && (
              <>
                <div style={{position: 'absolute', left: A_X + 160, top: 222, fontFamily: FONT, fontSize: 44, fontWeight: 600,
                  color: INK}}>
                  <Rise at={(cues as {countA?: number}).countA ?? cues.counts}>10 人</Rise>
                </div>
                <div style={{position: 'absolute', left: B_X + 160, top: 222, fontFamily: FONT, fontSize: 44, fontWeight: 600,
                  color: INK, opacity: lineDim}}>
                  <Rise at={(cues as {countA?: number}).countA !== undefined ? cues.counts : cues.counts + 4}>22 人</Rise>
                </div>
              </>
            )}
          </>
        )}
      </AbsoluteFill>

      {/* 等的时候四周越压越暗 */}
      <AbsoluteFill style={{background: `radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,${dark}) 100%)`}} />
      {screen > 0 && <AbsoluteFill style={{background: '#EAF2FF', opacity: screen}} />}

      {!merged && frame >= SH.exp && frame < SH.pick && <Subtitle segs={[['2006 年，埃默里大学做过类似的实验。']]} />}
      {frame >= (merged ? SH.exp : SH.pick) && frame < SH.line && <Subtitle segs={[['近三分之一的人选了 '], ['A', RED], ['：']]} />}

      {frame >= SH.line && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 880, textAlign: 'center', fontFamily: FONT, fontSize: 84,
          letterSpacing: '0.04em', textShadow: '0 4px 30px rgba(0,0,0,0.9)'}}>
          <Rise at={cues.punch1} perChar={2} style={{fontWeight: 300, color: 'rgba(220,226,240,0.85)'}}>宁可更疼，</Rise>
          <Rise at={cues.punch2} perChar={2} style={{fontWeight: 600, color: INK}}>也</Rise>
          <Rise at={cues.punch2 + 2} perChar={2} style={{fontWeight: 600, color: RED}}>不想等</Rise>
          <Rise at={cues.punch2 + 8} style={{fontWeight: 600, color: INK}}>。</Rise>
        </div>
      )}
      {frame >= cues.source && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1012, textAlign: 'center', fontFamily: FONT, fontSize: 22,
          color: MUTE, letterSpacing: '0.06em'}}>
          <Rise at={cues.source}>Berns 等，2006，《科学》｜32 名受试者</Rise>
        </div>
      )}

      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs><filter id="boltGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14" /></filter></defs>
      </svg>
      {audio && <Html5Audio src={staticFile('001/opening.wav')} />}
    </AbsoluteFill>
  );
};
