// 《等待》观感样片：开头 0–12.2 秒（videos/001_等待/观感对照.md）。时间表和整条完全一样（full.json），声音用 full_audio.py 另出的 look.wav（多了 32 间房的声音）。
import {AbsoluteFill, Html5Audio, Sequence, staticFile} from 'remotion';
import full from '../full.json';
import {ExpLook} from './ExpLook';
import {HookLook} from './HookLook';

const OP = full.opening;
export const LOOK_FRAMES = OP.p2End;

// 整体提亮中间调（第三轮评审：房间平均亮度只有 25/255，缩到手机上光锥和光晕都看不见）。用 gamma 曲线，不用线性增益：暗部和剪影基本不动
export const LookSample: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <svg width={0} height={0} style={{position: 'absolute'}}>
      <filter id="lookTone" colorInterpolationFilters="sRGB">
        <feComponentTransfer>
          <feFuncR type="gamma" amplitude={1.04} exponent={0.74} offset={0} />
          <feFuncG type="gamma" amplitude={1.04} exponent={0.74} offset={0} />
          <feFuncB type="gamma" amplitude={1.04} exponent={0.76} offset={0} />
        </feComponentTransfer>
      </filter>
    </svg>
    <AbsoluteFill style={{filter: 'url(#lookTone)'}}>
      <Sequence durationInFrames={OP.p1End}><HookLook /></Sequence>
      <Sequence from={OP.p1End} durationInFrames={OP.p2Start - OP.p1End}><ExpLook /></Sequence>
      <Sequence from={OP.p2Start} durationInFrames={OP.p2End - OP.p2Start}><HookLook offset={OP.p2Offset} /></Sequence>
    </AbsoluteFill>
    <Html5Audio src={staticFile('001/look.wav')} />
  </AbsoluteFill>
);
