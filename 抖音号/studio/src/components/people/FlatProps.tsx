// 画风 A 的道具：画成实物，不画成界面卡片。
// 规矩（调研第二节第 3 条）：有材料（木纹、绒布、纸、皮革），有重量（软阴影、稍微歪着放），
// 有结构（牌有厚度和圆角、筹码有边纹和侧面、牌桌有包边），不用一圈细亮边。
// 牌、筹码、牌桌在 Cards.tsx。
// 场景里的光（灯光、光斑、光锥）可以用柔光；道具和人本身只用平涂两层色。
import React, {useId} from 'react';
import {P, add, mixHex, smoothClosed, polyPath} from './geom';

const useUid = () => useId().replace(/[^a-zA-Z0-9]/g, '');

// 软阴影：压扁的模糊椭圆
export const SoftShadow: React.FC<{x: number; y: number; rx: number; ry: number; o?: number; blur?: number; color?: string}> = (
  {x, y, rx, ry, o = 0.5, blur, color = '#000'},
) => {
  const id = useUid();
  const b = blur ?? Math.max(2, ry * 0.5 + rx * 0.02);
  // 滤镜范围按模糊半径留够边，不然模糊被裁出一道硬边
  return (
    <g>
      <filter id={id} filterUnits="userSpaceOnUse" x={x - rx - 3 * b} y={y - ry - 3 * b} width={2 * rx + 6 * b} height={2 * ry + 6 * b}>
        <feGaussianBlur stdDeviation={b} />
      </filter>
      <ellipse cx={x} cy={y} rx={rx} ry={ry} fill={color} opacity={o} filter={`url(#${id})`} />
    </g>
  );
};

// —— 吊灯：线、灯罩、灯泡、一束光、地上一圈光 ——
export const PendantLamp: React.FC<{
  x: number; y: number; w: number; top?: number; floorY: number; spread: number;
  glow?: number; swing?: number; warm?: string; cone?: number; pool?: number; poolW?: number;
}> = ({x, y, w, top = -40, floorY, spread, glow = 1, swing = 0, warm = '#FFDDA6', cone = 0.22, pool = 0.55, poolW}) => {
  const id = useUid();
  const h = w * 0.55;
  const dx = Math.tan((swing * Math.PI) / 180) * (floorY - top);
  return (
    <g>
      <defs>
        <linearGradient id={`${id}c`} x1="0" y1={y} x2="0" y2={floorY} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor={warm} stopOpacity={0.9} />
          <stop offset="1" stopColor={warm} stopOpacity={0.15} />
        </linearGradient>
        <radialGradient id={`${id}p`}>
          <stop offset="0" stopColor={warm} stopOpacity={1} />
          <stop offset="0.6" stopColor={warm} stopOpacity={0.35} />
          <stop offset="1" stopColor={warm} stopOpacity={0} />
        </radialGradient>
        <radialGradient id={`${id}b`}>
          <stop offset="0" stopColor="#FFF8EC" stopOpacity={1} />
          <stop offset="0.25" stopColor={warm} stopOpacity={0.6} />
          <stop offset="1" stopColor={warm} stopOpacity={0} />
        </radialGradient>
        <filter id={`${id}f`} x="-30%" y="-10%" width="160%" height="120%"><feGaussianBlur stdDeviation={w * 0.12} /></filter>
      </defs>
      <ellipse cx={x + dx} cy={floorY} rx={poolW ?? spread * 1.1} ry={(poolW ?? spread * 1.1) * 0.16} fill={`url(#${id}p)`} opacity={pool * glow} />
      <g transform={`rotate(${swing} ${x} ${top})`}>
        <polygon points={`${x - w * 0.42},${y} ${x + w * 0.42},${y} ${x + spread},${floorY} ${x - spread},${floorY}`}
          fill={`url(#${id}c)`} opacity={cone * glow} filter={`url(#${id}f)`} style={{mixBlendMode: 'screen'}} />
        <line x1={x} y1={top} x2={x} y2={y - h} stroke="#2A211B" strokeWidth={Math.max(2, w * 0.03)} />
        <circle cx={x} cy={y + w * 0.05} r={w * 1.6} fill={`url(#${id}b)`} opacity={0.55 * glow} />
        {/* 灯罩：外面深色，里面一圈被灯照亮的内壁 */}
        <path d={`M ${x - w * 0.14} ${y - h} L ${x + w * 0.14} ${y - h} C ${x + w * 0.2} ${y - h * 0.5} ${x + w * 0.42} ${y - h * 0.25} ${x + w * 0.5} ${y}
          L ${x - w * 0.5} ${y} C ${x - w * 0.42} ${y - h * 0.25} ${x - w * 0.2} ${y - h * 0.5} ${x - w * 0.14} ${y - h} Z`} fill="#3B2E25" />
        <path d={`M ${x - w * 0.14} ${y - h} L ${x - w * 0.02} ${y - h} C ${x - w * 0.06} ${y - h * 0.5} ${x - w * 0.2} ${y - h * 0.2} ${x - w * 0.24} ${y}
          L ${x - w * 0.5} ${y} C ${x - w * 0.42} ${y - h * 0.25} ${x - w * 0.2} ${y - h * 0.5} ${x - w * 0.14} ${y - h} Z`} fill="#4E3E31" />
        <ellipse cx={x} cy={y} rx={w * 0.5} ry={w * 0.07} fill={mixHex('#3B2E25', warm, 0.75 * glow)} />
        <ellipse cx={x} cy={y + w * 0.02} rx={w * 0.16} ry={w * 0.09} fill="#FFF7E6" opacity={0.4 + 0.6 * glow} />
      </g>
    </g>
  );
};

// —— 一个斜着看的长方体面：o 原点，a、b 两条边 ——
const quad = (o: P, a: P, b: P) => polyPath([o, add(o, a), add(add(o, a), b), add(o, b)]);

// —— 木椅：侧 3/4，椅面朝右。原点 = 椅面前沿正下方的地面；单位和人一样（椅面高 40） ——
export const Chair: React.FC<{x: number; y: number; s: number; dim?: number}> = ({x, y, s, dim = 0}) => {
  const C = (c: string) => mixHex(c, '#0E0B0A', dim);
  const lit = '#A26F49', mid = '#83583A', dark = '#5E3E29', grain = '#6E482F';
  const off = {x: 12, y: -9};   // 远侧（往画面里）的偏移
  const seatY = -40, front = 16, back = -40;
  const leg = (lx: number, top: number, far: boolean, lean = 0) => (
    <path d={polyPath([{x: lx - 3.2, y: 0}, {x: lx + 3.2, y: 0}, {x: lx + 3.2 + lean, y: top}, {x: lx - 3.2 + lean, y: top}].map((q) => far ? add(q, off) : q))}
      fill={C(far ? dark : mid)} />
  );
  const postTop = -122;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <SoftShadow x={-8} y={2} rx={78} ry={8} o={0.6} />
      {/* 远侧的腿、靠背立柱 */}
      {leg(front - 3, seatY, true)}
      {leg(back + 3, postTop, true, -12)}
      {/* 靠背：顶上一块弯的横板，下面一根横档 */}
      <path d={quad({x: back - 9, y: postTop + 2}, off, {x: 0, y: 20})} fill={C(dark)} />
      <path d={smoothClosed([{x: back - 12, y: postTop + 1}, {x: back - 6 + off.x, y: postTop - 1 + off.y}, {x: back - 6 + off.x, y: postTop + 20 + off.y}, {x: back - 12, y: postTop + 22}], 0.3)} fill={C(mid)} />
      <path d={quad({x: back - 6, y: -82}, off, {x: 0, y: 7})} fill={C(dark)} />
      {/* 椅面：顶面（受光）+ 前沿厚度 */}
      <path d={quad({x: back - 2, y: seatY}, {x: front - back + 4, y: 0}, off)} fill={C(lit)} />
      <path d={`M ${back + 6} ${seatY - 4} Q ${back + 26} ${seatY - 7} ${front - 4} ${seatY - 5}`} fill="none" stroke={C(grain)} strokeWidth={1.2} opacity={0.6} />
      <path d={quad({x: back - 2, y: seatY}, {x: front - back + 4, y: 0}, {x: 0, y: 6})} fill={C(mid)} />
      <path d={`M ${back + 2} ${seatY + 3} L ${front - 2} ${seatY + 3}`} stroke={C(grain)} strokeWidth={1} opacity={0.5} />
      {/* 近侧的腿、靠背立柱、横档 */}
      {leg(front - 3, seatY + 6, false)}
      {leg(back + 3, postTop, false, -12)}
      <path d={polyPath([{x: back + 3, y: -16}, {x: front - 3, y: -16}, {x: front - 3, y: -11}, {x: back + 3, y: -11}])} fill={C(dark)} />
      <path d={`M ${back + 1.6} ${-60} L ${back - 6} ${postTop + 6}`} stroke={C(lit)} strokeWidth={1.6} opacity={0.55} strokeLinecap="round" />
    </g>
  );
};

// —— 一只手（右手，手背朝上，往左伸）：手腕为原点，单位约等于手长 100。轮廓两种画风共用 ——
export const HAND_OUTLINE: P[] = [
  {x: 2, y: -22}, {x: -22, y: -25}, {x: -44, y: -26},
  {x: -58, y: -27}, {x: -67, y: -24}, {x: -69, y: -19}, {x: -60, y: -16},
  {x: -54, y: -14},
  {x: -67, y: -13}, {x: -80, y: -10}, {x: -81, y: -4}, {x: -67, y: -3},
  {x: -58, y: -1},
  {x: -73, y: 0}, {x: -89, y: 4}, {x: -89, y: 10}, {x: -73, y: 10},
  {x: -60, y: 11},
  {x: -71, y: 14}, {x: -84, y: 19}, {x: -83, y: 25}, {x: -68, y: 23},
  {x: -52, y: 23},
  {x: -47, y: 31}, {x: -57, y: 39}, {x: -53, y: 45}, {x: -38, y: 38}, {x: -24, y: 28},
  {x: 2, y: 22},
];
// 指缝（从指根往里的短线）
export const HAND_CREASES: P[][] = [
  [{x: -60, y: -16}, {x: -54, y: -14}, {x: -46, y: -14}],
  [{x: -67, y: -3}, {x: -58, y: -1}, {x: -48, y: -2}],
  [{x: -73, y: 10}, {x: -60, y: 11}, {x: -50, y: 11}],
];
// 指甲
export const HAND_NAILS: [P, number][] = [[{x: -64, y: -21.5}, -8], [{x: -77, y: -7.5}, -4], [{x: -84, y: 7}, 2], [{x: -79, y: 21}, 10]];

export const ReachHand: React.FC<{x: number; y: number; s: number; r?: number; skin?: string; shade?: string; sleeve?: string; sleeveShade?: string; reach?: number}> = (
  {x, y, s, r = 0, skin = '#F3CDAA', shade = '#DDA987', sleeve = '#5F7EA3', sleeveShade = '#4A6487'},
) => {
  const id = useUid();
  const d = smoothClosed(HAND_OUTLINE, 0.75);
  return (
    <g transform={`translate(${x} ${y}) rotate(${r}) scale(${s})`}>
      <SoftShadow x={-30} y={48} rx={70} ry={12} o={0.45} />
      <clipPath id={`${id}h`}><path d={d} /></clipPath>
      <path d={d} fill={shade} />
      <g clipPath={`url(#${id}h)`}><path d={d} fill={skin} transform="translate(-2 -6)" /></g>
      {HAND_CREASES.map((c, i) => <path key={i} d={`M ${c[0].x} ${c[0].y} Q ${c[1].x} ${c[1].y} ${c[2].x} ${c[2].y}`} fill="none" stroke={shade} strokeWidth={2.2} strokeLinecap="round" />)}
      {HAND_NAILS.map(([q, a], i) => <ellipse key={i} cx={q.x} cy={q.y} rx={4.6} ry={3} transform={`rotate(${a} ${q.x} ${q.y})`} fill="#F8DCC6" />)}
      <path d="M -40 -20 Q -30 -23 -20 -22" fill="none" stroke={shade} strokeWidth={2} strokeLinecap="round" opacity={0.7} />
      {/* 袖口：连帽衫的罗纹袖口，再往右是袖子 */}
      <path d={smoothClosed([{x: -2, y: -30}, {x: 22, y: -33}, {x: 22, y: 33}, {x: -2, y: 30}, {x: -6, y: 0}], 0.4)} fill={sleeveShade} />
      {[4, 10, 16].map((k) => <line key={k} x1={k} y1={-28} x2={k} y2={28} stroke={sleeve} strokeWidth={1.6} opacity={0.6} />)}
      <path d={polyPath([{x: 20, y: -38}, {x: 400, y: -52}, {x: 400, y: 58}, {x: 20, y: 38}])} fill={sleeve} />
      <path d={polyPath([{x: 20, y: 14}, {x: 400, y: 22}, {x: 400, y: 58}, {x: 20, y: 38}])} fill={sleeveShade} />
    </g>
  );
};

