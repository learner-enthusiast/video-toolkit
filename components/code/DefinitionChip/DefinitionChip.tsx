// Spec: components/specs/DefinitionChip.md · first built for system-design-of-ai/06-cancellation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, BORDER, inter, mono} from '../theme';
import {popIn} from '../anim';

export const DefinitionChip: React.FC<{term: string; def: string; at: number; out?: number; size?: number}> = ({term, def, at, out = 1e9, size = 30}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const n = Math.max(0, Math.floor((f - at - 3) * 3));
  return (
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, padding: `${size * 0.3}px ${size * 0.5}px ${size * 0.3}px ${size * 0.3}px`, borderRadius: 999, border: BORDER, background: C.surface, ...popIn(f, at, out)}}>
      <span style={{fontFamily: mono, fontWeight: 700, fontSize: size, color: C.white, background: C.accent, borderRadius: 999, padding: `2px ${size * 0.5}px`}}>{term}</span>
      <span style={{fontFamily: inter, fontWeight: 700, fontSize: size, color: C.textDim}}>=</span>
      <span style={{fontFamily: inter, fontWeight: 600, fontSize: size, color: C.text, whiteSpace: 'nowrap'}}>{def.slice(0, n)}<span style={{opacity: 0}}>{def.slice(n)}</span></span>
    </div>
  );
};
