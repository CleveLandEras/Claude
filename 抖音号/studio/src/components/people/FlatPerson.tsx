// 画风 A：扁平矢量小人。大头（约 2.65 头身），黑点眼带白高光，会演的小弯眉，嘴几笔，一块头发，
// 衣服一个主色加一层暗面。不描边、不用渐变。四肢是“锥形管”：沿肩、肘、腕算一条平滑中线，
// 每点一个半径，拼成一整块（不是胶囊叠起来）。暗面 = 同一块形状往光的方向挪一点、和原形状相交，剩下的那条边。
import React, {useId} from 'react';
import {P, add, clamp, crSample, lerp, mixHex, nrm, polyPath, rot, smoothClosed, smoothOpen, tube} from './geom';
import {HandShape, RPose, Skel, solve} from './rig';
import {Expr} from './face';
import {Look} from './look';

export type Glow = {at: P; color: string; amount: number; r?: number};
export type FlatPersonProps = {
  pose: RPose; expr: Expr; look: Look;
  x: number; y: number; s: number; facing?: 1 | -1;
  dim?: number; night?: string;       // 离灯远时压暗：往 night 色混
  light?: P;                          // 光从哪边来（屏幕方向），暗面在另一边
  glow?: Glow;                        // 一处小光源照在人身上（手机屏），坐标在身体单位里
  phone?: {lit: number; tilt?: number};   // 两手之间拿着一部手机；lit：屏幕亮度 0..1
  part?: 'all' | 'body' | 'arms';          // 坐在桌子后面时：先画身子，再画桌子，最后单画搭在桌上的两条胳膊
  debug?: boolean;
};

const loc = (o: P, ang: number, x: number, y: number) => add(o, rot({x, y}, ang));

// —— 脸 ——
export const faceLayout = (yaw: number, pitch: number) => {
  const fx = yaw * 22, fy = pitch * 13;
  const es = 35 - 12 * yaw;
  return {
    fx, fy, ey: 9 + fy,
    eyes: [
      {x: fx + es / 2, sc: 1, side: 1},
      {x: fx - es / 2 + 2 * yaw, sc: 1 - 0.22 * yaw, side: -1},
    ],
    mouth: {x: fx + 2.5 * yaw, y: 29 + fy * 0.9},
    earX: -50 * Math.cos((yaw * 85 * Math.PI) / 180),
  };
};

export const mouthCurves = (e: Expr, mx: number, my: number) => {
  const hw = 6.4 * e.mouthW * (1 - 0.42 * e.round);
  const N = 16;
  const up: P[] = [], lo: P[] = [];
  for (let i = 0; i <= N; i++) {
    const u = -1 + (2 * i) / N;
    const ring = Math.sqrt(Math.max(0, 1 - u * u));
    const y0 = my - e.smile * 3.4 * u * u + e.wobble * 1.25 * Math.sin(u * Math.PI * 2.2) * (1 - e.open)
      - e.round * e.open * 3.2 * ring - e.smirk * 3.2 * Math.max(0, u) * u;
    up.push({x: mx + u * hw, y: y0});
    lo.push({x: mx + u * hw, y: y0 + e.open * (7.5 + 3.5 * e.round) * Math.pow(ring, 0.75)});
  }
  return {up, lo, hw};
};

export const browLine = (e: Expr, ex: number, by0: number, side: number, sc: number) => {
  const by = by0 - (side > 0 ? e.asym * 4.5 : -e.asym * 1.2);
  const ia = side > 0 ? 1 - 0.8 * Math.max(0, e.asym) : 1;   // 挑起来的那条眉，眉头不往下压
  const inner = {x: ex - side * (6.6 * sc + e.knit * 2.4), y: by - e.browIn * 4.4 * (e.browIn < 0 ? ia : 1)};
  const outer = {x: ex + side * 6.8 * sc, y: by + e.browIn * 1.6 - e.brow * 0.6};
  const c = {x: (inner.x + outer.x) / 2, y: (inner.y + outer.y) / 2 - 2.4 - e.browArc * 3.2};
  return {inner, outer, c};
};

const Face: React.FC<{e: Expr; r: RPose; look: Look; id: string; C: (c: string) => string}> = ({e, r, look, id, C}) => {
  const L = faceLayout(r.yaw, r.pitch);
  const by = L.ey - 15.5 - e.brow * 5.5 + e.lid * 2.5;
  const m = mouthCurves(e, L.mouth.x, L.mouth.y);
  return (
    <g>
      {/* 腮红 */}
      {L.eyes.map((o, i) => (
        <ellipse key={`b${i}`} cx={o.x + o.side * 3} cy={L.ey + 11.5} rx={7.2 * o.sc} ry={3.9} fill={C(look.blush)} opacity={0.6 * e.blush} />
      ))}
      {/* 眼睛 */}
      {L.eyes.map((o, i) => {
        const rx = 5.2 * e.eye * o.sc, ry = 6.5 * e.eye;
        const cx = o.x + r.gx * 2.4, cy = L.ey + r.gy * 2.2;
        const k = `${id}e${i}`;
        if (e.lid >= 0.88) {
          const c = Math.abs(e.closed) > 0.05 ? e.closed : -0.7;
          return (
            <path key={k} d={`M ${cx - rx - 1.6} ${cy + 0.5} Q ${cx} ${cy - 6 * c} ${cx + rx + 1.6} ${cy + 0.5}`}
              fill="none" stroke={C(look.eye)} strokeWidth={2.6} strokeLinecap="round" />
          );
        }
        const cutY = cy - ry + 2 * ry * e.lid * 0.96;
        const s0 = clamp((cutY - cy) / ry, -1, 1);
        const t0 = Math.asin(s0);
        const xa = cx + rx * Math.cos(t0);
        const xb = cx - rx * Math.cos(t0);
        const large = t0 < 0 ? 1 : 0;
        const eyeD = e.lid < 0.02
          ? `M ${cx + rx} ${cy} A ${rx} ${ry} 0 1 1 ${cx - rx} ${cy} A ${rx} ${ry} 0 1 1 ${cx + rx} ${cy} Z`
          : `M ${xa} ${cutY} A ${rx} ${ry} 0 ${large} 1 ${xb} ${cutY} Z`;
        const hy = Math.max(cy - 2.5 * e.eye, cutY + 2.2);
        return (
          <g key={k}>
            <clipPath id={k}><path d={eyeD} /></clipPath>
            <path d={eyeD} fill={C(look.eye)} />
            {e.tear > 0.01 && (
              <g clipPath={`url(#${k})`}>
                <ellipse cx={cx} cy={cy + ry * 0.62} rx={rx * 1.1} ry={ry * 0.52} fill="#9CCBF2" opacity={0.85 * e.tear} />
              </g>
            )}
            {e.lid > 0.08 && (
              <line x1={xb - 1.4} y1={cutY} x2={xa + 1.4} y2={cutY} stroke={C(look.eye)} strokeWidth={2} strokeLinecap="round" />
            )}
            {hy < cy + ry - 2 && <circle cx={cx + 1.8 * o.sc} cy={hy} r={1.9 * e.shine} fill="#FFFFFF" />}
            {(e.shine > 1.15 || e.tear > 0.3) && hy < cy + ry - 3 && (
              <circle cx={cx - 1.7 * o.sc} cy={cy + 2.6} r={0.95 * e.shine} fill="#FFFFFF" opacity={0.9} />
            )}
            {e.tear > 0.01 && (
              <>
                <path d={`M ${cx - rx * 0.9} ${cy + ry + 1.6} Q ${cx} ${cy + ry + 3.6} ${cx + rx * 0.9} ${cy + ry + 1.6}`}
                  fill="none" stroke="#A8D6FA" strokeWidth={1.5} strokeLinecap="round" opacity={e.tear} />
                <path transform={`translate(${cx + o.side * rx * 0.95} ${cy + ry + 4.5}) scale(${0.9 * e.tear})`}
                  d="M 0 -4.6 C 2.2 -1.6 3.2 0.8 3.2 2.1 C 3.2 4 1.7 5.3 0 5.3 C -1.7 5.3 -3.2 4 -3.2 2.1 C -3.2 0.8 -2.2 -1.6 0 -4.6 Z"
                  fill="#CDEBFF" />
              </>
            )}
          </g>
        );
      })}
      {/* 眉毛 */}
      {L.eyes.map((o, i) => {
        const b = browLine(e, o.x, by, o.side, o.sc);
        return <path key={`w${i}`} d={`M ${b.inner.x} ${b.inner.y} Q ${b.c.x} ${b.c.y} ${b.outer.x} ${b.outer.y}`}
          fill="none" stroke={C(look.brow)} strokeWidth={3.3} strokeLinecap="round" />;
      })}
      {/* 嘴 */}
      {e.open < 0.06 ? (
        <path d={smoothOpen(m.up)} fill="none" stroke={C(look.mouth)} strokeWidth={2.5} strokeLinecap="round" />
      ) : (
        <g>
          <clipPath id={`${id}m`}><path d={polyPath([...m.up, ...m.lo.slice().reverse()])} /></clipPath>
          <path d={polyPath([...m.up, ...m.lo.slice().reverse()])} fill={C(look.mouth)} stroke={C(look.mouth)} strokeWidth={1.2} strokeLinejoin="round" />
          <g clipPath={`url(#${id}m)`}>
            <ellipse cx={L.mouth.x} cy={m.lo[8].y + 1} rx={m.hw * 0.62} ry={2.2 + 2.4 * e.open} fill="#D9776E" />
          </g>
        </g>
      )}
    </g>
  );
};

// —— 头发 ——
const hairShort = (yaw: number, pitch: number, earX: number) => {
  const fx = yaw * 22, fb = -31 + pitch * 11;
  const cap: P[] = [
    {x: -47 + 6 * yaw, y: 22 + 2 * yaw}, {x: -56, y: 2}, {x: -54, y: -26}, {x: -40, y: -49},
    {x: -14, y: -61}, {x: 16, y: -61}, {x: 40, y: -50}, {x: 53, y: -30}, {x: 55.5, y: -9},
  ];
  const tips = [
    {x: Math.min(51, fx + 37), y: fb + 7}, {x: fx + 19, y: fb + 12}, {x: fx - 1, y: fb + 9},
    {x: fx - 20, y: fb + 12}, {x: Math.max(earX + 8, fx - 36), y: fb + 7},
  ];
  const notch = [fb - 4, fb - 6, fb - 3, fb - 5];
  let d = `M ${cap[0].x} ${cap[0].y}`;
  const capPts = crSample(cap, 6);
  capPts.forEach((p) => {
    d += ` L ${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
  });
  d += ` Q ${(cap[cap.length - 1].x + tips[0].x) / 2 + 2} ${fb - 2} ${tips[0].x} ${tips[0].y}`;
  for (let i = 1; i < tips.length; i++) {
    d += ` Q ${(tips[i - 1].x + tips[i].x) / 2} ${notch[i - 1]} ${tips[i].x} ${tips[i].y}`;
  }
  // 鬓角、耳朵上面、绕到耳后
  d += ` Q ${earX + 10} ${fb + 6} ${earX + 7} ${-6} L ${earX + 1} ${-11} C ${earX - 6} ${-10} ${earX - 11} ${0} ${earX - 9} ${12} Z`;
  // 头顶翘起的一撮（这个人的记号）
  const tuft = `M ${-6 + 4 * yaw} ${-59} C ${-10 + 4 * yaw} ${-74} ${-2 + 4 * yaw} ${-84} ${10 + 4 * yaw} ${-82} C ${2 + 4 * yaw} ${-78} ${0 + 4 * yaw} ${-70} ${6 + 4 * yaw} ${-60} Z`;
  return {d, tuft};
};

const hairBob = (yaw: number, pitch: number, earX: number) => {
  const fx = yaw * 22, fb = -28 + pitch * 11;
  const back = smoothClosed([
    {x: -58, y: -18}, {x: -60, y: 14}, {x: -54, y: 40}, {x: -36, y: 46}, {x: -10, y: 30},
    {x: 20, y: 30}, {x: 46, y: 40}, {x: 58, y: 18}, {x: 56, y: -20},
  ]);
  const cap: P[] = [
    {x: earX - 12, y: 36}, {x: -58, y: 4}, {x: -55, y: -28}, {x: -38, y: -51}, {x: -10, y: -61},
    {x: 20, y: -59}, {x: 43, y: -46}, {x: 55, y: -22}, {x: 56, y: 6}, {x: 52, y: 34},
  ];
  let d = '';
  const pts = crSample(cap, 6);
  pts.forEach((p, i) => {
    d += `${i ? ' L' : 'M'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
  });
  // 右边一缕垂到下巴，刘海斜着扫向左边
  d += ` Q ${fx + 46} ${10} ${fx + 40} ${fb + 4} Q ${fx + 20} ${fb - 10} ${fx - 6} ${fb + 6} Q ${fx - 20} ${fb + 12} ${earX + 10} ${fb + 10}`;
  d += ` Q ${earX + 6} ${14} ${earX - 2} ${36} Z`;
  return {back, d};
};

// —— 手 ——（手腕为原点，+y 沿手的方向，+x 朝脸那一侧）
const handPath = (h: HandShape) => {
  switch (h) {
    case 'fist':
      return smoothClosed([{x: -6, y: 2}, {x: -6.5, y: 9}, {x: 0, y: 13}, {x: 6.5, y: 9}, {x: 6.5, y: 2}, {x: 0, y: -1}]);
    case 'hold':
      return smoothClosed([{x: -6, y: 1}, {x: -6.8, y: 9}, {x: -2, y: 14}, {x: 4, y: 12}, {x: 6.6, y: 6}, {x: 9.5, y: 1}, {x: 8, y: -2.5}, {x: 3, y: -1}]);
    case 'limp':
      return smoothClosed([{x: -5.5, y: 1}, {x: -6, y: 10}, {x: -2, y: 16}, {x: 3, y: 15}, {x: 5.6, y: 9}, {x: 7.5, y: 6}, {x: 5.5, y: 1}]);
    default:
      return smoothClosed([{x: -6, y: 1}, {x: -6.5, y: 10}, {x: -2.5, y: 16}, {x: 3.5, y: 15}, {x: 6, y: 9}, {x: 9.5, y: 5}, {x: 7.5, y: 1.5}, {x: 4.5, y: 2}]);
  }
};

// —— 鞋 ——（脚踝为原点，+x 脚尖方向）
const shoePath = (fl: number) => smoothClosed([
  {x: -8, y: -3}, {x: -8.5, y: 4}, {x: -6, y: 8}, {x: 6, y: 8.5}, {x: 24 * fl, y: 8.5}, {x: 24 * fl + 3.5, y: 5},
  {x: 24 * fl + 1, y: 0.5}, {x: 13 * fl, y: -3.5}, {x: 3, y: -6.5},
]);

export const FlatPerson: React.FC<FlatPersonProps> = (p) => {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');
  const {look, expr: e} = p;
  const r = p.pose;
  const sk: Skel = solve(r);
  const facing = p.facing ?? 1;
  const dim = p.dim ?? 0;
  const night = p.night ?? '#0E0B10';
  const C = (c: string) => (dim > 0 ? mixHex(c, night, dim) : c);
  const lightV = nrm(p.light ?? {x: -0.35, y: -1});
  const lv = {x: lightV.x * facing, y: lightV.y};
  const yaw = r.yaw;

  const Shaded = ({d, base, shade, k, id}: {d: string; base: string; shade: string; k: number; id: string}) => (
    <g>
      <clipPath id={id}><path d={d} /></clipPath>
      <path d={d} fill={C(shade)} />
      <g clipPath={`url(#${id})`}><path d={d} fill={C(base)} transform={`translate(${lv.x * k} ${lv.y * k})`} /></g>
    </g>
  );

  const limb = (a: P, b: P, c: P, r0: number, r1: number, r2: number) => {
    const pts = crSample([a, b, c], 7);
    const n = pts.length - 1;
    const radii = pts.map((_, i) => {
      const t = i / n;
      return t < 0.5 ? lerp(r0, r1, t * 2) : lerp(r1, r2, (t - 0.5) * 2);
    });
    return tube(pts, radii);
  };
  const armD = (s: P, el: P, w: P) => limb(s, el, w, 8.2, 7, 5.9);
  const legD = (h: P, k: P, a: P) => limb(h, k, a, 11.2, 8.8, 7.2);

  const hand = (w: P, ang: number, h: HandShape, shade: boolean, key: string) => {
    if (h === 'pocket') return null;
    return <path key={key} d={handPath(h)} fill={C(shade ? look.skinShade : look.skin)} transform={`translate(${w.x} ${w.y}) rotate(${ang})`} />;
  };
  const fl = 0.42 + 0.58 * yaw;
  const shoe = (an: P, ang: number, shade: boolean, key: string) => (
    <g key={key} transform={`translate(${an.x} ${an.y}) rotate(${ang})`}>
      <clipPath id={`${uid}${key}c`}><path d={shoePath(fl)} /></clipPath>
      <path d={shoePath(fl)} fill={C(shade ? look.shoeShade : look.shoe)} />
      <g clipPath={`url(#${uid}${key}c)`}><rect x={-12} y={5.2} width={40} height={6} fill={C(look.sole)} /></g>
    </g>
  );

  // 躯干（连帽衫 / 外套）：沿脊柱三个框架取点，平滑成一整块
  const wc = lerp(30, 21, yaw), wm = lerp(27.5, 20.5, yaw), wh = lerp(29.5, 22.5, yaw);
  const hemY = look.coat ? 40 : 11;
  const hemW = look.coat ? wh * 1.12 : wh;
  const fb = 1 + 0.12 * yaw, bb = 1 - 0.04 * yaw;   // 侧过去时肚子那边鼓一点
  const torsoPts: P[] = [
    loc(sk.chest, sk.angC, lerp(10, 8, yaw), -5),
    loc(sk.chest, sk.angC, wc * 0.8, -1),
    loc(sk.chest, sk.angC, wc * 1.0 * fb, 10),
    loc(sk.mid, sk.angM, wm * 1.03 * fb, 2),
    loc(sk.pelvis, sk.angP, hemW * fb, hemY - 2),
    loc(sk.pelvis, sk.angP, hemW * 0.4, hemY + 3),
    loc(sk.pelvis, sk.angP, -hemW * 0.4, hemY + 3),
    loc(sk.pelvis, sk.angP, -hemW * bb, hemY - 2),
    loc(sk.mid, sk.angM, -wm * bb, 2),
    loc(sk.chest, sk.angC, -wc * bb, 10),
    loc(sk.chest, sk.angC, -wc * 0.78, -1),
    loc(sk.chest, sk.angC, -lerp(10, 13, yaw), -5),
  ];
  const torsoD = smoothClosed(torsoPts);
  const neckD = tube([loc(sk.chest, sk.angC, 0, 4), sk.neckTop], [6.6, 6.2]);
  const hoodD = smoothClosed([
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) - 15, -9),
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) - 2, -13),
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) + 12, -9),
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) + 14, -2),
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) - 1, 1),
    loc(sk.chest, sk.angC, -lerp(4, 6, yaw) - 18, -2),
  ]);
  const pocketD = smoothClosed([
    loc(sk.pelvis, sk.angP, -wh * 0.55 + 8 * yaw, 6), loc(sk.mid, sk.angM, -wm * 0.42 + 9 * yaw, 4),
    loc(sk.mid, sk.angM, wm * 0.42 + 9 * yaw, 4), loc(sk.pelvis, sk.angP, wh * 0.55 + 8 * yaw, 6),
  ], 0.4);

  const L = faceLayout(yaw, r.pitch);
  const headD = smoothClosed(Array.from({length: 20}, (_, i) => {
    const t = (i / 20) * Math.PI * 2;
    const c = Math.cos(t), s = Math.sin(t);
    const x = 52 * Math.sign(c) * Math.pow(Math.abs(c), 0.9);
    const y = 49 * Math.sign(s) * Math.pow(Math.abs(s), 0.92);
    const jaw = y > 0 ? 1 - 0.1 * (y / 49) ** 2 : 1;
    const cheek = x > 0 ? 1 + 0.03 * yaw : 1 - 0.02 * yaw;
    return {x: x * jaw * cheek, y};
  }));
  const hair = look.hairStyle === 'bob' ? null : hairShort(yaw, r.pitch, L.earX);
  const bob = look.hairStyle === 'bob' ? hairBob(yaw, r.pitch, L.earX) : null;
  const ear = (x: number, key: string) => (
    <g key={key}>
      <ellipse cx={x} cy={5} rx={7.5} ry={10} fill={C(look.skin)} />
      <ellipse cx={x + 1} cy={5.5} rx={3.6} ry={5.6} fill={C(look.skinShade)} />
    </g>
  );

  const head = (
    <g transform={`translate(${sk.head.x} ${sk.head.y}) rotate(${sk.angH})`}>
      {bob && <path d={bob.back} fill={C(look.hair)} />}
      {yaw < 0.3 && ear(L.earX + 2, 'el')}
      {yaw < 0.3 && ear(-L.earX - 2, 'er')}
      <path d={headD} fill={C(look.skin)} />
      <clipPath id={`${uid}hd`}><path d={headD} /></clipPath>
      {yaw >= 0.3 && ear(L.earX, 'e1')}
      <Face e={e} r={r} look={look} id={uid} C={C} />
      {hair && <path d={hair.d} fill={C(look.hair)} />}
      {hair && <path d={hair.tuft} fill={C(look.hair)} />}
      {hair && <path d={`M ${-30} ${-44} Q ${-12} ${-55} ${10} ${-54}`} fill="none" stroke={C(look.hairHi)} strokeWidth={3} strokeLinecap="round" />}
      {bob && <path d={bob.d} fill={C(look.hair)} />}
      {bob && <path d={`M ${-28} ${-46} Q ${-8} ${-56} ${14} ${-54}`} fill="none" stroke={C(look.hairHi)} strokeWidth={3} strokeLinecap="round" />}
    </g>
  );

  const nearArm = (
    <g key="na">
      <Shaded d={armD(sk.sN, sk.eN, sk.wN)} base={look.top} shade={look.topShade} k={3} id={`${uid}an`} />
      {hand(sk.wN, sk.handN, r.hN, false, 'hn')}
      {r.hN === 'pocket' && !look.coat && <path d={pocketD} fill={C(look.topShade)} />}
    </g>
  );

  // 手机：两手之间，背面朝观众（深色机身、一圈侧边、摄像头），屏幕的光往脸上照
  const phone = p.phone ? (() => {
    const c = {x: (sk.wN.x + sk.wF.x) / 2, y: (sk.wN.y + sk.wF.y) / 2};
    const ang = (sk.handN + sk.handF) / 2 + 90 + (p.phone.tilt ?? 0);
    const pc = add(c, rot({x: 0, y: 7}, (sk.handN + sk.handF) / 2));
    return (
      <g transform={`translate(${pc.x} ${pc.y}) rotate(${ang})`}>
        <rect x={-15} y={-8.5} width={30} height={17} rx={3.6} fill={C('#1B1D24')} />
        <rect x={-15} y={-8.5} width={30} height={3.4} rx={1.7} fill={C('#3A3F4C')} />
        <rect x={9} y={-5} width={4.2} height={6} rx={1.6} fill={C('#2C303A')} />
        <rect x={-15} y={5.6} width={30} height={2.9} rx={1.4} fill="#CFE2FF" opacity={0.25 + 0.6 * p.phone.lit} />
      </g>
    );
  })() : null;

  const g = p.glow;
  const glowLayer = g && g.amount > 0 ? (
    <g style={{mixBlendMode: 'screen'}} opacity={g.amount}>
      <defs>
        <radialGradient id={`${uid}gl`} cx={g.at.x} cy={g.at.y} r={g.r ?? 80} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor={g.color} stopOpacity={0.95} />
          <stop offset="0.45" stopColor={g.color} stopOpacity={0.45} />
          <stop offset="1" stopColor={g.color} stopOpacity={0} />
        </radialGradient>
        <clipPath id={`${uid}gc`}>
          <path d={torsoD} />
          <path d={headD} transform={`translate(${sk.head.x} ${sk.head.y}) rotate(${sk.angH})`} />
          <path d={handPath(r.hN)} transform={`translate(${sk.wN.x} ${sk.wN.y}) rotate(${sk.handN})`} />
          <path d={handPath(r.hF)} transform={`translate(${sk.wF.x} ${sk.wF.y}) rotate(${sk.handF})`} />
          <path d={armD(sk.sN, sk.eN, sk.wN)} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${uid}gc)`}>
        <circle cx={g.at.x} cy={g.at.y} r={g.r ?? 80} fill={`url(#${uid}gl)`} />
      </g>
    </g>
  ) : null;

  const front = r.front > 0.5;
  const part = p.part ?? 'all';
  if (part === 'arms') {
    return (
      <g transform={`translate(${p.x} ${p.y}) scale(${p.s * facing} ${p.s})`}>
        <Shaded d={armD(sk.sF, sk.eF, sk.wF)} base={look.topShade} shade={mixHex(look.topShade, '#000000', 0.2)} k={3} id={`${uid}af`} />
        {hand(sk.wF, sk.handF, r.hF, true, 'hf')}
        {nearArm}
        {phone}
        {glowLayer}
      </g>
    );
  }
  const arms = part === 'all';
  return (
    <g transform={`translate(${p.x} ${p.y}) scale(${p.s * facing} ${p.s})`}>
      {/* 远侧：手臂、腿，都用暗面色 */}
      {arms && !front && <path d={armD(sk.sF, sk.eF, sk.wF)} fill={C(look.topShade)} />}
      {arms && !front && hand(sk.wF, sk.handF, r.hF, true, 'hf')}
      <path d={legD(sk.hipF, sk.kF, sk.anF)} fill={C(look.bottomShade)} />
      {shoe(sk.anF, sk.footF, true, 'sf')}
      {/* 胯、近侧腿 */}
      <path d={tube([sk.hipF, sk.hipN], [12, 12])} fill={C(look.bottom)} />
      <Shaded d={legD(sk.hipN, sk.kN, sk.anN)} base={look.bottom} shade={look.bottomShade} k={3.4} id={`${uid}ln`} />
      {shoe(sk.anN, sk.footN, false, 'sn')}
      {/* 脖子、帽子、上身 */}
      <path d={neckD} fill={C(look.skinShade)} />
      {look.hood && <path d={hoodD} fill={C(look.topShade)} />}
      <Shaded d={torsoD} base={look.top} shade={look.topShade} k={7} id={`${uid}t`} />
      {arms && !front && nearArm}
      {arms && phone}
      {head}
      {arms && front && <path d={armD(sk.sF, sk.eF, sk.wF)} fill={C(look.topShade)} />}
      {arms && front && hand(sk.wF, sk.handF, r.hF, true, 'hf2')}
      {arms && front && nearArm}
      {glowLayer}
      {p.debug && <Debug sk={sk} />}
    </g>
  );
};

const Debug: React.FC<{sk: Skel}> = ({sk}) => {
  const L = (a: P, b: P, c: string) => <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={c} strokeWidth={1.2} />;
  return (
    <g opacity={0.9}>
      {L(sk.pelvis, sk.mid, '#0f0')}{L(sk.mid, sk.chest, '#0f0')}{L(sk.chest, sk.neckTop, '#0f0')}
      {L(sk.sN, sk.eN, '#f0f')}{L(sk.eN, sk.wN, '#f0f')}{L(sk.sF, sk.eF, '#a0a')}{L(sk.eF, sk.wF, '#a0a')}
      {L(sk.hipN, sk.kN, '#0ff')}{L(sk.kN, sk.anN, '#0ff')}{L(sk.hipF, sk.kF, '#088')}{L(sk.kF, sk.anF, '#088')}
      <circle cx={sk.head.x} cy={sk.head.y} r={2} fill="#ff0" />
    </g>
  );
};
