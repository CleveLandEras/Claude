// 对照图：把两种画风的同一个镜头左右并排。另一张按手机实际大小缩小（竖屏片在手机上满屏，约 390 点宽）。
import React from 'react';
import {AbsoluteFill, Freeze} from 'remotion';
import {A1, A2, A3, A4, A5, AMini} from './FlatShots';
import {B1, B2, B3, B4, B5, BMini} from './InkShots';
import {STILL_FRAME} from './scene';

const SHOTS: {label: string; A: React.FC; B: React.FC; frame?: number}[] = [
  {label: '1 情绪特写：看底牌', A: A1, B: B1},
  {label: '2 全身姿势：输了瘫在椅背上', A: A2, B: B2},
  {label: '3 道具当主角：公共牌和筹码', A: A3, B: B3},
  {label: '4 两个人：全推 / 是不是在诈', A: A4, B: B4},
  {label: '5 比喻：差一张，有几成', A: A5, B: B5},
  {label: '小动作片第 100 帧：河牌翻开', A: AMini, B: BMini, frame: 100},
];

// 一格：把 1080×1920 的镜头缩到 w 宽
const Cell: React.FC<{C: React.FC; w: number; frame: number}> = ({C, w, frame}) => {
  const k = w / 1080;
  return (
    <div style={{position: 'relative', width: w, height: 1920 * k, overflow: 'hidden', borderRadius: 4}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `scale(${k})`, transformOrigin: '0 0'}}>
        <Freeze frame={frame}><C /></Freeze>
      </div>
    </div>
  );
};

const FONT = '"PingFang SC", "Hiragino Sans GB", sans-serif';

// 对照总图：三列镜头对，每对 A 左 B 右
export const CompareSheet: React.FC = () => {
  const w = 480, gap = 14, pairGap = 56;
  return (
    <AbsoluteFill style={{background: '#EAE6DE', padding: 40, fontFamily: FONT}}>
      <div style={{fontSize: 40, fontWeight: 600, color: '#2A2420', marginBottom: 8}}>画风测试：A 扁平矢量小人（左） / B 手绘墨线小人（右）</div>
      <div style={{fontSize: 24, color: '#6A625A', marginBottom: 28}}>同一镜头、同一套骨骼和表情，只换画风。1080×1920 缩到 {w} 宽。</div>
      <div style={{display: 'flex', flexWrap: 'wrap', columnGap: pairGap, rowGap: 34}}>
        {SHOTS.map((sh) => (
          <div key={sh.label}>
            <div style={{fontSize: 26, color: '#2A2420', marginBottom: 10, fontWeight: 600}}>{sh.label}</div>
            <div style={{display: 'flex', gap}}>
              <div>
                <Cell C={sh.A} w={w} frame={sh.frame ?? STILL_FRAME} />
                <div style={{fontSize: 22, color: '#6A625A', marginTop: 6}}>A</div>
              </div>
              <div>
                <Cell C={sh.B} w={w} frame={sh.frame ?? STILL_FRAME} />
                <div style={{fontSize: 22, color: '#6A625A', marginTop: 6}}>B</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
export const COMPARE_W = 40 * 2 + 3 * (480 * 2 + 14) + 2 * 56;
export const COMPARE_H = 40 * 2 + 48 + 8 + 30 + 28 + 2 * (36 + 853 + 34) + 34;

// 手机实际大小：一部 6.1 寸手机屏宽约 390 点，竖屏片满屏，就是 390×693。按 1 点 = 1 像素排，在电脑上 100% 看，大小接近手里那部手机
export const PhoneSheet: React.FC = () => {
  const w = 390;
  return (
    <AbsoluteFill style={{background: '#D9D4CB', padding: 30, fontFamily: FONT}}>
      <div style={{fontSize: 22, color: '#2A2420', marginBottom: 14, fontWeight: 600}}>按手机实际大小（390 点宽）：上排 A，下排 B</div>
      {(['A', 'B'] as const).map((k) => (
        <div key={k} style={{display: 'flex', gap: 18, marginBottom: 18}}>
          {SHOTS.map((sh) => (
            <div key={sh.label} style={{borderRadius: 26, overflow: 'hidden', border: '6px solid #1B1918'}}>
              <Cell C={sh[k]} w={w} frame={sh.frame ?? STILL_FRAME} />
            </div>
          ))}
        </div>
      ))}
    </AbsoluteFill>
  );
};
export const PHONE_W = 30 * 2 + 6 * (390 + 12) + 5 * 18;
export const PHONE_H = 30 * 2 + 36 + 2 * (693 + 12 + 18);

// 自己看图用：只排一种画风的几个镜头
export const Review: React.FC<{kind: 'A' | 'B'; frame?: number}> = ({kind, frame}) => (
  <AbsoluteFill style={{background: '#777', display: 'flex', flexDirection: 'row', gap: 10, padding: 10}}>
    {SHOTS.map((sh) => <Cell key={sh.label} C={sh[kind]} w={520} frame={sh.frame ?? frame ?? STILL_FRAME} />)}
  </AbsoluteFill>
);

// 小动作片分解：一条片子取 8 帧排成一排（看动作连不连得上）
export const MINI_STRIP_FRAMES = [0, 30, 50, 72, 88, 100, 116, 140];
export const MiniStrip: React.FC<{kind: 'A' | 'B'}> = ({kind}) => {
  const C = kind === 'A' ? AMini : BMini;
  return (
    <AbsoluteFill style={{background: '#D9D4CB', display: 'flex', flexDirection: 'row', gap: 12, padding: 16, fontFamily: FONT}}>
      {MINI_STRIP_FRAMES.map((fr) => (
        <div key={fr}>
          <Cell C={C} w={380} frame={fr} />
          <div style={{fontSize: 22, color: '#2A2420', marginTop: 6}}>第 {fr} 帧（{(fr / 30).toFixed(1)} 秒）</div>
        </div>
      ))}
    </AbsoluteFill>
  );
};
