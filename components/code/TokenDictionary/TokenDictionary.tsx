// Spec: components/specs/TokenDictionary.md · first built for system-design-of-ai/12-tokenizers. Every text, number and timing is a prop.
// Word pieces must come from a real tokenizer. Reusable for any "vocabulary / lookup table" explanation.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, deva, bengali, headline} from '../theme';
import {sp, ease, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';
import {Block, TokenBlocks, Piece, Script} from '../TokenBlocks/TokenBlocks';

/* ======================= TokenDictionary ======================= */
export type DictWord = {text: string; found: boolean; pieces: Piece[]; font?: Script};
/** a fixed vocabulary as an open book of whole (mostly English) entries; words look themselves up: found = one orange block, missing = pieces */
export const TokenDictionary: React.FC<{entries: string[]; words: DictWord[]; at: number; entriesAt: number; lookAt: number[]; footnote: string; footAt: number; out?: number; w?: number; vocabLabel?: string; entriesNote?: string; ids?: number[]; noEntry?: string}> =
  ({entries, words, at, entriesAt, lookAt, footnote, footAt, out = 1e9, w = 972, vocabLabel = 'Vocabulary', entriesNote = 'fixed', ids = [], noEntry = 'no entry'}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const open = sp(f, at, {damping: 16, stiffness: 110});
  const o = ease(f, out - 8, out, 1, 0);
  const pageW = 380, pageH = 380, bx = (w - pageW * 2) / 2, by = 10;
  const half = Math.ceil(entries.length / 2);
  // which entry is being looked up right now (for the ring)
  const active = words.findIndex((_, i) => f >= lookAt[i] && f < lookAt[i] + 16);
  const hitEntry = active >= 0 && words[active].found ? entries.findIndex((e) => e === words[active].text) : -1;
  return (
    <div style={{position: 'relative', width: w, height: 970, opacity: o}}>
      {/* book */}
      {[0, 1].map((side) => (
        <div key={side} style={{position: 'absolute', left: side === 0 ? bx : bx + pageW, top: by, width: pageW, height: pageH, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: side === 0 ? `${R}px 0 0 ${R}px` : `0 ${R}px ${R}px 0`, boxShadow: SHADOW, transform: `scaleX(${0.1 + 0.9 * open})`, transformOrigin: side === 0 ? 'right center' : 'left center', padding: '26px 30px', overflow: 'hidden',
          backgroundImage: `repeating-linear-gradient(${C.surface} 0 63px, ${C.grid} 63px 65px)`, backgroundPosition: '0 36px'}}>
          <div style={{fontFamily: inter, fontWeight: 800, fontSize: 20, letterSpacing: '0.14em', color: C.textDim, textTransform: 'uppercase', marginBottom: 6}}>{side === 0 ? vocabLabel : entriesNote}</div>
          {entries.slice(side * half, side * half + half).map((e, k) => {
            const idx = side * half + k;
            const ea = entriesAt + idx * 3;
            const ring = idx === hitEntry ? ease(f, lookAt[active], lookAt[active] + 6) * ease(f, lookAt[active] + 12, lookAt[active] + 16, 1, 0) : 0;
            return (
              <div key={e} style={{display: 'flex', alignItems: 'baseline', gap: 14, height: 63, opacity: f < ea ? 0 : Math.min(1, (f - ea) / 6)}}>
                <span style={{...headline, fontSize: 44, color: C.text, padding: '0 10px', margin: '0 -10px', borderRadius: 8, boxShadow: ring > 0 ? `0 0 0 ${3 * ring}px ${C.accent}` : 'none'}}>{e}</span>
                <span style={{fontFamily: mono, fontSize: 20, color: C.textDim}}>{ids[idx] !== undefined ? `#${ids[idx]}` : ''}</span>
              </div>
            );
          })}
        </div>
      ))}
      <div style={{position: 'absolute', left: w / 2 - 2, top: by + 6, width: 4, height: pageH - 12, background: C.border, opacity: open}} />
      {/* results: one row per looked-up word */}
      {words.map((wd, i) => {
        const a = lookAt[i];
        if (f < a - 1) return null;
        const y = 430 + i * 92;
        const res = a + 12;
        const pv = sp(f, a);
        return (
          <div key={i} style={{position: 'absolute', left: 30, top: y, width: w - 60, height: 80, display: 'flex', alignItems: 'center', gap: 20}}>
            <div style={{width: 230, display: 'flex', justifyContent: 'flex-end', opacity: Math.min(1, pv * 1.5), transform: `translateY(${(1 - pv) * -30}px)`}}>
              <Tag label={<span style={{fontFamily: wd.font === 'deva' ? deva : wd.font === 'bengali' ? bengali : inter, fontWeight: 700}}>{wd.text}</span>} tone="outline" size={36} />
            </div>
            <div style={{fontFamily: inter, fontWeight: 900, fontSize: 36, color: C.textDim, opacity: f >= res ? 1 : 0}}>→</div>
            {f >= res && !wd.found && f < res + 8 && <div style={{...popIn(f, res), fontFamily: inter, fontWeight: 800, fontSize: 26, color: C.textDim, display: 'flex', alignItems: 'center', gap: 8}}><WarnMark size={30} />{noEntry}</div>}
            {f >= res && (wd.found
              ? <div style={popIn(f, res)}><Block p={{text: wd.pieces[0].text}} size={36} tone="orange" /></div>
              : f >= res + 8 && <TokenBlocks pieces={wd.pieces} at={res + 8} stagger={3} size={36} font={wd.font} w={560} counter={false} gap={6} />)}
            {f >= res + (wd.found ? 4 : 8 + wd.pieces.length * 3 + 4) && (
              <div style={{marginLeft: 'auto', fontFamily: inter, fontWeight: 900, fontSize: 34, color: wd.found ? C.accent : C.text, ...popIn(f, res + (wd.found ? 4 : 8 + wd.pieces.length * 3 + 4))}}>{wd.pieces.length}</div>
            )}
          </div>
        );
      })}
      {f >= footAt - 1 && <div style={{position: 'absolute', left: 0, right: 0, top: 816, padding: '0 60px', textAlign: 'center', fontFamily: inter, fontWeight: 700, fontSize: 28, color: C.textDim, ...enter(f, footAt, 1e9, 10)}}>{footnote}</div>}
    </div>
  );
};

