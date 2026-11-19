// Spec: components/specs/TerminalCard.md · first built for system-design-of-ai/06-cancellation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, inter, mono} from '../theme';
import {popIn, enter} from '../anim';
import {WarnMark} from '../glyphs';

export type TermLine = {text: string; at: number; tone: 'dim' | 'orange'; mark?: 'warn'; label?: string};
export const TerminalCard: React.FC<{w?: number; cmd: {text: string; at: number; cps?: number}; keys?: {text: string; at: number; note?: string}; log: TermLine[]; labels?: [string, string]; at: number; out?: number; pulse?: {line: number; at: number}; note?: {line: number; at: number; text: string}}> = ({w = 892, cmd, keys, log, labels = ['client', 'server log'], at, out = 1e9, pulse, note}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const n = Math.max(0, Math.floor((f - cmd.at) * (cmd.cps ?? 1.6)));
  const typing = n < cmd.text.length;
  const caret = Math.floor(f / 8) % 2 === 0;
  const pane = (title: string) => <div style={{fontFamily: inter, fontWeight: 800, fontSize: 20, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'rgba(255,255,255,.5)', marginBottom: 12}}>{title}</div>;
  return (
    <div style={{width: w, boxSizing: 'border-box', background: C.dark, border: '2px solid rgba(255,255,255,.3)', borderRadius: R, overflow: 'hidden', ...enter(f, at, out)}}>
      <div style={{display: 'flex', gap: 10, padding: '12px 18px', borderBottom: '2px solid rgba(255,255,255,.12)'}}>
        {[0, 1, 2].map((i) => <div key={i} style={{width: 12, height: 12, borderRadius: 99, background: i === 0 ? C.orange : 'rgba(255,255,255,.25)'}} />)}
      </div>
      <div style={{padding: '20px 26px 24px', borderBottom: '2px solid rgba(255,255,255,.12)'}}>
        {pane(labels[0])}
        <div style={{display: 'flex', alignItems: 'center', gap: 14, fontFamily: mono, fontWeight: 500, fontSize: 30, color: C.white, whiteSpace: 'pre', fontVariantLigatures: 'none'}}>
          <span style={{color: C.orange, fontWeight: 700}}>$</span>
          <span>{cmd.text.slice(0, n)}<span style={{color: C.orange, opacity: (typing || !keys || f < keys.at) && caret ? 1 : 0}}>▍</span></span>
        </div>
        {keys && f >= keys.at - 1 && (
          <div style={{display: 'flex', alignItems: 'center', gap: 16, marginTop: 16, ...popIn(f, keys.at)}}>
            <span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.white, background: C.orange, borderRadius: 10, padding: '4px 14px', border: '2px solid rgba(255,255,255,.4)'}}>{keys.text}</span>
            {keys.note && <span style={{fontFamily: inter, fontWeight: 700, fontSize: 26, color: 'rgba(255,255,255,.6)'}}>{keys.note}</span>}
          </div>
        )}
      </div>
      <div style={{padding: '20px 26px 26px', minHeight: 230}}>
        {pane(labels[1])}
        <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
          {log.map((l, i) => {
            if (f < l.at - 1) return null;
            const pv = pulse && pulse.line === i && f >= pulse.at ? Math.sin(Math.min(1, (f - pulse.at) / 16) * Math.PI) : 0;
            return (
              <div key={i} style={{display: 'flex', flexDirection: 'column', gap: 6, ...enter(f, l.at, 1e9, 12)}}>
                {l.label && <span style={{fontFamily: inter, fontWeight: 800, fontSize: 20, color: l.tone === 'dim' ? 'rgba(255,255,255,.45)' : C.orange, letterSpacing: '0.1em', textTransform: 'uppercase'}}>{l.label}</span>}
                <div style={{display: 'flex', alignItems: 'center', gap: 14, transform: `scale(${1 + 0.04 * pv})`, transformOrigin: 'left center'}}>
                  {l.mark === 'warn' && <WarnMark size={40} />}
                  <span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: l.tone === 'dim' ? '#A39E95' : C.orange, whiteSpace: 'pre', fontVariantLigatures: 'none'}}>{l.text}</span>
                  {note && note.line === i && f >= note.at - 1 && <span style={{fontFamily: inter, fontWeight: 900, fontSize: 28, color: C.orange, whiteSpace: 'nowrap', ...popIn(f, note.at)}}>{note.text}</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
