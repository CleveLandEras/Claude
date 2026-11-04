// 第二版（照 Orbit 做的界面风，号主说格式不适配，留作对照）：照号主给的标杆（参考/orbit_拆解.md）重做质感和动效。
// 文案沿用 videos/001_等待/render.py 的前 10 秒；节拍表 cues.json（90 BPM，一拍 20 帧）；
// 声音由 videos/001_等待/opening_audio.py 生成。
//
// 三场，一张卡片贯穿：
//   一 你选哪个：A 一小段点阵，一电就整段亮；B 一长段点阵，红点（正在等的你）慢慢走。选择框在 A、B 间犹豫。
//   二 实验：卡片缩成药丸再展开，红点飞去当新卡片的标记；32 个人一格一格坐进来。
//   三 结果：标题原地变成“宁可更疼，也不想等。”，选 A 的 10 格亮起来、炸一下。
import {AbsoluteFill, Html5Audio, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Glass, Matrix, Rect, RedDot, lerpRect} from '../../components/Glass';
import {Rise} from '../../components/Rise';
import {blue, S, U} from '../../style';
import cues from './cues_v2.json';

const S1: Rect = {x: 410, y: 400, w: 1100, h: 400};
const PILL: Rect = {x: 700, y: 552, w: 520, h: 96};
const S2: Rect = {x: 410, y: 440, w: 1100, h: 372};

const ROW_A = S1.y + 150;
const ROW_B = S1.y + 285;
const CELL = 18;
const GAP = 7;
const MX = 1000;                                   // 两段点阵的起点
const A_COLS = 5;
const B_COLS = 16;
const B_W = B_COLS * CELL + (B_COLS - 1) * GAP;

const G_COLS = 16;
const G_CELL = 48;
const G_GAP = 14;
const G_W = G_COLS * G_CELL + (G_COLS - 1) * G_GAP;
const PICKED = [1, 4, 8, 11, 14, 17, 21, 24, 27, 30];   // 选了 A 的 10 个人，散在 32 格里

const HEADS = [
  {at: 0, l: '你选', b: '哪个？'},
  {at: cues.scene2 - 2, l: '2006 年，', b: '埃默里大学'},
  {at: cues.scene3, l: '近三分之一的人', b: '选了 A'},
  {at: cues.hit, l: '宁可更疼，', b: '也不想等。'},
];

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const recent = (frame: number, list: number[], life: number) => {
  let k = -1;
  for (const f of list) if (f <= frame && frame - f < life) k = frame - f;
  return k;
};

// 卡片在第 fr 帧的样子：第一场的大卡片 → 缩成药丸 → 弹开成第二场的卡片
const morphAt = (fr: number, fps: number) => {
  const out = spring({frame: fr - cues.morph, fps, config: {damping: 200, stiffness: 170}});
  const inn = spring({frame: fr - cues.scene2, fps, config: {damping: 16, stiffness: 110, mass: 0.9}});
  return {out, inn, card: lerpRect(lerpRect(S1, PILL, out), S2, inn)};
};

// 红点在第 fr 帧的位置：B 线上走 → 收进药丸左端 → 落到卡片左上角当标记（跟着卡片一起弹）
const useRedPos = () => {
  const {fps} = useVideoConfig();
  return (fr: number) => {
    const t = (Math.min(fr, cues.morph) % cues.bPeriod) / cues.bPeriod;
    const {out, inn, card} = morphAt(fr, fps);
    const a = {x: MX + B_W * t, y: ROW_B};
    const b = {x: PILL.x + 48, y: PILL.y + PILL.h / 2};
    const c = {x: card.x + 62, y: card.y + 58};
    const ab = {x: a.x + (b.x - a.x) * out, y: a.y + (b.y - a.y) * out};
    const k = Math.min(1, inn);
    return {x: ab.x + (c.x - ab.x) * k, y: ab.y + (c.y - ab.y) * k, t};
  };
};

const Head: React.FC = () => (
  <div style={{position: 'absolute', left: S1.x, top: 250, fontFamily: S.sans, fontSize: 92, lineHeight: 1.15,
    letterSpacing: '0.01em', whiteSpace: 'nowrap'}}>
    {HEADS.map((h, i) => {
      const next = HEADS[i + 1];
      const exitAt = next ? next.at - 4 : undefined;
      const n = Array.from(h.l).length;
      return (
        <div key={i} style={{position: 'absolute', left: 0, top: 0}}>
          <Rise at={h.at} perChar={1.2} exitAt={exitAt} style={{fontWeight: 300, color: 'rgba(200,206,222,0.62)'}}>
            {h.l}
          </Rise>
          <Rise at={h.at === 0 ? 0 : h.at + n * 1.2} perChar={1.2} exitAt={exitAt}
            style={{fontWeight: 600, color: '#E4ECFF'}}>{h.b}</Rise>
        </div>
      );
    })}
    <div style={{position: 'absolute', left: 4, top: 112, fontSize: 34, lineHeight: 1.2}}>
      {/* 第二场的小标题 */}
      <Rise at={cues.scene2 + 14} exitAt={cues.scene3 - 4} style={{fontWeight: 400, color: U.mute,
        letterSpacing: '0.04em'}}>做过类似的实验。</Rise>
    </div>
  </div>
);

// 第一场：两个选项
const Choice: React.FC<{out: number}> = ({out}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const red = useRedPos()(frame);

  // A：每次被电，光从左往右一扫而过
  const ka = recent(frame, cues.aStrikes, 16);
  const aLevel = (c: number, r: number) => {
    const shimmer = 0.05 + 0.05 * Math.sin(frame * 0.21 + c * 1.3 + r * 1.7);
    if (ka < 0) return shimmer;
    const kc = ka - c * 0.9;
    return kc < 0 ? shimmer : Math.max(shimmer, Math.exp(-kc / 3.6));
  };
  const aWhite = (c: number) => {
    const kc = ka - c * 0.9;
    return ka >= 0 && kc >= 0 && kc < 3 ? 1 - kc / 3 : 0;
  };
  // B：红点走过的格子留下一道暗光，走到头才轻轻亮一下
  const kb = recent(frame, cues.bStrikes, 14);
  const bLevel = (c: number, r: number) => {
    const shimmer = 0.04 + 0.04 * Math.sin(frame * 0.17 + c * 0.9 + r * 2.1);
    const cx = MX + c * (CELL + GAP) + CELL / 2;
    let v = cx < red.x ? (r === 1 ? 0.5 : 0.24) * (0.6 + 0.4 * (c / B_COLS)) : shimmer;
    if (kb >= 0 && c >= B_COLS - 4) v = Math.max(v, 0.6 * Math.exp(-kb / 3));
    return v;
  };

  // 选择框在 A、B 之间犹豫
  let sel = 0;
  cues.select.forEach((s, i) => {
    sel += (i % 2 === 0 ? 1 : -1) * spring({frame: frame - s, fps, config: {damping: 15, stiffness: 150}});
  });
  const selY = ROW_A + (ROW_B - ROW_A) * sel - 56;
  const flash = ka >= 0 ? Math.exp(-ka / 3) : 0;

  const typed = Math.max(0, Math.min(cues.type.n, Math.floor((frame - cues.type.start) / cues.type.step) + 1));
  const caret = frame < cues.type.start + cues.type.n * cues.type.step || Math.floor(frame / 12) % 2 === 0;

  const row = (y: number, letter: string, a: string, b: string) => (
    <div style={{position: 'absolute', left: S1.x + 70, top: y - 30, display: 'flex', alignItems: 'baseline',
      fontFamily: S.sans, whiteSpace: 'nowrap'}}>
      <span style={{width: 62, fontSize: 46, fontWeight: 600, color: U.ink}}>{letter}</span>
      <span style={{fontSize: 32, fontWeight: 400, color: U.soft}}>{a}</span>
      <span style={{fontSize: 32, fontWeight: 600, color: U.ink}}>{b}</span>
    </div>
  );

  return (
    <div style={{position: 'absolute', inset: 0, transformOrigin: '960px 600px',
      transform: `scale(${1 - 0.14 * out})`, filter: `blur(${out * 14}px)`, opacity: Math.max(0, 1 - out * 1.4)}}>
      <div style={{position: 'absolute', left: S1.x + 70, top: S1.y + 40, fontFamily: S.sans, fontSize: 24,
        color: U.mute, letterSpacing: '0.06em'}}>两个选项，只能选一个</div>

      <svg width={S1.w - 60} height={112} style={{position: 'absolute', left: S1.x + 30, top: selY, overflow: 'visible',
        filter: 'drop-shadow(0 0 14px rgba(80,140,255,0.22))'}}>
        <defs>
          <linearGradient id="selRim" x1="0" y1="0" x2="0.2" y2="1">
            <stop offset="0" stopColor="rgba(255,255,255,0.75)" />
            <stop offset="0.45" stopColor="rgba(255,255,255,0.08)" />
            <stop offset="1" stopColor="rgba(140,175,255,0.45)" />
          </linearGradient>
          <linearGradient id="selFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="rgba(255,255,255,0.06)" />
            <stop offset="1" stopColor="rgba(120,150,255,0.03)" />
          </linearGradient>
        </defs>
        <rect x={0.75} y={0.75} width={S1.w - 61.5} height={110.5} rx={30} fill="url(#selFill)" stroke="url(#selRim)"
          strokeWidth={1.5} />
      </svg>

      {row(ROW_A, 'A', '马上被电一下，', '重一点')}
      {row(ROW_B, 'B', '等一会儿再电，', '轻一点')}

      {flash > 0.02 && (
        <div style={{position: 'absolute', left: MX - 120, top: ROW_A - 110, width: 360, height: 220, borderRadius: '50%',
          background: `radial-gradient(ellipse, rgba(90,200,255,${0.55 * flash}), rgba(90,200,255,0) 65%)`,
          filter: 'blur(18px)'}} />
      )}
      <Matrix x={MX} y={ROW_A - 34} cols={A_COLS} rows={3} cell={CELL} gap={GAP} level={aLevel} white={aWhite} />
      <div style={{position: 'absolute', left: MX + A_COLS * (CELL + GAP) + 18, top: ROW_A - 15, fontFamily: S.sans,
        fontSize: 24, fontWeight: 500, color: U.readout, fontVariantNumeric: 'tabular-nums'}}>0 s</div>

      <Matrix x={MX} y={ROW_B - 34} cols={B_COLS} rows={3} cell={CELL} gap={GAP} level={bLevel} />
      <div style={{position: 'absolute', left: MX + B_W + 18, top: ROW_B - 15, fontFamily: S.sans, fontSize: 24,
        fontWeight: 500, color: U.readout, fontVariantNumeric: 'tabular-nums'}}>
        {(red.t * 4).toFixed(1)} s
      </div>

      {/* 输入框里逐字打出提示 */}
      <Glass r={{x: S1.x, y: 840, w: 520, h: 72}}>
        <div style={{position: 'absolute', left: 30, top: 27, width: 16, height: 16, borderRadius: 8,
          background: `radial-gradient(circle, #CFE6FF, rgb(${blue(0.7).join(',')}) 70%)`,
          boxShadow: `0 0 14px rgba(${blue(0.7).join(',')},0.8)`}} />
        <div style={{position: 'absolute', left: 66, top: 15, fontFamily: S.sans, fontSize: 30, color: U.soft,
          letterSpacing: '0.04em', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center'}}>
          {Array.from('先选，再往下看。').slice(0, typed).join('')}
          {caret && <span style={{display: 'inline-block', width: 2, height: 32, marginLeft: 4, background: U.readout}} />}
        </div>
      </Glass>
    </div>
  );
};

// 第二、三场：32 个人
// 卡片里的东西都跟着卡片当前的位置和大小走，展开时一起弹
const Subjects: React.FC<{inn: number; card: Rect}> = ({inn, card}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {cells, pick} = cues;
  const shown = Math.max(0, Math.min(cells.n, Math.floor((frame - cells.start) / cells.step) + 1));
  const kh = frame >= cues.hit ? frame - cues.hit : -1;
  const hitFlash = kh >= 0 ? Math.exp(-kh / 4) : 0;
  const dimRest = interpolate(frame, [cues.scene3, cues.scene3 + 14], [1, 0.45], clamp);
  const G_X = card.x + (card.w - G_W) / 2;
  const G_Y = card.y + 140;
  const swatch = (at: number) => spring({frame: frame - at, fps, config: {damping: 12, stiffness: 200}});
  return (
    <div style={{position: 'absolute', inset: 0, opacity: interpolate(inn, [0.5, 0.85], [0, 1], clamp)}}>
      <div style={{position: 'absolute', left: card.x + 92, top: card.y + 40, fontFamily: S.sans, fontSize: 26,
        color: U.soft, letterSpacing: '0.04em'}}>
        <div style={{position: 'absolute', whiteSpace: 'nowrap'}}>
          <Rise at={cues.scene2 + 6} exitAt={cues.scene3}>32 名受试者</Rise>
        </div>
        <div style={{position: 'absolute', whiteSpace: 'nowrap'}}>
          <Rise at={cues.scene3 + 4}>选了 A 的人</Rise>
        </div>
      </div>

      <div style={{position: 'absolute', right: 1920 - (card.x + card.w - 56), top: card.y + 22, fontFamily: S.sans,
        textAlign: 'right', whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'}}>
        <div style={{position: 'absolute', right: 0, display: 'flex', alignItems: 'baseline', gap: 10,
          opacity: frame < cues.scene3 ? 1 : 0}}>
          <span style={{fontSize: 64, fontWeight: 600, color: U.readout}}>{shown}</span>
          <span style={{fontSize: 28, color: U.mute}}>/ 32</span>
        </div>
        <div style={{position: 'absolute', right: 0, display: 'flex', alignItems: 'baseline', gap: 12}}>
          <Rise at={cues.scene3 + 4} style={{fontSize: 28, color: U.mute}}>10 / 32</Rise>
          <Rise at={cues.scene3 + 8} style={{fontSize: 64, fontWeight: 600, color: U.readout}}>≈ 1/3</Rise>
        </div>
      </div>

      {hitFlash > 0.02 && (
        <div style={{position: 'absolute', left: G_X - 100, top: G_Y - 160, width: G_W + 200, height: 430,
          borderRadius: '50%', background: `radial-gradient(ellipse, rgba(80,190,255,${0.5 * hitFlash}), rgba(80,190,255,0) 62%)`,
          filter: 'blur(30px)'}} />
      )}
      {Array.from({length: cells.n}, (_, i) => {
        const c = Math.floor(i / 2);
        const r = i % 2;
        const pop = spring({frame: frame - (cells.start + i * cells.step), fps, config: {damping: 11, stiffness: 210, mass: 0.6}});
        if (pop <= 0.001) return null;
        const j = PICKED.indexOf(i);
        const lit = j < 0 ? 0 : spring({frame: frame - (pick.start + j * pick.step), fps, config: {damping: 14, stiffness: 180}});
        const [R, G, B] = blue(c / (G_COLS - 1));
        const wh = j >= 0 ? hitFlash : 0;
        const fill = lit > 0.01
          ? `rgba(${Math.round(R + (255 - R) * wh * 0.8)},${Math.round(G + (255 - G) * wh * 0.8)},${Math.round(B + (255 - B) * wh * 0.8)},${0.12 + 0.88 * Math.min(1, lit)})`
          : 'linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.035))';
        return (
          <div key={i} style={{
            position: 'absolute', left: G_X + c * (G_CELL + G_GAP), top: G_Y + r * (G_CELL + G_GAP),
            width: G_CELL, height: G_CELL, borderRadius: 13, transform: `scale(${pop})`,
            background: fill,
            border: `1px solid rgba(255,255,255,${lit > 0.5 ? 0.45 : 0.14})`,
            boxShadow: lit > 0.01 ? `0 0 ${18 + 30 * wh}px rgba(${R},${G},${B},${0.55 * Math.min(1, lit) + 0.4 * wh})` : 'none',
            opacity: j >= 0 ? 1 : dimRest,
          }} />
        );
      })}

      <div style={{position: 'absolute', left: G_X, top: card.y + card.h - 84, display: 'flex', alignItems: 'center',
        fontFamily: S.sans, fontSize: 24, lineHeight: 1.3, whiteSpace: 'nowrap'}}>
        <div style={{width: 18, height: 18, borderRadius: 5, marginRight: 14,
          background: `linear-gradient(90deg, rgb(${blue(0).join(',')}), rgb(${blue(1).join(',')}))`,
          boxShadow: `0 0 12px rgba(${blue(0.6).join(',')},0.6)`, transform: `scale(${swatch(cues.cells.start + 10)})`}} />
        <Rise at={cues.cells.start + 10} style={{color: U.soft}}>A · 马上，重一点</Rise>
        <div style={{width: 18, height: 18, borderRadius: 5, marginLeft: 56, marginRight: 14,
          background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.18)',
          transform: `scale(${swatch(cues.cells.start + 14)})`}} />
        <Rise at={cues.cells.start + 14} style={{color: U.mute}}>B · 等一会儿，轻一点</Rise>
      </div>
    </div>
  );
};

// 出处：一个小药丸从左边展开
const Source: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (frame < cues.source) return null;
  const p = spring({frame: frame - cues.source, fps, config: {damping: 18, stiffness: 140}});
  return (
    <Glass r={{x: S2.x, y: S2.y + S2.h + 36, w: 64 + 556 * p, h: 64}} radius={32}>
      <div style={{position: 'absolute', left: 30, top: 17, fontFamily: S.sans, fontSize: 22, color: U.mute,
        whiteSpace: 'nowrap', letterSpacing: '0.03em'}}>
        <Rise at={cues.source + 4}>Berns 等，2006，《科学》｜32 名受试者</Rise>
      </div>
    </Glass>
  );
};

export const OpeningV2: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const redPos = useRedPos();

  const {out, inn, card} = morphAt(frame, fps);

  const ka = recent(frame, cues.aStrikes, 16);
  const flashA = ka >= 0 ? Math.exp(-ka / 3) : 0;
  const kh = frame >= cues.hit ? frame - cues.hit : -1;
  const hit = kh >= 0 ? Math.exp(-kh / 5) : 0;

  // 镜头：整段慢慢推近；A 被电时抖一下，最后那下抖得最狠，还往前顶一点
  const push = 1 + 0.03 * (frame / cues.frames) + 0.018 * hit;
  const shake = 2 * flashA + 9 * hit;
  const sx = (random(`sx${frame}`) - 0.5) * 2 * shake;
  const sy = (random(`sy${frame}`) - 0.5) * 2 * shake;

  const red = redPos(frame);
  // 彗尾：往回取 24 个很密的位置，越往后越细、越淡，再整体模糊
  const tail = Array.from({length: 24}, (_, i) => redPos(frame - (i + 1) * 0.35));
  const speed = Math.hypot(red.x - tail[2].x, red.y - tail[2].y);

  return (
    <AbsoluteFill style={{background: U.bg, overflow: 'hidden'}}>
      {/* 卡片背后一团模糊的蓝光，被电时亮一下 */}
      <div style={{position: 'absolute', left: 260 + 30 * Math.sin(frame / 50), top: 260, width: 1400, height: 760,
        borderRadius: '50%', filter: 'blur(70px)',
        background: `radial-gradient(ellipse, rgba(40,80,230,${0.16 + 0.2 * flashA + 0.35 * hit}), rgba(0,0,0,0) 62%)`}} />
      <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${push})`, transformOrigin: '960px 560px'}}>
        <Head />
        <Glass r={card} glow={0.5 * flashA * (1 - out) + 0.8 * hit} />
        {frame < cues.scene2 + 20 && <Choice out={out} />}
        {frame >= cues.scene2 - 4 && <Subjects inn={inn} card={card} />}
        <Source />
        {speed > 1.5 && (
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, filter: 'blur(3px)', overflow: 'visible'}}>
            {tail.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r={7 * (1 - i / 26)} fill={U.red} opacity={0.5 * (1 - i / 24)} />
            ))}
          </svg>
        )}
        <RedDot x={red.x} y={red.y} size={frame < cues.morph ? 18 : 18 + 4 * inn} />
      </AbsoluteFill>
      <Html5Audio src={staticFile('001/opening.wav')} />
    </AbsoluteFill>
  );
};
