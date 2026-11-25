// Spec: components/specs/BarCompare.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/* ---------------- BarCompare (shared scale) ---------------- */
export const BarCompare: React.FC<{w: number; rows: {label: string; value: number; tone: 'ink' | 'orange'; at: number}[]; max: number}> = ({w, rows, max}) => {
  const f = useCurrentFrame();
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 16, width: w}}>
      {rows.map((r, i) => f >= r.at - 1 && (
        <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16, ...enter(f, r.at, 1e9, 10)}}>
          <div style={{width: 200, fontFamily: inter, fontWeight: 800, fontSize: 28, color: r.tone === 'orange' ? C.orange : C.ink, whiteSpace: 'nowrap'}}>{r.label}</div>
          <div style={{flex: 1, height: 52, borderRadius: 10, background: C.fill, border: `2px solid ${C.grid}`, position: 'relative', overflow: 'hidden'}}>
            <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${(easeOut(f, r.at, r.at + 18) * r.value * 100) / max}%`, background: r.tone === 'orange' ? C.orange : C.ink, borderRight: BORDER}} />
            <span style={{position: 'absolute', right: 14, top: 8, fontFamily: mono, fontWeight: 700, fontSize: 28, color: r.tone === 'ink' && r.value / max > 0.85 ? C.white : C.ink}}>{Math.round(easeOut(f, r.at, r.at + 18) * r.value).toLocaleString('en-IN')}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

