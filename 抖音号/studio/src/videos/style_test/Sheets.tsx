// 姿势表、表情表：把组件里所有姿势、表情各画一遍，方便检查和挑。
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {FlatPerson} from '../../components/people/FlatPerson';
import {InkPerson} from '../../components/people/InkPerson';
import {EXPR, EXPR_NAMES} from '../../components/people/face';
import {ME} from '../../components/people/look';
import {pose} from '../../components/people/rig';
import {CHIP, CardFace, ChipStack, Felt, LooseChip, TableCard} from '../../components/people/FlatCards';
import {InkCardFace, InkChipStack, InkFelt, InkTableCard} from '../../components/people/InkCards';

const POSES: [string, string, number?][] = [
  ['sit', '坐'], ['slump', '瘫坐仰头'], ['phone', '低头看手机'], ['sigh', '叹气'],
  ['headInHands', '抱头'], ['stand', '站着等'], ['standLook', '站着低头'], ['peek', '看底牌'],
  ['peekSigh', '看完叹气'], ['board', '抬眼看桌面'], ['allIn', '全推'], ['think', '托腮盯着'],
  ['walk', '走 0', 0], ['walk', '走 0.25', 0.25], ['walk', '走 0.5', 0.5], ['walk', '走 0.75', 0.75],
];
const SEATED = ['sit', 'phone', 'sigh', 'headInHands', 'slump', 'peek', 'peekSigh', 'board', 'allIn', 'think'];
const TABLED = ['peek', 'peekSigh', 'board', 'allIn', 'think'];

export const PoseSheet: React.FC<{kind: 'flat' | 'ink'; debug?: boolean}> = ({kind, debug}) => {
  const f = useCurrentFrame();
  const flat = kind === 'flat';
  return (
    <AbsoluteFill style={{background: flat ? '#2A2230' : '#F3EEE3'}}>
      <svg width={1600} height={1960} viewBox="0 0 1600 1960">
        {POSES.map(([name, label, ph], i) => {
          const cx = 200 + (i % 4) * 400, gy = 420 + Math.floor(i / 4) * 480;
          const r = pose(name, ph ?? 0);
          const e = name === 'slump' ? EXPR.blank : ['phone', 'peek'].includes(name) ? EXPR.worry : name === 'headInHands' ? EXPR.sad
            : name === 'peekSigh' ? EXPR.sighing : name === 'think' ? EXPR.suspect : name === 'board' ? EXPR.surprise : EXPR.calm;
          return (
            <g key={i}>
              <line x1={cx - 170} y1={gy} x2={cx + 170} y2={gy} stroke={flat ? '#5A4C5E' : '#BDB4A4'} strokeWidth={2} />
              {SEATED.includes(name) && <rect x={cx - 60} y={gy - 40 * 1.3} width={100} height={8} fill={flat ? '#6B5A50' : '#9A8F80'} />}
              {TABLED.includes(name) && <rect x={cx + 30} y={gy - 88 * 1.3} width={150} height={10} fill={flat ? '#2F6B4C' : '#7FAE88'} />}
              {flat
                ? <FlatPerson pose={r} expr={e} look={ME} x={cx - 20} y={gy} s={1.3} debug={debug} phone={['phone', 'sigh'].includes(name) ? {lit: 1} : undefined} />
                : <InkPerson pose={r} expr={e} look={ME} x={cx - 20} y={gy} s={1.3} frame={f} phone={['phone', 'sigh'].includes(name) ? {lit: 1} : undefined} />}
              <text x={cx} y={gy + 50} textAnchor="middle" fontSize={26} fill={flat ? '#E8DCCB' : '#3A332C'} fontFamily="PingFang SC">{label}（{name}）</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

export const ExprSheet: React.FC<{kind: 'flat' | 'ink'}> = ({kind}) => {
  const f = useCurrentFrame();
  const flat = kind === 'flat';
  const LABEL: Record<string, string> = {calm: '平静', worry: '担心', teary: '委屈含泪', relief: '松一口气', blank: '发呆', surprise: '惊喜', sighing: '叹气', suspect: '怀疑', sad: '难过'};
  return (
    <AbsoluteFill style={{background: flat ? '#2A2230' : '#F3EEE3'}}>
      <svg width={1600} height={1330} viewBox="0 0 1600 1330">
        {EXPR_NAMES.map((n, i) => {
          const cx = 200 + (i % 4) * 400, cy = 330 + Math.floor(i / 4) * 420;
          const r = {...pose('sit'), yaw: 0.35, pitch: 0, neck: 0, lean: 0, chest: 0, pelvis: 0, gx: 0, gy: 0};
          return (
            <g key={n}>
              {flat
                ? <FlatPerson pose={r} expr={EXPR[n]} look={ME} x={cx} y={cy + 380} s={2.4} />
                : <InkPerson pose={r} expr={EXPR[n]} look={ME} x={cx} y={cy + 380} s={2.4} frame={f} />}
              <rect x={cx - 200} y={cy + 120} width={400} height={300} fill={flat ? '#2A2230' : '#F3EEE3'} />
              <text x={cx} y={cy + 170} textAnchor="middle" fontSize={30} fill={flat ? '#E8DCCB' : '#3A332C'} fontFamily="PingFang SC">{LABEL[n]}（{n}）</text>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// 牌表：四种花色 × 13 张，查点数、花色、颜色画得对不对；再加几张桌上的牌（扣着、掀角、翻到一半）和筹码
const RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] as const;
export const CardSheet: React.FC<{kind: 'flat' | 'ink'}> = ({kind}) => {
  const f = useCurrentFrame();
  const flat = kind === 'flat';
  return (
    <AbsoluteFill style={{background: flat ? '#1E3A2B' : '#F3EEE3'}}>
      <svg width={1800} height={1300} viewBox="0 0 1800 1300">
        {(['S', 'H', 'D', 'C'] as const).map((su, j) => RANKS.map((rk, i) => (
          <g key={`${su}${rk}`} transform={`translate(${80 + i * 130} ${110 + j * 190}) scale(1.15)`}>
            {flat ? <CardFace c={{r: rk, s: su}} /> : <InkCardFace c={{r: rk, s: su}} frame={f} seed={`${su}${rk}`} px={1.15} />}
          </g>
        )))}
        {flat ? (
          <g>
            <Felt pts={[{x: 0, y: 860}, {x: 1800, y: 860}, {x: 1800, y: 1300}, {x: 0, y: 1300}]} lx={900} ly={1080} lr={900} />
            <TableCard x={160} y={1080} s={1.4} rot={-8} />
            <TableCard x={380} y={1080} s={1.4} rot={6} face={{r: 'A', s: 'S'}} down peek={1} />
            <TableCard x={600} y={1080} s={1.4} rot={-3} face={{r: 'K', s: 'H'}} flip={0.35} />
            <TableCard x={820} y={1080} s={1.4} rot={4} face={{r: '9', s: 'D'}} />
            <ChipStack x={1060} y={1120} R={46} n={8} c={CHIP.navy} seed="a" />
            <ChipStack x={1180} y={1150} R={46} n={5} c={CHIP.cream} seed="b" />
            <ChipStack x={1300} y={1110} R={46} n={11} c={CHIP.black} seed="c" />
            <ChipStack x={1430} y={1160} R={46} n={3} c={CHIP.amber} seed="d" />
            <ChipStack x={1560} y={1120} R={46} n={6} c={CHIP.plum} seed="e" />
            <LooseChip x={1680} y={1200} R={46} c={CHIP.navy} />
          </g>
        ) : (
          <g>
            <InkFelt pts={[{x: 0, y: 860}, {x: 1800, y: 860}, {x: 1800, y: 1300}, {x: 0, y: 1300}]} frame={f} />
            <InkTableCard x={160} y={1080} s={1.4} rot={-8} frame={f} seed="t1" />
            <InkTableCard x={380} y={1080} s={1.4} rot={6} face={{r: 'A', s: 'S'}} down peek={1} frame={f} seed="t2" />
            <InkTableCard x={600} y={1080} s={1.4} rot={-3} face={{r: 'K', s: 'H'}} flip={0.35} frame={f} seed="t3" />
            <InkTableCard x={820} y={1080} s={1.4} rot={4} face={{r: '9', s: 'D'}} frame={f} seed="t4" />
            <InkChipStack x={1060} y={1120} R={46} n={8} tone={0} frame={f} seed="a" />
            <InkChipStack x={1180} y={1150} R={46} n={5} tone={1} frame={f} seed="b" />
            <InkChipStack x={1300} y={1110} R={46} n={11} tone={2} frame={f} seed="c" />
            <InkChipStack x={1430} y={1160} R={46} n={3} tone={0} frame={f} seed="d" />
          </g>
        )}
      </svg>
    </AbsoluteFill>
  );
};
