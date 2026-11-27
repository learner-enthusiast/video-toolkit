// Spec: components/specs/SourceChip.md · "where this number comes from": optional official logo + a mono label, ring pulses on landing.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, accentA, mono} from '../theme';
import {popIn} from '../anim';
import {Logo} from '../glyphs';

export const SourceChip: React.FC<{at: number; logo?: {file: string; w: number; h: number}; children: React.ReactNode; size?: number}> = ({at, logo, children, size = 28}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const ring = f - at < 18 ? 1 - (f - at) / 18 : 0;
  return (
    <div style={{...popIn(f, at), display: 'inline-flex', alignItems: 'center', gap: 12, padding: `${size * 0.32}px ${size * 0.7}px`, borderRadius: 999, background: C.surface, border: `3px solid ${C.accent}`, boxShadow: ring > 0 ? `0 0 0 ${14 * (1 - ring)}px ${accentA(0.35 * ring)}` : 'none', whiteSpace: 'nowrap'}}>
      {logo && <Logo file={logo.file} w={logo.w} h={logo.h} />}
      <span style={{fontFamily: mono, fontWeight: 700, fontSize: size, color: C.text}}>{children}</span>
    </div>
  );
};
