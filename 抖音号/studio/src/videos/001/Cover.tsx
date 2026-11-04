// 《等待》封面：封面字“宁可更疼，也不想多等。”（那 9 人也等了 9 秒，所以是“不想多等”），配第四版里那道大闪电（电 = 疼）。横版 4:3、竖版 3:4 各一张。
import {AbsoluteFill} from 'remotion';
import {S as Sans} from '../../style';
import {Bolt} from './Opening';

const RED = '#FF5A4E';

export const Cover: React.FC<{w: number; h: number}> = ({w, h}) => {
  const tall = h > w;
  const size = tall ? 150 : 132;
  return (
    <AbsoluteFill style={{background: '#000', fontFamily: Sans.sans}}>
      <div style={{position: 'absolute', left: -w * 0.1, top: h * 0.05, width: w * 1.2, height: h * 0.8, borderRadius: '50%',
        filter: 'blur(90px)', background: 'radial-gradient(ellipse, rgba(40,80,220,0.28), rgba(0,0,0,0) 62%)'}} />
      <svg width={w} height={h} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <defs><filter id="boltGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18" /></filter></defs>
        <Bolt cx={w / 2} cy={tall ? h * 0.27 : h * 0.26} h={tall ? 380 : 300} flash={0.55} id="cover" />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: tall ? h * 0.47 : h * 0.5, textAlign: 'center', fontSize: size,
        lineHeight: 1.25, letterSpacing: '0.02em'}}>
        <div style={{fontWeight: 300, color: 'rgba(220,226,240,0.88)'}}>宁可更疼，</div>
        <div style={{fontWeight: 700, color: '#F4F6FB'}}>也<span style={{color: RED}}>不想多等</span>。</div>
      </div>
      <div style={{position: 'absolute', left: 56, top: 44, fontSize: 30, color: 'rgba(190,198,220,0.6)', letterSpacing: '0.1em'}}>
        第 1 问
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 48, textAlign: 'center', fontSize: 28,
        color: 'rgba(190,198,220,0.55)', letterSpacing: '0.1em'}}>人间旁听生 · Claude（AI）</div>
    </AbsoluteFill>
  );
};
