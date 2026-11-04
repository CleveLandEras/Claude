// 003 成片画法（前 15 秒精修用）：照第二条成片（videos/002/film/）的质感——暗房间、头顶一盏暖灯、光锥里飘灰、扁平小人带软影、四角压暗；
// 字幕带、字幕样式、“AI 生成”标和第二条成片一致（002 的文件不改，这里照着重写，免得把 002 的数据文件带进来）。
// 手机做成真手机：钛色边框、侧键、灵动岛、状态栏图标、壁纸、横幅通知带 App 图标。
import React from 'react';
import {random} from 'remotion';
import {mixHex} from '../../components/people/geom';

export const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
export const CREAM = '#F6F3EC';
export const SHADOW = '0 3px 0 rgba(0,0,0,0.35), 0 6px 22px rgba(0,0,0,0.7)';
export const LAMP = '#FFD7A0';
export const PAPER = '#F2ECE1', INKD = '#1A1C23';

export const FilmDefs3: React.FC = () => (
  <defs>
    <filter id="fBlur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={4} /></filter>
    <filter id="fBlur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={8} /></filter>
    <filter id="fBlur16" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={16} /></filter>
    <filter id="fBlur28" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={28} /></filter>
    <radialGradient id="gPool">
      <stop offset="0" stopColor="#3A3128" stopOpacity={1} />
      <stop offset="0.5" stopColor="#241F1B" stopOpacity={0.6} />
      <stop offset="1" stopColor="#0D1016" stopOpacity={0} />
    </radialGradient>
    <linearGradient id="gCone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stopColor={LAMP} stopOpacity={0.5} />
      <stop offset="0.6" stopColor={LAMP} stopOpacity={0.16} />
      <stop offset="1" stopColor={LAMP} stopOpacity={0} />
    </linearGradient>
    <radialGradient id="gFloor"><stop offset="0" stopColor={LAMP} stopOpacity={0.32} /><stop offset="1" stopColor={LAMP} stopOpacity={0} /></radialGradient>
    <radialGradient id="gScreenLight"><stop offset="0" stopColor="#BFD4FF" stopOpacity={0.55} /><stop offset="1" stopColor="#BFD4FF" stopOpacity={0} /></radialGradient>
    <radialGradient id="gVig" cx="0.5" cy="0.45" r="0.78"><stop offset="0.55" stopColor="#000" stopOpacity={0} /><stop offset="1" stopColor="#000" stopOpacity={0.6} /></radialGradient>
    <linearGradient id="gWall" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stopColor="#5B6FA6" /><stop offset="0.55" stopColor="#3A3F73" /><stop offset="1" stopColor="#1F2340" />
    </linearGradient>
  </defs>
);

// 暗房间的底
export const RoomBase: React.FC<{o?: number}> = ({o = 1}) => (
  <g opacity={o}>
    <rect width={1920} height={1080} fill="#0D1016" />
    <rect width={1920} height={1080} fill="#16191F" opacity={0.9} />
  </g>
);

// 一盏头顶的灯：地上一圈光、一道光锥、光里飘几粒灰。k = 亮度 0..1
export const Lamp: React.FC<{x: number; k: number; f: number; spread?: number; cy?: number; floorY?: number; seed?: string}> = (
  {x, k, f, spread = 1, cy = 560, floorY, seed = 'l'},
) => {
  if (k <= 0.001) return null;
  const dust = Array.from({length: 18}, (_, i) => {
    const sx = x + (random(`${seed}dx${i}`) - 0.5) * 460 * spread;
    const sy = ((random(`${seed}dy${i}`) * 1100 + f * (0.25 + random(`${seed}dv${i}`) * 0.5)) % 1100) - 20;
    const tw = 0.4 + 0.6 * Math.abs(Math.sin(f / 23 + i));
    return <circle key={i} cx={sx + Math.sin(f / 40 + i) * 14} cy={sy} r={1.6 + random(`${seed}dr${i}`) * 2.2} fill={LAMP} opacity={0.35 * tw * k} />;
  });
  return (
    <g>
      <ellipse cx={x} cy={cy} rx={640 * spread} ry={560} fill="url(#gPool)" opacity={0.85 * k} style={{mixBlendMode: 'screen'}} />
      <polygon points={`${x - 100 * spread},-40 ${x + 100 * spread},-40 ${x + 420 * spread},1080 ${x - 420 * spread},1080`} fill="url(#gCone)"
        opacity={0.5 * k} filter="url(#fBlur28)" style={{mixBlendMode: 'screen'}} />
      {floorY !== undefined && <ellipse cx={x} cy={floorY} rx={330 * spread} ry={46} fill="url(#gFloor)" opacity={k} />}
      <g style={{mixBlendMode: 'screen'}}>{dust}</g>
    </g>
  );
};

export const Vignette3: React.FC<{o?: number}> = ({o = 1}) => <rect width={1920} height={1080} fill="url(#gVig)" opacity={o} pointerEvents="none" />;

// 软影
export const Shadow: React.FC<{x: number; y: number; rx: number; ry: number; o?: number}> = ({x, y, rx, ry, o = 0.5}) => (
  <ellipse cx={x} cy={y} rx={rx} ry={ry} fill="#000" opacity={o} filter="url(#fBlur8)" />
);

// “AI 生成”：左上角一直挂着（平台要求）。样片 v2：字抬到 40 像素（第二条是 28）
export const AiBadge: React.FC = () => (
  <div style={{position: 'absolute', left: 24, top: 24, padding: '1px 14px', borderRadius: 9, fontFamily: SANS, fontWeight: 600,
    fontSize: 40, lineHeight: '50px', color: 'rgba(246,240,228,0.92)', background: 'rgba(0,0,0,0.5)',
    border: '2px solid rgba(246,240,228,0.36)', letterSpacing: '0.04em'}}>AI 生成</div>
);

// 字幕带：和第二条成片同一条压暗（人腰以下沉进暗处）
export const SubBand3: React.FC<{o?: number}> = ({o = 1}) => (
  <div style={{position: 'absolute', left: 0, top: 740, width: 1920, height: 340, opacity: o,
    background: 'linear-gradient(180deg, rgba(8,9,13,0) 0%, rgba(8,9,13,0.55) 26%, rgba(8,9,13,0.86) 52%, rgba(8,9,13,0.92) 100%)'}} />
);

const tw = (s: string, size: number) => [...s].reduce((w, ch) => w + (/[　-鿿＀-￯]/.test(ch) ? size : ch === ' ' ? size * 0.3 : size * 0.58), 0);

// 贴纸标签：和第二条成片的标签同款（米白底、深字、下沿小尖角、微歪、落软影）
export const Sticker: React.FC<{x: number; y: number; text: string; size: number; o?: number; pop?: number; tilt?: number; ring?: number}> = (
  {x, y, text, size, o = 1, pop = 1, tilt = -1.5, ring = 0},
) => {
  const w = tw(text, size);
  const W = w + size * 0.66, H = size * 1.28;
  const s = 0.6 + 0.4 * pop;
  const x0 = x - W / 2, y0 = y - H / 2;
  return (
    <g opacity={o} transform={`rotate(${tilt} ${x} ${y}) translate(${x} ${y}) scale(${s}) translate(${-x} ${-y})`}>
      <rect x={x0 + 5} y={y0 + 12} width={W} height={H} rx={size * 0.26} fill="#000" opacity={0.45} filter="url(#fBlur8)" />
      {ring > 0 && <rect x={x0 - 8} y={y0 - 8} width={W + 16} height={H + 16} rx={size * 0.26 + 8} fill="none" stroke="#FFC94D" strokeWidth={5} opacity={ring} />}
      <path d={`M ${x - size * 0.2} ${y0 + H - 1} L ${x} ${y0 + H + size * 0.24} L ${x + size * 0.2} ${y0 + H - 1} Z`} fill={mixHex(PAPER, '#000000', 0.12)} />
      <rect x={x0} y={y0} width={W} height={H} rx={size * 0.26} fill={mixHex(PAPER, '#000000', 0.1)} />
      <rect x={x0} y={y0} width={W} height={H - size * 0.128} rx={size * 0.26} fill={PAPER} />
      <rect x={x0 + size * 0.18} y={y0 + size * 0.1} width={W - size * 0.36} height={size * 0.38} rx={size * 0.14} fill="#FFFFFF" opacity={0.25} />
      <text x={x} y={y + size * 0.3} fontSize={size} fontFamily={SANS} fontWeight={700} fill={INKD} textAnchor="middle">{text}</text>
    </g>
  );
};

// —— 真手机：钛色边框、黑边、侧键、灵动岛、状态栏 ——
export type Box = {x: number; y: number; w: number; h: number};
export const PhoneBody: React.FC<{b: Box; r?: number}> = ({b, r = 62}) => (
  <g>
    <rect x={b.x + 10} y={b.y + 26} width={b.w} height={b.h} rx={r} fill="#000" opacity={0.5} filter="url(#fBlur16)" />
    {/* 侧键：左边操作键、两个音量键；右边电源键 */}
    <rect x={b.x - 5} y={b.y + 118} width={8} height={40} rx={3} fill="#4A4F5A" />
    <rect x={b.x - 5} y={b.y + 180} width={8} height={72} rx={3} fill="#4A4F5A" />
    <rect x={b.x - 5} y={b.y + 268} width={8} height={72} rx={3} fill="#4A4F5A" />
    <rect x={b.x + b.w - 3} y={b.y + 210} width={8} height={110} rx={3} fill="#4A4F5A" />
    <rect x={b.x} y={b.y} width={b.w} height={b.h} rx={r} fill="#5D626D" />
    <rect x={b.x + 2.5} y={b.y + 2.5} width={b.w - 5} height={b.h - 5} rx={r - 2} fill="#2B2E35" />
    <rect x={b.x + 7} y={b.y + 7} width={b.w - 14} height={b.h - 14} rx={r - 6} fill="#06070A" />
  </g>
);
// 屏幕上层：灵动岛 + 状态栏图标（信号、Wi-Fi、电池），不写字
export const StatusBar: React.FC<{s: Box; light?: boolean}> = ({s, light = true}) => {
  const c = light ? '#F4F5F8' : '#1A1C23';
  const y = s.y + 34;
  const rx = s.x + s.w - 30;
  return (
    <g>
      <rect x={s.x + s.w / 2 - 58} y={s.y + 14} width={116} height={36} rx={18} fill="#000" />
      {/* 电池 */}
      <rect x={rx - 40} y={y - 10} width={36} height={20} rx={6} fill="none" stroke={c} strokeWidth={2.5} opacity={0.9} />
      <rect x={rx - 37} y={y - 7} width={24} height={14} rx={3.5} fill={c} />
      <rect x={rx - 2} y={y - 4} width={3} height={8} rx={1.5} fill={c} opacity={0.8} />
      {/* Wi-Fi */}
      {[0, 1, 2].map((i) => (
        <path key={i} d={`M ${rx - 72 - 7 - i * 5} ${y + 2 - i * 4} Q ${rx - 72} ${y - 8 - i * 6} ${rx - 72 + 7 + i * 5} ${y + 2 - i * 4}`} fill="none" stroke={c}
          strokeWidth={3} strokeLinecap="round" opacity={i === 0 ? 1 : 0.9} />
      ))}
      <circle cx={rx - 72} cy={y + 6} r={2.6} fill={c} />
      {/* 信号 */}
      {[0, 1, 2, 3].map((i) => <rect key={i} x={rx - 122 + i * 8} y={y + 8 - (6 + i * 4)} width={5} height={6 + i * 4} rx={1.5} fill={c} />)}
    </g>
  );
};

// App 图标：圆角方块 + 白色图形（不画任何真实 App 的商标）
export const AppIcon: React.FC<{x: number; y: number; size: number; kind: 'bag' | 'chat' | 'flame'}> = ({x, y, size, kind}) => {
  const bg = kind === 'bag' ? '#F2683A' : kind === 'chat' ? '#3CC27A' : '#E8434F';
  const k = size / 60;
  return (
    <g transform={`translate(${x} ${y}) scale(${k})`}>
      <rect x={-30} y={-30} width={60} height={60} rx={14} fill={bg} />
      <rect x={-30} y={-30} width={60} height={26} rx={14} fill="#FFFFFF" opacity={0.12} />
      {kind === 'bag' && (
        <g fill="none" stroke="#FFFFFF" strokeWidth={4} strokeLinejoin="round">
          <path d="M -15 -6 L 15 -6 L 13 18 L -13 18 Z" fill="#FFFFFF" stroke="none" />
          <path d="M -8 -6 Q -8 -18 0 -18 Q 8 -18 8 -6" />
        </g>
      )}
      {kind === 'chat' && (
        <g fill="#FFFFFF">
          <ellipse cx={-4} cy={-3} rx={17} ry={14} /><path d="M -14 7 L -18 17 L -6 10 Z" />
          <ellipse cx={10} cy={8} rx={12} ry={10} fill="#E9FFF1" />
        </g>
      )}
      {kind === 'flame' && (
        <path d="M 0 -20 C 10 -8 16 -2 14 8 C 12 17 5 21 0 21 C -7 21 -14 16 -14 7 C -14 -1 -8 -5 -6 -12 C -3 -6 -2 -3 0 -1 C 2 -8 1 -14 0 -20 Z" fill="#FFFFFF" />
      )}
    </g>
  );
};
