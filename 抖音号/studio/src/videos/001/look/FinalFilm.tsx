// 《等待》终版（10/28）：开头用观感样片第五版（HookLook、ExpLook），中段和结尾用同一套画风（RestLook）。
// 时间表 full.json，声音 full_audio.py 出的 final.wav（第五版那套音效加垫底的灯泡电流声，不加曲库配乐也能直接发）。
// 左上角一直有“AI 生成”标识。整片过同一条提亮中间调的曲线。
import {AbsoluteFill, Html5Audio, Sequence, staticFile} from 'remotion';
import full from '../full.json';
import {ExpLook} from './ExpLook';
import {HookLook} from './HookLook';
import {RestBeat} from './RestLook';
import {L} from './Room';

const OP = full.opening;

const AiBadge: React.FC = () => (
  <div lang="zh-Hans" style={{position: 'absolute', left: 28, top: 20, padding: '4px 14px', borderRadius: 8, fontFamily: L.serif,
    fontSize: 26, color: 'rgba(243,235,221,0.8)', border: '1.5px solid rgba(243,235,221,0.4)', background: 'rgba(0,0,0,0.35)',
    letterSpacing: '0.06em'}}>AI 生成</div>
);

export const FinalFilm: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <svg width={0} height={0} style={{position: 'absolute'}}>
      <filter id="finalTone" colorInterpolationFilters="sRGB">
        <feComponentTransfer>
          <feFuncR type="gamma" amplitude={1.04} exponent={0.74} offset={0} />
          <feFuncG type="gamma" amplitude={1.04} exponent={0.74} offset={0} />
          <feFuncB type="gamma" amplitude={1.04} exponent={0.76} offset={0} />
        </feComponentTransfer>
      </filter>
    </svg>
    <AbsoluteFill style={{filter: 'url(#finalTone)'}}>
      <Sequence durationInFrames={OP.p1End}><HookLook /></Sequence>
      <Sequence from={OP.p1End} durationInFrames={OP.p2Start - OP.p1End}><ExpLook /></Sequence>
      <Sequence from={OP.p2Start} durationInFrames={OP.p2End - OP.p2Start}><HookLook offset={OP.p2Offset} /></Sequence>
      {full.beats.filter((b) => b.id !== 'exp').map((b) => (
        <Sequence key={b.id} from={b.from} durationInFrames={b.dur}><RestBeat id={b.id} text={b.text} /></Sequence>
      ))}
    </AbsoluteFill>
    <AiBadge />
    <Html5Audio src={staticFile('001/final.wav')} />
  </AbsoluteFill>
);
