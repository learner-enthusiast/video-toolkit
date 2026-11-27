// The active brand's design tokens (/brand.md, /brands/). The brand is REMOTION_BRAND in the video's work/remotion/.env.
// Components never hard-code a colour, font, radius, border or shadow: they import from here.
// New code uses the semantic names. Legacy names are aliases.
import {inter, serif} from './fonts';
import type {Theme} from './themes/types';
import {brand1} from './themes/brand1';
import {brand2} from './themes/brand2';
import {brand3} from './themes/brand3';

export {inter, serif, mono, deva, bengali} from './fonts';
export type {Theme} from './themes/types';

// Remotion injects REMOTION_* variables into the page's process.env (declared here: no @types/node needed).
declare const process: {env: Record<string, string | undefined>};

const readBrand = (): 1 | 2 | 3 => {
  try {
    const v = String(process.env.REMOTION_BRAND ?? '').trim();
    return v === '2' ? 2 : v === '3' ? 3 : 1;
  } catch {
    return 1;
  }
};

export const BRAND = readBrand();
/** the active theme */
export const T: Theme = {1: brand1, 2: brand2, 3: brand3}[BRAND];

export const C = {
  ...T,
  // legacy aliases
  white: T.surface,
  ink: T.text,
  orange: T.accent,
  orangeSoft: T.accentSoft,
  dim: T.textDim,
  dark: T.punchBg,
};

/** a #RRGGBB token at a given alpha, e.g. rgba(228,87,46,0.14) */
const hexA = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};
export const accentA = (a: number) => hexA(T.accent, a);
export const accent2A = (a: number) => hexA(T.accent2, a);
export const surfaceA = (a: number) => hexA(T.surface, a);
export const bgA = (a: number) => hexA(T.bg, a);
export const dimA = (a: number) => hexA(T.textDim, a);
export const onAccentA = (a: number) => hexA(T.onAccent, a);
/** lines and text on punchBg (white in every brand) */
export const whiteA = (a: number) => hexA('#FFFFFF', a);
/** black drop shading, the same in every brand */
export const blackA = (a: number) => hexA('#000000', a);
export const orangeA = accentA;

export const R = 14; // the one radius
export const BORDER = `2px solid ${C.border}`;
export const SHADOW = T.shadow; // none on punch scenes

/** spread into a headline's style: <div style={{...headline, fontSize: 52}}> */
export const headline: {fontFamily: string; fontStyle: 'italic' | 'normal'; fontWeight?: number} =
  T.headlineFont === 'serif' ? {fontFamily: serif, fontStyle: 'italic'} : {fontFamily: inter, fontStyle: 'normal', fontWeight: 800};

export const FPS = 30;
export const CANVAS = {w: 1080, h: 1920} as const; // 9:16 reel (reels are 9:16 only); long-form 16:9 videos pass their own size via props

const SCANLINES = `repeating-linear-gradient(0deg, ${blackA(0.22)} 0 1px, transparent 1px 4px)`;
const VIGNETTE = `radial-gradient(ellipse at center, transparent 55%, ${blackA(0.45)} 100%)`;

/** the brand's page background pattern; `cell` defaults to 40 px for lines and 28 px for dots */
export const gridBg = (cell?: number) => {
  if (T.gridStyle === 'dots') {
    const c = cell ?? 28;
    return {backgroundColor: C.bg, backgroundImage: `radial-gradient(circle, ${C.grid} 1.8px, transparent 2.4px)`, backgroundSize: `${c}px ${c}px`};
  }
  const c = cell ?? 40;
  const lines = `linear-gradient(${C.grid} 1px, transparent 1px), linear-gradient(90deg, ${C.grid} 1px, transparent 1px)`;
  if (T.gridStyle === 'lines-scanlines') {
    return {backgroundColor: C.bg, backgroundImage: `${VIGNETTE}, ${SCANLINES}, ${lines}`, backgroundSize: `100% 100%, 100% 4px, ${c}px ${c}px, ${c}px ${c}px`};
  }
  return {backgroundColor: C.bg, backgroundImage: lines, backgroundSize: `${c}px ${c}px`};
};
