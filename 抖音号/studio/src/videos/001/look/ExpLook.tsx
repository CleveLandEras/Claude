// 观感样片里“2006 年，埃默里大学 / 真的做过这个实验。”那一镜（时间同 Full.tsx 的 Exp，读 full.json 的 exp）。
// 第四版（七维度评审第二轮 10/28）：
//   一镜到底：夜里的校舍（坡屋顶、钟楼、两层拱窗，只亮三扇），先慢慢推近 35%，再加速穿进二楼那扇亮着的窗；
//   窗里早就是实验室（同一张画面缩小放在窗里），穿过窗时它正好铺满画面，不再硬切、不再冲白。夜空是暖黑，蓝色只留给电。
//   实验室：家具是实心剪影；电极的线接到桌上的刺激器（琥珀色指示灯），再接到老式显示器；
//   显示器开机是一条横亮线展开，之后人脸和桌面上有一层淡淡的冷光；推进屏幕时扫描线淡掉，最后一帧和 HookLook 第二段第一帧一样。
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import full from '../full.json';
import {LINE_SIZE} from '../Hook';
import {HookLook, LOOK_LINE_TOP} from './HookLook';
import {Grain, L, Room} from './Room';
import {Wipe} from './Wipe';

const EX = full.exp;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const lin = (f: number, a: number, b: number, from = 0, to = 1, ease?: (t: number) => number) =>
  interpolate(f, [a, b], [from, to], {...clamp, easing: ease});
const SCREEN = {x: 1330, y: 420, w: 448, h: 448 * 1080 / 1920};
const CUT = 41;                       // 换成实验室本身的那一帧（画面和窗里的一样）
const LINE1_EXIT = 31;
const LINE2_AT = 42;
const WIN = {x: 1054, y: 436, w: 64, h: 98};   // 二楼亮着的那扇窗（实验室）
const ZEND = 30;                               // 穿过窗时的总放大倍数：窗宽 64 × 30 = 1920
const WC = {x: WIN.x + WIN.w / 2, y: WIN.y + WIN.h * 0.62};

const STARS = Array.from({length: 30}, (_, i) => ({x: random(`sx${i}`) * 1920, y: random(`sy${i}`) * 240, r: 0.6 + random(`sr${i}`) * 1.1,
  ph: random(`sp${i}`) * 6.28}));

const arch = (x: number, y: number, w: number, h: number) =>
  `M ${x} ${y + h} L ${x} ${y + w / 2} A ${w / 2} ${w / 2} 0 0 1 ${x + w} ${y + w / 2} L ${x + w} ${y + h} Z`;

// 实验室（窗里和推进后用的是同一张）
const Lab: React.FC<{f: number; crt: number; lineFlash: number; scan: number; corner: number}> = ({f, crt, lineFlash, scan, corner}) => (
  <AbsoluteFill style={{background: '#050403'}}>
    <Room id="re" w={1920} h={1080} f={f} fig={{x: 990, y: 650, s: 1.4}} lampX={960} charge={0.25 + 0.5 * crt}
      wireTo={{x: 1176, y: 690}} box={false}>
      <g fill={L.sil}>
        {/* 左边一个柜子 */}
        <rect x={140} y={390} width={230} height={470} rx={4} />
        {/* 桌子 */}
        <rect x={1150} y={700} width={730} height={20} rx={4} />
        <rect x={1176} y={720} width={16} height={140} />
        <rect x={1834} y={720} width={16} height={140} />
        {/* 刺激器、显示器的机身、底座、厚边框 */}
        <rect x={1176} y={652} width={110} height={48} rx={5} />
        <rect x={SCREEN.x + 40} y={SCREEN.y + 20} width={SCREEN.w - 80} height={SCREEN.h + 10} rx={20} />
        <rect x={SCREEN.x + SCREEN.w / 2 - 30} y={SCREEN.y + SCREEN.h + 26} width={60} height={700 - (SCREEN.y + SCREEN.h + 26)} />
        <rect x={SCREEN.x - 26} y={SCREEN.y - 26} width={SCREEN.w + 52} height={SCREEN.h + 52} rx={18} />
      </g>
      {/* 实心剪影只在朝灯的上沿有一道暖色轮廓光 */}
      <g stroke={L.rim} strokeWidth={2} strokeLinecap="round">
        <line x1={144} y1={391} x2={366} y2={391} opacity={0.35} />
        <line x1={1154} y1={701} x2={1876} y2={701} opacity={0.55} />
        <line x1={1180} y1={653} x2={1282} y2={653} opacity={0.6} />
        <line x1={SCREEN.x - 20} y1={SCREEN.y - 25} x2={SCREEN.x + SCREEN.w + 20} y2={SCREEN.y - 25} opacity={0.35} />
      </g>
      <circle cx={1270} cy={666} r={5} fill={L.amber} opacity={0.6 + 0.4 * Math.sin(f / 5)} />
      <path d={`M 1286 676 C 1310 676, 1312 ${SCREEN.y + SCREEN.h + 20}, ${SCREEN.x + 10} ${SCREEN.y + SCREEN.h + 20}`}
        fill="none" stroke="#2E2117" strokeWidth={4} />
    </Room>
    {/* 屏幕 */}
    <div style={{position: 'absolute', left: SCREEN.x, top: SCREEN.y, width: SCREEN.w, height: SCREEN.h, overflow: 'hidden',
      background: '#000', borderRadius: 6 * corner}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0',
        transform: `scale(${SCREEN.w / 1920}) translateY(${(1 - crt) * 540}px) scaleY(${Math.max(0.01, crt)})`, opacity: crt}}>
        <HookLook at={full.opening.p2Offset} />
      </div>
      {lineFlash > 0 && <div style={{position: 'absolute', left: 0, right: 0, top: SCREEN.h / 2 - 2, height: 4, background: '#FFF4E0',
        opacity: lineFlash, boxShadow: '0 0 18px #FFE2B0'}} />}
      <div style={{position: 'absolute', inset: 0, opacity: scan * crt,
        background: 'repeating-linear-gradient(180deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px, rgba(0,0,0,0) 1px, rgba(0,0,0,0) 2px)'}} />
      <div style={{position: 'absolute', inset: 0, opacity: scan,
        background: 'radial-gradient(ellipse 80% 70% at 35% 25%, rgba(255,255,255,0.06), rgba(0,0,0,0) 60%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.35) 100%)'}} />
    </div>
    {/* 屏幕的光：桌面上一层暖、人脸和胸口一层淡淡的冷 */}
    <div style={{position: 'absolute', left: SCREEN.x - 60, top: 650, width: SCREEN.w + 120, height: 110,
      background: 'radial-gradient(closest-side, rgba(255,226,176,0.18), rgba(0,0,0,0))', opacity: crt}} />
    <div style={{position: 'absolute', left: 880, top: 220, width: 640, height: 500, mixBlendMode: 'screen',
      background: 'radial-gradient(closest-side at 60% 50%, rgba(159,184,224,0.15), rgba(0,0,0,0))', opacity: crt}} />
  </AbsoluteFill>
);

const Campus: React.FC<{f: number; lab: React.ReactNode}> = ({f, lab}) => {
  const xs = [574, 694, 814, 934, 1054, 1174, 1294];
  const lit = new Set(['2-4', '1-1', '1-5']);
  return (
    <>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <defs>
          <linearGradient id="csky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#0B0806" />
            <stop offset="0.7" stopColor="#1E1712" />
            <stop offset="1" stopColor="#140E09" />
          </linearGradient>
          <linearGradient id="cwin" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#E9B26E" />
            <stop offset="1" stopColor="#9C6534" />
          </linearGradient>
          <filter id="crim" x="-10%" y="-10%" width="120%" height="120%">
            <feOffset in="SourceAlpha" dx={0} dy={4} result="off" />
            <feComposite in="SourceAlpha" in2="off" operator="out" result="edge" />
            <feFlood floodColor="#C9A27A" floodOpacity={0.45} />
            <feComposite in2="edge" operator="in" />
          </filter>
          <filter id="cglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={18} /></filter>
        </defs>
        <rect width={1920} height={1080} fill="url(#csky)" />
        {STARS.map((s, i) => <circle key={i} cx={s.x} cy={s.y} r={s.r} fill={L.ink} opacity={0.15 + 0.15 * Math.sin(f / 12 + s.ph)} />)}
        {/* 校舍剪影：坡屋顶、中间钟楼；屋脊一道很淡的暖色轮廓 */}
        <g fill="#0B0806">
          <polygon points="500,372 960,262 1420,372" />
          <rect x={520} y={372} width={880} height={398} />
          <rect x={906} y={176} width={108} height={110} />
          <polygon points="894,178 960,118 1026,178" />
          <rect x={956} y={96} width={8} height={26} />
        </g>
        <g filter="url(#crim)" fill="#0B0806">
          <polygon points="500,372 960,262 1420,372" />
          <polygon points="894,178 960,118 1026,178" />
        </g>
        <circle cx={960} cy={226} r={30} fill="#1C140D" stroke="#3A2A1C" strokeWidth={2} />
        {/* 两层拱窗，只亮三扇；二楼第 5 扇是实验室（它里面就是下一镜） */}
        {[1, 2].map((fl) => xs.map((x, i) => {
          const y = fl === 2 ? 436 : 600;
          const on = lit.has(`${fl}-${i}`);
          const labWin = fl === 2 && i === 4;
          if (fl === 1 && i === 3) return null;
          return (
            <g key={`${fl}-${i}`}>
              {on && <path d={arch(x - 20, y - 20, 104, 138)} fill="#E0A060" opacity={0.18} filter="url(#cglow)" />}
              <path d={arch(x, y, 64, 98)} fill={on ? 'url(#cwin)' : '#1F1812'} opacity={on && !labWin && fl === 1 ? 0.6 : 1} />
              {on && !labWin && <path d={`M ${x + 32} ${y + 4} L ${x + 32} ${y + 98} M ${x} ${y + 56} L ${x + 64} ${y + 56}`} stroke="#2A1A0E" strokeWidth={5} />}
            </g>
          );
        }))}
        {/* 门 */}
        <rect x={884} y={560} width={152} height={26} fill="#1A120B" />
        <path d={arch(918, 596, 84, 174)} fill="#1E140C" />
        <rect x={0} y={770} width={1920} height={310} fill="#0E0906" />
        <ellipse cx={1086} cy={772} rx={220} ry={24} fill="#E0A060" opacity={0.08} filter="url(#cglow)" />
      </svg>
      {/* 窗里的实验室：缩到 1/30，正好窗宽；上面接一段墙、下面接一段地，填满整扇拱窗，不露窗的底色 */}
      <div style={{position: 'absolute', left: WIN.x, top: WIN.y, width: WIN.w, height: WIN.h, overflow: 'hidden',
        clipPath: `path('${arch(0, 0, WIN.w, WIN.h)}')`}}>
        <div style={{position: 'absolute', left: 0, top: WC.y - WIN.y - 540 / ZEND - 1500 / ZEND, width: 1920, height: 4080,
          transformOrigin: '0 0', transform: `scale(${1 / ZEND})`, background: 'linear-gradient(180deg, #120C08 0%, #1C130C 36.8%, #0A0705 63.2%, #050403 100%)'}}>
          <div style={{position: 'absolute', left: 0, top: 1500, width: 1920, height: 1080}}>{lab}</div>
        </div>
      </div>
    </>
  );
};

export const ExpLook: React.FC = () => {
  const f = useCurrentFrame();
  // 一镜到底：0–30 帧慢慢推近到 1.35 倍（ease-in），30–40 帧加速穿过窗（放大到 30 倍），窗的中心同时移到画面中心
  const zA = 1 + 0.35 * Easing.in(Easing.quad)(Math.min(1, f / EX.enter));
  const tB = Math.max(0, Math.min(1, (f - EX.enter) / (CUT - 1 - EX.enter)));
  const zB = Math.pow(ZEND / 1.35, Easing.in(Easing.cubic)(tB));
  const bz = zA * zB;
  const ub = Math.log(bz) / Math.log(ZEND);
  const Fx = WC.x - (1 - ub) * (WC.x - 960) / bz, Fy = WC.y - (1 - ub) * (WC.y - 540) / bz;
  // 显示器
  const kOn = f - EX.on;
  const crt = kOn < 0 ? 0 : Math.min(1, (kOn + 1) / 3);
  const lineFlash = kOn >= 0 && kOn < 4 ? 1 - kOn / 4 : 0;
  const scan = 1 - lin(f, EX.push[1] - 6, EX.push[1]);
  const corner = 1 - lin(f, EX.push[1] - 4, EX.push[1]);
  const u = lin(f, EX.push[0], EX.push[1], 0, 1, Easing.inOut(Easing.cubic));
  const Z = 1920 / SCREEN.w;
  const z = Math.pow(Z, u);
  const sc = {x: SCREEN.x + SCREEN.w / 2, y: SCREEN.y + SCREEN.h / 2};
  const fx = sc.x - (1 - u) * (sc.x - 960) / z;
  const fy = sc.y - (1 - u) * (sc.y - 540) / z;
  const lab = <Lab f={f} crt={crt} lineFlash={lineFlash} scan={scan} corner={corner} />;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {f < CUT ? (
        <div style={{position: 'absolute', inset: 0, transformOrigin: '0 0', transform: `translate(${960 - bz * Fx}px, ${540 - bz * Fy}px) scale(${bz})`}}>
          <Campus f={f} lab={lab} />
        </div>
      ) : (
        <div style={{position: 'absolute', inset: 0, transformOrigin: '0 0', transform: `translate(${960 - z * fx}px, ${540 - z * fy}px) scale(${z})`}}>
          {lab}
        </div>
      )}
      {/* 字：全片同一行，宋体，原地换；前一句收完，后一句才出来 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 840, height: 240, background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.65))'}} />
      <div lang="zh-Hans" style={{position: 'absolute', left: 0, right: 0, top: LOOK_LINE_TOP, textAlign: 'center', fontFamily: L.serif,
        fontSize: LINE_SIZE, color: L.ink, textShadow: '0 2px 18px rgba(0,0,0,0.95)'}}>
        {f < LINE1_EXIT + 6 && <div style={{position: 'absolute', left: 0, right: 0}}>
          <Wipe at={1} exitAt={LINE1_EXIT} style={{fontWeight: 400}}>2006 年，</Wipe>
          <Wipe at={4} exitAt={LINE1_EXIT} style={{fontWeight: 700}}>埃默里大学</Wipe>
        </div>}
        {f >= LINE2_AT - 1 && <div style={{position: 'absolute', left: 0, right: 0}}>
          <Wipe at={LINE2_AT} exitAt={EX.push[1] - 8} style={{fontWeight: 700}}>真的</Wipe>
          <Wipe at={LINE2_AT + 2} exitAt={EX.push[1] - 8} style={{fontWeight: 400}}>做过这个实验。</Wipe>
        </div>}
      </div>
      <Grain f={f} />
    </AbsoluteFill>
  );
};
