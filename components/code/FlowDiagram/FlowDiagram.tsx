// Spec: components/specs/FlowDiagram.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/* ---------------- FlowDiagram · two lanes (5-day call vs five 1-day calls) ---------------- */
/** FlowLanes: one big call vs N small calls; a failure redoes everything in lane A but only one cell in lane B */
export const FlowLanes: React.FC<{aAt: number; failAt: number; bAt: number; retryAt: number; at: number; out?: number; n?: number; failIdx?: number; cell?: string;
  labels?: {a: string; b: string; redo: string; retry: string}}> = ({aAt, failAt, bAt, retryAt, at, out = 1e9, n = 5, failIdx = 3, cell: cl = 'Day', labels = {a: 'A · one call, 5 days', b: 'B · five calls, 1 day each', redo: 'cut at Day 3 → redo all 5 days', retry: 'retry, bigger budget'}}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const cell = (label: string, state: 'ok' | 'bad' | 'grey' | 'idle', key: string, style?: React.CSSProperties) => (
    <div key={key} style={{width: 150, height: 96, borderRadius: R, boxSizing: 'border-box', border: state === 'ok' ? `3px solid ${C.accent}` : state === 'bad' ? `3px dashed ${C.textDim}` : BORDER, background: state === 'grey' || state === 'bad' ? C.mute : C.surface, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 4, fontFamily: inter, fontWeight: 800, fontSize: 26, color: state === 'grey' || state === 'bad' ? C.textDim : C.text, ...style}}>
      {label}
      {state === 'ok' && <svg width={30} height={30} viewBox="0 0 48 48" fill="none" stroke={C.accent} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round"><path d="M10 25l9 9 19-20" /></svg>}
      {state === 'bad' && <WarnMark size={30} />}
    </div>
  );
  const aFail = f >= failAt;
  const redo = f >= failAt + 14;
  const bFail = f >= bAt + 30;
  const retried = f >= retryAt;
  return (
    <div style={{position: 'relative', width: 900, height: 760}}>
      {/* lane A */}
      {f >= aAt - 1 && (
        <div style={{position: 'absolute', left: 0, top: 0, width: 900, ...enter(f, aAt)}}>
          <div style={{fontFamily: inter, fontWeight: 900, fontSize: 32, color: C.text, marginBottom: 12}}>{labels.a}</div>
          <div style={{border: BORDER, borderRadius: R, background: C.surface, padding: 16, display: 'flex', gap: 14, boxShadow: SHADOW, opacity: redo ? 0.75 : 1}}>
            {Array.from({length: n}, (_, i) => i + 1).map((d) => cell(`${cl} ${d}`, !aFail ? 'ok' : d >= failIdx ? 'bad' : 'grey', `a${d}`))}
          </div>
          {redo && <div style={{marginTop: 12, display: 'flex', alignItems: 'center', gap: 10, ...popIn(f, failAt + 14)}}><WarnMark size={36} /><span style={{fontFamily: inter, fontWeight: 800, fontSize: 30, color: C.textDim}}>{labels.redo}</span></div>}
        </div>
      )}
      {/* lane B */}
      {f >= bAt - 1 && (
        <div style={{position: 'absolute', left: 0, top: 360, width: 900, ...enter(f, bAt)}}>
          <div style={{fontFamily: inter, fontWeight: 900, fontSize: 32, color: C.text, marginBottom: 12}}>{labels.b}</div>
          <div style={{display: 'flex', gap: 14, padding: 16}}>
            {Array.from({length: n}, (_, i) => i + 1).map((d) => (
              <div key={d} style={enter(f, bAt + d * 5)}>
                {cell(`${cl} ${d}`, d === failIdx ? (retried ? 'ok' : bFail ? 'bad' : 'idle') : f >= bAt + d * 5 + 10 ? 'ok' : 'idle', `b${d}`, d === failIdx && retried ? {transform: `scale(${1 + 0.08 * Math.sin(Math.PI * Math.min(1, (f - retryAt) / 10))})`} : undefined)}
              </div>
            ))}
          </div>
          {retried && <div style={{position: 'absolute', left: 16 + (failIdx - 1) * 164 - 40, top: 196, ...popIn(f, retryAt)}}><Tag label={labels.retry} tone="orange" size={26} /></div>}
        </div>
      )}
    </div>
  );
};

