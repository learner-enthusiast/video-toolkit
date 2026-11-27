// Spec: components/specs/TimerRing.md · Brand 3 signature: circular countdown with a big number and "SEC".
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, FPS, inter, mono} from '../../theme';
import {popIn, ease, bump} from '../../anim';

export const TimerRing: React.FC<{from: number; at: number; size?: number; out?: number}> = ({from, at, size = 360, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const done = Math.max(0, Math.min(from, Math.floor((f - at) / FPS)));
  const tickAt = at + done * FPS;
  // the arc eases to each new second (never linear)
  const gone = done === 0 ? 0 : done - 1 + ease(f, tickAt, tickAt + 12);
  const stroke = size * 0.07, r = (size - stroke) / 2, circ = 2 * Math.PI * r;
  return (
    <div style={{position: 'relative', width: size, height: size, ...popIn(f, at, out)}}>
      <svg width={size} height={size} style={{position: 'absolute', inset: 0}}>
        <defs>
          <linearGradient id="timer-ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor={C.accent} /><stop offset="1" stopColor={C.gradientEnd} /></linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} fill={C.surface} stroke={C.track} strokeWidth={stroke} />
        {gone < from && <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="url(#timer-ring)" strokeWidth={stroke} strokeLinecap="butt" strokeDasharray={circ} strokeDashoffset={circ * (gone / from)} transform={`rotate(-90 ${size / 2} ${size / 2})`} />}
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        <span style={{fontFamily: mono, fontWeight: 700, fontSize: size * 0.36, lineHeight: 1, color: C.text, fontVariantNumeric: 'tabular-nums', transform: `scale(${done > 0 ? bump(f, tickAt) : 1})`, display: 'inline-block'}}>{from - done}</span>
        <span style={{fontFamily: inter, fontWeight: 800, fontSize: size * 0.08, letterSpacing: '0.2em', color: C.textDim}}>SEC</span>
      </div>
    </div>
  );
};
