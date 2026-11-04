// 《等待》终版封面（10/28）：和片子同一套画风。灯下的人，脚背上的电极正炸开冷光；大字“宁可更疼，也不想多等。”
// （按 Berns 2006 原文：9 个人宁可电得更重也要早点挨，选早的那边也要等几秒，所以是“不想多等”）。横版 4:3、竖版 3:4 各一张。
import {AbsoluteFill} from 'remotion';
import {L, Room} from './Room';

export const CoverLook: React.FC<{w: number; h: number}> = ({w, h}) => {
  const tall = h > w;
  const fig = tall ? {x: 400, y: 1060, s: 1.75} : {x: 420, y: 720, s: 1.6};
  return (
    <AbsoluteFill style={{background: '#050403', filter: 'brightness(1.12)'}}>
      <Room id="cover" w={w} h={h} f={40} fig={fig} lampX={fig.x - 40} strike={{k: 1, power: 1}} cold={0.6} lamp={1.1}
        lean={6} look={-8} dial={1} dialHot={1} lampDrop={tall ? 40 : 0} />
      <div lang="zh-Hans" style={{position: 'absolute', fontFamily: L.serif, fontWeight: 700, lineHeight: 1.18, letterSpacing: '0.02em',
        textShadow: '0 4px 30px rgba(0,0,0,0.95)',
        ...(tall ? {left: 0, right: 0, top: 100, textAlign: 'center', fontSize: 150} : {left: 690, top: 270, fontSize: 112})}}>
        <div style={{color: L.red}}>宁可更疼，</div>
        <div style={{color: L.ink}}>也不想多等。</div>
      </div>
      <div lang="zh-Hans" style={{position: 'absolute', fontFamily: L.serif, color: 'rgba(243,235,221,0.75)', letterSpacing: '0.08em',
        ...(tall ? {left: 0, right: 0, top: 476, textAlign: 'center', fontSize: 42} : {left: 696, top: 560, fontSize: 38})}}>
        2006 · 埃默里大学的电击实验
      </div>
    </AbsoluteFill>
  );
};
