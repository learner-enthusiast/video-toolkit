// Spec: components/specs/ReceiptCard.md · Brand 2 signature: torn-edge mono receipt; one row can flip to an alert value.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, mono} from '../../theme';
import {enter, popIn, ease} from '../../anim';

const TEETH = 18;
const DEPTH = 14;
/** zigzag top and bottom edges */
const torn = () => {
  const top = Array.from({length: TEETH * 2 + 1}, (_, i) => `${(i / (TEETH * 2)) * 100}% ${i % 2 ? 0 : DEPTH}px`);
  const bottom = Array.from({length: TEETH * 2 + 1}, (_, i) => `${100 - (i / (TEETH * 2)) * 100}% calc(100% - ${i % 2 ? 0 : DEPTH}px)`);
  return `polygon(${[...top, ...bottom].join(', ')})`;
};

export type ReceiptRow = {label: string; value: string};
export const ReceiptCard: React.FC<{title: string; rows: ReceiptRow[]; alertRow?: {row: number; value: string; at: number}; at: number; out?: number; w?: number}> = ({title, rows, alertRow, at, out = 1e9, w = 640}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  return (
    <div style={{width: w, ...enter(f, at, out)}}>
      <div style={{background: C.paper, clipPath: torn(), padding: `${DEPTH + 28}px 36px ${DEPTH + 30}px`, fontFamily: mono, color: C.text}}>
        <div style={{textAlign: 'center', fontWeight: 700, fontSize: 32, letterSpacing: '0.2em', textTransform: 'uppercase', paddingBottom: 18, marginBottom: 18, borderBottom: `3px dashed ${C.track}`}}>{title}</div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
          {rows.map((r, i) => {
            const a = at + 6 + i * 5;
            const flip = alertRow && alertRow.row === i && f >= alertRow.at ? alertRow : undefined;
            return (
              <div key={r.label} style={{display: 'flex', alignItems: 'baseline', gap: 12, fontSize: 30, whiteSpace: 'nowrap', opacity: ease(f, a, a + 8)}}>
                <span style={{fontWeight: 500, color: flip ? C.alert : C.text}}>{r.label}</span>
                <span style={{flex: 1, borderBottom: `3px dotted ${flip ? C.alert : C.track}`}} />
                <span style={{fontWeight: 700, color: flip ? C.alert : C.text, display: 'inline-block', ...(flip ? popIn(f, flip.at) : {})}}>{flip ? flip.value : r.value}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
