// 《等待》开头的观感样片版（videos/001_等待/观感对照.md）。时间、顺序、字和 Hook.tsx 完全一样（节奏已锁定），只换画面。
// 一整幅房间，中间一道隔墙分成 A、B 两半，地面铺到画面底部，人约占画高 55%。
// 第四版（七维度评审第二轮 10/28，5.9 分）：
//   A：0.8 秒肩先往上一提（预备）；0.9 秒冷光在人身后炸开，人后弓、头后仰，原地左右抖 10 帧、每抖一次幅度乘 0.6（椅子不动）；
//      之后慢慢塌下去、低着头，一直保持到最后。指针甩到满格，红区亮起——全片红色第一次出现。
//   B：钟上每跳一下，人的肩就往上提一点、头往钟那边转一点，一路绷紧；电下去时只在手腕附近冒火花、钟面只吃一点冷光。
//   “9 人选了 A”：9 间房的 A 半边依次冷光一闪再变红（每间隔 80 毫秒，像在数）；红用颜色混合，不经过紫色。
//   “宁可更疼”：A 的电极放出一圈红色脉冲扩满半边，灯过曝两帧，指针再打进红区；这四个字两帧内整个出现，带一圈红光。
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import full from '../full.json';
import {LINE_SIZE} from '../Hook';
import {ELEC, Grain, L, MiniCell, Room} from './Room';
import {Wipe} from './Wipe';

const OP = full.opening;
const GR = full.grid;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const HALF = 952;          // 每一半的宽；中间 16 像素是隔墙
const B_LEFT = 968;
const S = 1.55;
const FIG_Y = 648;         // 坐面上沿；地面在 FIG_Y + 150 * S = 880
const FLOOR = 880;
const A_FIG_X = 400;
export const LOOK_LINE_TOP = 896;
// 32 间房：8×4，每间 200×112.5，间隔 16；原来那一间是第 2 行第 4 列（编号 11，它也是选了 A 的 9 间之一）
const CW = 200, CH = 112.5, GAP = 16, X0 = 104, Y0 = 221, HOME = 11;
const cellXY = (i: number) => ({x: X0 + (i % 8) * (CW + GAP), y: Y0 + Math.floor(i / 8) * (CH + GAP)});
const ORDER = Array.from({length: 32}, (_, i) => i).sort((a, b) => random(`ord${a}`) - random(`ord${b}`));
const PUNCH_HIT = OP.punchAt + 22;           // “宁可更疼”出来的那一帧

const shake = (f: number, at: number, amp: number, seed: string, len = 6) => {
  const k = f - at;
  if (k < 0 || k > len) return {x: 0, y: 0};
  const a = amp * Math.exp(-k / 2);
  return {x: (random(`${seed}x${f}`) - 0.5) * 2 * a, y: (random(`${seed}y${f}`) - 0.5) * 2 * a};
};

// 每一半左上角的标题：一行宋体，“早点 / 晚点”用灯光的琥珀色
const Title: React.FC<{left: number; letter: string; time: string; strong: string}> = ({left, letter, time, strong}) => (
  <div lang="zh-Hans" style={{position: 'absolute', left, top: 64, display: 'flex', alignItems: 'baseline', gap: 18, fontFamily: L.serif,
    whiteSpace: 'nowrap', color: L.ink, textShadow: '0 2px 20px rgba(0,0,0,0.95)'}}>
    <span style={{fontSize: 100, fontWeight: 700, lineHeight: 1}}>{letter}</span>
    <span style={{fontSize: 90, lineHeight: 1}}>
      <span style={{color: L.amber}}>{time}</span>电你，<span style={{fontWeight: 700}}>{strong}</span>
    </span>
  </div>
);

export const HookLook: React.FC<{offset?: number; at?: number}> = ({offset = 0, at}) => {
  const local = useCurrentFrame();
  const bare = at !== undefined;
  const f = bare ? at : local + offset;
  const segLen = offset === 0 ? OP.p1End : OP.p2End - OP.p2Start;
  const cam = bare ? 1 : 1 + 0.07 * Math.min(1, local / segLen);       // 匀速慢推，一段一共 7%，到段尾也不停
  const p2 = offset > 0 && !bare;

  // A：早点、重
  const kA = f - OP.aStrike;
  const pulses = kA < 0 ? OP.charge.filter((a) => f >= a - 6 && f < a).map((a) => (f - (a - 6)) / 6) : [];
  const zap = kA < 0 && (OP.charge.includes(f) || OP.charge.includes(f - 1));
  const chargeA = kA < 0 ? 0.15 + 0.7 * (f / OP.aStrike) ** 2 : 0;
  const kP = p2 ? f - PUNCH_HIT : -1;                                   // “宁可更疼”之后第几帧
  // 灯：电下去的 3 帧变冷，第 4 帧跳闸，然后亮 2 帧、四成 2 帧，闪三下；“宁可更疼”时过曝两帧
  const lampA = kP >= 0 && kP < 2 ? 1.6
    : kA < 0 ? (zap ? 0.86 : 1) : kA <= 2 ? 1.3 : kA === 3 ? 0 : kA < 16 ? (Math.floor((kA - 4) / 2) % 2 === 0 ? 1 : 0.4) : 1;
  const coldA = kA < 0 ? 0 : kA <= 2 ? 1 : kA === 3 ? 0.5 : 0;
  // 身体：预备（肩往上一提）→ 后弓、头后仰、原地抖 → 慢慢塌下去、低头，一直保持
  const slump = kA < 10 ? 0 : Easing.out(Easing.cubic)(Math.min(1, (kA - 10) / 15));
  const leanA = kA < 0 ? 0 : kA < 10 ? 6 * Math.pow(0.85, kA) : -4 * slump;
  const lookA = kA < 0 ? 0 : kA < 10 ? -10 * Math.pow(0.8, kA) : 9 * slump;
  const breathA = kA >= -3 && kA < 0 ? -2.6 : kA >= 10 ? 3 * slump : 0;
  const jitAmp = kA >= 0 && kA < 10 ? 3.9 * Math.pow(0.6, Math.floor(kA / 2)) : kP >= 0 && kP < 4 ? 1.5 : 0;
  const jitA = {x: (Math.floor(Math.max(0, kA) / 2) % 2 === 0 ? 1 : -1) * jitAmp, y: jitAmp * 0.3};
  const hopA = kA < 0 ? 0 : ([4, 6, 2][kA] ?? 0);
  const swingA = kA < 0 ? 0 : 7 * Math.exp(-kA / 22) * Math.sin(kA / 4.5);
  const dialA = (kA < 0 ? 0.08 : kA === 0 ? 0.6 : kA === 1 ? 1.04 : kA === 2 ? 1.02 : 1)
    + (kA > 3 ? 0.013 * Math.sin((f / 30) * Math.PI * 2 * 7) : 0);   // 电过以后指针一直在满格附近微微抖
  const hotA = Math.max(kA < 0 ? 0 : kA <= 10 ? 1 : Math.max(0, 1 - (kA - 10) / 10), kP >= 0 ? Math.max(0, 1 - kP / 14) : 0);
  const sa = shake(f, OP.aStrike, 4, 'a', 4);

  // B：晚点、轻
  const [, b1] = OP.bSweep;
  const kB = f - b1;
  const idx = OP.count.findIndex((c0, i) => f >= c0 && f < (OP.count[i + 1] ?? b1));
  const counting = f >= OP.count[0] && f < b1;
  const digit = f < OP.count[0] ? '3' : counting ? String(3 - idx) : '';
  const steps = OP.count.filter((c0) => f >= c0).length;
  const sinceTick = steps > 0 ? f - OP.count[steps - 1] : 99;
  // 秒针：每跳一下 2 帧到位，第 2 帧过冲 4°；数字竖向翻牌 3 帧
  const hand = steps === 0 ? 0 : sinceTick === 0 ? 30 * (steps - 1) + 15 : sinceTick === 1 ? 30 * steps + 4 : 30 * steps;
  const flip = steps > 1 && sinceTick < 3 ? Easing.out(Easing.cubic)((sinceTick + 1) / 3) : 1;
  const clockFlash = kB >= 0 && kB < 3 ? 0.2 - kB * 0.06 : 0;
  const clockDark = kB < 3 ? 0 : interpolate(kB, [3, 9], [0, 1], clamp);
  // 人：钟每跳一下，肩往上提一点、头往钟那边转一点，一路绷紧；电完以后慢慢松下来
  const stepEase = (n: number) => (n === 0 ? 0 : n - 1 + Easing.out(Easing.cubic)(Math.min(1, sinceTick / 4)));
  const wind = f < b1 ? stepEase(steps) : 3 * (1 - interpolate(f, [b1 + 4, b1 + 28], [0, 1], clamp));
  const tense = wind / 3;
  const breathB = -1.9 * wind;
  const lookB = -4 * wind;
  const leanB = kB >= 0 && kB < 3 ? 2 : 0;
  const jitB = {x: kB === 0 ? 1.5 : kB === 1 ? -1 : 0, y: 0};
  const lampB = kB < 0 ? 1 : ([1.1, 0.8, 1][kB] ?? 1);
  const coldB = kB >= 0 && kB <= 1 ? 0.3 : 0;
  const swingB = kB < 0 ? 0 : 1.5 * Math.exp(-kB / 15) * Math.sin(kB / 4);
  const dialB = kB < 0 ? 0.08 : kB === 0 ? 0.22 : kB === 1 ? 0.33 : 0.3;

  // 32 间房：拉远、一盏盏亮灯、9 间的 A 依次冷光一闪再变红、推回来
  const gOut = p2 ? interpolate(f, [GR.out, GR.out + GR.outLen], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)}) : 0;
  const gBack = p2 ? interpolate(f, [GR.back, GR.back + GR.backLen], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)}) : 0;
  const g = gOut * (1 - gBack);
  const gridCam = p2 ? 1 + 0.035 * interpolate(f, [GR.out, GR.back], [0, 1], clamp) * g : 1;
  const home = cellXY(HOME);
  const z = 1 + (CW / 1920 - 1) * g;
  const cx = 960 + (home.x + CW / 2 - 960) * g, cy = 540 + (home.y + CH / 2 - 540) * g;
  const nineAt = (i: number) => GR.nine + OP.picked.indexOf(i) * 2.4;
  const flashOf = (i: number) => {
    const k = f - nineAt(i);
    return p2 && k >= 0 && k < 3 ? 0.75 - k * 0.22 : 0;
  };
  const redOf = (i: number) => (p2 ? interpolate(f - nineAt(i), [3, 11], [0, 1], clamp) : 0);
  const homeRed = redOf(HOME) * (1 - 0.55 * gBack) * (1 + 0.08 * Math.sin((f / 30) * Math.PI * 2 * 0.8));   // 回来以后红光慢慢呼吸
  const dimB = p2 ? 0.45 * interpolate(f, [GR.nine, GR.nine + 8], [0, 1], clamp) : 0;
  // “宁可更疼”：红色脉冲从 A 的电极扩满半边
  const ring = kP >= 0 && kP < 14 ? Easing.out(Easing.cubic)(Math.min(1, kP / 10)) : -1;
  const wristA = {x: A_FIG_X + ELEC.x * S, y: FIG_Y + ELEC.y * S};   // 电极在脚背上

  const line = (a: number, exit: number | undefined, children: React.ReactNode) => (
    <div style={{position: 'absolute', left: 0, right: 0}}>{!bare && f >= a - 1 && (exit === undefined || f < exit + 6) ? children : null}</div>
  );

  return (
    <AbsoluteFill style={{background: '#050403'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${gridCam})`, transformOrigin: '960px 470px'}}>
        {/* 32 间房（拉远时才出现） */}
        {g > 0.001 && Array.from({length: 32}, (_, i) => {
          if (i === HOME) return null;
          const {x, y} = cellXY(i);
          const order = ORDER.indexOf(i);
          const on = interpolate(f, [GR.out + 2 + order * 0.4, GR.out + 5 + order * 0.4], [0, 1], clamp);
          const pick = OP.picked.includes(i);
          return (
            <div key={i} style={{position: 'absolute', left: x, top: y, opacity: g}}>
              <MiniCell w={CW} h={CH} on={on * (0.9 + 0.1 * Math.sin(f / 7 + i * 1.7))} seed={i} pick={pick ? redOf(i) : 0}
                flash={pick ? flashOf(i) : 0} dimA={pick ? 0 : dimB * 1.1} dimB={pick ? dimB * 1.1 : 0} />
            </div>
          );
        })}

        {/* 原来那一间：两半房间、隔墙、标题（拉远时一起缩成一格） */}
        <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0',
          transform: `translate(${cx - 960 * z}px, ${cy - 540 * z}px) scale(${z})`, overflow: 'hidden',
          borderRadius: g > 0.01 ? 3 / z : 0}}>
          <div style={{position: 'absolute', inset: 0, transform: `scale(${cam})`, transformOrigin: '960px 540px'}}>
            <div style={{position: 'absolute', left: 0, top: 0, width: HALF, height: 1080, overflow: 'hidden'}}>
              <div style={{position: 'absolute', inset: 0, transform: `translate(${sa.x}px, ${sa.y}px)`}}>
                <Room id="ra" w={HALF} h={1080} f={f} fig={{x: A_FIG_X, y: FIG_Y, s: S}} lamp={lampA} cold={coldA} swing={swingA}
                  charge={chargeA} pulses={pulses} zap={zap} dial={dialA} dialHot={hotA} lampDrop={30}
                  strike={kA >= 0 ? {k: kA, power: 1} : undefined} lean={leanA} look={lookA} breath={breathA} jit={jitA} hop={hopA} />
              </div>
              {ring >= 0 && (
                <svg width={HALF} height={1080} style={{position: 'absolute', inset: 0, mixBlendMode: 'screen'}}>
                  <circle cx={wristA.x} cy={wristA.y} r={40 + 1260 * ring} fill="none" stroke="#E2493B" strokeWidth={60 - 40 * ring}
                    opacity={0.3 * (1 - ring * 0.7)} />
                  <circle cx={wristA.x} cy={wristA.y} r={30 + 300 * ring} fill="#E2493B" opacity={0.18 * (1 - ring)} />
                </svg>
              )}
              {homeRed > 0 && <>
                <div style={{position: 'absolute', inset: 0, background: '#B8382C', opacity: 0.5 * homeRed, mixBlendMode: 'color'}} />
                <div style={{position: 'absolute', inset: 0, background: L.red, opacity: 0.1 * homeRed, mixBlendMode: 'screen'}} />
              </>}
              {flashOf(HOME) > 0 && <div style={{position: 'absolute', inset: 0, background: L.cold, opacity: flashOf(HOME) * 0.6}} />}
            </div>
            {/* 隔墙：立在地面上，两边各被自己那盏灯照亮一条边；地面在下面连成一片 */}
            <div style={{position: 'absolute', left: HALF, top: 0, width: B_LEFT - HALF, height: FLOOR,
              background: 'linear-gradient(90deg, #3A2818 0%, #0A0705 25%, #0A0705 75%, #3A2818 100%)'}} />
            <div style={{position: 'absolute', left: HALF, top: FLOOR, width: B_LEFT - HALF, height: 1080 - FLOOR, background: '#070504'}} />
            <div style={{position: 'absolute', left: B_LEFT, top: 0, width: HALF, height: 1080, overflow: 'hidden'}}>
              <Room id="rb" w={HALF} h={1080} f={f + 40} fig={{x: 330, y: FIG_Y, s: S}} lamp={lampB} cold={coldB} swing={swingB}
                dial={dialB} dialWarm charge={kB >= 0 && kB < 6 ? 0.5 : 0} tense={tense} breath={breathB} look={lookB}
                strike={kB >= 0 ? {k: kB, power: 0.33} : undefined} lean={leanB} jit={jitB} lampDrop={30}
                clock={{x: 600, y: 360, r: 80, digit, hand, flash: clockFlash, dark: clockDark, flip}} />
              {dimB > 0 && <div style={{position: 'absolute', inset: 0, background: '#000', opacity: dimB}} />}
            </div>
          </div>
          <Title left={96} letter="A" time="早点" strong="重" />
          <Title left={B_LEFT + 96} letter="B" time="晚点" strong="轻" />
        </div>
      </div>

      {/* 字幕区：一条渐暗的地面带；全片唯一的读字处，宋体。每段字从一开始就占好位置，出场不横跳 */}
      {!bare && <div style={{position: 'absolute', left: 0, right: 0, top: 840, height: 240,
        background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,0.65))'}} />}
      <div lang="zh-Hans" style={{position: 'absolute', left: 0, right: 0, top: LOOK_LINE_TOP, textAlign: 'center', fontFamily: L.serif,
        fontSize: LINE_SIZE, color: L.ink, textShadow: '0 2px 18px rgba(0,0,0,0.95)'}}>
        {offset === 0 && line(OP.askAt, undefined, <>
          <Wipe at={OP.askAt} style={{fontWeight: 400}}>你选</Wipe>
          <Wipe at={OP.askAt + 3} style={{fontWeight: 700}}>哪个？</Wipe>
        </>)}
        {offset > 0 && line(OP.resultAt, OP.punchAt - 10, <>
          <Wipe at={-offset + OP.resultAt} exitAt={-offset + OP.punchAt - 10} style={{fontWeight: 400}}>32 人里，</Wipe>
          <Wipe at={-offset + OP.resultAt + 8} exitAt={-offset + OP.punchAt - 10} pop style={{fontWeight: 700, color: L.red}}>9 人选了 A</Wipe>
        </>)}
        {/* 金句按原文核过（10/28）：9 个“极度害怕等待的人”宁可电得更重也要早点挨；选早的那边也要等几秒，所以是“不想多等” */}
        {offset > 0 && line(OP.punchAt, undefined, <>
          <Wipe at={-offset + OP.punchAt} style={{fontWeight: 400}}>近三成的人，</Wipe>
          <Wipe at={-offset + PUNCH_HIT} fast pop glow="#E2493B" style={{fontWeight: 700, color: L.red}}>宁可更疼</Wipe>
          <Wipe at={-offset + PUNCH_HIT + 8} style={{fontWeight: 400}}>，也不想多等。</Wipe>
        </>)}
      </div>
      {!bare && f >= OP.punchAt + 30 && (
        <div lang="zh-Hans" style={{position: 'absolute', left: 0, right: 0, top: 1008, textAlign: 'center', fontFamily: L.serif, fontSize: 25,
          color: L.mute, letterSpacing: '0.02em'}}>
          <Wipe at={-offset + OP.punchAt + 30}>出处：Berns 等，《科学》，2006｜32 人，电击左脚脚背；选项如「3 秒后 90%」对「27 秒后 60%」</Wipe>
        </div>
      )}
      {!bare && <Grain f={local} />}
    </AbsoluteFill>
  );
};
