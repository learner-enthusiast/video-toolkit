// Spec: components/specs/PhoneMockup.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

export type Day = {title: string; text: string};
/* plan variant: an AI planner types day cards word by word and freezes mid-sentence; home variant: the app's start screen */
const PinIcon: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.accent}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round"><path d="M24 44s14-13 14-24a14 14 0 0 0-28 0c0 11 14 24 14 24z" fill={C.white} /><circle cx="24" cy="20" r="5" /></svg>
);
export const PhoneMockup: React.FC<{
  w: number; h: number; app?: string; variant?: 'plan' | 'home'; days?: Day[]; typeFrom?: number; typeTo?: number; blinkFrom?: number; emptyDays?: number;
  dark?: boolean; tagline?: string; cta?: string; prefilled?: number; subtitle?: string; heroA?: string; heroB?: string; placeholder?: string; emptyLabel?: string; at: number; out?: number;
}> = ({w, h, app = 'TripMate', variant = 'plan', days = [], typeFrom = 0, typeTo = 1, blinkFrom = 1e9, emptyDays = 0, dark, prefilled = 0, tagline = 'Your AI trip planner', cta = 'Plan my trip', subtitle = '', heroA = 'Where to', heroB = 'next?', placeholder = 'Type a trip…', emptyLabel = 'DAY', at, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const s = w / 440; // design at 440 px wide
  // word-granular typing across all day texts
  const words = days.flatMap((d, di) => d.text.split(' ').map((x) => ({di, x})));
  const n = prefilled + Math.round(ease(f, typeFrom, typeTo) * (words.length - prefilled));
  const typing = f >= typeFrom && f < typeTo;
  const lastDay = n > 0 ? words[n - 1].di : 0;
  const shownDays = days.slice(0, lastDay + 1);
  // cursor: solid while typing, blinks 3x from blinkFrom, then stays on
  const bl = f - blinkFrom;
  const cursorOn = typing || f < blinkFrom || bl >= 48 || Math.floor(bl / 8) % 2 === 1;
  const scroll = Math.max(0, lastDay - 2) * 170 * s * ease(f, typeFrom, typeTo);
  const o = ease(f, out - 8, out, 1, 0);
  return (
    <div style={{position: 'relative', width: w, height: h, boxSizing: 'border-box', borderRadius: 54 * s, border: `${5 * s}px solid ${dark ? '#3A3A3A' : C.border}`, background: C.ink, padding: 11 * s, boxShadow: dark ? 'none' : SHADOW, opacity: o}}>
      <div style={{position: 'relative', width: '100%', height: '100%', borderRadius: 42 * s, overflow: 'hidden', background: C.bg}}>
        <div style={{position: 'relative', zIndex: 2, height: 104 * s, background: C.surface, borderBottom: BORDER, display: 'flex', alignItems: 'center', gap: 12 * s, padding: `${26 * s}px ${20 * s}px 0`, boxSizing: 'border-box'}}>
          <PinIcon size={40 * s} />
          <div>
            <div style={{fontFamily: inter, fontWeight: 900, fontSize: 26 * s, color: C.text, lineHeight: 1.05}}>{app}</div>
            <div style={{fontFamily: inter, fontWeight: 600, fontSize: 17 * s, color: C.textDim}}>{variant === 'home' ? tagline : subtitle}</div>
          </div>
        </div>
        <div style={{position: 'absolute', left: '50%', top: 8 * s, width: 96 * s, height: 20 * s, borderRadius: 99, background: C.ink, transform: 'translateX(-50%)'}} />
        {variant === 'home' ? (
          <div style={{position: 'absolute', left: 22 * s, right: 22 * s, top: 130 * s, display: 'flex', flexDirection: 'column', gap: 18 * s}}>
            <div style={{fontFamily: serif, fontStyle: 'italic', fontSize: 52 * s, lineHeight: 1, color: C.text}}>{heroA}<br /><span style={{color: C.accent}}>{heroB}</span></div>
            <div style={{border: BORDER, borderRadius: R, background: C.surface, padding: `${14 * s}px ${16 * s}px`, fontFamily: inter, fontWeight: 600, fontSize: 21 * s, color: C.textDim}}>{placeholder}</div>
            <div style={{alignSelf: 'flex-start', background: C.accent, color: C.white, border: BORDER, borderRadius: 99, padding: `${10 * s}px ${22 * s}px`, fontFamily: inter, fontWeight: 800, fontSize: 22 * s}}>{cta}</div>
            {[0, 1, 2].map((i) => <div key={i} style={{height: 64 * s, borderRadius: R, border: `2px solid ${C.grid}`, background: C.surface, opacity: 0.8 - i * 0.2}} />)}
          </div>
        ) : (
          <div style={{position: 'absolute', left: 18 * s, right: 18 * s, top: 122 * s, transform: `translateY(${-scroll}px)`, display: 'flex', flexDirection: 'column', gap: 14 * s}}>
            {shownDays.map((d, di) => {
              const ws = words.filter((x) => x.di === di);
              const before = words.findIndex((x) => x.di === di);
              const k = Math.max(0, Math.min(ws.length, n - before));
              const isLast = di === lastDay;
              return (
                <div key={di} style={{border: BORDER, borderRadius: R, background: C.surface, padding: `${12 * s}px ${14 * s}px`}}>
                  <div style={{fontFamily: inter, fontWeight: 800, fontSize: 19 * s, color: C.accent, letterSpacing: '0.06em'}}>{d.title.toUpperCase()}</div>
                  <div style={{fontFamily: inter, fontWeight: 600, fontSize: 25 * s, lineHeight: 1.3, color: C.text}}>
                    {ws.slice(0, k).map((x) => x.x).join(' ')}
                    {isLast && <span style={{display: 'inline-block', width: 4 * s, height: 24 * s, marginLeft: 3 * s, verticalAlign: 'middle', background: C.accent, opacity: cursorOn ? 1 : 0}} />}
                  </div>
                </div>
              );
            })}
            {f >= typeTo && Array.from({length: emptyDays}).map((_, i) => (
              <div key={`e${i}`} style={{border: `${3 * s}px dashed ${C.textDim}`, borderRadius: R, height: 70 * s, display: 'flex', alignItems: 'center', padding: `0 ${14 * s}px`, fontFamily: inter, fontWeight: 800, fontSize: 17 * s, color: C.textDim, letterSpacing: '0.06em', ...enter(f, typeTo + 8 + i * 5)}}>{emptyLabel} {days.length + 1 + i}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

