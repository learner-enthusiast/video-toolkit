// Spec: components/specs/CounterPair.md · dark punch: one number counts up beside one that stays stark (e.g. 1,500 vs 0).
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, inter, whiteA} from '../theme';
import {pop, enter} from '../anim';

export const CounterPair: React.FC<{left: {label: string; to: number; from?: number; at: number; dur?: number; countAt?: number}; right: {label: string; value: React.ReactNode; at: number; showAt?: number; pending?: React.ReactNode}; w?: number; y?: number}> = ({left, right, w = 972, y = 120}) => {
  const f = useCurrentFrame();
  const colW = (w - 100) / 2;
  const lv = interpolate(f, [left.countAt ?? left.at, (left.countAt ?? left.at) + (left.dur ?? 30)], [left.from ?? 0, left.to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <>
      {[0, 1].map((i) => {
        // right tile can enter early (showAt) with a pending value, then its value pops on `at`
        const a = i === 0 ? left.at : right.showAt ?? right.at;
        const landed = i === 0 || f >= right.at;
        if (f < a - 1) return null;
        return (
          <div key={i} style={{position: 'absolute', left: 40 + i * (colW + 20), top: y, width: colW, ...enter(f, a)}}>
            <div style={{borderRadius: R, border: `2px solid ${i === 1 ? C.accent : whiteA(0.35)}`, padding: '34px 20px', textAlign: 'center', background: C.darkPanel}}>
              <div style={{fontFamily: inter, fontWeight: 800, fontSize: 32, color: whiteA(0.7), letterSpacing: '0.06em', textTransform: 'uppercase'}}>{i === 0 ? left.label : right.label}</div>
              <div style={{fontFamily: inter, fontWeight: 900, fontSize: 150, lineHeight: 1.05, color: i === 1 ? C.accent : C.white, transform: i === 1 && landed ? `scale(${0.8 + 0.2 * pop(f, right.at)})` : undefined, opacity: landed ? 1 : 0.35}}>
                {i === 0 ? Math.round(lv).toLocaleString('en-US') : landed ? right.value : right.pending ?? '?'}
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
};
