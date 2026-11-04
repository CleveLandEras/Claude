// 第一版（编辑排版风，没被采用，留作对照）：笔记 001《等待》开头 11 秒样片。文案沿用 videos/001_等待/render.py 的前 10 秒。
// 节拍表在 cues.json（90 BPM，一拍 20 帧）；声音由 videos/001_等待/opening_audio.py 生成。
import {AbsoluteFill, Easing, Html5Audio, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Backdrop, Film} from '../../components/Backdrop';
import {Draw, Rise} from '../../components/Rise';
import {Spark, Strike, flashOf} from '../../components/Spark';
import {C, F, L, smallCaps} from '../../style';
import cues from './cues_v1.json';

const ROW_A = 540;
const ROW_B = 770;
const X0 = 1060;                 // “现在”那条竖线
const XA = 1170;                 // A：马上
const XB = 1700;                 // B：等 4 秒，每秒 160px
const PER_SEC = (XB - X0) / 4;
const DOT0 = L + 110;
const DOT_GAP = 28;

const A_STRIKES: Strike[] = cues.aStrikes.map((f) => ({f, s: f === cues.hit ? 1.6 : 1}));
const B_STRIKES: Strike[] = cues.bStrikes.map((f) => ({f, s: 0.45}));

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Row: React.FC<{y: number; letter: string; text: string; sub: string; opacity: number; lit: number}> = (
  {y, letter, text, sub, opacity, lit},
) => (
  <div style={{position: 'absolute', left: L, top: y - 50, display: 'flex', alignItems: 'center', opacity}}>
    <div style={{width: 110, fontFamily: F.latin, fontStyle: 'italic', fontSize: 100, lineHeight: 1,
      color: lit > 0.5 ? C.goldHi : C.gold, marginTop: -8}}>
      {letter}
    </div>
    <div>
      <div style={{fontFamily: F.serif, fontSize: 50, color: C.ink, letterSpacing: '0.06em', lineHeight: 1.25}}>
        {text}
      </div>
      <div style={{...smallCaps(14), marginTop: 10}}>{sub}</div>
    </div>
  </div>
);

// A：一小段线就到头，马上被电
const TrackA: React.FC = () => (
  <>
    <div style={{position: 'absolute', left: X0, top: ROW_A - 1, width: XA - X0, height: 2, background: C.dim}} />
    <div style={{position: 'absolute', left: XA + 26, top: ROW_A - 12, fontFamily: F.mono, fontSize: 18,
      color: C.dim}}>0 s</div>
    <Spark x={XA} y={ROW_A} strikes={A_STRIKES} />
  </>
);

// B：一条带刻度的长线，一个点慢慢走过去，走到头才挨一下轻的
const TrackB: React.FC = () => {
  const frame = useCurrentFrame();
  const t = (frame % cues.bPeriod) / cues.bPeriod;
  const x = X0 + (XB - X0) * t;
  const secs = (t * 4).toFixed(1);
  return (
    <>
      <div style={{position: 'absolute', left: X0, top: ROW_B, width: XB - X0, height: 1, background: C.faint}} />
      {Array.from({length: 21}, (_, i) => {
        const major = i % 5 === 0;
        const tx = X0 + i * (PER_SEC / 5);
        return (
          <div key={i}>
            <div style={{position: 'absolute', left: tx, top: ROW_B - (major ? 8 : 4), width: 1,
              height: major ? 16 : 8, background: major ? C.dim : C.faint}} />
            {major && i > 0 && (
              <div style={{position: 'absolute', left: tx - 30, width: 60, top: ROW_B + 18, textAlign: 'center',
                fontFamily: F.latin, fontStyle: 'italic', fontSize: 20, color: C.dim}}>{i / 5} s</div>
            )}
          </div>
        );
      })}
      <div style={{position: 'absolute', left: X0, top: ROW_B - 1, width: x - X0, height: 2,
        background: `linear-gradient(90deg, rgba(201,163,94,0.15), ${C.gold})`}} />
      <div style={{position: 'absolute', left: x - 9, top: ROW_B - 9, width: 18, height: 18, borderRadius: 9,
        background: C.ink, boxShadow: '0 0 14px rgba(236,230,216,0.35)'}} />
      <div style={{position: 'absolute', left: x - 40, width: 80, top: ROW_B - 48, textAlign: 'center',
        fontFamily: F.mono, fontSize: 18, color: C.goldHi}}>{secs} s</div>
      <Spark x={XB} y={ROW_B} strikes={B_STRIKES} />
    </>
  );
};

// “现在”：两条线共同的起点
const NowLine: React.FC = () => (
  <>
    <div style={{position: 'absolute', left: X0, top: 452, width: 1, height: 390,
      backgroundImage: `linear-gradient(${C.faint} 50%, rgba(0,0,0,0) 50%)`, backgroundSize: '1px 8px'}} />
    <div style={{position: 'absolute', left: X0 - 1, top: 412, display: 'flex', alignItems: 'baseline', gap: 12}}>
      <span style={{fontFamily: F.serif, fontSize: 20, color: C.dim, letterSpacing: '0.2em'}}>现在</span>
      <span style={smallCaps(12)}>Now</span>
    </div>
  </>
);

// 32 个人：10 个选 A，22 个选 B
const People: React.FC<{gold: number}> = ({gold}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dot = (key: string, x: number, y: number, at: number, color: string) => {
    const p = spring({frame: frame - at, fps, config: {damping: 14, stiffness: 180, mass: 0.6}});
    if (p <= 0.001) return null;
    return <div key={key} style={{position: 'absolute', left: x - 7, top: y - 7 - (1 - Math.min(1, p)) * 18,
      width: 14, height: 14, borderRadius: 7, background: color, transform: `scale(${p})`}} />;
  };
  const {peopleA: pa, peopleB: pb} = cues;
  const aColor = gold > 0.5 ? C.goldHi : C.ink;
  return (
    <>
      {Array.from({length: pa.n}, (_, i) => dot(`a${i}`, DOT0 + i * DOT_GAP, ROW_A + 84, pa.start + i * pa.step, aColor))}
      {Array.from({length: pb.n}, (_, j) => dot(`b${j}`, DOT0 + j * DOT_GAP, ROW_B + 84, pb.start + j * pb.step,
        'rgba(236,230,216,0.75)'))}
      <div style={{position: 'absolute', left: DOT0 + pa.n * DOT_GAP + 6, top: ROW_A + 68, display: 'flex',
        alignItems: 'baseline', gap: 26}}>
        <Rise at={pa.start + pa.n * pa.step} style={{fontFamily: F.serif, fontSize: 26, color: C.dim}}>10 人</Rise>
        <Rise at={cues.scene3 + 6} style={{fontFamily: F.latin, fontStyle: 'italic', fontSize: 58, color: C.goldHi,
          marginTop: -24}}>≈ 1/3</Rise>
      </div>
      <div style={{position: 'absolute', left: DOT0 + pb.n * DOT_GAP + 6, top: ROW_B + 68}}>
        <Rise at={pb.start + pb.n * pb.step} style={{fontFamily: F.serif, fontSize: 26, color: C.dim}}>22 人</Rise>
      </div>
    </>
  );
};

const Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const two = frame >= cues.scene2;
  return (
    <>
      <div style={{position: 'absolute', left: L, top: 66, display: 'flex', alignItems: 'center', gap: 18}}>
        <Draw at={0} width={36} color={C.gold} thick={1.5} />
        <Rise key={two ? 2 : 1} at={two ? cues.scene2 : 0} style={{fontFamily: F.serif, fontSize: 20,
          color: C.ink, letterSpacing: '0.24em'}}>{two ? '02 · 实验' : '01 · 选择'}</Rise>
        <Rise key={two ? 'b' : 'a'} at={two ? cues.scene2 + 3 : 0} style={smallCaps(13)}>
          {two ? 'The Experiment' : 'The Choice'}
        </Rise>
      </div>
      <div style={{position: 'absolute', right: L, top: 62, textAlign: 'right'}}>
        <div style={{fontFamily: F.serif, fontSize: 20, color: C.dim, letterSpacing: '0.24em'}}>人间旁听生 · 笔记 001</div>
        <div style={{...smallCaps(12), marginTop: 8, color: C.faint}}>AI 生成 · Made by Claude</div>
      </div>
    </>
  );
};

export const OpeningV1: React.FC = () => {
  const frame = useCurrentFrame();
  const flashA = flashOf(frame, A_STRIKES);
  const flashB = flashOf(frame, B_STRIKES);

  // 镜头：以左边距为中心慢慢推近（左列和角标始终对齐）；A 被电时抖一下，最后那下抖得最狠
  const push = interpolate(frame, [0, cues.frames], [1, 1.04]);
  const camX = interpolate(frame, [0, cues.frames], [4, -4]);
  const camY = interpolate(frame, [0, cues.frames], [4, -8]);
  const shake = flashA > 1.1 ? 9 * (flashA / 1.6) : 2.2 * flashA;
  const sx = (random(`sx${frame}`) - 0.5) * 2 * shake;
  const sy = (random(`sy${frame}`) - 0.5) * 2 * shake;

  const lit = interpolate(frame, [cues.scene3, cues.scene3 + 14], [0, 1], clamp);
  const bFade = interpolate(frame, [cues.scene3, cues.scene3 + 16], [1, 0.36], {...clamp, easing: Easing.out(Easing.cubic)});
  const ulAt = cues.hit + 18;

  return (
    <AbsoluteFill style={{background: C.bg, overflow: 'hidden'}}>
      <Backdrop camX={camX} camY={camY} light={flashA * 0.5 + flashB * 0.3} />
      <AbsoluteFill style={{transform: `translate(${camX + sx}px, ${camY + sy}px) scale(${push})`,
        transformOrigin: `${L}px 52%`}}>

        {/* 01 选择：第一帧就完整 */}
        <div style={{position: 'absolute', left: L, top: 150}}>
          <Rise at={0} exitAt={cues.scene2 - 8} style={{fontFamily: F.serif, fontWeight: 300, fontSize: 132,
            color: C.ink, letterSpacing: '0.06em', lineHeight: 1.2}}>你选哪个？</Rise>
          <div style={{marginTop: 18, marginLeft: 6}}>
            <Rise at={0} exitAt={cues.scene2 - 10} style={smallCaps(15)}>Which one would you choose?</Rise>
          </div>
        </div>

        {/* 02 实验 */}
        <div style={{position: 'absolute', left: L, top: 138}}>
          {frame >= cues.scene2 - 1 && (
            <>
              <Rise at={cues.scene2} exitAt={cues.scene3 - 6} style={{...smallCaps(15), color: C.gold}}>
                Emory University · 2006
              </Rise>
              <div style={{height: 22}} />
              <Rise at={cues.scene2 + 2} perChar={1.2} exitAt={cues.scene3 - 6} style={{fontFamily: F.serif,
                fontWeight: 300, fontSize: 80, color: C.ink, letterSpacing: '0.05em', lineHeight: 1.25}}>
                2006 年，埃默里大学
              </Rise>
              <br />
              <Rise at={cues.scene2 + 10} perChar={1.2} exitAt={cues.scene3 - 6} style={{fontFamily: F.serif,
                fontWeight: 300, fontSize: 80, color: C.ink, letterSpacing: '0.05em', lineHeight: 1.25}}>
                做过类似的实验。
              </Rise>
            </>
          )}
        </div>

        {/* 03 结果：宁可更疼，也不想等 */}
        {frame >= cues.scene3 - 1 && (
          <div style={{position: 'absolute', left: L, top: 140}}>
            <Rise at={cues.scene3} perChar={1} style={{fontFamily: F.serif, fontWeight: 300, fontSize: 50,
              color: C.dim, letterSpacing: '0.08em'}}>近三分之一的人选了 A：</Rise>
            <div style={{height: 14}} />
            <div style={{position: 'relative', fontFamily: F.serif, fontWeight: 400, fontSize: 124,
              letterSpacing: '0.04em', lineHeight: 1.2, whiteSpace: 'nowrap'}}>
              <Rise at={cues.hit} perChar={1.6} style={{color: C.ink}}>宁可更疼，也</Rise>
              <span style={{position: 'relative', display: 'inline-block'}}>
                <Rise at={cues.hit + 6 * 1.6} perChar={1.6} style={{color: C.goldHi}}>不想等</Rise>
                <Draw at={ulAt} width={372} color={C.gold} thick={3}
                  style={{position: 'absolute', left: 4, bottom: -8}} />
              </span>
              <Rise at={cues.hit + 9 * 1.6} style={{color: C.ink}}>。</Rise>
            </div>
          </div>
        )}

        <NowLine />
        <Row y={ROW_A} letter="A" text="马上被电一下，重一点" sub="Now · Stronger" opacity={1} lit={lit} />
        <Row y={ROW_B} letter="B" text="等一会儿再电，轻一点" sub="Later · Weaker" opacity={bFade} lit={0} />
        <TrackA />
        <div style={{opacity: bFade}}><TrackB /></div>
        <People gold={lit} />

        {/* 底部一行：先是提示，后是出处 */}
        <div style={{position: 'absolute', left: L, top: 968, display: 'flex', alignItems: 'center', gap: 18}}>
          {frame < cues.scene2 ? (
            <>
              <Draw at={cues.hint} width={36} color={C.gold} thick={1.5} />
              <Rise at={cues.hint} perChar={1.5} exitAt={cues.scene2 - 10} style={{fontFamily: F.serif, fontSize: 30,
                color: C.dim, letterSpacing: '0.12em'}}>先选，再往下看。</Rise>
            </>
          ) : frame >= cues.source ? (
            <>
              <Draw at={cues.source} width={36} color={C.faint} thick={1} />
              <Rise at={cues.source} style={{fontFamily: F.serif, fontSize: 22, color: C.dim, letterSpacing: '0.08em'}}>
                Berns 等，2006，《科学》｜32 名受试者
              </Rise>
            </>
          ) : null}
        </div>
      </AbsoluteFill>
      {/* 角标不跟镜头动 */}
      <Hud />
      <Film />
      <Html5Audio src={staticFile('001/opening.wav')} />
    </AbsoluteFill>
  );
};
