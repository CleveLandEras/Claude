// FK 骨骼：一个姿势 = 一组关节角度。转肩带动整条手臂，转骨盆带动上身和腿。
// 单位：头高约 100（头半径 50），站直从脚底到头顶约 265，约 2.65 头身。
// 人默认脸朝右（+x）。facing = -1 时整个人左右镜像。
// 角度都是屏幕上的转角，正负按“朝脸那一侧”来记，写姿势时不用管 SVG 的方向：
//   lean / chest：上身往前弯（+）往后仰（-）；neck：低头（+）仰头（-）；pelvis：骨盆往前转（+）
//   手臂 sh：上臂从下垂往前抬（+）；el：肘弯，前臂往前上弯（+）；wr：手腕往前弯（+）
//   腿 hip：大腿从下垂往前抬（+，坐着约 90）；knee：膝弯，小腿往后弯（+）；ank：脚尖往下（+）
//   也可以给手腕、脚踝一个目标点（to，以骨盆为原点），用两节 IK 反算肘和膝。
import {P, add, angDown, clamp, dirDown, dirUp, dist, lerp, lerpAng, nrm, rot, scl, sub, wrap} from './geom';

export const B = {
  spine1: 30, spine2: 30, neck: 12, headUp: 46, headR: 50,
  upper: 34, fore: 31, thigh: 44, shin: 42, sole: 6, foot: 24,
  shW: 26, hipW: 13,
};

export type HandShape = 'open' | 'fist' | 'hold' | 'limp' | 'pocket';
export type Arm = {sh?: number; el?: number; wr?: number; to?: P; bend?: 1 | -1};
export type Leg = {hip?: number; knee?: number; ank?: number; to?: P; bend?: 1 | -1; flat?: boolean; fs?: number};   // fs：大腿缩短（正面坐着时大腿朝着观众）
export type Pose = {
  x?: number; y?: number;          // 骨盆在锚点坐标里的位置（锚点 = 人脚下的地面）
  pelvis?: number; lean?: number; chest?: number; neck?: number;
  yaw?: number;                    // 0 正面，1 全侧面（脸朝 +x）
  pitch?: number;                  // 五官上下挪：+ 往下看，- 往上看
  gaze?: P;                        // 眼珠方向，-1..1
  shrug?: number;                  // 耸肩 +，塌肩 -
  duck?: number;                   // 头往下缩（正面低头时，头往胸口沉）
  aN?: Arm; aF?: Arm; lN?: Leg; lF?: Leg;   // N = 近侧（靠观众），F = 远侧
  hN?: HandShape; hF?: HandShape;
  front?: boolean;                 // 手臂画在头前面（抱头）
  ground?: boolean;                // 自动把最低的脚底落到 y=0
};

// 解算后的姿势：全部是数字，可以直接插值
export type RPose = {
  x: number; y: number; pelvis: number; lean: number; chest: number; neck: number;
  yaw: number; pitch: number; gx: number; gy: number; shrug: number; duck: number;
  fsN: number; fsF: number;
  aN: [number, number, number]; aF: [number, number, number];
  lN: [number, number, number]; lF: [number, number, number];
  flatN: number; flatF: number;
  hN: HandShape; hF: HandShape; front: number;
};

export type Skel = {
  r: RPose;
  pelvis: P; mid: P; chest: P; neckTop: P; head: P;
  angP: number; angM: number; angC: number; angH: number;
  sN: P; eN: P; wN: P; handN: number;
  sF: P; eF: P; wF: P; handF: number;
  hipN: P; kN: P; anN: P; footN: number;
  hipF: P; kF: P; anF: P; footF: number;
};

const ik2 = (root: P, target: P, a: number, b: number, bend: number): [P, P] => {
  const d0 = sub(target, root);
  const d = clamp(Math.hypot(d0.x, d0.y), Math.abs(a - b) + 0.5, a + b - 0.05);
  const dir = nrm(d0);
  const A = (Math.acos(clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1)) * 180) / Math.PI;
  const e = add(root, scl(rot(dir, A * bend), a));
  return [e, add(root, scl(dir, d))];
};

const torso = (x: number, y: number, pelvis: number, lean: number, chest: number, neck: number, yaw: number, shrug: number, duck = 0) => {
  const pel = {x, y};
  const angP = pelvis, angM = pelvis + lean, angC = angM + chest, angH = angC + neck;
  const mid = add(pel, scl(dirUp(angM), B.spine1));
  const ch = add(mid, scl(dirUp(angC), B.spine2));
  const neckTop = add(ch, scl(dirUp(angC + neck * 0.4), B.neck - duck * 10));
  const head = add(neckTop, rot({x: 5 * yaw, y: -B.headUp}, angH));
  const sx = B.shW * (1 - yaw) + 3 * yaw;
  const sy = 5 - shrug * 7;
  const sN = add(ch, rot({x: sx, y: sy}, angC));
  const sF = add(ch, rot({x: -sx, y: sy}, angC));
  const hx = B.hipW * (1 - yaw) + 2 * yaw;
  const hipN = add(pel, rot({x: hx, y: 6}, angP));
  const hipF = add(pel, rot({x: -hx, y: 6}, angP));
  return {pel, angP, angM, angC, angH, mid, ch, neckTop, head, sN, sF, hipN, hipF};
};

const armAngles = (s: P, a: Arm, angC: number, pel: P): [number, number, number] => {
  if (a.to) {
    const [e, w] = ik2(s, add(pel, a.to), B.upper, B.fore, a.bend ?? 1);
    const upW = angDown(sub(e, s));
    const foreW = angDown(sub(w, e));
    return [wrap(angC - upW), wrap(upW - foreW), a.wr ?? 0];
  }
  return [a.sh ?? 0, a.el ?? 0, a.wr ?? 0];
};
const legAngles = (h: P, l: Leg, angP: number, pel: P): [number, number, number] => {
  if (l.to) {
    const [k, an] = ik2(h, add(pel, l.to), B.thigh * (l.fs ?? 1), B.shin, l.bend ?? -1);
    const thW = angDown(sub(k, h));
    const shW = angDown(sub(an, k));
    return [wrap(angP - thW), wrap(shW - thW), l.ank ?? 0];
  }
  return [l.hip ?? 0, l.knee ?? 0, l.ank ?? 0];
};

export const resolve = (p: Pose): RPose => {
  const yaw = p.yaw ?? 0.55;
  const shrug = p.shrug ?? 0;
  const t = torso(p.x ?? 0, p.y ?? -98, p.pelvis ?? 0, p.lean ?? 0, p.chest ?? 0, p.neck ?? 0, yaw, shrug, p.duck ?? 0);
  const r: RPose = {
    x: p.x ?? 0, y: p.y ?? -98, pelvis: p.pelvis ?? 0, lean: p.lean ?? 0, chest: p.chest ?? 0, neck: p.neck ?? 0,
    yaw, pitch: p.pitch ?? 0, gx: p.gaze?.x ?? 0, gy: p.gaze?.y ?? 0, shrug, duck: p.duck ?? 0,
    fsN: p.lN?.fs ?? 1, fsF: p.lF?.fs ?? 1,
    aN: armAngles(t.sN, p.aN ?? {sh: 6, el: 10}, t.angC, t.pel),
    aF: armAngles(t.sF, p.aF ?? {sh: -6, el: 10}, t.angC, t.pel),
    lN: legAngles(t.hipN, p.lN ?? {}, t.angP, t.pel),
    lF: legAngles(t.hipF, p.lF ?? {}, t.angP, t.pel),
    flatN: (p.lN?.flat ?? true) ? 1 : 0, flatF: (p.lF?.flat ?? true) ? 1 : 0,
    hN: p.hN ?? 'open', hF: p.hF ?? 'open', front: p.front ? 1 : 0,
  };
  if (p.ground) {
    const s = solve(r);
    const low = Math.max(s.anN.y, s.anF.y) + B.sole;
    r.y -= low;
  }
  return r;
};

export const solve = (r: RPose): Skel => {
  const t = torso(r.x, r.y, r.pelvis, r.lean, r.chest, r.neck, r.yaw, r.shrug, r.duck);
  const arm = (s: P, a: [number, number, number]) => {
    const upW = t.angC - a[0];
    const e = add(s, scl(dirDown(upW), B.upper));
    const foreW = upW - a[1];
    const w = add(e, scl(dirDown(foreW), B.fore));
    return {e, w, hand: foreW - a[2]};
  };
  const leg = (h: P, l: [number, number, number], flat: number, fs: number) => {
    const thW = t.angP - l[0];
    const k = add(h, scl(dirDown(thW), B.thigh * fs));
    const shW = thW + l[1];
    const an = add(k, scl(dirDown(shW), B.shin));
    const free = shW + l[2];
    return {k, an, foot: lerpAng(free, l[2], flat)};
  };
  const aN = arm(t.sN, r.aN), aF = arm(t.sF, r.aF);
  const lN = leg(t.hipN, r.lN, r.flatN, r.fsN), lF = leg(t.hipF, r.lF, r.flatF, r.fsF);
  return {
    r, pelvis: t.pel, mid: t.mid, chest: t.ch, neckTop: t.neckTop, head: t.head,
    angP: t.angP, angM: t.angM, angC: t.angC, angH: t.angH,
    sN: t.sN, eN: aN.e, wN: aN.w, handN: aN.hand,
    sF: t.sF, eF: aF.e, wF: aF.w, handF: aF.hand,
    hipN: t.hipN, kN: lN.k, anN: lN.an, footN: lN.foot,
    hipF: t.hipF, kF: lF.k, anF: lF.an, footF: lF.foot,
  };
};

const la = (a: [number, number, number], b: [number, number, number], t: number): [number, number, number] =>
  [lerpAng(a[0], b[0], t), lerpAng(a[1], b[1], t), lerpAng(a[2], b[2], t)];

export const mixPose = (a: RPose, b: RPose, t: number): RPose => ({
  x: lerp(a.x, b.x, t), y: lerp(a.y, b.y, t),
  pelvis: lerp(a.pelvis, b.pelvis, t), lean: lerp(a.lean, b.lean, t), chest: lerp(a.chest, b.chest, t), neck: lerp(a.neck, b.neck, t),
  yaw: lerp(a.yaw, b.yaw, t), pitch: lerp(a.pitch, b.pitch, t), gx: lerp(a.gx, b.gx, t), gy: lerp(a.gy, b.gy, t),
  shrug: lerp(a.shrug, b.shrug, t), duck: lerp(a.duck, b.duck, t), fsN: lerp(a.fsN, b.fsN, t), fsF: lerp(a.fsF, b.fsF, t),
  aN: la(a.aN, b.aN, t), aF: la(a.aF, b.aF, t), lN: la(a.lN, b.lN, t), lF: la(a.lF, b.lF, t),
  flatN: lerp(a.flatN, b.flatN, t), flatF: lerp(a.flatF, b.flatF, t),
  hN: t < 0.5 ? a.hN : b.hN, hF: t < 0.5 ? a.hF : b.hF, front: lerp(a.front, b.front, t),
});

// 在已解算的姿势上叠一点小动作（呼吸、叹气），不改原姿势
export const nudge = (r: RPose, d: Partial<Record<'x' | 'y' | 'pelvis' | 'lean' | 'chest' | 'neck' | 'pitch' | 'shrug' | 'gx' | 'gy' | 'yaw' | 'duck', number>>): RPose => {
  const o = {...r};
  (Object.keys(d) as (keyof typeof d)[]).forEach((k) => {
    (o as unknown as Record<string, number>)[k] += d[k] ?? 0;
  });
  return o;
};

// 走路：phase 0..1 一个完整步态周期（两步）。侧身，脸朝 +x，脚自动落地
export const walk = (phase: number, o: {yaw?: number; stride?: number} = {}): RPose => {
  const a = phase * Math.PI * 2;
  const st = o.stride ?? 1;
  const swing = (ph: number) => {
    const s = Math.sin(a + ph);
    const c = Math.cos(a + ph);
    // 大腿前后摆；往前摆的半程膝盖弯起来；落地前伸直
    const hip = 24 * st * s;
    const knee = Math.max(0, 38 * st * Math.sin(a + ph + 0.9)) + 6;
    const ank = -10 * st * c;
    return {hip, knee, ank, flat: false as const};
  };
  const L1 = swing(0), L2 = swing(Math.PI);
  const p = resolve({
    yaw: o.yaw ?? 0.9, lean: 4, chest: 2, neck: 2,
    pelvis: 2 * Math.sin(a * 2),
    lN: L1, lF: L2,
    aN: {sh: -20 * st * Math.sin(a), el: 18 + 8 * Math.max(0, -Math.sin(a))},
    aF: {sh: 20 * st * Math.sin(a), el: 18 + 8 * Math.max(0, Math.sin(a))},
    hN: 'limp', hF: 'limp',
    ground: true,
  });
  p.flatN = Math.max(0, Math.cos(a)) * 0.9;
  p.flatF = Math.max(0, -Math.cos(a)) * 0.9;
  // 重新落地（脚的角度改了以后再贴一次地）
  const s = solve(p);
  const sole = (an: P, foot: number) => Math.max(an.y + rot({x: 0, y: B.sole}, foot).y, an.y + rot({x: B.foot * 0.9, y: B.sole}, foot).y, an.y + rot({x: -5, y: B.sole}, foot).y);
  p.y -= Math.max(sole(s.anN, s.footN), sole(s.anF, s.footF));
  return p;
};

// —— 姿势库 ——
// 锚点：人脚下的地面（y = 0）。坐姿默认坐在高 SEAT 的椅面上：骨盆 y = -54，脚踝 y = -6。
// 牌桌桌面高 TABLE（骨盆往上 34）。IK 目标点（to）以骨盆为原点。
export const SEAT = 40;
export const TABLE = 88;
const POSE_DEFS: Record<string, Pose> = {
  // 坐：端坐，两手搭在大腿上
  sit: {
    x: 0, y: -54, pelvis: -4, lean: 3, chest: 2, neck: 6, yaw: 0.6, pitch: 0.05,
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 44, y: 48}},
    aN: {to: {x: 36, y: -4}, wr: -10}, aF: {to: {x: 28, y: -6}, wr: -10},
    hN: 'open', hF: 'open',
  },
  // 瘫坐仰头：屁股滑到椅面前沿，背靠椅背，头仰过椅背看天花板，两手垂在椅子两边，腿伸直
  slump: {
    x: 0, y: -50, pelvis: -26, lean: -10, chest: -2, neck: -24, yaw: 0.62, pitch: -0.05, gaze: {x: 0.2, y: -0.5},
    lN: {to: {x: 78, y: 44}}, lF: {to: {x: 68, y: 44}},
    aN: {sh: -34, el: 8, wr: 4}, aF: {sh: -30, el: 12},
    hN: 'limp', hF: 'limp', shrug: -0.5,
  },
  // 低头看手机：坐着，背微驼，两手捧着手机在胸前
  phone: {
    x: 0, y: -54, pelvis: -2, lean: 6, chest: 10, neck: 10, yaw: 0.55, pitch: 0.6, gaze: {x: 0.35, y: 0.8},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 46, y: -34}, wr: 20}, aF: {to: {x: 40, y: -32}, wr: 30},
    hN: 'hold', hF: 'hold',
  },
  // 叹气：在看手机的姿势上肩落下、背再驼一点、头再低一点
  sigh: {
    x: 0, y: -54, pelvis: -4, lean: 8, chest: 14, neck: 16, yaw: 0.55, pitch: 0.7, gaze: {x: 0.3, y: 0.9},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 45, y: -27}, wr: 24}, aF: {to: {x: 39, y: -25}, wr: 34},
    hN: 'hold', hF: 'hold', shrug: -1,
  },
  // 抱头：正面坐着，肩耸起来、头往下沉，两手抱住头两边，手肘往外
  headInHands: {
    x: 0, y: -54, pelvis: 0, lean: 2, chest: 2, neck: 4, yaw: 0.12, pitch: 0.75, gaze: {x: 0, y: 1}, duck: 1,
    lN: {to: {x: 14, y: 48}, fs: 0.3}, lF: {to: {x: -14, y: 48}, fs: 0.3},
    aN: {to: {x: 42, y: -104}, bend: 1}, aF: {to: {x: -40, y: -106}, bend: -1},
    hN: 'open', hF: 'open', front: true, shrug: 1,
  },
  // 看底牌：坐在牌桌边，往前探，两只前臂搭在桌上，近侧那只手掀起牌角，低头看
  peek: {
    x: 0, y: -54, pelvis: 2, lean: 9, chest: 5, neck: 6, yaw: 0.32, pitch: 0.7, gaze: {x: 0.45, y: 0.9},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 62, y: -36}, wr: -30}, aF: {to: {x: -4, y: -40}, wr: -10},
    hN: 'open', hF: 'open',
  },
  // 看完底牌叹气：肩落下，背驼一点，头更低
  peekSigh: {
    x: 0, y: -54, pelvis: 0, lean: 9, chest: 10, neck: 9, yaw: 0.32, pitch: 0.8, gaze: {x: 0.3, y: 1},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 60, y: -33}, wr: -30}, aF: {to: {x: -6, y: -38}, wr: -10},
    hN: 'open', hF: 'open', shrug: -1.1,
  },
  // 抬头看桌上（公共牌在前面）：上身直起来一点，眼睛往前下方看
  board: {
    x: 0, y: -54, pelvis: 0, lean: 6, chest: 2, neck: 0, yaw: 0.3, pitch: 0.35, gaze: {x: 0.5, y: 0.8},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 60, y: -35}, wr: -30}, aF: {to: {x: -6, y: -40}, wr: -10},
    hN: 'open', hF: 'open',
  },
  // 全推：整个人往前压，两条胳膊伸直，把面前的筹码推出去
  allIn: {
    x: 0, y: -54, pelvis: 6, lean: 20, chest: 8, neck: -6, yaw: 0.55, pitch: 0, gaze: {x: 1, y: -0.1},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 96, y: -33}, wr: -55}, aF: {to: {x: 90, y: -35}, wr: -55},
    hN: 'open', hF: 'open', shrug: 0.5,
  },
  // 盯着对面想：往前倾，远侧胳膊横搭在桌上，近侧手肘撑桌、手托着下巴
  think: {
    x: 0, y: -54, pelvis: 2, lean: 10, chest: 4, neck: 2, yaw: 0.45, pitch: 0.05, gaze: {x: 1, y: 0.15},
    lN: {to: {x: 51, y: 48}}, lF: {to: {x: 45, y: 48}},
    aN: {to: {x: 52, y: -82}, bend: 1, wr: -60}, aF: {to: {x: 58, y: -38}, wr: -70},
    hN: 'fist', hF: 'open',
  },
  // 站着等：重心在近侧那条腿上，手插兜，头偏一点望向前方
  stand: {
    x: 0, yaw: 0.4, pelvis: -3, lean: -2, chest: 1, neck: -4, pitch: -0.05, gaze: {x: 0.8, y: 0},
    lN: {hip: 2, knee: 0}, lF: {hip: 12, knee: 14},
    aN: {to: {x: 14, y: -12}}, aF: {to: {x: 4, y: -14}},
    hN: 'pocket', hF: 'pocket', ground: true,
  },
  // 站着、低头看脚下（比喻镜头用）
  standLook: {
    x: 0, yaw: 0.5, pelvis: -2, lean: 1, chest: 2, neck: 10, pitch: 0.3, gaze: {x: 0.6, y: 0.4},
    lN: {hip: 3, knee: 0}, lF: {hip: 10, knee: 10},
    aN: {sh: 2, el: 8}, aF: {sh: -6, el: 10},
    hN: 'limp', hF: 'limp', ground: true,
  },
  // 坐在长椅上等：两手撑在椅面上，脚往前伸，头转向来人那边
  benchWait: {
    x: 0, y: -54, pelvis: -6, lean: 2, chest: -2, neck: -2, yaw: 0.55, pitch: -0.05, gaze: {x: 0.9, y: -0.1},
    lN: {to: {x: 62, y: 46}}, lF: {to: {x: 54, y: 48}},
    aN: {to: {x: 22, y: 2}, wr: -40}, aF: {to: {x: -16, y: 0}, wr: -40},
    hN: 'open', hF: 'open',
  },
};

const CACHE: Record<string, RPose> = {};
export type PoseName = keyof typeof POSE_DEFS | 'walk';
export const POSE_NAMES = Object.keys(POSE_DEFS).concat(['walk']);
export const pose = (name: string, phase = 0): RPose => {
  if (name === 'walk') return walk(phase);
  if (!CACHE[name]) CACHE[name] = resolve(POSE_DEFS[name]);
  return CACHE[name];
};
export const poseDef = (name: string) => POSE_DEFS[name];

// 关键帧姿势：keys = [[帧, 姿势], ...]
export const poseTrack = (f: number, keys: [number, RPose][], ease: (t: number) => number): RPose => {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i][0]) {
      const [f0, a] = keys[i - 1], [f1, b] = keys[i];
      return mixPose(a, b, ease((f - f0) / Math.max(1e-6, f1 - f0)));
    }
  }
  return keys[keys.length - 1][1];
};

export const handDir = (s: Skel, near: boolean) => dirDown(near ? s.handN : s.handF);
export const mid2 = (a: P, b: P) => ({x: (a.x + b.x) / 2, y: (a.y + b.y) / 2});
export const span = (a: P, b: P) => dist(a, b);
