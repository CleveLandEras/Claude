import {random, useCurrentFrame} from 'remotion';
import {C} from '../style';

export type Strike = {f: number; s: number};

// 最近一次电击，以及它过去了几帧
export const lastStrike = (frame: number, strikes: Strike[]) => {
  let last: Strike | null = null;
  for (const st of strikes) if (st.f <= frame) last = st;
  return last ? {...last, k: frame - last.f} : null;
};

// 这一帧电击的亮度（0–s），给背景和镜头抖动用
export const flashOf = (frame: number, strikes: Strike[]) => {
  const l = lastStrike(frame, strikes);
  return l && l.k < 12 ? l.s * Math.exp(-l.k / 2.6) : 0;
};

const ray = (x: number, y: number, ang: number, len: number, jag: number, seed: string) => {
  const pts: string[] = [];
  const n = 7;
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const off = i === 0 ? 0 : (random(`${seed}-${i}`) - 0.5) * 2 * jag * (1 - t * 0.4);
    const px = x + Math.cos(ang) * len * t - Math.sin(ang) * off;
    const py = y + Math.sin(ang) * len * t + Math.cos(ang) * off;
    pts.push(`${px.toFixed(1)},${py.toFixed(1)}`);
  }
  return pts.join(' ');
};

// 电极：平时是一个小圆环；被电的那几帧，几道折线从它这里炸开，四周被照亮
export const Spark: React.FC<{x: number; y: number; strikes: Strike[]}> = ({x, y, strikes}) => {
  const frame = useCurrentFrame();
  const l = lastStrike(frame, strikes);
  const live = l && l.k < 12 ? l : null;
  const flash = live ? live.s * Math.exp(-live.k / 2.6) : 0;
  const showBolt = live && [0, 1, 2, 4].includes(live.k);
  const rays = live ? Math.round(3 + live.s * 2) : 0;
  const R = 520 * Math.min(1.4, 0.45 + (live?.s ?? 0) * 0.6);
  return (
    <>
      {flash > 0.01 && (
        <div style={{
          position: 'absolute', left: x - R / 2, top: y - R / 2, width: R, height: R, borderRadius: '50%',
          background: `radial-gradient(circle, rgba(238,245,255,${0.42 * Math.min(1, flash)}) 0%, rgba(200,220,255,${0.12 * Math.min(1, flash)}) 28%, rgba(0,0,0,0) 62%)`,
        }} />
      )}
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        {showBolt && live && Array.from({length: rays}, (_, i) => {
          const seed = `b${live.f}-${live.k}-${i}`;
          const ang = (i / rays) * Math.PI * 2 + random(`${seed}-a`) * 0.9;
          const len = (48 + random(`${seed}-l`) * 70) * (0.55 + live.s * 0.55);
          const pts = ray(x, y, ang, len, 9 * live.s + 4, seed);
          return (
            <g key={i}>
              <polyline points={pts} fill="none" stroke={C.spark} strokeOpacity={0.16} strokeWidth={7 * live.s + 2}
                strokeLinejoin="round" />
              <polyline points={pts} fill="none" stroke={C.spark} strokeWidth={1.4 + live.s * 1.2}
                strokeLinejoin="round" />
            </g>
          );
        })}
        <circle cx={x} cy={y} r={8} fill={flash > 0.3 ? C.spark : C.bg} stroke={C.ink} strokeOpacity={0.85}
          strokeWidth={1.5} />
        <circle cx={x} cy={y} r={2.5} fill={C.ink} />
      </svg>
    </>
  );
};
