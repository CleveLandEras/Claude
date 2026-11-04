// 002 补的新姿势和表情一览（灰框自查用）
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {EX, Man, POSE, PoseKey} from './people';
import {I, SANS} from './lib';

const ITEMS: [PoseKey, string, number, string][] = [
  ['idle', 'calm', I.ALLC, '站着'],
  ['give', 'calm', I.ALLC, '递'],
  ['reach', 'cold', I.ALLD, '伸手抢'],
  ['pull', 'cold', I.ALLD, '收回'],
  ['hunch', 'worry', I.ALLC, '缩肩'],
  ['cross', 'cold', I.GRIM, '抱胳膊'],
  ['lookUp', 'blank', I.ALLC, '抬头看'],
  ['front', 'calm', I.GTFT, '面对镜头'],
  ['idle', 'smirk', I.GRIM, '一边嘴角翘'],
  ['idle', 'stiff', I.TFT, '僵着'],
  ['idle', 'smile', I.GTFT, '笑'],
  ['idle', 'calm', I.ALLC, '影子你 35%'],
];

export const PoseSheet002: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#20232B'}}>
      <svg width={2400} height={1500}>
        <defs>
          <radialGradient id="sparkGlow"><stop offset="0" stopColor="#FFE9C2" stopOpacity={0.6} /><stop offset="1" stopColor="#FFE9C2" stopOpacity={0} /></radialGradient>
        </defs>
        {ITEMS.map(([p, e, s, label], i) => {
          const x = 200 + (i % 6) * 380, G = 680 + Math.floor(i / 6) * 740;
          return (
            <g key={i}>
              <Man f={f} pose={POSE[p]} expr={EX[e]} strategy={s} who={i === 2 || i === 3 ? 'other' : 'me'} x={x} G={G} s={2.3}
                opacity={label.startsWith('影子') ? 0.35 : 1} seed={`s${i}`} />
              <text x={x} y={G + 50} fontSize={40} fontFamily={SANS} fill="#fff" textAnchor="middle">{label}</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
