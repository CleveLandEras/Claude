// 《等待》开头 0–7 秒（第七次）。前 4 秒要同时做到三件事：留住、给理由（一个反常识的兑现）、落到“你”；
// 并满足剪辑认知第 22 条的七条。分镜和理由见 videos/001_等待/分镜_开头_v7.md。
//   两张大卡从头到尾占满画面、不缩小；电只发生在当前那张卡里；卡片下方只有一行字，原地依次换成：
//   “你选哪个？” → “32 人里，9 人选了 A” → “只为少等 18 秒，近三成的人宁可更疼。”（实验里没有“马上”，那 9 人也等了 9 秒，所以不说“不想等”）
// 事实（Berns 等，2006，《科学》）：32 人里 9 人（28%）宁可更强的电也要早点来；典型选项是 9 秒后 60% 强度 vs 27 秒后 30% 强度。
// 卡片写“早点 / 晚点”，和实验的真实条件一致。
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame} from 'remotion';
import {Glass} from '../../components/Glass';
import {Rise} from '../../components/Rise';
import {S as Sans} from '../../style';
import full from './full.json';
import {Arcs, Bolt} from './Opening';

const OP = full.opening;
const INK = '#F4F6FB';
const SOFT = 'rgba(214,220,236,0.8)';
const MUTE = 'rgba(190,198,220,0.55)';
const TIME = '#8CC8FF';
const RED = '#FF5A4E';
const FONT = Sans.sans;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const W = 860;
const H = 640;
const CY = 430;
const A_X = 500;
const B_X = 1420;
const ICON_Y = 380;           // 卡片里图标的中心（卡片自己的坐标）

const shake = (f: number, at: number, amp: number, seed: string) => {
  const k = f - at;
  if (k < 0 || k > 14) return {x: 0, y: 0};
  const a = amp * Math.exp(-k / 3);
  return {x: (random(`${seed}x${f}`) - 0.5) * 2 * a, y: (random(`${seed}y${f}`) - 0.5) * 2 * a};
};

// 卡片标题：一行，带“你”，84 像素（手机上约 17 像素），最长的“等一会儿电你，轻”也不出卡片
const Title: React.FC<{letter: string; time: string; rest: string; strong: string}> = ({letter, time, rest, strong}) => (
  <div style={{position: 'absolute', left: 52, top: 46, display: 'flex', alignItems: 'baseline', gap: 18, fontFamily: FONT,
    whiteSpace: 'nowrap'}}>
    <span style={{fontSize: 100, fontWeight: 700, color: INK, lineHeight: 1}}>{letter}</span>
    <span style={{fontSize: 92, color: SOFT, lineHeight: 1}}>
      <span style={{color: TIME}}>{time}</span>{rest}<span style={{color: INK, fontWeight: 700}}>{strong}</span>
    </span>
  </div>
);

// offset：整条里开头分两段用同一个组件（先给选项和问题；插进埃默里大学的实验两格；再回来给结果），第二段从中间接着播
export const Hook: React.FC<{offset?: number}> = ({offset = 0}) => {
  const f = useCurrentFrame() + offset;
  const settle = 0.97 + 0.03 * spring({frame: f + 2, fps: 30, config: {damping: 20, stiffness: 200}});

  // A：马上，重。整张卡闪白、猛抖，闪电劈下来
  const kA = f - OP.aStrike;
  const whiteA = kA >= 0 ? [0.85, 0.6, 0.35, 0.18, 0.06][kA] ?? 0 : 0;
  const sa = shake(f, OP.aStrike, 18, 'a');
  const flashA = kA >= 0 ? Math.exp(-kA / 4) : 0;

  // B：晚点，轻。计时圈里倒数 3、2、1（每个数 0.5 秒，号主：这个对留存很重要，必须留），走到头整卡淡淡闪一下
  const [b0, b1] = OP.bSweep;
  const idx = OP.count.findIndex((c0, i) => f >= c0 && f < (OP.count[i + 1] ?? b1));
  const counting = f >= OP.count[0] && f < b1;
  const digit = counting ? String(3 - idx) : '';
  const pop = counting ? interpolate(f - OP.count[idx], [0, 6], [1.18, 1], {...clamp, easing: Easing.out(Easing.cubic)}) : 1;
  const kB = f - b1;
  const sb = shake(f, b1, 4, 'b');
  const flashB = kB >= 0 ? 0.5 * Math.exp(-kB / 3) : 0;
  const whiteB = kB >= 0 ? [0.32, 0.24, 0.16, 0.1, 0.05, 0.02][kB] ?? 0 : 0;
  const frac = f < b0 ? 1 : interpolate(f, [b0, b1], [1, 0], clamp);
  const R = 110;
  const c = 2 * Math.PI * R;

  // 结果那句读完以后，才点亮 A 框、压暗 B（一次只变一处，独立审片 10/28）
  const red = interpolate(f, [OP.markAt, OP.markAt + 8], [0, 1], clamp);

  const line = (at: number, exit: number | undefined, children: React.ReactNode) => (
    <div style={{position: 'absolute', left: 0, right: 0}}>{f >= at - 1 && (exit === undefined || f < exit + 12) ? children : null}</div>
  );

  return (
    <AbsoluteFill style={{background: '#000'}}>
      <div style={{position: 'absolute', left: 160, top: 80, width: 1600, height: 760, borderRadius: '50%', filter: 'blur(80px)',
        background: `radial-gradient(ellipse, rgba(40,80,200,${0.14 + 0.12 * flashA}), rgba(0,0,0,0) 62%)`}} />
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs><filter id="boltGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="16" /></filter></defs>
      </svg>

      {/* A */}
      <div style={{position: 'absolute', left: A_X - W / 2 + sa.x, top: CY - H / 2 + sa.y, width: W, height: H,
        transform: `scale(${settle})`}}>
        <Glass r={{x: 0, y: 0, w: W, h: H}} radius={48} glow={flashA * 0.8} />
        {red > 0 && <div style={{position: 'absolute', inset: -3, borderRadius: 50, border: `5px solid ${RED}`, opacity: red,
          boxShadow: `0 0 30px rgba(255,90,78,${0.5 * red})`}} />}
        <Title letter="A" time="早点" rest="电你，" strong="重" />
        <svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
          <Arcs cx={W / 2} cy={ICON_Y} size={1.6} k={kA} seed="hookA" />
          <Bolt cx={W / 2} cy={ICON_Y} h={300} flash={flashA} id="hookA" />
        </svg>
        {whiteA > 0 && <div style={{position: 'absolute', inset: 0, borderRadius: 48, background: '#F4F9FF', opacity: whiteA}} />}
      </div>

      {/* B */}
      <div style={{position: 'absolute', left: B_X - W / 2 + sb.x, top: CY - H / 2 + sb.y, width: W, height: H,
        transform: `scale(${settle})`, opacity: 1 - 0.45 * red}}>
        <Glass r={{x: 0, y: 0, w: W, h: H}} radius={48} glow={flashB * 0.5} />
        <Title letter="B" time="晚点" rest="电你，" strong="轻" />
        <svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
          <circle cx={300} cy={ICON_Y} r={R} fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.14)" strokeWidth={8} />
          {frac > 0.001 && (
            <circle cx={300} cy={ICON_Y} r={R} fill="none" stroke={TIME} strokeWidth={8} strokeLinecap="round"
              strokeDasharray={`${c * frac} ${c}`} transform={`rotate(-90 300 ${ICON_Y})`}
              style={{filter: `drop-shadow(0 0 10px ${TIME})`}} />
          )}
          <Arcs cx={620} cy={ICON_Y} size={0.45} k={kB} seed="hookB" />
          <Bolt cx={620} cy={ICON_Y} h={140} flash={flashB} id="hookB" />
        </svg>
        <div style={{position: 'absolute', left: 300 - 120, top: ICON_Y - 62, width: 240, textAlign: 'center', fontFamily: FONT,
          fontSize: 110, fontWeight: 300, color: INK, lineHeight: 1, transform: `scale(${pop})`}}>{digit}</div>
        {whiteB > 0 && <div style={{position: 'absolute', inset: 0, borderRadius: 48, background: '#F4F9FF', opacity: whiteB}} />}
      </div>

      {/* 卡片下方只有一行字，原地依次换 */}
      <div style={{position: 'absolute', left: 0, right: 0, top: CY + H / 2 + 40, textAlign: 'center', fontFamily: FONT,
        fontSize: 88, color: INK}}>
        {line(OP.askAt, OP.resultAt - 4, <>
          <Rise at={-offset + OP.askAt} perChar={2} exitAt={-offset + OP.resultAt - 4} style={{fontWeight: 400}}>你选</Rise>
          <Rise at={-offset + OP.askAt + 4} perChar={2} exitAt={-offset + OP.resultAt - 4} style={{fontWeight: 700}}>哪个？</Rise>
        </>)}
        {line(OP.resultAt, OP.punchAt - 4, <>
          <Rise at={-offset + OP.resultAt} perChar={1.5} exitAt={-offset + OP.punchAt - 4} style={{fontWeight: 400}}>32 人里，</Rise>
          <Rise at={-offset + OP.resultAt + 8} perChar={1.5} exitAt={-offset + OP.punchAt - 4} style={{fontWeight: 700, color: RED}}>9 人选了 A</Rise>
        </>)}
        {line(OP.punchAt, undefined, <>
          <Rise at={-offset + OP.punchAt} perChar={1.5} style={{fontWeight: 400, fontSize: 78}}>只为少等 </Rise>
          <Rise at={-offset + OP.punchAt + 6} perChar={1.5} style={{fontWeight: 700, fontSize: 78, color: TIME}}>18 秒</Rise>
          <Rise at={-offset + OP.punchAt + 12} perChar={1.5} style={{fontWeight: 400, fontSize: 78}}>，近三成的人</Rise>
          <Rise at={-offset + OP.punchAt + 22} perChar={1.5} style={{fontWeight: 700, fontSize: 78, color: RED}}>宁可更疼</Rise>
          <Rise at={-offset + OP.punchAt + 28} style={{fontWeight: 700, fontSize: 78}}>。</Rise>
        </>)}
      </div>
      {f >= OP.punchAt + 10 && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1024, textAlign: 'center', fontFamily: FONT, fontSize: 26,
          color: MUTE, letterSpacing: '0.04em'}}>
          <Rise at={-offset + OP.punchAt + 10}>埃默里大学 Berns 等，2006，《科学》｜32 人，典型选项是“9 秒后强电”对“27 秒后弱电”</Rise>
        </div>
      )}
    </AbsoluteFill>
  );
};
