// Spec: components/specs/CodeCard.md · white code panel with a window-dot header, typed lines and orange line / range highlights.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, accentA, inter, mono} from '../theme';
import {ease, sp} from '../anim';
import {Logo} from '../glyphs';

export type CodeHl = {line: number; at: number; off?: number; from?: number; to?: number};

const HeaderPill: React.FC<{children: React.ReactNode; dot?: boolean}> = ({children, dot}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 8, padding: '5px 14px', borderRadius: 999, border: BORDER, background: C.surface, fontFamily: inter, fontWeight: 800, fontSize: 20, color: C.text, whiteSpace: 'nowrap'}}>
    {dot && <span style={{width: 10, height: 10, borderRadius: 99, background: C.accent}} />}
    {children}
  </div>
);

/** An inserted line (a fix): hidden until `at`, then it springs open in place, types fast and stays orange. */
export type CodeAdd = {line: number; at: number};

/** `tags` are the header pills (first one gets an orange dot), e.g. ["server", "pseudo-code"]. `//` starts a dim comment.
 *  `logos` shows several official logos in the header (`logo` still works for one). `adds` marks lines that slide in later, `drops` lines that collapse away (a diff). */
export const CodeCard: React.FC<{lines: string[]; at: number; width: number; size?: number; cps?: number; hl?: CodeHl[]; logo?: {file: string; w: number; h: number}; logos?: {file: string; w: number; h: number}[]; tags?: string[]; adds?: CodeAdd[]; drops?: CodeAdd[]}> = ({lines, at, width, size = 28, cps = 4, hl = [], logo, logos = [], tags = [], adds = [], drops = []}) => {
  const f = useCurrentFrame();
  let budget = Math.max(0, (f - at) * cps);
  const lh = Math.round(size * 1.38);
  const allLogos = logo ? [logo, ...logos] : logos;
  return (
    <div style={{width, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, overflow: 'hidden'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '10px 16px', borderBottom: `2px solid ${C.grid}`, background: C.paper}}>
        {[0, 1, 2].map((i) => <div key={i} style={{width: 12, height: 12, borderRadius: 99, background: i === 0 ? C.accent : C.track}} />)}
        <div style={{flex: 1}} />
        {allLogos.map((l) => <Logo key={l.file} file={l.file} w={l.w} h={l.h} style={{marginRight: 6}} />)}
        {tags.map((t, i) => <HeaderPill key={t} dot={i === 0}>{t}</HeaderPill>)}
      </div>
      <div style={{padding: '14px 18px 16px'}}>
        {lines.map((ln, i) => {
          const add = adds.find((a) => a.line === i);
          let shown: string;
          let open = 1;
          if (add) {
            if (f < add.at) return null;
            open = sp(f, add.at, {damping: 18, stiffness: 160});
            shown = ln.slice(0, Math.max(0, Math.floor((f - add.at - 2) * cps * 2.5)));
          } else {
            const n = Math.min(ln.length, Math.floor(budget));
            budget -= ln.length + 4;
            shown = ln.slice(0, n);
          }
          const drop = drops.find((d) => d.line === i);
          if (drop && f >= drop.at) {
            open = 1 - ease(f, drop.at, drop.at + 8);
            if (open <= 0.01) return null;
          }
          const h = [...hl].reverse().find((x) => x.line === i && f >= x.at - 1);
          const hv = h ? ease(f, h.at, h.at + 6) * (h.off ? ease(f, h.off, h.off + 8, 1, 0) : 1) : 0;
          const ci = shown.indexOf('//');
          const body = ci >= 0 ? shown.slice(0, ci) : shown;
          const cmt = ci >= 0 ? shown.slice(ci) : '';
          let content: React.ReactNode;
          if (h && h.from !== undefined) {
            const a = h.from, z = h.to ?? ln.length;
            content = <><span>{shown.slice(0, a)}</span><span style={{background: accentA(hv), color: hv > 0.5 ? C.white : undefined, borderRadius: 6, padding: '0 4px', margin: '0 -4px'}}>{shown.slice(a, z)}</span><span style={{color: z >= (ci >= 0 ? ci : 1e9) ? C.textDim : undefined}}>{shown.slice(z)}</span></>;
          } else {
            content = <><span style={{color: hv > 0.5 ? C.white : add ? C.accent : C.ink}}>{body}</span><span style={{color: hv > 0.5 ? C.white : C.textDim}}>{cmt}</span></>;
          }
          return (
            <div key={i} style={{position: 'relative', height: lh * open, opacity: Math.min(1, open * 1.4), display: 'flex', alignItems: 'center', fontWeight: add ? 700 : undefined}}>
              {add && <div style={{position: 'absolute', left: -18, top: 4, bottom: 4, width: 6, borderRadius: 3, background: C.accent}} />}
              {h && h.from === undefined && <div style={{position: 'absolute', left: -8, right: -8, top: 2, bottom: 2, borderRadius: 8, background: C.accent, opacity: hv}} />}
              <span style={{position: 'relative', fontFamily: mono, fontWeight: add ? 700 : 500, fontSize: size, whiteSpace: 'pre', color: C.text, fontVariantLigatures: 'none'}}>{content}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
