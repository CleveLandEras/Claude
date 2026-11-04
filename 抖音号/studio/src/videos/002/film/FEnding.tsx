// 002 成片：中近景里的“影子你”（S17）、473 人方块（S24）、四个你（S25，第五版带走句也在这一拍）、第七版 S26 接着跑的点阵（Cycle）
// 从灰框 Ending.tsx 复制过来改画法，时间不动。
import React from 'react';
import {random} from 'remotion';
import {mixHex} from '../../../components/people/geom';
import {COL, Cam, D, HARSH, I, LAY, MID, TL, YOU_W, barLen, camAt, cellXY, clamp, ease, easeOut, eva, lerp, prog, toScreen, FAR} from '../lib';
import {Crowd, CrowdFloor} from './FCrowd';
import {Bar, EX, FaceDot, GrabHand, Man, POSE, Tag, YOU_BG, YOU_FG, headTop, still} from './fpeople';
import {NL, YouLamp} from './FNear';

// —— S17：中近景。镜头从 25.2 秒起一直往你那颗点推，推到这里，点变成红衣的你（比灰框大）；
//          同样大小的“影子你”（黄衣，约六成不透明，外面一圈淡黄光边）站在旁边，两根粗条上下并排、左对齐比长短 ——
export const MY = {x: 1110, G: 1180, s: 3.0, gx: 600};
const myHead = (() => {
  const h = headTop(POSE.cross, MY.x, MY.G, MY.s, 1);
  return {x: h.x, y: h.y + 62 * MY.s};
})();
export const PUSH_END: Cam = {wx: YOU_W.x, wy: YOU_W.y, ax: myHead.x, ay: myHead.y, z: 4.6};
const MID_CLOSE: Cam = {...PUSH_END, z: 6.5};
const MB = {x0: 470, y1: 246, y2: 322, h: 58, full: 760};
const beatF0 = () => eva('S17', 'push')[0];

export const MidYou: React.FC<{f: number; gen: number}> = ({f, gen}) => {
  const [p0, p1] = eva('S17', 'push');
  // 接着上一段推镜的速度慢慢推（上一段最后 0.5 秒已经减速到这个速度）
  const cam = camAt(PUSH_END, MID_CLOSE, prog(f, [p0, p1]));
  const meO = ease(prog(f, eva('S17', 'meIn')));
  const gIn = prog(f, eva('S17', 'ghostIn')) * (1 - prog(f, eva('S17', 'ghostOut')));
  const {x, G, s, gx} = MY;
  const wob = Math.sin(f / 4) * 12;
  // 零星的“抢”：每 0.5 秒一道
  const grabs: React.ReactNode[] = [];
  for (let k = 0; k < 6; k++) {
    const t0 = beatF0() + 8 + k * 15;
    const u = (f - t0) / 8;
    if (u < 0 || u > 1) continue;
    const a = {x: 200 + random(`ga${k}`) * 1300, y: 420 + random(`gb${k}`) * 300};
    const b = {x: a.x + (random(`gc${k}`) - 0.5) * 300, y: a.y + (random(`gd${k}`) - 0.5) * 200};
    const pp = {x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u)};
    grabs.push(<GrabHand key={k} x={pp.x} y={pp.y} r={18} dir={Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI} close={clamp((u - 0.6) / 0.4)} o={(1 - u * 0.5) * 0.85} trail={1} sleeve={0.7} />);
  }
  return (
    <>
      <CrowdFloor gen={gen} />
      <Crowd f={f} gen={gen} cam={cam} sparks dim={() => lerp(1, 0.4, meO)} ring={{o: 1 - meO}} tint={gen} />
      {grabs}
      {gIn > 0.005 && (
        <g>
          <Man f={f} pose={POSE.idle} expr={EX.calm} strategy={I.ALLC} who="me" x={gx} G={G} s={s} opacity={gIn} ghost seed="ghost" />
          <FaceDot x={MB.x0 - 46} y={MB.y1} r={24} color={COL[I.ALLC]} o={gIn} gx={0.8} />
          <Bar x={MB.x0} y={MB.y1} len={barLen(D.youAvg[0], MB.full)} full={MB.full} h={MB.h} color={COL[I.ALLC]} align="left" o={gIn} />
        </g>
      )}
      <g opacity={meO}>
        <Man f={f} pose={still('cross')} expr={EX.cold} strategy={I.GRIM} who="me" x={x} G={G} s={s} seed="midme" tint={{color: '#9FB6DA', amount: 0.1}} />
        <FaceDot x={MB.x0 - 46} y={MB.y2} r={24} color={COL[I.GRIM]} gx={0.8} />
        <Bar x={MB.x0} y={MB.y2} len={barLen(D.youAvg[1], MB.full) + wob} full={MB.full} h={MB.h} color={COL[I.GRIM]} align="left" />
        <Tag x={x + 300} y={myHead.y - 40} text="你" bg={YOU_BG} fg={YOU_FG} size={88} point="none" tilt={2} />
      </g>
    </>
  );
};

// —— S24：开局那 500 个老实人亮起；变狠过的 473 个飞到中间聚成方块，先是红（两种狠），读到“九成后来”一格格翻成第 300 代的颜色（第七版三改：方块上不再挂标签）——
const BLK = {cols: 30, rows: 16, gap: 30, cell: 26};
const blockXY = (i: number) => ({
  x: 900 - ((BLK.cols - 1) * BLK.gap) / 2 + (i % BLK.cols) * BLK.gap,
  y: 322 + Math.floor(i / BLK.cols) * BLK.gap,
});
const STARTERS = new Set(D.grid.starters);
const BLOCK_CELLS = new Set(D.starters.block.map((c) => c.cell));

// 第七版重排：ungather（0..1）把聚好的方块反着散回点阵里各自的格子（S26 开头，接着跑之前）；cellsOnly 只画飞的这些格，点阵由外面画
export const Block: React.FC<{f: number; gen: number; scatter?: number; ungather?: number; cellsOnly?: boolean}> = ({f, gen, scatter = 0, ungather, cellsOnly}) => {
  const ug = ungather ?? 0;
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
    // 翻牌：每格像一张小牌翻过去，翻到一半换成新颜色
    const fp = clamp((f - flipAt) / 5);
    const col = fp >= 0.5 ? COL[c.end] : gp > 0 ? COL[c.main] : COL[D.grid.s[Math.min(300, gen)].charCodeAt(c.cell) - 48];
    // 聚拢时各自走一条略弯的路，晚一点出发的落后一点
    const lag = random(`bl${i}`) * 0.25;
    const gq = ease(clamp(((ungather !== undefined ? 1 - ug : prog(f, [g0, g1])) - lag) / (1 - lag)));
    const bend = (random(`bb${i}`) - 0.5) * 160 * Math.sin(gq * Math.PI);
    let p = {x: lerp(from.x, to.x, gq) + bend, y: lerp(from.y, to.y, gq) - Math.sin(gq * Math.PI) * 40};
    let o = 1 - clamp((ug - 0.8) / 0.2);      // 落回格子的最后两成里淡掉，交给点阵自己画
    if (scatter > 0) {
      const a = random(`sc${i}`) * Math.PI * 2;
      p = {x: p.x + Math.cos(a) * 900 * easeOut(scatter), y: p.y + Math.sin(a) * 600 * easeOut(scatter)};
      o = 1 - scatter;
    }
    const size = lerp(LAY.far.dot, BLK.cell, gq);
    return {p, col, o, you: c.you, size, gp: gq, fp};
  });
  // 第七版三改：方块上的标签“变狠过的老实人”去掉（和字幕“变狠过的人”两行一起出来、对不上），只留字幕
  const you = cells.find((c) => c.you)!;
  return (
    <>
      {!cellsOnly && <CrowdFloor gen={gen} o={1} />}
      {!cellsOnly && gp < 1 && scatter === 0 && (
        <Crowd f={f} gen={gen} cam={cam} sparks={hi < 0.5}
          dim={(cell) => (STARTERS.has(cell) ? 1 : lerp(1, 0.12, hi))}
          skip={gp > 0 ? BLOCK_CELLS : undefined} ring={{o: 1 - hi}} tint={gen} />
      )}
      {!cellsOnly && gp >= 1 && scatter === 0 && (
        <Crowd f={f} gen={gen} cam={FAR} dim={(cell) => (STARTERS.has(cell) ? 0.45 : 0.07)} skip={BLOCK_CELLS} ring={{o: 0}} />
      )}
      {gp > 0 && (
        <g>
          {/* 方块落在地上的一整块软影 */}
          <rect x={900 - 450 + 10} y={322 - 13 + 24} width={900} height={16 * 30} rx={12} fill="#000" opacity={0.5 * gp * (1 - scatter) * (1 - ug)} filter="url(#fBlur24)" />
          {cells.map((c, i) => {
            const sy = c.fp > 0 && c.fp < 1 ? Math.abs(Math.cos(c.fp * Math.PI)) : 1;
            const rx = c.gp > 0.5 ? 5 : c.size / 2;
            return (
              <g key={i} opacity={c.o} transform={`translate(${c.p.x} ${c.p.y}) scale(1 ${Math.max(0.06, sy)})`}>
                <rect x={-c.size / 2} y={-c.size / 2} width={c.size} height={c.size} rx={rx} fill={mixHex(c.col, '#000000', 0.25)} />
                <rect x={-c.size / 2} y={-c.size / 2} width={c.size} height={c.size * 0.84} rx={rx} fill={c.col} />
                <rect x={-c.size / 2 + 4} y={-c.size / 2 + 3} width={c.size - 8} height={c.size * 0.18} rx={2} fill="#FFFFFF" opacity={0.16} />
              </g>
            );
          })}
        </g>
      )}
      {gp > 0 && <circle cx={you.p.x} cy={you.p.y} r={LAY.far.ring / 2} fill="none" stroke="#FFFFFF" strokeWidth={LAY.far.ringStroke} opacity={you.o * (1 - clamp(ug * 2))} />}
    </>
  );
};

// —— 四个你：黄、红、蓝、绿（就是放大的路线图）。每人头顶一盏灯：灯的冷暖亮暗 = 这一段的平均分（1.99 / 1.46 / 2.39 / 2.83）。
//    红衣那个灯最暗最冷、条最短、抱着胳膊；绿衣那个灯最暖最亮、条最长、笑着 ——
const lampWarm = (i: number) => {
  const lo = Math.min(...D.youAvg), hi = Math.max(...D.youAvg);
  return (D.youAvg[i] - lo) / (hi - lo);
};
const FOUR = [
  {s: I.ALLC, pose: still('idle'), e: EX.calm, x: 250},
  {s: I.GRIM, pose: still('cross'), e: EX.cold, x: 670},
  {s: I.TFT, pose: still('idle'), e: EX.stiff, x: 1090},
  {s: I.GTFT, pose: still('idle'), e: EX.smile, x: 1510},
];
// 第七版重排：hideGreen 不画绿衣那个你（S27 由 EndYou 接着画它走到结尾的位置），others 是另外三个你和四根条的不透明度
export const Four: React.FC<{f: number; up?: number; o?: number; hideGreen?: boolean; others?: number}> = ({f, up = 0, o = 1, hideGreen, others = 1}) => {
  const ap = ease(prog(f, eva('S25', 'appear')));
  const lamps = eva('S25', 'lamps');
  const G = 1220, s = 3.0;
  const sc = lerp(1, 0.08, ease(up));
  const ty = lerp(0, -(G - 164) * 0.92, ease(up));
  return (
    <g opacity={ap * (1 - ease(up)) * o} transform={`translate(900 ${G + ty}) scale(${sc}) translate(-900 ${-G})`}>
      <rect width={1920} height={1080} fill="#0B0E13" opacity={0.0} />
      {FOUR.map((q, i) => {
        const on = ease(prog(f, [lamps[i], lamps[i] + 6]));
        const k = lampWarm(i);
        if (hideGreen && i === 3) {
          return <Bar key={i} x={q.x} y={300} len={barLen(D.youAvg[i], 360) * on} full={360} h={56} color={COL[q.s]} o={(0.4 + 0.6 * on) * others} />;
        }
        return (
          <g key={i} opacity={i < 3 ? others : 1}>
            <YouLamp x={q.x} warm={k} on={on} y={212} G={G} />
            <Man f={f} pose={q.pose} expr={q.e} strategy={q.s} who="me" x={q.x} G={G} s={s} seed={`four${i}`}
              dim={lerp(0.62, 0.42 * (1 - k), on)} night={i === 1 ? '#0E1320' : '#0B0D12'}
              tint={{color: mixHex('#8E9BB3', '#FFD596', k), amount: 0.12 * on}} />
            <Bar x={q.x} y={300} len={barLen(D.youAvg[i], 360) * on} full={360} h={56} color={COL[q.s]} o={(0.4 + 0.6 * on) * (i < 3 ? 1 : others)} />
          </g>
        );
      })}
    </g>
  );
};

// —— 第七版 S26 / S26b：从第 300 代接着往下跑（data.json 的 cycle：0.5% 的新人，s[k] 是第 300 + k 代）——
// 代数按 timeline.json 的 cycle.keys 走（秒, 代），两点之间线性，最后一点之后停住：S26 第 300 → 750 代（好欺负的人多起来），S26b 第 750 → 860 代（狠人回来）。
// 一帧跨好几代：每颗点取这一帧前后几代（k±5）的平均色，像相机快门，不逐帧乱闪；中间那一代 s[k] 定这颗点算哪一种（光点、狠人判断）。
// 第七版三改：好欺负的人（cycle.soft：老实人、不点名）在这一幕都画成老实人的黄、满不透明度——观众要看到绿里长出一片黄、再被红吃掉；
// 片子前半段不点名的灰不动。其余颜色照实。
// 冷暖按这几代里狠人（骗子 + 记仇）的占比：0 → 最暖，85% 以上 → 最冷（第 62 代狠人 85% 时片子前半段就是最冷）。
// back（第 773 代狠人回到三成）、peak（第 840 代到 88%）：狠的点各亮一下（8 帧：往亮红 #FF6A4A 提四成，不往白提，免得发粉；柔光只加一点），整片跟着变冷。
const CYC = D.cycle;
const CYC_W = 5;
const LIFT = [255, 106, 74];     // 亮一下时往这个亮红提
const hexRgb = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const rgbHex = (c: number[]) => '#' + c.map((v) => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join('');
const SOFT = new Set<number>(TL.cycle.soft.map((c) => I[c as keyof typeof I]));
const PAL = COL.map((c, s) => {
  const base = SOFT.has(s) ? COL[I.ALLC] : c;
  return {col: hexRgb(base), sh: hexRgb(mixHex(base, '#000000', 0.24)), lt: hexRgb(mixHex(base, '#FFFFFF', 0.12)), o: 1};
});
const CYC_KEYS = TL.cycle.keys.map(([t, g]) => ({f: Math.round(t * TL.fps), g}));
export const cycleGen = (f: number) => {
  const K = CYC_KEYS;
  if (f <= K[0].f) return K[0].g;
  for (let i = 1; i < K.length; i++) if (f <= K[i].f) return lerp(K[i - 1].g, K[i].g, (f - K[i - 1].f) / Math.max(1e-6, K[i].f - K[i - 1].f));
  return K[K.length - 1].g;
};
export const cycleK = (f: number) => clamp(Math.round(cycleGen(f) - TL.cycle.gen0), 0, CYC.s.length - 1);
const harshShare = (k: number) => {
  const n = CYC.counts[k];
  return (n[I.ALLD] + n[I.GRIM]) / n.reduce((a, v) => a + v, 0);
};
// back / peak 挂在哪一拍就从哪一拍取（第七版三改在 S26b）
const evAny = (k: string) => TL.beats.find((bt) => bt.ev[k] !== undefined)!.ev[k] as number;
// 给 Crowd 的那几样（S26、S26b 和 S25 开头点阵淡出时共用）
export const cycleCrowd = (f: number) => {
  const k = cycleK(f);
  const a = Math.max(0, k - CYC_W), b = Math.min(CYC.s.length - 1, k + CYC_W);
  let h = 0;
  for (let j = a; j <= b; j++) h += harshShare(j);
  h /= b - a + 1;
  const w = clamp(1 - h / 0.85);
  const bump = (t: number) => Math.sin(Math.PI * prog(f, [t, t + 8]));
  const pulse = Math.max(bump(evAny('back')), bump(evAny('peak')));
  const row = CYC.s[k];
  const strat = (cell: number) => row.charCodeAt(cell) - 48;
  const paint = (cell: number) => {
    const col = [0, 0, 0], sh = [0, 0, 0], lt = [0, 0, 0];
    let o = 0, harsh = 0;
    const n = b - a + 1;
    for (let j = a; j <= b; j++) {
      const st = CYC.s[j].charCodeAt(cell) - 48;
      const P = PAL[st];
      for (let c = 0; c < 3; c++) { col[c] += P.col[c]; sh[c] += P.sh[c]; lt[c] += P.lt[c]; }
      o += P.o;
      if (HARSH(st)) harsh++;
    }
    const lift = 0.4 * pulse * (harsh / n);
    const up = (v: number[]) => rgbHex(v.map((x, c) => lerp(x / n, LIFT[c], lift)));
    return {col: up(col), sh: up(sh), lt: up(lt), o: o / n, glow: 0.6 * pulse * (harsh / n)};
  };
  return {strat, paint, coop: 1 - h, tintW: w, w};
};

// 第七版重排：S26 接在 S24 方块后面。gather 里方块反着散回点阵各自的格子，其余的点从压暗回到全亮（第 300 代，一片绿）；
// 路线图在这一拍开头退场（route 的 out）；run 照旧跑到第 900 代。不再画你的白圈（下一拍是四个你，不从你的点往里扎）
export const FOUR_GREEN = {x: 1510, G: 1220, s: 3.0, lampY: 212};
export const Cycle: React.FC<{f: number}> = ({f}) => {
  const [g0, g1] = eva('S26', 'gather');
  const gr = prog(f, [g0, g1]);
  const ug = ease(gr);
  const land = clamp((gr - 0.8) / 0.2);
  const cc = cycleCrowd(f);
  const dim = (cell: number) => (BLOCK_CELLS.has(cell) ? land : lerp(STARTERS.has(cell) ? 0.45 : 0.07, 1, ug));
  return (
    <>
      <CrowdFloor gen={300} w={cc.w} />
      <Crowd f={f} gen={300} cam={FAR} sparks={gr > 0.5} strat={cc.strat} paint={cc.paint} coop={cc.coop} tint={300} tintW={cc.tintW}
        dim={dim} ring={{o: 0}} />
      {land < 1 && <Block f={f} gen={300} ungather={gr} cellsOnly />}
    </>
  );
};

export const NL_ = NL;
