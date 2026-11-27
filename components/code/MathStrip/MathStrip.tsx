// Spec: components/specs/MathStrip.md · terms pop in on the words that name them: "a × b × c".
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, BORDER, inter, mono} from '../theme';
import {popIn} from '../anim';

export type Term = {text: React.ReactNode; at: number; op?: string};
export const MathStrip: React.FC<{terms: Term[]; size?: number; style?: React.CSSProperties}> = ({terms, size = 36, style}) => {
  const f = useCurrentFrame();
  return (
    <div style={{display: 'flex', alignItems: 'center', flexWrap: 'nowrap', gap: 12, ...style}}>
      {terms.map((t, i) => f >= t.at - 1 && (
        <React.Fragment key={i}>
          {t.op && <span style={{fontFamily: inter, fontWeight: 800, fontSize: size, color: C.textDim, ...popIn(f, t.at)}}>{t.op}</span>}
          <span style={{...popIn(f, t.at), fontFamily: mono, fontWeight: 700, fontSize: size, color: C.text, background: C.surface, border: BORDER, borderRadius: 10, padding: '6px 14px', whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'}}>{t.text}</span>
        </React.Fragment>
      ))}
    </div>
  );
};

/** Indian digit grouping: 3000000 -> 30,00,000 */
export const inr = (n: number) => {
  const s = Math.round(n).toString();
  if (s.length <= 3) return s;
  return s.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + s.slice(-3);
};
