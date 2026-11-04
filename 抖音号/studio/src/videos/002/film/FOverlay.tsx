// 002 成片：顶栏（常驻小问题、第五版的路线图）、字幕带、“AI 生成”标（第七版去掉了 20 条历史条，HistBar / MeDot 一起删了）。
// 版面和字号照分镜第三节、第七节（timeline.json 的 layout）。
// 第五版：去掉“第 N 轮”计数器、顶上的历史条和开场大计数（观众不需要知道轮数），换成路线图：
//   顶上四个小头像“老实 → 狠 → 有来有往 → 原谅”，你在哪一段哪一个亮，没走到的是一个“？”（timeline.json 的 route）。
import React from 'react';
import {mixHex} from '../../../components/people/geom';
import {COL_HI, LAY, Line, SANS, Seg, TL, clamp, colOf, ease, lerp, prog} from '../lib';
import {FaceDot, YOU_BG, YOU_FG} from './fpeople';

// —— 字幕：固定两行高，单行放在下面那一行；数字 100 px，其余 88 px；上了色的字用打法颜色 ——
type SubStyle = {size: number; num: number; lineH: number; y0: number};
const DEF: SubStyle = {size: LAY.sub.size, num: LAY.sub.numSize, lineH: LAY.sub.lineH, y0: LAY.sub.y0};
const segs = (line: Line): Seg[] => (typeof line === 'string' ? [line] : line);
const SHADOW = '0 3px 0 rgba(0,0,0,0.35), 0 6px 22px rgba(0,0,0,0.7)';
const Text: React.FC<{s: string; color?: string; num: number; o?: number; glow?: number}> = ({s, color, num, o = 1, glow = 0}) => {
  const parts = s.split(/([0-9]+%?)/);
  const shadow = glow > 0 ? `0 0 ${18 + 26 * glow}px rgba(255,255,255,${0.6 * glow}), ${SHADOW}` : undefined;
  const st: React.CSSProperties = {color, opacity: o, textShadow: shadow, filter: glow > 0 ? `brightness(${1 + 0.4 * glow})` : undefined};
  return (
    <>
      {parts.map((t, i) => (/^[0-9]+%?$/.test(t)
        ? <span key={i} style={{...st, fontSize: num}}>{t}</span>
        : <span key={i} style={st}>{t}</span>))}
    </>
  );
};
// 字幕里上色的字：绿 / 粉换成亮一点的同色，暗底上读得清
const brightOf = (code: string) => (COL_HI as Record<string, string>)[code] ?? colOf(code);
export const SubLine: React.FC<{line: Line; top: number; f: number; st: SubStyle}> = ({line, top, f, st}) => (
  <div style={{
    position: 'absolute', top, height: st.lineH, left: LAY.sub.cx - 960, width: 1920,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: SANS, fontWeight: 600, fontSize: st.size, color: '#F6F3EC', letterSpacing: 0,
    whiteSpace: 'nowrap', textShadow: SHADOW,
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
      return <Text key={i} s={sg[0]} color={sg[1] ? brightOf(sg[1]) : undefined} num={st.num} o={o} glow={glow} />;
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

// 字幕带后面压暗（人腰以下沉进暗处）
export const SubBand: React.FC<{o?: number}> = ({o = 1}) => (
  <div style={{position: 'absolute', left: 0, top: 740, width: 1920, height: 340, opacity: o,
    background: 'linear-gradient(180deg, rgba(8,9,13,0) 0%, rgba(8,9,13,0.55) 26%, rgba(8,9,13,0.86) 52%, rgba(8,9,13,0.92) 100%)'}} />
);

// 常驻问题：0–1.6 秒是上方一行大题（132 px），之后缩到左上角（80 px，约三成亮）；
// 第五版：只挂到 3.8 秒，outP（S03 的 qOut）里淡出，把顶栏让给路线图
export const QUESTION_DIM = 0.32;
export const Question: React.FC<{f: number; outP?: number; o?: number}> = ({f, outP = 0, o: oMul = 1}) => {
  const q = TL.question;
  const t = ease(prog(f, [q.small[0], q.small[0] + 18]));
  const size = lerp(LAY.titleBig, LAY.top.questionSize, t);
  const w = size * 11;
  const left = lerp(960 - (LAY.titleBig * 11) / 2, 120, t);
  const top = lerp(56, LAY.top.y0, t);
  const o = lerp(1, QUESTION_DIM, t) * (1 - outP) * oMul;
  if (o <= 0.001) return null;
  return (
    <div style={{position: 'absolute', left, top, width: w + 40, height: size * 1.2, fontFamily: SANS, fontWeight: 700,
      fontSize: size, color: '#FFF8EC', opacity: o, whiteSpace: 'nowrap', lineHeight: `${size * 1.15}px`,
      textShadow: t < 0.5 ? '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)' : '0 3px 14px rgba(0,0,0,0.5)'}}>
      {q.text}
    </div>
  );
};

// “AI 生成”：左上角一直挂着（平台要求），压在最上层
export const AiBadge: React.FC = () => (
  <div style={{position: 'absolute', left: 22, top: 6, padding: '1px 12px', borderRadius: 7, fontFamily: SANS, fontWeight: 500,
    fontSize: 28, lineHeight: '34px', color: 'rgba(246,240,228,0.85)', background: 'rgba(0,0,0,0.42)',
    border: '1.5px solid rgba(246,240,228,0.32)', letterSpacing: '0.04em'}}>AI 生成</div>
);

// —— 第五版：路线图。顶部中间（中心 x 900，和字幕同一条中线），整块在 y 24–170；四个小圆脸（片里中景那套，有眼睛），之间暗箭头，头像下面写名字（56 px）——
// 当前格：全亮、放大 1.18 倍、一圈柔光；亮出来了但不是当前的：压到约一半亮；没走到的：暗灰圆里一个“？”，不写名字。
// 动作（timeline.json 的 route.keys）：in 12 帧淡入；reveal “？”翻成头像（8 帧弹出），名字淡入，当前标记从上一格滑过来；
// ask 没亮出来的“？”一个接一个跳一下；back 当前标记滑回老实；on 当前标记换到已亮出来的那一格；out 9 帧淡出。
export const RT = {cx: 900, sp: 280, y: 64, r: 34, nameY: 160, nameSize: 56};
export const routeX = (i: number) => RT.cx + (i - 1.5) * RT.sp;
const RT_YOU_X = routeX(0) - 150;   // 第六版：“你”牌的中心
const SLIDE = 12;          // 当前标记滑过去用的帧数
const FLIP = 8;            // “？”翻成头像用的帧数
const stageCol = (code: string) => colOf(code === 'HARSH' ? 'GRIM' : code);
export const routeState = (f: number) => {
  const K = TL.route.keys;
  const inK = K.find((k) => k.act === 'in');
  const outK = K.find((k) => k.act === 'out');
  if (!inK || f < inK.f) return null;
  if (outK && f >= outK.f + 9) return null;
  // 淡入先慢后快（平方）：同一段里左上角的小问题先快后慢地淡掉（Film002 里 qOut 用 easeOut），两样叠着的那几帧都很淡，不糊成一片
  const o = Math.pow(prog(f, [inK.f, inK.f + 12]), 2) * (outK ? 1 - ease(prog(f, [outK.f, outK.f + 9])) : 1);
  const rev = TL.route.stages.map((_, i) => (i === inK.i ? inK.f : Infinity));
  for (const k of K) if (k.act === 'reveal' && !(rev[k.i] <= k.f)) rev[k.i] = k.f;
  let cur = inK.i, prev = inK.i, moveF = -1e9;
  for (const k of K) {
    if (k.f > f) break;
    if (k.act === 'reveal' || k.act === 'back' || k.act === 'on') { prev = cur; cur = k.i; moveF = k.f; }
  }
  const pos = lerp(prev, cur, ease(prog(f, [moveF, moveF + SLIDE])));
  return {o, rev, pos, cur, asks: K.filter((k) => k.act === 'ask').map((k) => k.f)};
};

const Arrow: React.FC<{x0: number; x1: number; y: number; o: number}> = ({x0, x1, y, o}) => (
  <g opacity={o} stroke="#C9CDD6" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" fill="none">
    <line x1={x0} y1={y} x2={x1} y2={y} />
    <path d={`M ${x1 - 14} ${y - 13} L ${x1} ${y} L ${x1 - 14} ${y + 13}`} />
  </g>
);

export const RouteMap: React.FC<{f: number; o?: number}> = ({f, o: oMul = 1}) => {
  const st = routeState(f);
  if (!st || st.o * oMul <= 0.001) return null;
  const {rev, pos, asks} = st;
  const stages = TL.route.stages;
  const shown = (i: number) => f >= rev[i];
  // 没亮出来的“？”在 ask 时一个接一个跳一下（间隔 3 帧，每个 10 帧）
  const hop = (i: number) => {
    const hidden = stages.map((_, j) => j).filter((j) => !shown(j));
    const n = hidden.indexOf(i);
    if (n < 0) return 0;
    return asks.reduce((m, a) => Math.max(m, Math.sin(Math.PI * prog(f, [a + n * 3, a + n * 3 + 10]))), 0);
  };
  const mx = lerp(routeX(Math.floor(pos)), routeX(Math.ceil(pos)), pos - Math.floor(pos));
  const curCol = stageCol(stages[Math.round(pos)].code);
  return (
    <g opacity={st.o * oMul}>
      {/* 当前标记：一圈柔光，跟着当前格滑 */}
      <circle cx={mx} cy={RT.y} r={RT.r * 2.5} fill="url(#gRouteGlow)" />
      <circle cx={mx} cy={RT.y} r={RT.r * 1.6} fill={mixHex(curCol, '#FFFFFF', 0.35)} opacity={0.22} filter="url(#fBlur8)" />
      {/* 第六版：最左边一块白底“你”牌（和人身上的“你”同款），箭头接到“老实”：读成“你 → 老实 → 狠 → …”（成片测试两人都没看懂这排小脸是什么） */}
      <rect x={RT_YOU_X - 36} y={RT.y - 36} width={72} height={72} rx={14} fill="#000" opacity={0.4} filter="url(#fBlur4)" />
      <rect x={RT_YOU_X - 36} y={RT.y - 38} width={72} height={72} rx={14} fill={YOU_BG} />
      <text x={RT_YOU_X} y={RT.y + 16} fontSize={50} fontFamily={SANS} fontWeight={800} fill={YOU_FG} textAnchor="middle">你</text>
      <Arrow x0={RT_YOU_X + 36 + 16} x1={routeX(0) - RT.r - 20} y={RT.y} o={0.42} />
      {stages.slice(0, -1).map((_, i) => (
        <Arrow key={`a${i}`} x0={routeX(i) + RT.r + 20} x1={routeX(i + 1) - RT.r - 20} y={RT.y} o={shown(i + 1) ? 0.42 : 0.26} />
      ))}
      {stages.map((sg, i) => {
        const x = routeX(i);
        const k = clamp(1 - Math.abs(pos - i));               // 离当前标记多近
        const fl = i === 0 ? 1 : prog(f, [rev[i], rev[i] + FLIP]);
        const pop = i === 0 ? 0 : Math.sin(Math.PI * prog(f, [rev[i], rev[i] + FLIP + 2]));
        const isFace = shown(i) && fl >= 0.5;
        const sx = shown(i) && fl < 1 ? Math.abs(Math.cos(Math.PI * fl)) : 1;     // 翻牌：先压扁“？”，再展开头像
        const sc = (isFace ? lerp(1, 1.18, k) : 1) * (1 + 0.2 * pop);
        const dy = -20 * hop(i);
        const faceO = isFace ? lerp(0.5, 1, k) : 1;
        const nameO = shown(i) ? lerp(0.5, 1, k) * ease(prog(f, [rev[i] + 3, rev[i] + 11])) : 0;
        const lid = ((Math.floor(f) + i * 41) % 113) < 3 ? 1 : 0;
        return (
          <g key={i}>
            <g transform={`translate(${x} ${RT.y + dy}) scale(${sx * sc} ${sc}) translate(${-x} ${-RT.y})`}>
              {isFace ? (
                <g opacity={faceO}>
                  <circle cx={x + 3} cy={RT.y + 6} r={RT.r} fill="#000" opacity={0.4} filter="url(#fBlur4)" />
                  <FaceDot x={x} y={RT.y} r={RT.r} color={stageCol(sg.code)} gx={0.6} lid={lid} shadow={false} />
                </g>
              ) : (
                <g>
                  <circle cx={x} cy={RT.y} r={RT.r} fill="#262A34" />
                  <circle cx={x} cy={RT.y} r={RT.r - 3} fill="none" stroke="#3A3F4B" strokeWidth={3} />
                  <text x={x} y={RT.y + 15} fontSize={44} fontFamily={SANS} fontWeight={800} fill="#9EA3AE" textAnchor="middle">?</text>
                </g>
              )}
            </g>
            {nameO > 0.001 && (
              <g opacity={nameO}>
                <text x={x + 2} y={RT.nameY + 4} fontSize={RT.nameSize} fontFamily={SANS} fontWeight={700} fill="#000" opacity={0.55}
                  textAnchor="middle" filter="url(#fBlur4)">{sg.label}</text>
                <text x={x} y={RT.nameY} fontSize={RT.nameSize} fontFamily={SANS} fontWeight={700} fill="#F6F3EC" textAnchor="middle">{sg.label}</text>
              </g>
            )}
          </g>
        );
      })}
    </g>
  );
};
export const RouteDefs: React.FC = () => (
  <defs>
    <radialGradient id="gRouteGlow">
      <stop offset="0" stopColor="#FFF4DC" stopOpacity={0.42} />
      <stop offset="0.45" stopColor="#FFE7B8" stopOpacity={0.16} />
      <stop offset="1" stopColor="#FFE7B8" stopOpacity={0} />
    </radialGradient>
  </defs>
);
