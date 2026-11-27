// Spec: components/specs/PullRequestCard.md · a pull request as a card: title, files, +N −M chip, optional diff and warning.
// Also exports MiniPR (the small PR pill used inside RoutingLadder).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, accentA, inter, mono} from '../theme';
import {ease, popIn} from '../anim';
import {PRGlyph, WarnMark} from '../glyphs';

export type DiffLine = {op: '-' | '+' | ' '; text: string};

export const SizeChip: React.FC<{add: number; del: number; size?: number; dim?: boolean}> = ({add, del, size = 28, dim}) => (
  <div style={{display: 'inline-flex', gap: 12, padding: `${size * 0.18}px ${size * 0.45}px`, borderRadius: 999, border: `2px solid ${dim ? C.textDim : C.border}`, background: C.surface, fontFamily: mono, fontWeight: 700, fontSize: size, whiteSpace: 'nowrap'}}>
    <span style={{color: dim ? C.textDim : C.accent}}>+{add}</span><span style={{color: C.textDim}}>−{del}</span>
  </div>
);

/** `dimT` greys the card out at that frame ("not this one"); tone 'risky' = orange outline, 'dim' = greyed from the start */
export const PullRequestCard: React.FC<{title: string; files: string; add: number; del: number; diff?: DiffLine[]; diffAt?: number; tone?: 'plain' | 'risky' | 'dim'; dimT?: number; tag?: React.ReactNode; warn?: {at: number; text: string}; w?: number; size?: number}> = ({title, files, add, del, diff, diffAt = -100, tone = 'plain', dimT, tag, warn, w = 880, size = 36}) => {
  const f = useCurrentFrame();
  const dv = dimT !== undefined ? ease(f, dimT, dimT + 8) : tone === 'dim' ? 1 : 0;
  const risky = tone === 'risky';
  const ink = dv > 0.5 ? C.textDim : C.text;
  return (
    <div style={{width: w, boxSizing: 'border-box', background: dv > 0.5 ? C.mute : C.surface, border: risky ? `5px solid ${C.accent2}` : `2px solid ${dv > 0.5 ? C.textDim : C.border}`, borderRadius: R, boxShadow: dv > 0.5 ? 'none' : SHADOW, padding: `${size * 0.5}px ${size * 0.66}px`}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <PRGlyph size={size * 1.1} color={risky ? C.accent : ink} />
        <span style={{flex: 1, fontFamily: inter, fontWeight: 800, fontSize: size, color: ink, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{title}</span>
        {tag}
      </div>
      <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: size * 0.35}}>
        <span style={{flex: 1, fontFamily: mono, fontWeight: 500, fontSize: size * 0.78, color: C.textDim, whiteSpace: 'nowrap'}}>{files}</span>
        <SizeChip add={add} del={del} size={size * 0.75} dim={dv > 0.5} />
      </div>
      {diff && (
        <div style={{marginTop: size * 0.45, borderRadius: 10, overflow: 'hidden', border: `2px solid ${C.grid}`}}>
          {diff.map((d, i) => {
            const v = ease(f, diffAt + i * 6, diffAt + i * 6 + 8);
            return (
              <div key={i} style={{display: 'flex', alignItems: 'center', opacity: v, transform: `translateX(${(1 - v) * -16}px)`, background: d.op === '+' ? accentA(0.14) : d.op === '-' ? C.fill : C.surface, padding: '6px 0'}}>
                <span style={{width: 46, textAlign: 'center', fontFamily: mono, fontWeight: 700, fontSize: 30, color: d.op === '+' ? C.accent : C.textDim}}>{d.op === ' ' ? '' : d.op === '-' ? '−' : '+'}</span>
                <span style={{fontFamily: mono, fontWeight: 500, fontSize: 29, color: d.op === '-' ? C.textDim : C.text, whiteSpace: 'pre'}}>{d.text}</span>
              </div>
            );
          })}
        </div>
      )}
      {warn && f >= warn.at - 1 && (
        <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: size * 0.4, ...popIn(f, warn.at)}}>
          <WarnMark size={46} at={warn.at} />
          <span style={{fontFamily: inter, fontWeight: 800, fontSize: size * 0.8, color: C.text, whiteSpace: 'nowrap'}}>{warn.text}</span>
        </div>
      )}
    </div>
  );
};

export const MiniPR: React.FC<{label: string; tone?: 'ink' | 'orange' | 'dim'; size?: number}> = ({label, tone = 'ink', size = 28}) => {
  const fg = tone === 'orange' ? C.onAccent : tone === 'dim' ? C.textDim : C.text;
  return (
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 10, padding: `${size * 0.3}px ${size * 0.55}px`, borderRadius: 999, background: tone === 'orange' ? C.accent : C.surface, border: `3px solid ${tone === 'dim' ? C.textDim : C.border}`, boxShadow: SHADOW, whiteSpace: 'nowrap'}}>
      <PRGlyph size={size * 1.1} color={fg} />
      <span style={{fontFamily: mono, fontWeight: 700, fontSize: size, color: fg}}>{label}</span>
    </div>
  );
};
