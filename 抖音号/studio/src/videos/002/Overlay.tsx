// 顶栏（常驻问题、第 N 代）、历史条（白点 = 我 = 播放头）、字幕带。版面和字号都从 timeline.json 的 layout 来。
import React from 'react';
import {COL, D, LAY, Line, SANS, Seg, TL, clamp, colOf, ease, genF, lerp, prog} from './lib';

const H = LAY.hist;
const ORDER = [0, 1, 4, 5, 2, 3];   // 历史条从上往下：老实人、骗子、记仇、不点名、以牙还牙、会原谅

// 一条历史条：每代一列，按人数堆六色；画到 upTo 代为止
export const HistBar: React.FC<{counts: number[][]; x0: number; x1: number; y0: number; y1: number; upTo: number; o?: number}> = (
  {counts, x0, x1, y0, y1, upTo, o = 1},
) => {
  const G = counts.length - 1;
  const cw = (x1 - x0) / (G + 1);
  const cols: React.ReactNode[] = [];
  const last = Math.min(G, Math.floor(upTo));
  for (let g = 0; g <= last; g++) {
    const c = counts[g];
    const n = c.reduce((a, b) => a + b, 0);
    let y = y0;
    const w = g === last ? cw * clamp(upTo - last + 1e-6) + 0.6 : cw + 0.6;
    for (const k of ORDER) {
      const h = ((y1 - y0) * c[k]) / n;
      if (h > 0) cols.push(<rect key={`${g}-${k}`} x={x0 + g * cw} y={y} width={w} height={h + 0.3} fill={COL[k]} />);
      y += h;
    }
  }
  return (
    <g opacity={o}>
      <rect x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill="#FFFFFF" opacity={0.07} />
      {cols}
    </g>
  );
};

// 白点：我。纯白，没有眼睛，有柔光
export const MeDot: React.FC<{x: number; y: number; r?: number; o?: number}> = ({x, y, r = 15, o = 1}) => (
  <g opacity={o}>
    <circle cx={x} cy={y} r={r * 2.4} fill="url(#meGlow)" />
    <circle cx={x} cy={y} r={r} fill="#FFFFFF" />
  </g>
);

export const histX = (gen: number) => H.x0 + (clamp(gen, 0, 300) / 300) * (H.x1 - H.x0);
export const HIST_Y = (H.y0 + H.y1) / 2;

// 字幕：固定两行高，单行放在下面那一行；数字 100 px，其余 88 px；上了色的字用打法颜色
// 一段字可以晚一点出现（第三项是帧）：没出场时透明但占着位置，行不跳；出现那一下轻轻亮一下
type SubStyle = {size: number; num: number; lineH: number; y0: number};
const DEF: SubStyle = {size: LAY.sub.size, num: LAY.sub.numSize, lineH: LAY.sub.lineH, y0: LAY.sub.y0};
const segs = (line: Line): Seg[] => (typeof line === 'string' ? [line] : line);
const Text: React.FC<{s: string; color?: string; num: number; o?: number; glow?: number}> = ({s, color, num, o = 1, glow = 0}) => {
  const parts = s.split(/([0-9]+%?)/);
  const shadow = glow > 0
    ? `0 0 ${18 + 26 * glow}px rgba(255,255,255,${0.75 * glow}), 0 4px 18px rgba(0,0,0,0.6)`
    : undefined;
  const st: React.CSSProperties = {color, opacity: o, textShadow: shadow, filter: glow > 0 ? `brightness(${1 + 0.45 * glow})` : undefined};
  return (
    <>
      {parts.map((t, i) => (/^[0-9]+%?$/.test(t)
        ? <span key={i} style={{...st, fontSize: num}}>{t}</span>
        : <span key={i} style={st}>{t}</span>))}
    </>
  );
};
export const SubLine: React.FC<{line: Line; top: number; f: number; st: SubStyle}> = ({line, top, f, st}) => (
  <div style={{
    position: 'absolute', top, height: st.lineH, left: LAY.sub.cx - 960, width: 1920,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: SANS, fontWeight: 600, fontSize: st.size, color: '#F4F5F8', letterSpacing: 0,
    whiteSpace: 'nowrap', textShadow: '0 4px 18px rgba(0,0,0,0.6)',
  }}>
    {segs(line).map((sg, i) => {
      if (typeof sg === 'string') return <Text key={i} s={sg} num={st.num} />;
      if (sg[1] === 'ME') {
        return <span key={i} style={{display: 'inline-block', width: 40, height: 40, borderRadius: 20, background: '#FFFFFF',
          boxShadow: '0 0 24px 10px rgba(255,255,255,0.45)', marginRight: 26, verticalAlign: 'middle'}} />;
      }
      const at = sg.length > 2 ? (sg[2] as number) : -1;
      const o = at < 0 ? 1 : clamp((f - at) / 4);
      const glow = at < 0 || !sg[1] ? 0 : Math.max(0, 1 - Math.abs(f - at - 6) / 9);
      return <Text key={i} s={sg[0]} color={sg[1] ? colOf(sg[1]) : undefined} num={st.num} o={o} glow={glow} />;
    })}
  </div>
);

export const Subtitles: React.FC<{lines: Line[]; f: number; sub?: SubStyle | null}> = ({lines, f, sub}) => {
  if (!lines.length) return null;
  const st = sub ?? DEF;
  return (
    <>
      {lines.length === 1
        ? <SubLine line={lines[0]} top={st.y0 + st.lineH} f={f} st={st} />
        : lines.map((l, i) => <SubLine key={i} line={l} top={st.y0 + i * st.lineH} f={f} st={st} />)}
    </>
  );
};

// 字幕带后面压暗（人腰以下压在字幕带后面）
export const SubBand: React.FC<{o?: number}> = ({o = 1}) => (
  <div style={{position: 'absolute', left: 0, top: 790, width: 1920, height: 290, opacity: o,
    background: 'linear-gradient(180deg, rgba(10,11,15,0) 0%, rgba(10,11,15,0.82) 22%, rgba(10,11,15,0.9) 100%)'}} />
);

// 常驻问题：0–1.2 秒是上方一行大题（132 px），1.2 秒起缩到左上角（80 px，八成亮），50.9 秒淡出
export const Question: React.FC<{f: number; outP?: number}> = ({f, outP = 0}) => {
  const q = TL.question;
  const t = ease(prog(f, [q.small[0], q.small[0] + 18]));
  const size = lerp(LAY.titleBig, LAY.top.questionSize, t);
  // 大题：水平居中，y 60；小题：左边 x 120，y 36
  const w = size * 11;
  const left = lerp(960 - (LAY.titleBig * 11) / 2, 120, t);
  const top = lerp(56, LAY.top.y0, t);
  const o = lerp(1, LAY.top.questionOpacity, t) * (1 - outP);
  if (f >= q.small[1] + 12) return null;
  return (
    <div style={{position: 'absolute', left, top, width: w + 40, height: size * 1.2, fontFamily: SANS, fontWeight: 700,
      fontSize: size, color: '#FFFFFF', opacity: o, whiteSpace: 'nowrap', lineHeight: `${size * 1.15}px`,
      textShadow: '0 4px 20px rgba(0,0,0,0.5)'}}>
      {q.text}
    </div>
  );
};

// 第 N 代：数字 96 px，“第”“代” 80 px，右边缘不超过 x 1680
export const GenCounter: React.FC<{gen: number; o?: number}> = ({gen, o = 1}) => (
  <div style={{position: 'absolute', right: 1920 - LAY.top.counterRight, top: LAY.top.y0 - 18, height: 110, opacity: o,
    fontFamily: SANS, fontWeight: 600, color: '#FFFFFF', whiteSpace: 'nowrap', display: 'flex', alignItems: 'baseline'}}>
    <span style={{fontSize: LAY.top.counterWord}}>第</span>
    <span style={{fontSize: LAY.top.counterNum, fontVariantNumeric: 'tabular-nums', minWidth: LAY.top.counterNum * 1.7, textAlign: 'center',
      display: 'inline-block'}}>{Math.floor(gen + 1e-9)}</span>
    <span style={{fontSize: LAY.top.counterWord}}>代</span>
  </div>
);

// 开场大计数：“变狠过”88 px，数字 160 px
export const HarshCounter: React.FC<{n: number; o?: number}> = ({n, o = 1}) => (
  <div style={{position: 'absolute', left: 900 - 680, width: 1360, top: 300, height: 220, opacity: o, display: 'flex',
    alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 700, color: '#FFFFFF'}}>
    <div style={{background: 'rgba(12,13,18,0.82)', borderRadius: 36, padding: '6px 48px', display: 'flex', alignItems: 'baseline', gap: 24, whiteSpace: 'nowrap'}}>
      <span style={{fontSize: LAY.harshCounter.word}}>变狠过</span>
      <span style={{fontSize: LAY.harshCounter.num, fontVariantNumeric: 'tabular-nums', minWidth: 290, textAlign: 'right', color: '#FFB3A0'}}>{n}</span>
      <span style={{fontSize: LAY.harshCounter.word}}>/ <span style={{fontSize: 100}}>500</span> 个老实人</span>
    </div>
  </div>
);

export const everHarshAt = (gen: number) => D.starters.everByGen[clamp(Math.floor(gen), 0, 300)];
export const genNow = genF;
