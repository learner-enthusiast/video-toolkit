// Spec: components/specs/PrefixMatch.md · first built for system-design-of-ai/09-prompt-caching. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, inter, mono, accentA} from '../theme';
import {popIn, enter} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/** Two prompts as token rows, scanned from the left: ✓ while identical, ⚠ on the first different token, everything after it dims. */
export const PrefixMatch: React.FC<{rows: [string[], string[]]; labels?: [string, string]; at: number; step?: number; size?: number; pulseAt?: number; w?: number; reusedLabel?: (n: number) => string; restLabel?: string}> = ({rows, labels = ['request 1', 'request 2'], at, step = 4, size = 26, pulseAt, reusedLabel = (n: number) => (n === 0 ? 'nothing reused' : `reused: ${n} token${n === 1 ? '' : 's'}`), restLabel = 'the rest: full price'}) => {
  const f = useCurrentFrame();
  const n = Math.max(rows[0].length, rows[1].length);
  let m = -1;
  for (let i = 0; i < n; i++) if (rows[0][i] !== rows[1][i]) { m = i; break; }
  const reached = Math.floor((f - at) / step);
  const pulse = pulseAt === undefined ? 0 : Math.max(0, Math.sin(Math.PI * Math.min(1, Math.max(0, (f - pulseAt) / 16))));
  const cell = (tok: string, i: number, r: number) => {
    const done = reached >= i;
    const after = m >= 0 && i > m && reached >= m;
    const isM = i === m && done;
    const ok = done && (m < 0 || i < m);
    return (
      <div key={i} style={{position: 'relative', fontFamily: mono, fontWeight: 700, fontSize: size, padding: '6px 10px', borderRadius: 8, whiteSpace: 'nowrap', border: isM ? `3px solid ${C.textDim}` : ok ? `3px solid ${C.accent}` : `2px solid ${C.grid}`, background: isM ? C.mute : ok ? accentA(0.1) : C.surface, color: after ? C.textDim : C.text, opacity: after ? 0.45 : 1, transform: i === 0 ? `scale(${1 + 0.15 * pulse})` : undefined}}>
        {tok}
        {r === 1 && ok && <div style={{position: 'absolute', left: '50%', bottom: -34, transform: 'translateX(-50%)', color: C.accent, fontFamily: inter, fontWeight: 900, fontSize: 24}}>✓</div>}
        {r === 1 && isM && <div style={{position: 'absolute', left: '50%', bottom: -42, transform: 'translateX(-50%)'}}><WarnMark size={34} /></div>}
      </div>
    );
  };
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 22}}>
      {rows.map((row, r) => (
        <div key={r} style={{display: 'flex', flexDirection: 'column', gap: 8, ...enter(f, at - 12 + r * 5)}}>
          <span style={{fontFamily: inter, fontWeight: 800, fontSize: 22, color: C.textDim, letterSpacing: '0.08em', textTransform: 'uppercase'}}>{labels[r]}</span>
          <div style={{display: 'flex', gap: 6, flexWrap: 'nowrap'}}>{row.map((t, i) => cell(t, i, r))}</div>
        </div>
      ))}
      {m >= 0 && reached >= m + 1 && (
        <div style={{marginTop: 24, display: 'flex', gap: 16, alignItems: 'center', ...popIn(f, at + (m + 1) * step)}}>
          <Tag label={reusedLabel(m)} tone={m === 0 ? 'dim' : 'orange'} size={28} />
          <Tag label={restLabel} tone="dim" size={28} />
        </div>
      )}
    </div>
  );
};
