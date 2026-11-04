// 画风 B：手绘墨线小人，纸色底。圆头（手画的一圈，起笔收笔不对齐），眉和嘴两三笔，
// 身体和四肢是有粗细变化、两头收尖的线（perfect-freehand）。线条每 3 帧换一次噪声种子轻轻抖。
// 和画风 A 用同一套骨骼（rig.ts）和同一套表情数字（face.ts）。
import React, {useId} from 'react';
import {P, add, dirDown, rot} from './geom';
import {B, RPose, Skel, solve} from './rig';
import {Expr} from './face';
import {Look} from './look';
import {ink, inkCircle} from './ink';
import {browLine, faceLayout, mouthCurves} from './FlatPerson';

export const INK = '#211C19';
export const PAPER = '#F3EEE3';

export type InkPersonProps = {
  pose: RPose; expr: Expr; look: Look;
  x: number; y: number; s: number; facing?: 1 | -1;
  frame: number;
  seed?: string;
  color?: string;             // 墨色（远处的人可以淡一点）
  weight?: number;            // 线粗倍数
  phone?: {lit: number; tilt?: number};
  blushColor?: string;
  part?: 'all' | 'body' | 'arms';
  halo?: number;              // 每笔外面先垫一圈纸白（屏幕像素），把后面的线挡开，人不会和椅子的线缠在一起
};

export const InkPerson: React.FC<InkPersonProps> = (p) => {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');
  const r = p.pose;
  const e = p.expr;
  const sk: Skel = solve(r);
  const facing = p.facing ?? 1;
  const col = p.color ?? INK;
  const w = p.weight ?? 1;
  const seed = p.seed ?? 'ink';
  const f = p.frame;
  const px = p.s;
  const o = (name: string, size: number, extra: Record<string, unknown> = {}) => ({size: size * w, seed: `${seed}-${name}`, frame: f, px, ...extra});
  const yaw = r.yaw;
  const L = faceLayout(yaw, r.pitch);

  // 头在身体坐标里：头的局部坐标 → 身体坐标
  const H = (q: P) => add(sk.head, rot(q, sk.angH));
  const Hs = (qs: P[]) => qs.map(H);

  const part = p.part ?? 'all';
  const strokes: {d: string; fill?: string; op?: number}[] = [];
  const pushAny = (d: string, fill = col, op = 1) => strokes.push({d, fill, op});
  let armMode = false;   // 只画胳膊时，身子那几笔跳过
  const push = (d: string, fill = col, op = 1) => {
    if (part === 'arms' && !armMode) return;
    if (part === 'body' && armMode) return;
    pushAny(d, fill, op);
  };
  const asArm = (fn: () => void) => {
    armMode = true;
    fn();
    armMode = false;
  };

  // 远侧手臂、腿（稍淡、稍细）
  const handTip = (wpt: P, ang: number, l: number) => add(wpt, scl1(dirDown(ang), l));
  // 墨线小人的四肢都从脊柱上长出来：手臂从锁骨那一点，腿从胯那一点
  const sh = (side: number) => add(sk.chest, rot({x: side * B.shW * (1 - yaw * 0.7) * 0.7, y: 9 - r.shrug * 7}, sk.angC));
  const hp = add(sk.pelvis, rot({x: 0, y: 3}, sk.angP));
  if (r.front < 0.5) asArm(() => push(ink([sh(-1), sk.eF, sk.wF, handTip(sk.wF, sk.handF, 7)], o('aF', 5.2)), col, 0.92));
  push(ink([hp, sk.kF, sk.anF], o('lF', 6)), col, 0.92);
  const foot = (an: P, ang: number) => [an, add(an, rot({x: 9, y: 4}, ang)), add(an, rot({x: 17 * (0.45 + 0.55 * yaw), y: 5}, ang))];
  push(ink(foot(sk.anF, sk.footF), o('fF', 5.4, {taper: [0.1, 0.5]})), col, 0.92);
  // 身体：一笔，从脖子到胯，中间最粗
  const neckBase = add(sk.chest, rot({x: 0, y: -2}, sk.angC));
  push(ink([sk.neckTop, neckBase, sk.mid, sk.pelvis], o('body', 8.5, {taper: [0.18, 0.3], press: (t: number) => 0.45 + 0.55 * Math.sin(Math.PI * Math.min(1, t * 1.1))})));
  // 肩：一笔从左肩过锁骨到右肩，两头随耸肩/塌肩上下（叹气时肩落下要看得见）
  const shw = B.shW * (1 - yaw * 0.7) * 0.75;
  const shY = 9 - r.shrug * 7;
  push(ink([add(sk.chest, rot({x: -shw, y: shY}, sk.angC)), add(sk.chest, rot({x: -shw * 0.4, y: 4 - r.shrug * 2}, sk.angC)),
    add(sk.chest, rot({x: shw * 0.4, y: 4 - r.shrug * 2}, sk.angC)), add(sk.chest, rot({x: shw, y: shY}, sk.angC))], o('shoulder', 5.4, {taper: [0.3, 0.3]})));
  // 近侧腿、脚
  push(ink([hp, sk.kN, sk.anN], o('lN', 6.4)));
  push(ink(foot(sk.anN, sk.footN), o('fN', 5.8, {taper: [0.1, 0.5]})));
  // 近侧手臂（抱头时画在头前面，这里先不画）
  const nearArm = () => push(ink([sh(1), sk.eN, sk.wN, ...(r.hN === 'pocket' ? [] : [handTip(sk.wN, sk.handN, 7)])], o('aN', 5.6)));
  if (r.front < 0.5) asArm(nearArm);

  // 手机：两手之间的一个圆角长方块，手画的
  if (p.phone) asArm(() => {
    if (!p.phone) return;
    const c = {x: (sk.wN.x + sk.wF.x) / 2, y: (sk.wN.y + sk.wF.y) / 2};
    const ang = (sk.handN + sk.handF) / 2 + 90 + (p.phone.tilt ?? 0);
    const pc = add(c, rot({x: 0, y: 7}, (sk.handN + sk.handF) / 2));
    const R = (q: P) => add(pc, rot(q, ang));
    const box = [R({x: -14, y: -8}), R({x: 14, y: -8.5}), R({x: 14.5, y: 8}), R({x: -14, y: 8.5}), R({x: -14.3, y: -7})];
    push(ink(box, o('ph', 3.4, {smooth: false, taper: [0.05, 0.08], press: () => 0.7})));
    push(ink([R({x: -12, y: 5.5}), R({x: 12, y: 5.2})], o('ph2', 2.2)), col, 0.8);
  });

  // 头：手画的一圈，起笔在右上，转 348 度，不完全闭合
  push(inkCircle(sk.head, 50, 47.5, {...o('head', 5.6), a0: -58 + sk.angH, sweep: 350}));
  // 耳朵（侧过去时在后脑那边）
  if (yaw >= 0.3) push(ink(Hs([{x: L.earX + 2, y: -1}, {x: L.earX - 4, y: 4}, {x: L.earX - 2, y: 13}]), o('ear', 3)), col, 0.8);

  // 头发：短发 = 头顶一撮翘起来的 + 额前两笔；齐肩短发 = 两边垂到下巴
  if (p.look.hairStyle === 'short') {
    // 头顶翘起的一撮（这个人的记号）
    const fx = yaw * 22, fb = -31 + r.pitch * 11;
    push(ink(Hs([{x: -2 + 4 * yaw, y: -46}, {x: -6 + 4 * yaw, y: -63}, {x: 4 + 4 * yaw, y: -75}, {x: 15 + 4 * yaw, y: -70}]), o('tuft', 4.8, {taper: [0.25, 0.5]})));
    // 额前不画刘海：一笔斜线在小人脸上像一道疤，留白反而干净
    void fx; void fb;
  } else {
    // 齐肩短发：一顶帽子似的头发线（盖住头顶到耳朵），两边垂到下巴往外翘，额前斜刘海
    const fb = -28 + r.pitch * 11, fx = yaw * 22;
    push(ink(Hs([{x: 48, y: 4}, {x: 50, y: -26}, {x: 34, y: -46}, {x: 6, y: -54}, {x: -26, y: -50}, {x: -46, y: -30}, {x: -50, y: 4}]), o('bobTop', 3.4, {taper: [0.1, 0.1]})), col, 0.9);
    push(ink(Hs([{x: 47, y: -14}, {x: 50, y: 18}, {x: 46, y: 38}, {x: 56, y: 44}]), o('bobR', 4.6, {taper: [0.15, 0.5]})));
    push(ink(Hs([{x: -48, y: -14}, {x: -51, y: 18}, {x: -46, y: 38}, {x: -56, y: 44}]), o('bobL', 4.6, {taper: [0.15, 0.5]})));
    push(ink(Hs([{x: fx + 40, y: -40}, {x: fx + 16, y: fb - 4}, {x: fx - 10, y: fb + 6}, {x: fx - 28, y: fb + 14}]), o('bobF', 4.2, {taper: [0.2, 0.55]})));
  }

  // 脸
  const by = L.ey - 15.5 - e.brow * 5.5 + e.lid * 2.5;
  L.eyes.forEach((q, i) => {
    // 墨线的眉：比扁平版长一点、细一点，不然短短一笔像一粒米
    const b0 = browLine(e, q.x, by, q.side, q.sc);
    const mid = {x: (b0.inner.x + b0.outer.x) / 2, y: (b0.inner.y + b0.outer.y) / 2};
    const ext = (pp: P) => ({x: mid.x + (pp.x - mid.x) * 1.25, y: mid.y + (pp.y - mid.y) * 1.25});
    push(ink(Hs([ext(b0.inner), b0.c, ext(b0.outer)]), o(`brow${i}`, 3.6, {taper: [0.1, 0.5]})));
  });
  const eyes = L.eyes.map((q, i) => {
    const rx = 5 * e.eye * q.sc, ry = 6.3 * e.eye;
    const cx = q.x + r.gx * 2.4, cy = L.ey + r.gy * 2.2;
    return {q, i, rx, ry, cx, cy};
  });
  const dots: {c: P; rx: number; ry: number; cut: number; glint: number; glint2: boolean}[] = [];
  eyes.forEach(({q, i, rx, ry, cx, cy}) => {
    if (e.lid >= 0.88) {
      const c = Math.abs(e.closed) > 0.05 ? e.closed : -0.7;
      push(ink(Hs([{x: cx - rx - 2, y: cy}, {x: cx, y: cy - 6 * c}, {x: cx + rx + 2, y: cy}]), o(`eyeC${i}`, 3, {taper: [0.25, 0.25]})));
      return;
    }
    if (e.lid > 0.08) {
      const cut = cy - ry + 2 * ry * e.lid * 0.96;
      push(ink(Hs([{x: cx - rx - 2.4, y: cut + 0.6}, {x: cx, y: cut - 0.6}, {x: cx + rx + 2.4, y: cut + 0.4}]), o(`lid${i}`, 2.6, {taper: [0.2, 0.2]})));
    }
    dots.push({c: {x: cx, y: cy}, rx, ry, cut: e.lid, glint: e.shine, glint2: e.shine > 1.15 || e.tear > 0.3});
    if (e.tear > 0.05) {
      const tx = cx + q.side * rx * 0.9, ty = cy + ry + 5;
      push(ink(Hs([{x: tx, y: ty - 4.5}, {x: tx + 2.8, y: ty + 1}, {x: tx, y: ty + 4.4}, {x: tx - 2.8, y: ty + 1}, {x: tx, y: ty - 4.5}]), o(`tear${i}`, 1.8, {taper: [0, 0], press: () => 0.7})), col, e.tear);
      push(ink(Hs([{x: cx - rx, y: cy + ry + 1.5}, {x: cx, y: cy + ry + 3}, {x: cx + rx, y: cy + ry + 1.5}]), o(`wl${i}`, 1.6)), col, 0.7 * e.tear);
    }
    // 腮红：两三道斜的短排线
    if (e.blush > 0.3) {
      [0, 1, 2].forEach((j) => {
        const bx = q.x + q.side * 3 - 5 + j * 4.2, byy = L.ey + 12;
        push(ink(Hs([{x: bx + 1.6, y: byy - 2.4}, {x: bx - 1.6, y: byy + 2.4}]), o(`bl${i}${j}`, 1.7)), p.blushColor ?? '#C9604F', 0.75 * Math.min(1, e.blush));
      });
    }
  });
  // 嘴
  const m = mouthCurves({...e, mouthW: e.mouthW * 1.45, smile: e.smile * 1.3}, L.mouth.x, L.mouth.y);
  if (e.open < 0.06) {
    push(ink(Hs(m.up.filter((_, i) => i % 2 === 0)), o('mouth', 2.8, {taper: [0.25, 0.3]})));
  } else {
    const loop = Hs([...m.up.filter((_, i) => i % 2 === 0), ...m.lo.slice().reverse().filter((_, i) => i % 2 === 0)]);
    push(`M ${loop.map((q) => `${q.x.toFixed(2)} ${q.y.toFixed(2)}`).join(' L ')} Z`, col, 0.9);
    push(ink([...loop, loop[0]], o('mouthO', 2.4, {taper: [0.05, 0.05], press: () => 0.6})));
  }

  if (r.front >= 0.5) asArm(() => {
    nearArm();
    push(ink([sh(-1), sk.eF, sk.wF, handTip(sk.wF, sk.handF, 7)], o('aF2', 5.4)));
  });

  return (
    <g transform={`translate(${p.x} ${p.y}) scale(${p.s * facing} ${p.s})`}>
      {p.halo ? strokes.map((s, i) => <path key={`h${i}`} d={s.d} fill={PAPER} stroke={PAPER} strokeWidth={(p.halo ?? 0) / p.s} strokeLinejoin="round" />) : null}
      {strokes.map((s, i) => <path key={i} d={s.d} fill={s.fill} opacity={s.op} />)}
      <g transform={`translate(${sk.head.x} ${sk.head.y}) rotate(${sk.angH})`}>
      {part !== 'arms' && dots.map((d, i) => {
        const cutY = d.c.y - d.ry + 2 * d.ry * d.cut * 0.96;
        return (
          <g key={`d${i}`}>
            <clipPath id={`${uid}ck${i}`}><rect x={d.c.x - 20} y={cutY} width={40} height={40} /></clipPath>
            <g clipPath={d.cut > 0.08 ? `url(#${uid}ck${i})` : undefined}>
              <ellipse cx={d.c.x} cy={d.c.y} rx={d.rx} ry={d.ry} fill={col} />
              <circle cx={d.c.x + 1.4} cy={Math.max(d.c.y - 2, cutY + 2)} r={1.35 * d.glint} fill={PAPER} />
              {d.glint2 && <circle cx={d.c.x - 1.3} cy={d.c.y + 2.2} r={0.75 * d.glint} fill={PAPER} />}
            </g>
          </g>
        );
      })}
      </g>
    </g>
  );
};

const scl1 = (a: P, k: number): P => ({x: a.x * k, y: a.y * k});
