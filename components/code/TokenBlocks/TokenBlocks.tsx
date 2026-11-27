// Spec: components/specs/TokenBlocks.md · first built for system-design-of-ai/12-tokenizers. Every text, number and timing is a prop.
// `pieces` must come from a real tokenizer (decode token by token); never hand-split.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, inter, deva, bengali, onAccentA} from '../theme';
import {sp, ease, enter} from '../anim';

export type Piece = {text: string; byte?: boolean};
export type Script = 'latin' | 'deva' | 'bengali';
const FONT: Record<Script, string> = {latin: inter, deva, bengali};

/** One token block. A leading space shows as a small dim dot; a byte piece (decodes to U+FFFD) is a small grey block with no glyph. */
export const Block: React.FC<{p: Piece; size: number; font?: Script; tone?: 'white' | 'orange' | 'dim'}> = ({p, size, font = 'latin', tone = 'white'}) => {
  if (p.byte) return <div style={{width: size * 0.62, height: size * 1.5, borderRadius: R * 0.7, background: C.tint, border: `2px solid ${C.textDim}`, boxSizing: 'border-box'}} />;
  const lead = p.text.startsWith(' ');
  const t = lead ? p.text.slice(1) : p.text;
  const bg = tone === 'orange' ? C.accent : tone === 'dim' ? C.mute : C.surface;
  const fg = tone === 'orange' ? C.onAccent : tone === 'dim' ? C.textDim : C.text;
  return (
    <div style={{position: 'relative', height: size * 1.5, boxSizing: 'border-box', padding: `0 ${size * 0.34}px 0 ${size * (lead ? 0.5 : 0.34)}px`, borderRadius: R * 0.7, background: bg, border: `2px solid ${C.line}`, display: 'flex', alignItems: 'center', fontFamily: FONT[font], fontWeight: font === 'latin' ? 600 : 500, fontSize: size, lineHeight: 1, color: fg, whiteSpace: 'pre'}}>
      {lead && <span style={{position: 'absolute', left: size * 0.17, top: '50%', width: size * 0.13, height: size * 0.13, marginTop: -size * 0.065, borderRadius: 99, background: tone === 'orange' ? onAccentA(0.7) : C.track}} />}
      {t}
    </div>
  );
};

/** A string as the row of tokens a real tokenizer produced; blocks drop like coins with a running counter. */
export const TokenBlocks: React.FC<{pieces: Piece[]; at: number; stagger?: number; out?: number; size?: number; font?: Script; w: number;
  label?: React.ReactNode; counter?: 'ink' | 'orange' | false; highlight?: number[]; tone?: 'white' | 'orange'; charCount?: {value: number; at: number}; countLabel?: string; charLabel?: string; gap?: number}> =
  ({pieces, at, stagger = 3, out = 1e9, size = 34, font = 'latin', w, label, counter = 'ink', highlight = [], tone = 'white', charCount, countLabel = 'tokens', charLabel = 'characters', gap = 8}) => {
  const f = useCurrentFrame();
  if (f < at - 2) return null;
  const o = ease(f, out - 8, out, 1, 0);
  const landed = pieces.filter((_, i) => f >= at + i * stagger + 6).length;
  const lastLand = at + (pieces.length - 1) * stagger + 6;
  const bumpV = landed === pieces.length ? 1 + 0.08 * Math.sin(Math.PI * Math.min(1, Math.max(0, (f - lastLand) / 10))) : 1;
  return (
    <div style={{width: w, opacity: o}}>
      {(label || counter) && (
        <div style={{display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12, ...enter(f, at - 2, 1e9, 10)}}>
          <div style={{fontFamily: inter, fontWeight: 800, fontSize: 32, color: C.text, display: 'flex', alignItems: 'center', gap: 12}}>{label}</div>
          {counter && (
            <div style={{fontFamily: inter, fontWeight: 900, fontSize: 52, color: counter === 'orange' ? C.accent : C.text, fontVariantNumeric: 'tabular-nums', transform: `scale(${bumpV})`, transformOrigin: 'right center'}}>
              {landed}<span style={{fontSize: 30, fontWeight: 800, color: C.textDim, marginLeft: 10}}>{countLabel}</span>
            </div>
          )}
        </div>
      )}
      <div style={{display: 'flex', flexWrap: 'wrap', gap, alignItems: 'center'}}>
        {pieces.map((p, i) => {
          const a = at + i * stagger;
          const v = sp(f, a, {damping: 10, stiffness: 190, mass: 0.6});
          return (
            <div key={i} style={{opacity: f < a ? 0 : Math.min(1, v * 2), transform: `translateY(${(1 - v) * -46}px)`}}>
              <Block p={p} size={size} font={font} tone={highlight.includes(i) ? 'orange' : tone} />
            </div>
          );
        })}
      </div>
      {charCount && f >= charCount.at - 1 && (
        <div style={{marginTop: 12, fontFamily: inter, fontWeight: 700, fontSize: 30, color: C.textDim, ...enter(f, charCount.at, 1e9, 8)}}>{charCount.value} {charLabel}</div>
      )}
    </div>
  );
};
