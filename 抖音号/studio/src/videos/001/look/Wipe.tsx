// 观感样片的字幕动效。
// 第三版评审（10/28）：后半句一出现整行就往左跳，是因为没出场的字不占位置。现在每段字从第一帧起就占好位置（透明），
// 只动透明度和上下位置：8 帧内从下方 24 像素升到原位，曲线 cubic-bezier(0.2, 0.8, 0.2, 1)；不用硬遮罩、不改字距（改字距也会让整行横移）。
// pop：关键词从 1.04 倍缩回原大；glow：带一圈外发光，24 帧内衰减。退场：4 帧淡出。
import {Easing, interpolate, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(0.2, 0.8, 0.2, 1);

export const Wipe: React.FC<{at: number; exitAt?: number; children: string; style?: React.CSSProperties; pop?: boolean; glow?: string;
  fast?: boolean}> = ({at, exitAt, children, style, pop, glow, fast}) => {
  const f = useCurrentFrame();
  const len = fast ? 2 : 8;
  const p = interpolate(f, [at, at + len], [0, 1], {...clamp, easing: ease});
  const out = exitAt === undefined ? 0 : interpolate(f, [exitAt, exitAt + 4], [0, 1], clamp);
  const sc = pop ? interpolate(f, [at, at + 6], [1.04, 1], {...clamp, easing: Easing.out(Easing.cubic)}) : 1;
  const g = glow ? interpolate(f, [at, at + 24], [1, 0], clamp) : 0;
  return (
    <span style={{display: 'inline-block', whiteSpace: 'pre', opacity: f < at ? 0 : p * (1 - out),
      transform: `translateY(${(1 - p) * 24}px) scale(${sc})`, transformOrigin: '50% 80%',
      ...style, textShadow: g > 0 ? `0 0 ${12 * g}px ${glow}, 0 0 ${24 * g}px ${glow}, 0 2px 18px rgba(0,0,0,0.95)` : style?.textShadow}}>
      {children}
    </span>
  );
};
