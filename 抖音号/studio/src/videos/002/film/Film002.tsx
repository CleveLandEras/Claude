// 002《被坑多了，你会变狠吗？》横屏成片（第五版）。
// 时间、字幕、镜头远近、路线图全读 timeline.json（timeline.py 生成，这里不写死帧号）；点阵、方块、历史条全读 data.json。
// 和灰框（../Gray002.tsx，保留不动）相比只换画法：人、道具、光、字、点阵都是正式画法（见 film/ 下各文件开头的说明）。
// 镜头远近变化的画法：
//   - 拉远（1.6 秒）：近景的两个人跟着镜头缩小，缩到点那么大时淡成你和骗子两颗点；点阵里的点要等直径小于约 150 px 才淡入，
//     所以不会有几颗被放大裁切的大点。往里扎（8.2、37.4 秒）反过来：点长大时淡出，近景从你那颗点的位置展开。
//   - 推镜（25.2–29.6 秒）：开头 0.4 秒起步，最后 0.5 秒减速到中近景那一段的推速，接上不顿。
// 声音：public/002/sfx.wav（另一个代理按 timeline.json 生成）。文件在就放进去；不在就是无声版（也可以传 audio: false）。
import React from 'react';
import {AbsoluteFill, Html5Audio, getStaticFiles, staticFile, useCurrentFrame} from 'remotion';
import {mixHex} from '../../../components/people/geom';
import {COL, COL_HI, Cam, D, FAR, HARSH, I, MID, TL, YOU_W, animF, beat, beatAt, camAt, cellXY, clamp, ease, easeOut, eva, evn, genAt, genF, lerp, prog, toScreen, zoomOn} from '../lib';
import {Crowd, CrowdDefs, CrowdFloor, Vignette} from './FCrowd';
import {FilmDefs, Tag, YOU_BG, YOU_FG} from './fpeople';
import {EndYou, NL, NearBeat, NearOpen, OPEN, Room, RoomDefs} from './FNear';
import {Block, Cycle, Four, MidYou, PUSH_END, cycleCrowd} from './FEnding';
import {AiBadge, Question, RouteDefs, RouteMap, SubBand, Subtitles} from './FOverlay';

export const FILM_FRAMES = TL.frames;
// 第五版：“狠”的红（记仇那一档），连线、你变狠时那圈白圈都用它
const RED = COL[I.GRIM];
const RED_HI = COL_HI.GRIM;

// S15：红线从你的点一根根连到第 7 代被你坑的 6 个老实人（画成那时的黄色），线上有一层红光
const Victims: React.FC<{f: number; cam: Cam}> = ({f, cam}) => {
  const [l0, l1] = eva('S15', 'lines');
  const me = toScreen(cam, YOU_W);
  const r = (TL.layout.far.dot / 2) * cam.z;
  const youCol = COL[I.GRIM];
  return (
    <g>
      <circle cx={me.x} cy={me.y} r={r * 2.4} fill={youCol} opacity={0.35} filter="url(#fBlur8)" />
      {D.grid.victims.map((c, i) => {
        const p = toScreen(cam, cellXY(c));
        const t0 = lerp(l0, l1 - 5, i / (D.grid.victims.length - 1));
        const u = ease(prog(f, [t0, t0 + 5]));
        if (u <= 0) return null;
        const x2 = lerp(me.x, p.x, u), y2 = lerp(me.y, p.y, u);
        return (
          <g key={c}>
            <line x1={me.x} y1={me.y} x2={x2} y2={y2} stroke={RED} strokeWidth={16} strokeLinecap="round" opacity={0.35} filter="url(#fBlur6)" />
            <line x1={me.x} y1={me.y} x2={x2} y2={y2} stroke={RED_HI} strokeWidth={6} strokeLinecap="round" />
            <g opacity={u}>
              <circle cx={p.x} cy={p.y} r={r * 2.2} fill={COL[I.ALLC]} opacity={0.25} filter="url(#fBlur6)" />
              <circle cx={p.x} cy={p.y} r={r * 1.15} fill={COL[I.ALLC]} />
              <circle cx={p.x - r * 0.25} cy={p.y - r * 0.3} r={r * 0.45} fill="#FFE09A" />
              <circle cx={p.x} cy={p.y} r={r + 10} fill="none" stroke={RED_HI} strokeWidth={4} />
            </g>
          </g>
        );
      })}
      <circle cx={me.x} cy={me.y} r={r * 1.05} fill={youCol} />
      <circle cx={me.x - r * 0.25} cy={me.y - r * 0.3} r={r * 0.4} fill={mixHex(RED, '#FFFFFF', 0.55)} />
    </g>
  );
};

// 第四版：S03 开局的 500 个老实人（D.grid.starters）全亮，其余压到这个亮度
const STARTER_SET = new Set(D.grid.starters);
const OTHERS_DIM = 0.12;

// 第五版：S03–S04 点阵极慢地推近 3.5%（以点阵中心为准），S04 停在第 70 代时画面不整幅静止；S05 从推完的地方倒带、扎进去
const DRIFT_END: Cam = {...FAR, z: 1.035};
const driftCam = (f: number) => camAt(FAR, DRIFT_END, prog(f, [beat('S03').f0, beat('S05').f0]));
// 第五版 youRed（5.6 秒，“你也是”）：你那颗点的白圈变红、跳一下，旁边弹一个白底“你”；倒带时圈变回白，扎进去前“你”淡掉
const YouMark: React.FC<{f: number; cam: Cam; o: number}> = ({f, cam, o}) => {
  const t = evn('S03', 'youRed');
  if (f < t || o <= 0.001) return null;
  const ys = toScreen(cam, YOU_W);
  const ringR = Math.max(TL.layout.far.ring / 2, (TL.layout.far.dot / 2) * cam.z + 16);
  return (
    <Tag x={ys.x} y={ys.y - ringR - 70} text="你" bg={YOU_BG} fg={YOU_FG} size={80} o={prog(f, [t, t + 5]) * o}
      pop={ease(prog(f, [t, t + 8]))} tilt={-2} />
  );
};
const youRing = (f: number) => {
  const t = evn('S03', 'youRed');
  const back = prog(f, eva('S05', 'rewind'));
  return {color: mixHex('#FFFFFF', RED_HI, prog(f, [t, t + 4]) * (1 - back)), scale: 1 + 0.35 * Math.sin(Math.PI * prog(f, [t, t + 9]))};
};

// 推镜的速度曲线：开头 12 帧起步，中间匀速，最后 15 帧（0.5 秒）减到 35%（= 中近景那一段的推速）
const pushProfile = (t: number, T: number) => {
  const a = 12, b = 15, end = 0.35;
  const v = (x: number) => (x < a ? x / a : x > T - b ? lerp(1, end, (x - (T - b)) / b) : 1);
  // 积分（每帧求和，T 只有一百多帧）
  let tot = 0, cur = 0;
  for (let x = 0; x < T; x++) {
    const dv = v(x + 0.5);
    tot += dv;
    if (x + 1 <= t) cur += dv;
    else if (x < t) cur += dv * (t - x);
  }
  return cur / tot;
};
const pushCam = (f: number) => {
  const a = animF(evn('S14', 'pushFrom')), b = animF(evn('S16', 'pushTo'));
  const t = clamp(animF(f) - a, 0, b - a);
  return camAt(FAR, PUSH_END, pushProfile(t, b - a));
};

// 近景跟着镜头缩放：你那颗点在屏幕上的位置 = 近景里你脸的位置；外圈用一圈柔边遮住（不露出方框）
// 近景跟着镜头缩放：你那颗点在屏幕上的位置 = 近景里你脸的位置；外圈用一圈柔边遮住（不露出方框）
const NearIris: React.FC<{cam: Cam; zNear: number; anchor: {x: number; y: number}; o: number; id: string; children: React.ReactNode}> = (
  {cam, zNear, anchor, o, id, children},
) => {
  if (o <= 0.005) return null;
  const s = toScreen(cam, YOU_W);
  const k = cam.z / zNear;
  const R = 1250 * k;
  return (
    <g opacity={o}>
      <defs>
        <radialGradient id={`iris${id}`} cx={s.x} cy={s.y} r={R} gradientUnits="userSpaceOnUse">
          <stop offset="0.55" stopColor="#fff" stopOpacity={1} />
          <stop offset="1" stopColor="#fff" stopOpacity={0} />
        </radialGradient>
        <mask id={`irm${id}`} maskUnits="userSpaceOnUse" x={0} y={0} width={1920} height={1080}>
          <rect width={1920} height={1080} fill={`url(#iris${id})`} />
        </mask>
      </defs>
      <g mask={`url(#irm${id})`}>
        <g transform={`translate(${s.x} ${s.y}) scale(${k}) translate(${-anchor.x} ${-anchor.y})`}>{children}</g>
      </g>
    </g>
  );
};
// 近景淡入淡出按镜头远近：点的直径大于约 150 px 时近景已经全亮
const nearO = (z: number, zNear: number) => clamp((Math.log(z) - Math.log(zNear * 0.2)) / (Math.log(zNear * 0.42) - Math.log(zNear * 0.2)));

const Stage: React.FC<{f: number}> = ({f}) => {
  const b = beatAt(f);
  const gen = genAt(f);
  switch (b.scene) {
    case 'open':
      return <NearOpen f={f} />;
    case 'pullback': {
      // 往后拉：近景的两个人一边缩小一边淡出（1.6–2.0 秒），同时点阵从中景远近（点直径约 100 px、看得见眼睛）淡入，
      // 你那颗点正落在近景里你的位置上，然后一路退到全场。点阵从不在点比 100 px 还大的时候出现。
      const t = prog(f, eva('S02', 'zoomOut'));
      const u = 1 - Math.pow(1 - t, 2.2);
      const start = zoomOn(YOU_W, OPEN.youX, 650, 4.5);
      const cam = camAt(start, FAR, u);
      const fn = eva('S02', 'fadeNear');
      const nearK = Math.exp(lerp(0, Math.log(0.42), 1 - Math.pow(1 - prog(f, [fn[0], fn[1] + 4]), 2)));
      const nearOp = 1 - ease(prog(f, fn));
      const crowdOp = ease(prog(f, [fn[0], fn[1] - 2]));
      const rp = prog(f, [evn('S02', 'ringPulse'), evn('S02', 'ringPulse') + 9]);
      const ys = toScreen(cam, YOU_W);
      return (
        <>
          <CrowdFloor gen={0} />
          <Room x={OPEN.youX} f={f} o={nearOp} />
          <Crowd f={f} gen={0} cam={cam} sparks opacity={crowdOp} ring={{scale: 1 + 0.35 * Math.sin(Math.PI * rp), o: crowdOp}} tint={0} />
          {nearOp > 0.01 && (
            <g opacity={nearOp}>
              <NearOpen f={f} noRoom tf={`translate(${ys.x} ${ys.y}) scale(${nearK}) translate(${-OPEN.youX} ${-650})`} />
            </g>
          )}
        </>
      );
    }
    case 'far': {
      let cam = FAR;
      let opacity = 1;
      let dim: ((c: number, s: number) => number) | undefined;
      let ring: {color?: string; scale?: number} | undefined;
      let links: number | undefined;
      // 3.8 秒那拍开局那 500 个老实人亮着，其余压到约 0.12（一片黄变成一片红）；S04 停在第 70 代，undim 里其余的点回到全亮
      if (b.id === 'S03') { const k = lerp(1, OTHERS_DIM, ease(prog(f, eva('S03', 'dimCrowd')))); dim = (c) => (STARTER_SET.has(c) ? 1 : k); }
      if (b.id === 'S04') { const k = lerp(OTHERS_DIM, 1, ease(prog(f, eva('S04', 'undim')))); dim = (c) => (STARTER_SET.has(c) ? 1 : k); }
      if (b.id === 'S03' || b.id === 'S04') { cam = driftCam(f); ring = youRing(f); }
      if (b.id === 'S14') { cam = f < evn('S14', 'pushFrom') ? camAt(MID, FAR, ease(prog(f, eva('S14', 'zoom')))) : pushCam(f); links = genF(f); }
      if (b.id === 'S15' || b.id === 'S16') cam = pushCam(f);
      // 第五版补改：S15 不再画连向被你坑的人的红线（没字看不懂，只看片的审片），“可狠的人越来越多”接着挂；只留你身上的红圈
      if (b.id === 'S15') ring = {color: RED_HI, scale: 1.08};
      if (b.id === 'S19') { cam = camAt(MID, FAR, ease(prog(f, eva('S19', 'zoom')))); dim = (_c, s) => (HARSH(s) ? 0.45 : 1); }
      return (
        <>
          <CrowdFloor gen={gen} />
          <Crowd f={f} gen={gen} cam={cam} opacity={opacity} sparks dim={dim} ring={ring} links={links} tint={gen} />
          {(b.id === 'S03' || b.id === 'S04') && <YouMark f={f} cam={cam} o={1} />}
        </>
      );
    }
    case 'rewind': {
      // 倒带 0.3 秒：颜色倒回一片黄，画面变暗；扎进去 0.3 秒：点长大时淡出，近景从你那颗点展开
      const dv = prog(f, eva('S05', 'dive'));
      const zN = 18;
      const cam = camAt(DRIFT_END, zoomOn(YOU_W, NL.youX, 640, zN), Math.pow(dv, 1.6));
      const dv0 = eva('S05', 'dive')[0];
      return (
        <>
          <CrowdFloor gen={gen} />
          <Crowd f={f} gen={gen} cam={cam} sparks fadeBig tint={gen} ring={youRing(f)} />
          <YouMark f={f} cam={cam} o={1 - prog(f, [dv0 - 3, dv0 + 2])} />
          <rect width={1920} height={1080} fill="#000" opacity={0.35 * prog(f, eva('S05', 'rewind')) * (1 - dv)} />
          <NearIris cam={cam} zNear={zN} anchor={{x: NL.youX, y: 640}} o={nearO(cam.z, zN)} id="rw">
            <NearBeat f={beat('S06').f0} id="S06" />
          </NearIris>
        </>
      );
    }
    case 'mid': {
      // 中景（约 60 个点）：要变的黄点眼睛先转向旁边条长的点，再从上往下刷成那个颜色
      // 第五版第二轮：S11 的中景镜头整体往下让 36 px，第一排脸不贴着顶上的路线图（S11 前后都是硬切，只动这一拍）；
      // 再往上那一排本来被舞台上沿的渐隐压着，下沿会从路线图名字底下露出来，用 topFade 按点的中心 y 175–262 淡掉（推镜时一排排平滑地淡进来）
      const MID11 = {...MID, ay: MID.ay + 36};
      const cam = camAt({...MID11, z: 6}, MID11, ease(prog(f, eva('S11', 'zoom'))));
      const ticks = TL.gen.filter((k) => k.mode === 'step' && k.f > b.f0 && k.f <= b.f1).map((k) => k.f);
      const last = ticks.filter((t) => t <= f).pop();
      const next = ticks.find((t) => t > f);
      const sweep = last !== undefined && f - last < 9 ? {from: gen - 1, p: (f - last) / 9} : null;
      return (
        <>
          <CrowdFloor gen={gen} />
          <Crowd f={f} gen={gen} cam={cam} sparks bars={f >= evn('S11', 'bars')} sweep={sweep} lookAt={next !== undefined && next - f <= 10} tint={gen} topFade={[175, 262]} />
        </>
      );
    }
    case 'midYou':
      return <MidYou f={f} gen={gen} />;
    case 'near': {
      if (b.id === 'S20') {
        const [p0, p1] = eva('S20', 'push');
        if (f < p1) {
          const zN = 14;
          const cam = camAt(FAR, zoomOn(YOU_W, NL.youX, 640, zN), Math.pow(ease(prog(f, [p0, p1])), 1.3));
          return (
            <>
              <CrowdFloor gen={gen} />
              <Crowd f={f} gen={gen} cam={cam} sparks fadeBig tint={gen} />
              <NearIris cam={cam} zNear={zN} anchor={{x: NL.youX, y: 640}} o={nearO(cam.z, zN)} id="s20">
                <NearBeat f={p1} id="S20" />
              </NearIris>
            </>
          );
        }
      }
      // 第五版：S18b 接着画 S18 的近景（timeline.json 的 as），S18 的转头、比条、变色都落在 S18b 的时间里，34.6 秒硬切到 S19
      return <NearBeat f={f} id={b.as ?? b.id} />;
    }
    case 'block':
      return <Block f={f} gen={gen} />;
    case 'four': {
      // 第七版重排：四个你从红色点阵过来（上一拍 S26 停在第 900 代）。scatter 里点阵往前推近、淡掉，地面从冷慢慢回暖，四个你在 appear 里亮出来，四盏灯照旧
      const sc = ease(prog(f, eva('S25', 'scatter')));
      const cc = cycleCrowd(f);
      const [sc0] = eva('S25', 'scatter'), ap1 = eva('S25', 'appear')[1];
      return (
        <>
          <CrowdFloor gen={300} w={lerp(cc.w, 1, ease(prog(f, [sc0, ap1])))} />
          {/* 点阵的淡出拉到 appear 结束（线性），和四个你亮出来叠着，中间不黑一下 */}
          {f < ap1 && (
            <Crowd f={f} gen={300} cam={camAt(FAR, {...FAR, z: 1.5}, sc)} opacity={1 - prog(f, [sc0, ap1])} sparks strat={cc.strat} paint={cc.paint} coop={cc.coop}
              tint={300} tintW={cc.tintW} ring={{o: 0}} />
          )}
          <Four f={f} />
        </>
      );
    }
    case 'cycle':
      // 第七版 S26：从第 300 代接着往下跑，“可新人一多，狠人又回来了”（FEnding 的 Cycle）
      return <Cycle f={f} />;
    case 'endYou': {
      // 第七版重排：S27、S27h 不出字。S27 的 dive 里从四个你过渡到结尾的你：另外三个你和四根条淡掉，
      // 绿衣的你从那一排里走到结尾的位置、经正面转身朝左，灯跟着挪，房间和“你”标签淡入（EndYou 的 morph）；
      // dive 结束 = pushFrom，慢推从这一帧起，S27h、S28 照旧（S28 开头平移回 0 秒构图）
      if (b.id === 'S27' && f < eva('S27', 'dive')[1]) {
        const m = ease(prog(f, eva('S27', 'dive')));
        return (
          <>
            <CrowdFloor gen={300} />
            {/* 另外三个在前七成里淡完，“你”标签后四成半才淡入（途中标签会落在蓝衣那个你的脸上） */}
            <Four f={f} hideGreen others={1 - ease(clamp(m / 0.7))} />
            <EndYou f={f} morph={m} />
          </>
        );
      }
      return <EndYou f={f} />;
    }
    default:
      return null;
  }
};

const hasSfx = () => {
  try {
    return getStaticFiles().some((s) => s.name === '002/sfx.wav');
  } catch {
    return false;
  }
};

export const Film002: React.FC<{audio?: boolean}> = ({audio = true}) => {
  const f = useCurrentFrame();
  const b = beatAt(f);
  const gen = genAt(f);
  const vignette = b.scene === 'far' || b.scene === 'mid' || b.scene === 'rewind' || b.scene === 'pullback' || b.scene === 'midYou' || b.scene === 'block' || b.scene === 'cycle' || (b.scene === 'near' && b.id === 'S20' && f < eva('S20', 'push')[1]);
  // 第七版重排：S25 从点阵（四角压暗 1）过来，scatter 里慢慢回到四个你那一拍的 0.7，不在拍边界跳
  const vigO = b.id === 'S25' ? lerp(1, 0.7, prog(f, eva('S25', 'scatter'))) : vignette ? 1 : 0.7;
  const sfx = audio && hasSfx();
  // S08 推镜（zoomIn 开始到 zoomOut 结束）时顶栏 6 帧淡出，推完 6 帧淡回来（“AI 生成”不动）
  const [zi0] = eva('S08', 'zoomIn');
  const zo1 = eva('S08', 'zoomOut')[1];
  const topO = 1 - ease(prog(f, [zi0, zi0 + 6])) + ease(prog(f, [zo1, zo1 + 6]));
  // 第五版：S24 方块聚拢后路线图压到一半亮（一屏一个焦点：方块；第七版三改方块上的标签已去掉），一直到 S26 开头退场
  const g1 = eva('S24', 'gather')[1];
  const routeO = topO * lerp(1, 0.5, ease(prog(f, [g1 - 4, g1 + 6])));
  return (
    <AbsoluteFill style={{background: '#0D1016'}}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <FilmDefs /><CrowdDefs /><RoomDefs gen={gen} />
        <Stage f={f} />
        <Vignette o={vigO} />
      </svg>
      <SubBand />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <FilmDefs /><RouteDefs />
        <RouteMap f={f} o={routeO} />
      </svg>
      <Question f={f} outP={easeOut(prog(f, eva('S03', 'qOut')))} o={topO} />
      <Subtitles lines={b.lines} f={f} sub={b.sub} />
      <AiBadge />
      {sfx && <Html5Audio src={staticFile('002/sfx.wav')} />}
    </AbsoluteFill>
  );
};


export const _unused2 = {Victims};
