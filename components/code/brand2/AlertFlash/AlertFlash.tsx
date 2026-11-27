// Spec: components/specs/AlertFlash.md · Brand 2 signature: full-frame failure punch with a 2-frame flicker in.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, inter, mono, whiteA} from '../../theme';
import {pop, ease, enter} from '../../anim';

export const AlertFlash: React.FC<{word: string; sub?: string; at: number; out?: number; icon?: React.ReactNode; size?: number}> = ({word, sub, at, out = 1e9, icon, size = 132}) => {
  const f = useCurrentFrame();
  if (f < at || f > out + 1) return null;
  // flicker: on, off, on
  const flicker = f - at === 1 ? 0.15 : 1;
  const o = ease(f, out - 8, out, 1, 0);
  return (
    <div style={{position: 'absolute', inset: 0, background: C.punchBg, opacity: o}}>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 28, padding: '0 54px', opacity: flicker, transform: `scale(${1.12 - 0.12 * Math.min(1, pop(f, at))})`}}>
        {icon ?? (
          <svg width={180} height={180} viewBox="0 0 48 48" fill="none" stroke={C.alert} strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round">
            <path d="M24 5 L45 42 H3 Z" /><path d="M24 18v11M24 35.5v.5" />
          </svg>
        )}
        <div style={{fontFamily: inter, fontWeight: 900, fontSize: size, lineHeight: 1, textTransform: 'uppercase', color: C.alert, textAlign: 'center'}}>{word}</div>
        {sub && <div style={{fontFamily: mono, fontWeight: 500, fontSize: 32, color: whiteA(0.75), textAlign: 'center', ...enter(f, at + 6, 1e9, 10)}}>{sub}</div>}
      </div>
    </div>
  );
};
