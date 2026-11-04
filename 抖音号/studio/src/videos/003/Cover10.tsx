// 003 v10 封面：竖版 3:4、横版 4:3。字照 videos/003_消息提醒/发布文案.md 最上面“封面字”；
// 画面取成片第 24.6 秒（开了免打扰，手机没响，手伸向手机）冻结，只截人和手机那一块。
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Notice10} from './Notice10';

const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
const FRAME = 738;                                   // 24.6 秒
const CROP = {x: 770, y: 110, w: 845, h: 790};       // 成片画面里人和手机那一块

const Crop: React.FC<{left: number; top: number; k: number}> = ({left, top, k}) => (
  <div style={{position: 'absolute', left, top, width: CROP.w * k, height: CROP.h * k, overflow: 'hidden', borderRadius: 28}}>
    <div style={{position: 'absolute', left: -CROP.x * k, top: -CROP.y * k, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>
      <Notice10 atFrame={FRAME} />
    </div>
  </div>
);

export const Cover10: React.FC<{w: number; h: number}> = ({w, h}) => {
  const tall = h > w;
  const big: React.CSSProperties = {fontFamily: SANS, fontWeight: 800, color: '#FFF8EC', lineHeight: 1.18,
    textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'};
  const small: React.CSSProperties = {fontFamily: SANS, fontWeight: 700, color: '#FFC94D', lineHeight: 1.3};
  return (
    <AbsoluteFill style={{background: '#101219'}}>
      {tall ? (
        <>
          <Crop left={(w - CROP.w * 1.1) / 2} top={570} k={1.1} />
          <div style={{position: 'absolute', left: 70, top: 96, width: w - 140}}>
            <div style={{...big, fontSize: 118}}>开了免打扰，<br />手还是会伸过去</div>
            <div style={{...small, fontSize: 56, marginTop: 30}}>我觉得，不全是消息多，还有怕漏</div>
          </div>
        </>
      ) : (
        <>
          <Crop left={w - CROP.w * 0.9 - 40} top={(h - CROP.h * 0.9) / 2 + 30} k={0.9} />
          <div style={{position: 'absolute', left: 56, top: 220, width: 620}}>
            <div style={{...big, fontSize: 100}}>开了免打扰，<br />手还是会<br />伸过去</div>
            <div style={{...small, fontSize: 50, marginTop: 34}}>我觉得，不全是消息多，<br />还有怕漏</div>
          </div>
        </>
      )}
      <div style={{position: 'absolute', left: 24, top: 24, padding: '1px 14px', borderRadius: 9, fontFamily: SANS, fontWeight: 600, fontSize: 40, lineHeight: '50px',
        color: 'rgba(246,240,228,0.92)', background: 'rgba(0,0,0,0.5)', border: '2px solid rgba(246,240,228,0.36)'}}>AI 生成</div>
    </AbsoluteFill>
  );
};
