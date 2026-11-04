// 中景里的“影子你”（S17）、473 人方块（S24）、四个你（S25）、20 条历史条（S26–S27）
import React from 'react';
import {random} from 'remotion';
import {COL, Cam, D, FAR, GRABHAND, I, LAY, MID, SANS, YOU_W, barLen, camAt, cellXY, clamp, ease, easeOut, eva, evn, lerp, prog, toScreen} from './lib';
import {Crowd} from './Crowd';
import {Bar, EX, Man, POSE, Tag, headTop} from './people';
import {HistBar, MeDot} from './Overlay';

// —— S17：中近景。镜头从 24.4 秒起一直往你那颗点推，推到这里，点变成粉衣的你（占画面高度四成多）；
//          同样大小的半透明黄衣“影子你”站在旁边，两根条又粗又长，上下并排、左对齐比长短 ——
export const MY = {x: 1080, G: 1080, s: 2.5, gx: 620};
const myHead = (() => {
  const h = headTop(POSE.cross, MY.x, MY.G, MY.s, 1);
  return {x: h.x, y: h.y + 62 * MY.s};
})();
// 推镜的终点：你那颗点落在中近景里你的脸上
export const PUSH_END: Cam = {wx: YOU_W.x, wy: YOU_W.y, ax: myHead.x, ay: myHead.y, z: 4.6};
const MID_CLOSE: Cam = {...PUSH_END, z: 6.5};
const MB = {x0: 470, y1: 246, y2: 318, h: 52, full: 760};

export const MidYou: React.FC<{f: number; gen: number}> = ({f, gen}) => {
  const cam = camAt(PUSH_END, MID_CLOSE, prog(f, eva('S17', 'push')));
  const meO = ease(prog(f, eva('S17', 'meIn')));
  const gIn = prog(f, eva('S17', 'ghostIn')) * (1 - prog(f, eva('S17', 'ghostOut')));
  const gO = 0.5 * gIn;
  const {x, G, s, gx} = MY;
  const wob = Math.sin(f / 4) * 12;
  // 零星的“抢”：每 0.5 秒一道，在看得见的点之间
  const grabs: React.ReactNode[] = [];
  for (let k = 0; k < 6; k++) {
    const t0 = beatF0 + 8 + k * 15;
    const u = (f - t0) / 8;
    if (u < 0 || u > 1) continue;
    const a = {x: 200 + random(`ga${k}`) * 1400, y: 420 + random(`gb${k}`) * 340};
    const b = {x: a.x + (random(`gc${k}`) - 0.5) * 300, y: a.y + (random(`gd${k}`) - 0.5) * 200};
    const p = {x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u)};
    grabs.push(<g key={k} opacity={1 - u * 0.4}><line x1={lerp(a.x, p.x, 0.6)} y1={lerp(a.y, p.y, 0.6)} x2={p.x} y2={p.y} stroke={GRABHAND} strokeWidth={10} strokeLinecap="round" /><circle cx={p.x} cy={p.y} r={13} fill={GRABHAND} /></g>);
  }
  return (
    <>
      <Crowd f={f} gen={gen} cam={cam} eyes sparks dim={() => lerp(1, 0.45, meO)} ring={{o: 1 - meO}} tint={gen} />
      {grabs}
      {gO > 0.005 && (
        <g>
          <Man f={f} pose={POSE.idle} expr={EX.calm} strategy={I.ALLC} who="me" x={gx} G={G} s={s} opacity={gO} seed="ghost" />
          <circle cx={MB.x0 - 44} cy={MB.y1} r={22} fill={COL[I.ALLC]} opacity={gIn * 0.7} />
          <Bar x={MB.x0} y={MB.y1} len={barLen(D.youAvg[0], MB.full)} full={MB.full} h={MB.h} color={COL[I.ALLC]} align="left" o={gIn * 0.7} />
        </g>
      )}
      <g opacity={meO}>
        <Man f={f} pose={POSE.cross} expr={EX.cold} strategy={I.GRIM} who="me" x={x} G={G} s={s} seed="midme" />
        <circle cx={MB.x0 - 44} cy={MB.y2} r={22} fill={COL[I.GRIM]} />
        <Bar x={MB.x0} y={MB.y2} len={barLen(D.youAvg[1], MB.full) + wob} full={MB.full} h={MB.h} color={COL[I.GRIM]} align="left" />
        <Tag x={x + 270} y={myHead.y} text="你" bg="rgba(255,255,255,0.16)" size={88} />
      </g>
    </>
  );
};
const beatF0 = eva('S17', 'push')[0];

// —— S24：开局那 500 个老实人亮起；变狠过的 473 个飞到中间聚成方块，先粉橙，读到“九成后来”一格格翻成第 300 代的颜色 ——
const BLK = {cols: 30, rows: 16, gap: 30, cell: 26};
const blockXY = (i: number) => ({
  x: 900 - ((BLK.cols - 1) * BLK.gap) / 2 + (i % BLK.cols) * BLK.gap,
  y: 322 + Math.floor(i / BLK.cols) * BLK.gap,
});
const STARTERS = new Set(D.grid.starters);
const BLOCK_CELLS = new Set(D.starters.block.map((c) => c.cell));

export const Block: React.FC<{f: number; gen: number; scatter?: number}> = ({f, gen, scatter = 0}) => {
  const cam: Cam = camAt(MID, FAR, ease(prog(f, eva('S24', 'zoom'))));
  const hi = prog(f, eva('S24', 'starters'));
  const [g0, g1] = eva('S24', 'gather');
  const gp = ease(prog(f, [g0, g1]));
  const [fl0, fl1] = eva('S24', 'flip');
  const n = D.starters.block.length;
  const cells = D.starters.block.map((c, i) => {
    const from = toScreen(FAR, cellXY(c.cell));
    const to = blockXY(i);
    const flipAt = lerp(fl0, fl1, i / (n - 1));
    const col = f >= flipAt ? COL[c.end] : gp > 0 ? COL[c.main] : COL[D.grid.s[Math.min(300, gen)].charCodeAt(c.cell) - 48];
    let p = {x: lerp(from.x, to.x, gp), y: lerp(from.y, to.y, gp)};
    let o = 1;
    if (scatter > 0) {
      const a = random(`sc${i}`) * Math.PI * 2;
      p = {x: p.x + Math.cos(a) * 900 * easeOut(scatter), y: p.y + Math.sin(a) * 600 * easeOut(scatter)};
      o = 1 - scatter;
    }
    const size = lerp(LAY.far.dot, BLK.cell, gp);
    return {p, col, o, you: c.you, size, gp};
  });
  const label = prog(f, [g1 - 4, g1 + 6]) * (1 - scatter);
  const you = cells.find((c) => c.you)!;
  return (
    <>
      {gp < 1 && scatter === 0 && (
        <Crowd f={f} gen={gen} cam={cam} sparks={hi < 0.5}
          dim={(cell) => (STARTERS.has(cell) ? 1 : lerp(1, 0.12, hi))}
          skip={gp > 0 ? BLOCK_CELLS : undefined} ring={{o: 1 - hi}} tint={gen} />
      )}
      {gp >= 1 && scatter === 0 && (
        <Crowd f={f} gen={gen} cam={FAR} dim={(cell) => (STARTERS.has(cell) ? 0.5 : 0.08)} skip={BLOCK_CELLS} ring={{o: 0}} />
      )}
      {gp > 0 && cells.map((c, i) => (
        <rect key={i} x={c.p.x - c.size / 2} y={c.p.y - c.size / 2} width={c.size} height={c.size} rx={c.gp > 0.5 ? 3 : c.size / 2} fill={c.col} opacity={c.o} />
      ))}
      {gp > 0 && <circle cx={you.p.x} cy={you.p.y} r={LAY.far.ring / 2} fill="none" stroke="#FFFFFF" strokeWidth={LAY.far.ringStroke} opacity={you.o} />}
      {label > 0 && (
        <foreignObject x={400} y={190} width={1000} height={110} opacity={label}>
          <div style={{fontFamily: SANS, fontWeight: 600, fontSize: LAY.blockLabel.text, color: '#FFFFFF', textAlign: 'center', lineHeight: '110px'}}>
            变狠过的 <span style={{fontSize: LAY.blockLabel.num}}>473</span> 人
          </div>
        </foreignObject>
      )}
    </>
  );
};

// —— S25：方块散开，四个你从左到右站成一排：黄、粉、蓝、绿；灯每 0.5 秒亮一盏 ——
const FOUR = [
  {s: I.ALLC, pose: POSE.idle, e: EX.calm, x: 250},
  {s: I.GRIM, pose: POSE.cross, e: EX.cold, x: 670},
  {s: I.TFT, pose: POSE.idle, e: EX.stiff, x: 1090},
  {s: I.GTFT, pose: POSE.idle, e: EX.smile, x: 1510},
];
export const Four: React.FC<{f: number; up?: number; o?: number; zoom?: number}> = ({f, up = 0, o = 1, zoom = 1}) => {
  const ap = ease(prog(f, eva('S25', 'appear')));
  const lamps = eva('S25', 'lamps');
  // 放大到铺满画面宽度：每人露在字幕上面的部分约占画面高度四成
  const G = 1236, s = 3.2;
  const lo = Math.min(...D.youAvg), hi = Math.max(...D.youAvg);
  // up：S26 四个你缩回顶上的历史条
  const sc = lerp(1, 0.08, ease(up));
  const ty = lerp(0, -(G - 164) * 0.92, ease(up));
  const lampY = 232;
  return (
    <g opacity={ap * (1 - ease(up)) * o} transform={`translate(900 560) scale(${zoom}) translate(-900 -560) translate(900 ${G + ty}) scale(${sc}) translate(-900 ${-G})`}>
      {FOUR.map((q, i) => {
        const on = ease(prog(f, [lamps[i], lamps[i] + 6]));
        const k = (D.youAvg[i] - lo) / (hi - lo);   // 灯的亮度 = 这一段的平均分（1.99 / 1.46 / 2.39 / 2.83）
        return (
          <g key={i}>
            {/* 一束光：从灯往下照到人身上，分越高越亮 */}
            <polygon points={`${q.x - 34},${lampY} ${q.x + 34},${lampY} ${q.x + 230},${G - 380} ${q.x - 230},${G - 380}`}
              fill="#FFD9A0" opacity={on * (0.06 + 0.34 * k)} />
            <circle cx={q.x} cy={500} r={330} fill="url(#warmGlow)" opacity={on * (0.2 + 0.8 * k)} />
            <rect x={q.x - 44} y={lampY - 30} width={88} height={28} rx={7} fill="#3A3D46" />
            <circle cx={q.x} cy={lampY + 6} r={56} fill="#FFE2B0" opacity={on * (0.08 + 0.5 * k)} />
            <circle cx={q.x} cy={lampY + 6} r={30} fill={on > 0 ? (k > 0.6 ? '#FFD38A' : k > 0.2 ? '#F1E4CC' : '#6E7079') : '#3A3D46'} opacity={0.35 + 0.65 * on} />
            <Man f={f} pose={q.pose} expr={q.e} strategy={q.s} who="me" x={q.x} G={G} s={s} dim={lerp(0.6, 0.5 * (1 - k), on)} seed={`four${i}`} />
            <Bar x={q.x} y={296} len={barLen(D.youAvg[i], 360) * on} full={360} h={48} color={COL[q.s]} />
          </g>
        );
      })}
    </g>
  );
};

// —— 带走句那拍：绿衣的你（END_X）不动，另外三个你在左边淡入；四个人头上都有灯和条，灯按这一段的平均分亮 ——
const OTHERS = [
  {s: I.ALLC, pose: POSE.idle, e: EX.calm, x: 280},
  {s: I.GRIM, pose: POSE.cross, e: EX.cold, x: 650},
  {s: I.TFT, pose: POSE.idle, e: EX.stiff, x: 1020},
];
export const Others: React.FC<{f: number; o: number; endX: number; G: number; s: number}> = ({f, o, endX, G, s}) => {
  const lo = Math.min(...D.youAvg), hi = Math.max(...D.youAvg);
  const lampY = 172, barY = 244;
  const all = [...OTHERS, {s: I.GTFT, pose: POSE.idle, e: EX.smile, x: endX}];
  return (
    <g opacity={o}>
      {all.map((q, i) => {
        const k = (D.youAvg[i] - lo) / (hi - lo);
        const lit = i < 3 ? o : 1;
        return (
          <g key={i}>
            <polygon points={`${q.x - 30},${lampY} ${q.x + 30},${lampY} ${q.x + 210},${G - 420} ${q.x - 210},${G - 420}`}
              fill="#FFD9A0" opacity={lit * (0.06 + 0.3 * k)} />
            <rect x={q.x - 40} y={lampY - 28} width={80} height={26} rx={7} fill="#3A3D46" />
            <circle cx={q.x} cy={lampY + 4} r={50} fill="#FFE2B0" opacity={lit * (0.08 + 0.5 * k)} />
            <circle cx={q.x} cy={lampY + 4} r={26} fill={k > 0.6 ? '#FFD38A' : k > 0.2 ? '#F1E4CC' : '#6E7079'} />
            {i < 3 && <Man f={f} pose={q.pose} expr={q.e} strategy={q.s} who="me" x={q.x} G={G} s={s} dim={0.5 * (1 - k)} seed={`oth${i}`} />}
            <Bar x={q.x} y={barY} len={barLen(D.youAvg[i], 300)} full={300} h={44} color={COL[q.s]} />
          </g>
        );
      })}
    </g>
  );
};

// —— S26–S27：历史条往下复制成 20 条，白点一条接一条跑过去；然后 19 条淡掉，只剩一条 ——
const H = LAY.hist;
export const Hist20: React.FC<{f: number}> = ({f}) => {
  const cp = ease(prog(f, eva('S26', 'copyDown')));
  const [r0, r1] = eva('S26', 'runs');
  const d = (r1 - r0) / 20;
  const fade19 = prog(f, eva('S27', 'fade19'));
  const dive = prog(f, eva('S27', 'dive'));
  const bh = LAY.hist20.barH;
  const rows = D.hist20.counts.map((counts, i) => {
    const y = lerp(H.y0, 215 + i * 28, cp);
    const run = clamp((f - (r0 + i * d)) / d);
    const upTo = i === 0 ? 300 : run * 300;
    const o = (i === 0 ? 1 : cp * (1 - fade19)) * (1 - dive);
    return {i, y, upTo, o, run, counts};
  });
  let dot: {x: number; y: number} | null = null;
  for (const r of rows) {
    if (f >= r0 + r.i * d && f < r0 + (r.i + 1) * d) dot = {x: H.x0 + r.run * (H.x1 - H.x0), y: r.y + bh / 2};
  }
  if (f < r0) dot = {x: H.x1, y: rows[0].y + bh / 2};
  if (f >= r1) dot = {x: H.x1, y: rows[19].y + bh / 2};
  return (
    <>
      {rows.map((r) => (r.o > 0.01 ? <HistBar key={r.i} counts={r.counts} x0={H.x0} x1={H.x1} y0={r.y} y1={r.y + bh} upTo={r.upTo} o={r.o} /> : null))}
      {dot && <MeDot x={dot.x} y={dot.y} r={12} o={(1 - fade19) * (1 - dive)} />}
    </>
  );
};

export const YOU_SCREEN_FAR = toScreen(FAR, YOU_W);
