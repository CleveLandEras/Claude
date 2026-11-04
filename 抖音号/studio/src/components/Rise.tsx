import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// 字从一道看不见的缝里升上来（不是淡入）。at <= 0 时第一帧就是完整的。
// perChar：逐字错开升起；exitAt：往上收走。
export const Rise: React.FC<{
  at: number;
  exitAt?: number;
  perChar?: number;
  style?: React.CSSProperties;
  children: string;
}> = ({at, exitAt, perChar = 0, style, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = exitAt === undefined ? 0
    : interpolate(frame, [exitAt, exitAt + 10], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic),
    });
  if (out >= 1) return null;
  const chars = perChar ? Array.from(children) : [children];
  return (
    <span style={{display: 'inline-block', whiteSpace: 'pre', ...style}}>
      {chars.map((ch, i) => {
        const p = at <= 0 ? 1 : spring({
          frame: frame - at - i * perChar, fps, config: {damping: 200, stiffness: 140, mass: 0.8},
        });
        return (
          <span key={i} style={{display: 'inline-block', overflow: 'hidden', paddingBottom: '0.12em',
            marginBottom: '-0.12em', verticalAlign: 'top'}}>
            <span style={{
              display: 'inline-block',
              transform: `translateY(${(1 - p) * 105 - out * 60}%)`,
              filter: `blur(${(1 - p) * 6 + out * 6}px)`,
              opacity: Math.min(1, p * 1.4) * (1 - out),
            }}>
              {ch}
            </span>
          </span>
        );
      })}
    </span>
  );
};

// 一根从左往右画出来的细线
export const Draw: React.FC<{at: number; width: number; color: string; thick?: number; style?: React.CSSProperties}> = (
  {at, width, color, thick = 2, style},
) => {
  const frame = useCurrentFrame();
  const k = at <= 0 ? 1 : interpolate(frame, [at, at + 14], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });
  return <div style={{width: width * k, height: thick, background: color, ...style}} />;
};
