// Shared small drawings used by several components. Strokes are near-black on the 48 grid; accents are orange.
import React from 'react';
import {useCurrentFrame, Img, staticFile} from 'remotion';
import {C} from './theme';
import {pop, ease} from './anim';

/** true on a dark punch-moment scene: components that care read it instead of taking a prop on every call */
export const DarkCtx = React.createContext(false);

/** Official logo from the shared icon library (icons/icons.md). `file` is a name under icons/logos/. Never recolour or stretch. */
export const Logo: React.FC<{file: string; w: number; h: number; style?: React.CSSProperties}> = ({file, w, h, style}) => (
  <Img src={staticFile(`icons/logos/${file}`)} style={{width: w, height: h, objectFit: 'contain', ...style}} />
);

/** orange warning mark: triangle with "!" ("bad" is dim grey plus this, never red) */
export const WarnMark: React.FC<{size?: number; at?: number; style?: React.CSSProperties}> = ({size = 56, at = -100, style}) => {
  const f = useCurrentFrame();
  const v = pop(f, at);
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" style={{transform: `scale(${v})`, ...style}}>
      <path d="M24 4 L45 42 H3 Z" fill={C.accent2} stroke={C.border} strokeWidth={2.5} strokeLinejoin="round" />
      <rect x="22" y="16" width="4" height="14" rx="2" fill={C.onAccent} />
      <circle cx="24" cy="35.5" r="2.6" fill={C.onAccent} />
    </svg>
  );
};

/** orange round tick that draws itself ("good" is orange) */
export const Tick: React.FC<{size?: number; at: number}> = ({size = 52, at}) => {
  const f = useCurrentFrame();
  const v = pop(f, at);
  const d = ease(f, at + 2, at + 10);
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" style={{transform: `scale(${Math.max(0, v)})`, flexShrink: 0}}>
      <circle cx="24" cy="24" r="22" fill={C.accent} stroke={C.border} strokeWidth={2} />
      <path d="M13 25 L21 33 L36 16" fill="none" stroke={C.onAccent} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - d)} />
    </svg>
  );
};

/** padlock for budget / hold markers */
export const IconLock: React.FC<{size?: number; color?: string}> = ({size = 72, color = C.text}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round">
    <rect x="10" y="21" width="28" height="21" rx="4" /><path d="M16 21v-6a8 8 0 0 1 16 0v6" /><path d="M24 29v6" />
  </svg>
);

/** pull-request glyph (two nodes and a merge arrow) */
export const PRGlyph: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.text}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}>
    <circle cx="13" cy="10" r="5" /><circle cx="13" cy="38" r="5" /><circle cx="35" cy="38" r="5" />
    <path d="M13 15v18M35 33V20c0-4-3-7-7-7h-7" /><path d="M24 8l-4 5 4 5" />
  </svg>
);

/** chip glyph; `big` fills the die orange (the "big model" object) */
export const ChipGlyph: React.FC<{size?: number; color?: string; big?: boolean}> = ({size = 64, color = C.text, big}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}>
    <rect x="11" y="11" width="26" height="26" rx="4" fill={C.surface} />
    <rect x="18" y="18" width="12" height="12" rx="2" fill={big ? C.accent : C.surface} />
    {[17, 24, 31].map((p) => <path key={p} d={`M${p} 4v7M${p} 37v7M4 ${p}h7M37 ${p}h7`} />)}
  </svg>
);

/** server rack (two units, orange status dots) */
export const ServerGlyph: React.FC<{size?: number; color?: string}> = ({size = 64, color = C.text}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}>
    <rect x="8" y="6" width="32" height="14" rx="3" /><rect x="8" y="26" width="32" height="14" rx="3" />
    <circle cx="15" cy="13" r="1.8" fill={C.accent} stroke="none" /><circle cx="15" cy="33" r="1.8" fill={C.accent} stroke="none" /><path d="M22 13h12M22 33h12" />
  </svg>
);

/** generic user (head and shoulders) */
export const UserGlyph: React.FC<{size?: number; color?: string}> = ({size = 60, color = C.text}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}><circle cx="24" cy="17" r="8" /><path d="M9 42c2-9 8-13 15-13s13 4 15 13" /></svg>
);

/** phone handset (a call); `color` fills it: orange = live, grey = dead */
export const HandsetGlyph: React.FC<{size?: number; color?: string}> = ({size = 48, color = C.accent}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" style={{overflow: 'visible'}}>
    <path d="M13 6c-3 0-6 3-6 6 1 17 13 29 30 30 3 0 6-3 6-6v-6l-9-4-5 5c-5-2-9-6-11-11l5-5-4-9z" fill={color} stroke={C.border} strokeWidth={2.4} strokeLinejoin="round" />
  </svg>
);

/** dim "failed" badge: white circle, grey ✕ ("bad" is grey, never red) */
export const XMark: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.textDim}) => (
  <div style={{width: size, height: size, borderRadius: 999, background: C.surface, border: `3px solid ${color}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
    <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24"><path d="M5 5l14 14M19 5L5 19" stroke={color} strokeWidth={3.6} strokeLinecap="round" /></svg>
  </div>
);
/** static "good" badge: orange circle with a white tick */
export const TickMark: React.FC<{size?: number}> = ({size = 44}) => (
  <div style={{width: size, height: size, borderRadius: 999, background: C.accent, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
    <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" stroke={C.onAccent} strokeWidth={3.6} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
  </div>
);
