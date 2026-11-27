// Spec: components/specs/HighlighterText.md · Brand 2 signature: a marker sweeps under chosen words, in order.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, inter} from '../../theme';
import {enter, ease} from '../../anim';

export type Mark = {word: string; at: number};
const clean = (s: string) => s.toLowerCase().replace(/[^\p{L}\p{M}\p{N}]/gu, '');

export const HighlighterText: React.FC<{lines: string[]; marks: Mark[]; size?: number; at?: number}> = ({lines, marks, size = 64, at = 0}) => {
  const f = useCurrentFrame();
  const used = new Set<number>();
  /** each mark takes the first unmarked occurrence of its word, in reading order */
  const rows = lines.map((l) => l.split(' ').map((w) => {
    const i = marks.findIndex((m, k) => !used.has(k) && clean(m.word) === clean(w));
    if (i >= 0) used.add(i);
    return {w, mark: i >= 0 ? marks[i] : undefined};
  }));
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: size * 0.28}}>
      {rows.map((row, r) => (
        <div key={r} style={{display: 'flex', gap: size * 0.28, whiteSpace: 'nowrap', fontFamily: inter, fontWeight: 800, fontSize: size, lineHeight: 1.2, ...enter(f, at + r * 5)}}>
          {row.map(({w, mark}, k) => {
            const p = mark ? ease(f, mark.at, mark.at + 10) : 0;
            return (
              <span key={k} style={{position: 'relative', color: C.text}}>
                {w}
                {/* the swept copy: marker block plus dark text, revealed left to right */}
                {mark && p > 0 && (
                  <span style={{position: 'absolute', left: -size * 0.1, top: 0, bottom: 0, right: -size * 0.1, clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`, background: C.accent2, borderRadius: 6, color: C.onAccent, paddingLeft: size * 0.1}}>{w}</span>
                )}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};
