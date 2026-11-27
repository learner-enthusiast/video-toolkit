// Spec: components/specs/KycCounter.md · first built for system-design-of-ai/09-prompt-caching. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, accentA, onAccentA} from '../theme';
import {ease, popIn} from '../anim';
import {UserGlyph} from '../glyphs';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const DocTile: React.FC<{label: string; tone?: 'plain' | 'orange' | 'cheque'}> = ({label, tone = 'plain'}) => (
  <div style={{width: tone === 'cheque' ? 200 : 150, height: tone === 'cheque' ? 90 : 120, borderRadius: 8, border: tone === 'cheque' ? `3px solid ${C.accent}` : BORDER, background: tone === 'orange' ? C.accent : C.surface, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: tone === 'cheque' ? 'center' : 'flex-end', paddingBottom: tone === 'cheque' ? 0 : 6, boxSizing: 'border-box', gap: 4, boxShadow: SHADOW}}>
    {tone !== 'cheque' && [0, 1].map((i) => <div key={i} style={{width: 64 - i * 16, height: 7, borderRadius: 4, background: tone === 'orange' ? onAccentA(0.7) : C.track}} />)}
    <span style={{fontFamily: inter, fontWeight: 800, fontSize: 28, color: tone === 'orange' ? C.onAccent : tone === 'cheque' ? C.accent : C.text}}>{label}</span>
  </div>
);
/** every: each visit slides the full pile + one cheque. shared: A's pile goes into one shared folder; B hands over only a cheque. */
export const KycCounter: React.FC<{mode: 'every' | 'shared'; visits: number[]; w?: number; docs?: string[]; payLabel?: string; desk?: string; deskSub?: string; sharedLabel?: string; sharedDone?: string; users?: [string, string]; visitLabel?: (n: number) => string; everyNote?: string; sharedNote?: string}> = ({mode, visits, docs = ['ID', 'Address', 'Photo', 'Form'], payLabel = '₹ cheque', desk = 'BANK', deskSub = 'counter', sharedLabel = 'shared file', sharedDone = 'KYC ✓', users = ['User A', 'User B'], visitLabel = (n: number) => `visit ${n}`, everyNote = 'full KYC again, for one cheque', sharedNote = '→ uses the shared file'}) => {
  const f = useCurrentFrame();
  const vi = visits.reduce((k, v, i) => (f >= v ? i : k), -1);
  const v0 = visits[Math.max(0, vi)];
  const slide = vi < 0 ? 0 : ease(f, v0, v0 + 16);
  const pile = mode === 'every' || vi <= 0;
  const into = mode === 'shared' && vi >= 0 ? ease(f, visits[0] + 18, visits[0] + 34) : 0;
  return (
    <div style={{position: 'relative', width: 900, height: 760}}>
      {/* bank counter */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 470, height: 26, background: C.text, borderRadius: 8}} />
      <div style={{position: 'absolute', left: 620, top: 40, width: 260, height: 430, border: BORDER, borderRadius: R, background: C.surface, boxShadow: SHADOW, display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 20, gap: 8}}>
        <span style={{fontFamily: inter, fontWeight: 900, fontSize: 30, color: C.text}}>{desk}</span>
        <span style={{fontFamily: inter, fontWeight: 700, fontSize: 22, color: C.textDim}}>{deskSub}</span>
        {mode === 'shared' && (
          <div style={{marginTop: 30, width: 200, height: 150, borderRadius: 10, border: `3px solid ${C.accent}`, background: accentA(0.1), display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 4}}>
            <span style={{fontFamily: inter, fontWeight: 900, fontSize: 26, color: C.accent}}>{sharedLabel}</span>
            <span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.text}}>{into > 0.9 ? sharedDone : ''}</span>
          </div>
        )}
      </div>
      {/* customer */}
      <div style={{position: 'absolute', left: 20, top: 230, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
        <UserGlyph size={150} />
        <span style={{fontFamily: inter, fontWeight: 900, fontSize: 30, color: C.text}}>{vi < 0 ? '' : mode === 'shared' ? (vi === 0 ? users[0] : users[1]) : visitLabel(vi + 1)}</span>
      </div>
      {/* pile + cheque slide onto the counter */}
      {vi >= 0 && (
        <div style={{position: 'absolute', left: lerp(180, 250, slide), bottom: 760 - 470, display: 'flex', alignItems: 'flex-end', opacity: Math.min(1, slide * 2)}}>
          {pile && docs.map((k, i) => (
            <div key={k} style={{marginLeft: i ? -90 : 0, marginBottom: i * 46, transform: `translate(${into * (415 - i * 60)}px, ${into * -150}px) scale(${1 - into * 0.6})`, opacity: 1 - into * 0.9}}><DocTile label={k} /></div>
          ))}
        </div>
      )}
      {vi >= 0 && (
        <div style={{position: 'absolute', left: lerp(160, 300, slide), top: 560, ...popIn(f, v0 + 6)}}><DocTile label={payLabel} tone="cheque" /></div>
      )}
      {mode === 'every' && vi >= 0 && <div style={{position: 'absolute', left: 300, top: 660, fontFamily: inter, fontWeight: 800, fontSize: 30, color: C.textDim, ...popIn(f, v0 + 10)}}>{everyNote}</div>}
      {mode === 'shared' && vi >= 1 && <div style={{position: 'absolute', left: 480, top: 580, fontFamily: inter, fontWeight: 900, fontSize: 30, color: C.accent, ...popIn(f, visits[1] + 10)}}>{sharedNote}</div>}
    </div>
  );
};
