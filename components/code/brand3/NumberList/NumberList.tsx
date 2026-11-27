// Spec: components/specs/NumberList.md · Brand 3 signature: numbered term cards that light up in spoken order.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, accentA} from '../../theme';
import {enter, ease, bump} from '../../anim';

export const NumberList: React.FC<{items: string[]; litAt: number[]; cols?: number; w?: number; at?: number; out?: number}> = ({items, litAt, cols = 2, w = 900, at = 0, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const rows = Math.ceil(items.length / cols);
  const gradient: React.CSSProperties = {backgroundImage: `linear-gradient(135deg, ${C.accent}, ${C.gradientEnd})`, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'};
  return (
    <div style={{width: w, display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gridTemplateRows: `repeat(${rows}, auto)`, gridAutoFlow: 'column', gap: 18, opacity: ease(f, out - 8, out, 1, 0)}}>
      {items.map((term, i) => {
        const on = litAt[i] === undefined ? 0 : ease(f, litAt[i], litAt[i] + 8);
        return (
          <div key={term} style={enter(f, at + i * 4)}>
            <div style={{display: 'flex', alignItems: 'center', gap: 18, padding: '18px 22px', borderRadius: R, border: on > 0.5 ? `2px solid ${C.accent2}` : BORDER, background: C.surface, boxShadow: on > 0 ? `0 0 ${24 * on}px ${accentA(0.35 * on)}` : SHADOW, transform: `scale(${litAt[i] === undefined ? 1 : bump(f, litAt[i])})`}}>
              <span style={{fontFamily: mono, fontWeight: 700, fontSize: 44, lineHeight: 1, ...(on > 0.5 ? gradient : {color: C.textDim})}}>{String(i + 1).padStart(2, '0')}</span>
              <span style={{fontFamily: inter, fontWeight: 700, fontSize: 32, lineHeight: 1.15, color: on > 0.5 ? C.text : C.textDim}}>{term}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
