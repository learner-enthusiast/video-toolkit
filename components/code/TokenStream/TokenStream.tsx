// Spec: components/specs/TokenStream.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/* ---------------- TokenStream ---------------- */
export const TokenStream: React.FC<{w?: number; chips: string[]; cutTail: string; from: number; to: number; capAt: number; cap: number; at: number; out?: number; payAt: number; perTok: number; prefix?: string;
  labels?: {header: string; tokens: string; pay: string; wall: string; never: string; cap: string}}> = ({w = 900, chips, cutTail, from, to, capAt, cap, at, out = 1e9, payAt, perTok, prefix = '₹',
  labels = {header: 'MODEL OUTPUT · ONE TOKEN AT A TIME', tokens: 'tokens written', pay: 'you pay', wall: 'max_tokens → hard stop', never: 'never written', cap: 'cap'}}) => {
  const money = (n: number) => `${prefix}${n.toFixed(2)}`;
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  // token count ramps 0 -> cap-chips.length over [from, to], then the last chips arrive one by one until capAt
  const per = Math.max(3, Math.min(6, Math.floor((capAt - to) / chips.length)));
  const shown = f < to ? 0 : Math.min(chips.length, Math.floor((f - to) / per) + 1);
  const tok = f < to ? Math.round(easeOut(f, from, to, 0, cap - chips.length)) : cap - chips.length + shown;
  const hit = f >= capAt;
  const wallV = hit ? sp(f, capAt, {damping: 13, stiffness: 260}) : 0;
  const shk = hit && f < capAt + 12 ? Math.sin((f - capAt) * 2.6) * 7 * (1 - (f - capAt) / 12) : 0;
  const box = (label: string, value: string, tone: 'ink' | 'orange', show: boolean) => (
    <div style={{flex: 1, borderRadius: R, border: `2px solid ${tone === 'orange' ? C.accent : C.border}`, background: C.surface, padding: '12px 14px', display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: show ? 1 : 0.25}}>
      <span style={{fontFamily: inter, fontWeight: 900, fontSize: 76, lineHeight: 1.05, color: tone === 'orange' ? C.accent : C.ink, fontVariantNumeric: 'tabular-nums', transform: `scale(${hit ? 1 + 0.06 * Math.sin(Math.PI * Math.min(1, (f - capAt) / 10)) : 1})`}}>{value}</span>
      <span style={{fontFamily: inter, fontWeight: 700, fontSize: 26, color: C.textDim}}>{label}</span>
    </div>
  );
  return (
    <div style={{position: 'relative', width: w, height: 760, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at, out), transform: `translateX(${shk}px)`}}>
      <div style={{position: 'absolute', left: 36, top: 26, fontFamily: inter, fontWeight: 800, fontSize: 24, letterSpacing: '0.12em', color: C.textDim}}>{labels.header}</div>
      {/* earlier text, faded */}
      <div style={{position: 'absolute', left: 36, right: 110, top: 74, display: 'flex', flexDirection: 'column', gap: 12}}>
        {[0.94, 0.8, 0.62].map((x, i) => <div key={i} style={{height: 18, width: `${x * 100}%`, borderRadius: 9, background: C.fill, opacity: Math.min(1, ease(f, from + i * 6, from + 10 + i * 6))}} />)}
      </div>
      {/* chip row */}
      <div style={{position: 'absolute', left: 30, right: 30, top: 150, height: 140, display: 'flex', alignItems: 'center', flexWrap: 'nowrap', gap: 7, overflow: 'hidden'}}>
        {chips.slice(0, shown).map((c, i) => {
          const a = to + i * per;
          const v = sp(f, a, {damping: 12, stiffness: 220});
          const newest = i === shown - 1 && !hit;
          return <span key={i} style={{fontFamily: mono, fontWeight: 700, fontSize: 38, padding: '8px 10px', borderRadius: 10, border: BORDER, background: newest ? C.accent : C.white, color: newest ? C.white : C.ink, whiteSpace: 'pre', transform: `translateY(${(1 - v) * -60}px)`, opacity: Math.min(1, v * 1.6)}}>{c}</span>;
        })}
        <span style={{width: 12, height: 150, borderRadius: 6, background: C.ink, flexShrink: 0, opacity: Math.min(1, wallV * 2), transform: `translateY(${(1 - wallV) * -200}px)`}} />
        {hit && (
          <span style={{fontFamily: mono, fontWeight: 700, fontSize: 38, padding: '8px 10px', borderRadius: 10, border: `2px dashed ${C.textDim}`, color: C.textDim, background: `repeating-linear-gradient(135deg, #E7E3DC 0 8px, ${C.white} 8px 16px)`, whiteSpace: 'pre', opacity: ease(f, capAt + 6, capAt + 14)}}>{cutTail}</span>
        )}
      </div>
      {hit && <div style={{position: 'absolute', left: 30, top: 104, ...popIn(f, capAt + 2)}}><Tag label={labels.wall} tone="ink" size={26} monoFont /></div>}
      {hit && <div style={{position: 'absolute', right: 40, top: 296, display: 'flex', alignItems: 'center', gap: 8, ...popIn(f, capAt + 8)}}><WarnMark size={34} /><span style={{fontFamily: inter, fontWeight: 800, fontSize: 26, color: C.textDim}}>{labels.never}</span></div>}
      {/* counters */}
      <div style={{position: 'absolute', left: 30, right: 30, top: 380, display: 'flex', gap: 18}}>
        {box(labels.tokens, tok.toLocaleString('en-IN'), 'ink', f >= from)}
        {box(labels.pay, money(tok * perTok), 'orange', f >= payAt)}
      </div>
      <div style={{position: 'absolute', left: 30, right: 30, top: 590, height: 26, borderRadius: 13, background: C.fill, border: `2px solid ${C.grid}`, overflow: 'hidden'}}>
        <div style={{width: `${(tok / cap) * 100}%`, height: '100%', background: C.accent}} />
      </div>
      <div style={{position: 'absolute', left: 30, right: 30, top: 630, display: 'flex', justifyContent: 'space-between', fontFamily: mono, fontWeight: 700, fontSize: 24, color: C.textDim}}><span>0</span><span style={{color: hit ? C.ink : C.textDim}}>{labels.cap} · {cap.toLocaleString('en-IN')}</span></div>
    </div>
  );
};

