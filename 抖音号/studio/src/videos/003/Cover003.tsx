// 003《消息提醒》封面（第八版）：竖版 3:4、横版 4:3。字照 videos/003_消息提醒/发布文案.md “封面字”；
// 画面取成片第 31.6 秒（“以下消息仍通知”页：三个开关全开、老师和领导已加进去）冻结，只截设置页那一块。
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Notice8} from './Notice8';

const SANS = '"PingFang SC", "Hiragino Sans GB", "Heiti SC", system-ui, sans-serif';
const FRAME = 948;                                  // 31.6 秒
const CROP = {x: 500, y: 26, w: 920, h: 900};       // 成片画面里设置页那一块

const Crop: React.FC<{left: number; top: number; k: number}> = ({left, top, k}) => (
  <div style={{position: 'absolute', left, top, width: CROP.w * k, height: CROP.h * k, overflow: 'hidden', borderRadius: 28}}>
    <div style={{position: 'absolute', left: -CROP.x * k, top: -CROP.y * k, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>
      <Notice8 atFrame={FRAME} />
    </div>
  </div>
);

export const Cover003: React.FC<{w: number; h: number}> = ({w, h}) => {
  const tall = h > w;
  const big: React.CSSProperties = {fontFamily: SANS, fontWeight: 800, color: '#FFF8EC', lineHeight: 1.18,
    textShadow: '0 4px 0 rgba(0,0,0,0.35), 0 8px 30px rgba(0,0,0,0.65)'};
  const small: React.CSSProperties = {fontFamily: SANS, fontWeight: 700, color: '#FFC94D', lineHeight: 1.3};
  return (
    <AbsoluteFill style={{background: '#101219'}}>
      {tall ? (
        <>
          <Crop left={(w - CROP.w * 1.0) / 2} top={500} k={1.0} />
          <div style={{position: 'absolute', left: 70, top: 90, width: w - 140}}>
            <div style={{...big, fontSize: 124}}>群太吵，<br />又怕漏通知？</div>
            <div style={{...small, fontSize: 60, marginTop: 30}}>开免打扰，留住老师和 @所有人</div>
          </div>
        </>
      ) : (
        <>
          <Crop left={w - CROP.w * 0.86 - 40} top={(h - CROP.h * 0.86) / 2} k={0.86} />
          <div style={{position: 'absolute', left: 60, top: 230, width: 620}}>
            <div style={{...big, fontSize: 112}}>群太吵，<br />又怕漏<br />通知？</div>
            <div style={{...small, fontSize: 54, marginTop: 34}}>开免打扰，<br />留住老师和<br />@所有人</div>
          </div>
        </>
      )}
      <div style={{position: 'absolute', left: 24, top: 24, padding: '1px 14px', borderRadius: 9, fontFamily: SANS, fontWeight: 600, fontSize: 40, lineHeight: '50px',
        color: 'rgba(246,240,228,0.92)', background: 'rgba(0,0,0,0.5)', border: '2px solid rgba(246,240,228,0.36)'}}>AI 生成</div>
    </AbsoluteFill>
  );
};
