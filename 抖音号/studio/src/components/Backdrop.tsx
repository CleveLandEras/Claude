import {AbsoluteFill, Img, random, staticFile, useCurrentFrame} from 'remotion';
import {C} from '../style';

const DUST = Array.from({length: 150}, (_, i) => {
  const z = [0.35, 0.65, 1][i % 3];
  return {
    x: random(`dx${i}`) * 2100 - 90,
    y: random(`dy${i}`) * 1200 - 60,
    r: (0.5 + random(`dr${i}`) * 1.3) * (0.6 + z),
    a: (0.12 + random(`da${i}`) * 0.4) * z,
    vx: (0.06 + random(`dv${i}`) * 0.16) * z,
    vy: -(0.03 + random(`dw${i}`) * 0.08) * z,
    tw: random(`dt${i}`) * Math.PI * 2,
    z,
  };
});

// 底色、光池、星尘（三层景深，跟着镜头有视差）
export const Backdrop: React.FC<{camX: number; camY: number; light?: number}> = ({camX, camY, light = 0}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 72% 62% at 64% 50%, ${C.pool} 0%, rgba(20,25,37,0) 72%)`,
          opacity: 0.9 + light * 0.6,
        }}
      />
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {DUST.map((d, i) => {
          const x = ((d.x + d.vx * frame + camX * d.z * 0.6) % 2100 + 2100) % 2100 - 90;
          const y = ((d.y + d.vy * frame + camY * d.z * 0.6) % 1200 + 1200) % 1200 - 60;
          const tw = 0.75 + 0.25 * Math.sin(frame * 0.07 + d.tw);
          return <circle key={i} cx={x} cy={y} r={d.r} fill={C.ink} opacity={d.a * tw} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};

// 胶片颗粒 + 暗角，盖在最上面
export const Film: React.FC = () => {
  const frame = useCurrentFrame();
  const ox = Math.round(random(`gx${frame}`) * 40 - 20);
  const oy = Math.round(random(`gy${frame}`) * 40 - 20);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <Img
        src={staticFile(`grain/g${frame % 6}.png`)}
        style={{
          position: 'absolute', left: -40 + ox, top: -40 + oy, width: 2000, height: 1160,
          opacity: 0.06, mixBlendMode: 'screen',
        }}
      />
      <AbsoluteFill
        style={{background: 'radial-gradient(ellipse 85% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.62) 100%)'}}
      />
    </AbsoluteFill>
  );
};
