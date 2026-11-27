// Spec: components/specs/Stamp.md · a verdict stamp that lands with a stiff spring and a 2 px shake.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, inter, surfaceA} from '../theme';
import {pop, ease} from '../anim';

export const Stamp: React.FC<{x: number; y: number; at: number; out?: number; text: React.ReactNode; tone?: 'orange' | 'dim'; rotate?: number; size?: number}> = ({x, y, at, out = 1e9, text, tone = 'orange', rotate = -6, size = 46}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const v = pop(f, at);
  const shake = f - at > 6 && f - at < 10 ? Math.sin((f - at) * 3) * 2 : 0;
  const o = Math.min(Math.min(1, (f - at) / 4), ease(f, out - 8, out, 1, 0));
  const col = tone === 'orange' ? C.accent : C.textDim;
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `translate(-50%,-50%) translateX(${shake}px) rotate(${rotate}deg) scale(${1.6 - 0.6 * v})`}}>
      <div style={{border: `5px solid ${col}`, color: col, background: surfaceA(0.92), borderRadius: R, padding: '12px 26px', fontFamily: inter, fontWeight: 900, fontSize: size, letterSpacing: '0.04em', textTransform: 'uppercase', whiteSpace: 'nowrap'}}>{text}</div>
    </div>
  );
};
