// 002《被坑多了，人会变狠吗？》横屏灰框预演。目的：锁节奏、量读字负担、看字在手机上够不够大。不是成片。
// 时间、字幕、镜头远近全读 timeline.json（timeline.py 生成）；点阵、计数、方块、历史条全读 data.json（make_data.py 生成）。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {COL, Cam, D, FAR, HARSH, I, MID, TL, YOU_W, animF, beat, beatAt, camAt, cellXY, clamp, ease, eva, evn, genAt, genF, lerp, prog, toScreen, zoomOn} from './lib';
import {Crowd} from './Crowd';
import {Tag} from './people';
import {END_X, EndYou, NL, NearBeat, NearOpen, OPEN, endPush} from './Near';
import {Block, Four, Hist20, MidYou, Others, PUSH_END} from './Ending';
import {GenCounter, HarshCounter, HistBar, MeDot, Question, SubBand, Subtitles, everHarshAt, histX, HIST_Y} from './Overlay';

export const GRAY_FRAMES = TL.frames;

const Defs: React.FC = () => (
  <defs>
    <radialGradient id="sparkGlow"><stop offset="0" stopColor="#FFE9C2" stopOpacity={0.65} /><stop offset="1" stopColor="#FFE9C2" stopOpacity={0} /></radialGradient>
    <radialGradient id="meGlow"><stop offset="0" stopColor="#FFFFFF" stopOpacity={0.55} /><stop offset="1" stopColor="#FFFFFF" stopOpacity={0} /></radialGradient>
    <radialGradient id="warmGlow"><stop offset="0" stopColor="#FFD9A0" stopOpacity={0.45} /><stop offset="1" stopColor="#FFD9A0" stopOpacity={0} /></radialGradient>
    <radialGradient id="lampGlow"><stop offset="0" stopColor="#4A3F31" stopOpacity={0.95} /><stop offset="0.55" stopColor="#2A2620" stopOpacity={0.5} /><stop offset="1" stopColor="#11141B" stopOpacity={0} /></radialGradient>
  </defs>
);

const PINK = '#d55181';

// “和你”：粉线从你的点一根根连到第 7 代被你坑的 6 个老实人（画成那时的黄色）
const Victims: React.FC<{f: number; cam: Cam}> = ({f, cam}) => {
  const [l0, l1] = eva('S15', 'lines');
  const me = toScreen(cam, YOU_W);
  const r = (TL.layout.far.dot / 2) * cam.z;
  return (
    <g>
      {D.grid.victims.map((c, i) => {
        const p = toScreen(cam, cellXY(c));
        const t0 = lerp(l0, l1 - 5, i / (D.grid.victims.length - 1));
        const u = ease(prog(f, [t0, t0 + 5]));
        if (u <= 0) return null;
        return (
          <g key={c}>
            <line x1={me.x} y1={me.y} x2={lerp(me.x, p.x, u)} y2={lerp(me.y, p.y, u)} stroke={PINK} strokeWidth={6} strokeLinecap="round" />
            <circle cx={p.x} cy={p.y} r={r} fill={COL[I.ALLC]} opacity={u} />
            <circle cx={p.x} cy={p.y} r={r + 8} fill="none" stroke={COL[I.ALLC]} strokeWidth={4} opacity={u} />
          </g>
        );
      })}
    </g>
  );
};

// 24.4–28.4 秒：镜头一直往你那颗点推（定住的 0.3 秒里也停），推到 28.4 秒接上中近景
const pushCam = (f: number) => {
  const a = animF(evn('S14', 'pushFrom')), b = animF(evn('S16', 'pushTo'));
  return camAt(FAR, PUSH_END, clamp((animF(f) - a) / (b - a)));
};

const Stage: React.FC<{f: number}> = ({f}) => {
  const b = beatAt(f);
  const gen = genAt(f);
  switch (b.scene) {
    case 'open':
      return <NearOpen f={f} />;
    case 'pullback': {
      // 往后拉：你和骗子缩成一黄一橙两颗带眼睛的点，四周铺开 1000 个点
      const fn = eva('S02', 'fadeNear');
      const start = zoomOn(YOU_W, OPEN.youX, 650, 24);
      const cam = camAt(start, FAR, ease(prog(f, eva('S02', 'zoomOut'))));
      const rp = prog(f, [evn('S02', 'ringPulse'), evn('S02', 'ringPulse') + 9]);
      return (
        <>
          <Crowd f={f} gen={0} cam={cam} eyes sparks opacity={prog(f, [fn[0], fn[0] + 6])} ring={{scale: 1 + 0.35 * Math.sin(Math.PI * rp)}} tint={0} />
          <NearOpen f={f} o={1 - prog(f, fn)} scale={lerp(1, 0.3, ease(prog(f, fn)))} />
        </>
      );
    }
    case 'far': {
      let cam = FAR;
      let opacity = 1;
      let dim: ((c: number, s: number) => number) | undefined;
      let ring: {color?: string; scale?: number} | undefined;
      let links: number | undefined;
      if (b.id === 'S03') opacity = lerp(1, 0.7, prog(f, eva('S03', 'dimCrowd')));
      if (b.id === 'S04') opacity = lerp(0.7, 1, prog(f, eva('S04', 'undim')));
      if (b.id === 'S14') { cam = f < evn('S14', 'pushFrom') ? camAt(MID, FAR, ease(prog(f, eva('S14', 'zoom')))) : pushCam(f); links = genF(f); }
      if (b.id === 'S15' || b.id === 'S16') cam = pushCam(f);
      if (b.id === 'S15') {
        // “和你”：从你的点连出粉线，连到第 7 代被你坑的那 6 颗黄点，再定住；其余压暗
        ring = {color: PINK, scale: 1.08};
        const vic = new Set(D.grid.victims);
        dim = (c) => (vic.has(c) ? 1 : lerp(1, 0.35, prog(f, [b.f0, b.f0 + 5])));
      }
      if (b.id === 'S19') { cam = camAt(MID, FAR, ease(prog(f, eva('S19', 'zoom')))); dim = (_c, s) => (HARSH(s) ? 0.45 : 1); }
      return (
        <>
          <Crowd f={f} gen={gen} cam={cam} opacity={opacity} sparks dim={dim} ring={ring} links={links} eyes={cam.z > 2} tint={gen} />
          {b.id === 'S15' && <Victims f={f} cam={cam} />}
          {(b.id === 'S04' || b.id === 'S19') && f >= evn(b.id, 'greenTag') && (
            <Tag x={1430} y={262} text="绿＝会原谅" bg={COL[I.GTFT]} size={80} o={prog(f, [evn(b.id, 'greenTag'), evn(b.id, 'greenTag') + 6])} />
          )}
        </>
      );
    }
    case 'rewind': {
      // 倒带 0.3 秒：颜色倒回一片黄，画面变暗；扎进去 0.3 秒：镜头扎进你的点
      const dv = ease(prog(f, eva('S05', 'dive')));
      const cam = camAt(FAR, zoomOn(YOU_W, NL.youX, 640, 18), dv);
      return (
        <>
          <Crowd f={f} gen={gen} cam={cam} sparks eyes={cam.z > 2} tint={gen} />
          <rect width={1920} height={1080} fill="#000" opacity={0.35 * prog(f, eva('S05', 'rewind')) * (1 - dv)} />
        </>
      );
    }
    case 'mid': {
      // 拉到中景（约 60 个点）：要变的黄点眼睛先转向旁边条长的点，再从上往下刷成那个颜色
      const cam = camAt({...MID, z: 9}, MID, ease(prog(f, eva('S11', 'zoom'))));
      const ticks = TL.gen.filter((k) => k.mode === 'step' && k.f > b.f0 && k.f <= b.f1).map((k) => k.f);
      const last = ticks.filter((t) => t <= f).pop();
      const next = ticks.find((t) => t > f);
      const sweep = last !== undefined && f - last < 9 ? {from: gen - 1, p: (f - last) / 9} : null;
      return (
        <>
          <Crowd f={f} gen={gen} cam={cam} eyes sparks bars={f >= evn('S11', 'bars')} sweep={sweep}
            lookAt={next !== undefined && next - f <= 10} tint={gen} />
        </>
      );
    }
    case 'midYou':
      return <MidYou f={f} gen={gen} />;
    case 'near': {
      if (b.id === 'S20') {
        const [p0, p1] = eva('S20', 'push');
        if (f < p1) {
          const cam = camAt(FAR, zoomOn(YOU_W, NL.youX, 640, 14), ease(prog(f, [p0, p1])));
          return <Crowd f={f} gen={gen} cam={cam} sparks eyes={cam.z > 2} tint={gen} />;
        }
      }
      return <NearBeat f={f} id={b.id} />;
    }
    case 'block':
      return <Block f={f} gen={gen} />;
    case 'four':
      return (
        <>
          {f < eva('S25', 'scatter')[1] && <Block f={f} gen={gen} scatter={prog(f, eva('S25', 'scatter'))} />}
          <Four f={f} />
        </>
      );
    case 'hist20':
      return (<><Four f={f} up={prog(f, eva('S26', 'shrinkUp'))} /><Hist20 f={f} /></>);
    case 'fourEnd': {
      // 带走句“狠是学来的，原谅也是”：绿衣的你原地不动，另外三个你在左边淡入（只淡入一次），灯都亮着，镜头慢推
      const fi = ease(prog(f, eva('S27b', 'fourIn')));
      return (
        <>
          <EndYou f={f} tagO={1 - fi} />
          <g transform={endPush(f)}><Others f={f} o={fi} endX={END_X} G={NL.G} s={NL.s} /></g>
        </>
      );
    }
    case 'endYou': {
      const fo = b.id === 'S28' ? ease(prog(f, eva('S28', 'fourOut'))) : b.id === 'S29' ? 1 : 0;
      return (
        <>
          {b.id === 'S27' && <Hist20 f={f} />}
          <EndYou f={f} o={b.id === 'S27' ? ease(prog(f, eva('S27', 'dive'))) : 1} tagO={b.id === 'S27' ? 1 : fo} />
          {b.id === 'S28' && fo < 1 && <g transform={endPush(f)}><Others f={f} o={1 - fo} endX={END_X} G={NL.G} s={NL.s} /></g>}
        </>
      );
    }
    default:
      return null;
  }
};

export const Gray002: React.FC = () => {
  const f = useCurrentFrame();
  const b = beatAt(f);
  const gf = genF(f);
  const gen = genAt(f);
  const cf = TL.counterFrom;
  const copy0 = eva('S26', 'copyDown')[0];
  const dive = prog(f, eva('S27', 'dive'));
  // 白点：3.4 秒从字幕最前面飞上去，落到历史条左端，之后就是播放头
  const [m0, m1] = eva('S03', 'meFly');
  const flyP = ease(prog(f, [m0, m1]));
  const w02 = (beat('S02') as unknown as {read: {widths: number[]}}).read.widths[0];
  const meAt = f < m1 ? {x: lerp(TL.layout.sub.cx - w02 / 2 + 20, histX(0), flyP), y: lerp(995, HIST_Y, flyP)} : {x: histX(gf), y: HIST_Y};
  const harshO = b.id === 'S03' || b.id === 'S04' ? prog(f, eva('S03', 'counterIn')) * (1 - prog(f, eva('S04', 'counterOut'))) : 0;
  const histO = prog(f, [cf, cf + 4]);
  return (
    <AbsoluteFill style={{background: '#101219'}}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <Defs />
        <Stage f={f} />
      </svg>
      <SubBand />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute'}}>
        <Defs />
        {f >= cf && f < copy0 && <HistBar counts={D.counts} x0={TL.layout.hist.x0} x1={TL.layout.hist.x1} y0={TL.layout.hist.y0} y1={TL.layout.hist.y1} upTo={gf} o={histO} />}
        {f >= m0 && f < copy0 && <MeDot x={meAt.x} y={meAt.y} r={15} />}
      </svg>
      <Question f={f} outP={prog(f, eva('S26', 'questionOut'))} />
      {f >= cf && <GenCounter gen={gen} o={histO * (1 - dive)} />}
      {harshO > 0 && <HarshCounter n={everHarshAt(gen)} o={harshO} />}
      <Subtitles lines={b.lines} f={f} sub={b.sub} />
    </AbsoluteFill>
  );
};

