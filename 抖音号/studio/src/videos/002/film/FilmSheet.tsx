// 002 成片自查用：姿势、手、光点、抢的手、分数条、标签一览（不进成片）
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {COL, I, SANS, tagText} from '../lib';
import {Bar, EX, FaceDot, FilmDefs, GrabHand, Man, POSE, PoseKey, Spark, Tag, YOU_BG, YOU_FG, still} from './fpeople';

const ITEMS: [PoseKey, string, number, string][] = [
  ['idle', 'calm', I.ALLC, '站着'],
  ['give', 'calm', I.ALLC, '递'],
  ['reach', 'cold', I.ALLD, '伸手抢'],
  ['pull', 'cold', I.ALLD, '收回'],
  ['hunch', 'worry', I.ALLC, '缩肩'],
  ['cross', 'cold', I.GRIM, '抱胳膊'],
  ['lookUp', 'blank', I.ALLC, '转头看'],
  ['startle', 'stun', I.GRIM, '愣住'],
  ['cross', 'angry', I.GRIM, '翻脸'],
  ['front', 'calm', I.GTFT, '面对镜头'],
  ['quarter', 'calm', I.GTFT, '转身半路'],
  ['idle', 'smirk', I.GRIM, '一边嘴角翘'],
];

export const FilmSheet002: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#20232B'}}>
      <svg width={2400} height={2100}>
        <FilmDefs />
        {ITEMS.map(([p, e, s, label], i) => {
          const x = 200 + (i % 6) * 380, G = 680 + Math.floor(i / 6) * 700;
          return (
            <g key={i}>
              <Man f={f} pose={still(p)} expr={EX[e]} strategy={s} who={i === 2 || i === 3 ? 'other' : 'me'} x={x} G={G} s={2.3} seed={`s${i}`} />
              <text x={x} y={G + 50} fontSize={40} fontFamily={SANS} fill="#fff" textAnchor="middle">{label}</text>
            </g>
          );
        })}
        <Man f={f} pose={still('idle')} expr={EX.calm} strategy={I.ALLC} who="me" x={300} G={2060} s={2.3} ghost seed="gh" />
        <text x={300} y={2090} fontSize={36} fontFamily={SANS} fill="#fff" textAnchor="middle">影子你</text>
        <Spark x={600} y={1600} r={32} ground={1700} />
        <Spark x={760} y={1690} r={38} ground={1700} />
        <Spark x={920} y={1600} r={42} warm={1} />
        <GrabHand x={1150} y={1560} r={36} close={0} trail={1} />
        <GrabHand x={1150} y={1700} r={36} close={1} />
        <Spark x={1340} y={1700} r={32} />
        <GrabHand x={1360} y={1700} r={36} close={0.8} dir={180} />
        <Bar x={1500} y={1560} len={300} full={520} color={COL[I.ALLC]} align="left" />
        <Bar x={1500} y={1640} len={480} full={520} color={COL[I.GRIM]} align="left" glow={0.6} />
        <Bar x={1500} y={1720} len={140} full={520} color="#EEF1F6" align="left" />
        <Tag x={1700} y={1850} text={tagText(I.ALLD)} bg={COL[I.ALLD]} />
        <Tag x={2250} y={1850} text={tagText(I.GRIM)} bg={COL[I.GRIM]} stack />
        <Tag x={2000} y={1700} text={tagText(I.GTFT)} bg={COL[I.GTFT]} />
        <Tag x={1280} y={1850} text="你 · 老实人" bg={YOU_BG} fg={YOU_FG} size={88} />
        <FaceDot x={700} y={1900} r={50} color={COL[I.TFT]} />
        <FaceDot x={830} y={1900} r={50} color={COL[I.GRIM]} lid={0.4} gx={1} />
        <FaceDot x={960} y={1900} r={32} color={COL[I.ALLC]} />
      </svg>
    </AbsoluteFill>
  );
};
