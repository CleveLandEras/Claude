import {blue, U} from '../style';

export type Rect = {x: number; y: number; w: number; h: number};

export const lerpRect = (a: Rect, b: Rect, t: number): Rect => ({
  x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, w: a.w + (b.w - a.w) * t, h: a.h + (b.h - a.h) * t,
});

// 毛玻璃卡片：深色里透一点亮，细亮边上亮下暗，外面一圈柔和的影子；glow>0 时边缘泛蓝光
export const Glass: React.FC<{r: Rect; radius?: number; glow?: number; children?: React.ReactNode}> = (
  {r, radius = 44, glow = 0, children},
) => (
  <div style={{
    position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h,
    borderRadius: Math.min(radius, r.h / 2),
    border: '1.5px solid transparent',
    background: [
      'linear-gradient(180deg, rgba(22,24,32,0.96), rgba(9,10,14,0.98)) padding-box',
      `linear-gradient(170deg, rgba(255,255,255,${0.62 + glow * 0.3}), rgba(255,255,255,0.10) 38%, rgba(255,255,255,0.05) 62%, rgba(150,180,255,${0.32 + glow * 0.5})) border-box`,
    ].join(', '),
    boxShadow: [
      '0 40px 120px rgba(0,0,0,0.9)',
      `0 0 ${50 + glow * 60}px rgba(70,140,255,${0.08 + glow * 0.35})`,
      'inset 0 1px 0 rgba(255,255,255,0.10)',
      `inset 0 0 80px rgba(90,130,255,${0.05 + glow * 0.12})`,
    ].join(', '),
    overflow: 'hidden',
  }}>
    {children}
  </div>
);

// 点阵：圆角小方块，暗的时候是浅浅的槽，亮的时候按列从靛蓝渐到青，再叠一层模糊过的光
export const Matrix: React.FC<{
  x: number; y: number; cols: number; rows: number; cell: number; gap: number;
  level: (c: number, r: number) => number;
  white?: (c: number, r: number) => number;
}> = ({x, y, cols, rows, cell, gap, level, white}) => {
  const w = cols * cell + (cols - 1) * gap;
  const h = rows * cell + (rows - 1) * gap;
  const cells: {c: number; r: number; v: number; wh: number}[] = [];
  for (let c = 0; c < cols; c++) {
    for (let r = 0; r < rows; r++) {
      cells.push({c, r, v: Math.max(0, Math.min(1, level(c, r))), wh: white ? Math.max(0, Math.min(1, white(c, r))) : 0});
    }
  }
  const color = (c: number, v: number, wh: number, base: number) => {
    const [R, G, B] = blue(cols > 1 ? c / (cols - 1) : 1);
    const mix = (k: number) => Math.round(k + (255 - k) * wh * 0.8);
    return `rgba(${mix(R)},${mix(G)},${mix(B)},${base + (1 - base) * v})`;
  };
  const draw = (lit: boolean) => cells
    .filter((q) => !lit || q.v > 0.15)
    .map((q) => (
      <rect key={`${q.c}-${q.r}`} x={q.c * (cell + gap)} y={q.r * (cell + gap)} width={cell} height={cell}
        rx={cell * 0.26} fill={lit ? color(q.c, q.v, q.wh, 0) : q.v < 0.02 ? 'rgba(120,130,210,0.10)' : color(q.c, q.v, q.wh, 0.08)} />
    ));
  return (
    <>
      <svg width={w} height={h} style={{position: 'absolute', left: x, top: y, overflow: 'visible',
        filter: `blur(${cell * 0.55}px)`, opacity: 0.95, mixBlendMode: 'screen'}}>{draw(true)}</svg>
      <svg width={w} height={h} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>{draw(false)}</svg>
    </>
  );
};

// 红点：正在等的你。实心的芯 + 一圈模糊过的红光
export const RedDot: React.FC<{x: number; y: number; size?: number; opacity?: number}> = (
  {x, y, size = 18, opacity = 1},
) => (
  <>
    <div style={{position: 'absolute', left: x - size * 2, top: y - size * 2, width: size * 4, height: size * 4,
      borderRadius: '50%', background: `radial-gradient(circle, rgba(255,75,62,${0.55 * opacity}), rgba(255,75,62,0) 65%)`,
      filter: 'blur(4px)'}} />
    <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size,
      borderRadius: '50%', opacity,
      background: `radial-gradient(circle at 40% 35%, #FFE9E4 0%, #FF8A7C 35%, ${U.red} 70%)`}} />
  </>
);
