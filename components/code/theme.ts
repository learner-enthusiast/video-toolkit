// Design tokens from /brand.md. A brand change is one edit in this file.
// Components never hard-code a colour, font, radius, border or shadow: they import from here.
export {inter, serif, mono} from './fonts';

export const C = {
  bg: '#F7F4EE', // page + grid card background
  white: '#FFFFFF',
  grid: '#DCD8D0', // notebook grid lines, hairlines
  border: '#1A1A1A', // 2 px card/pill border
  orange: '#E4572E', // the only accent
  ink: '#111111', // text
  dim: '#8A857C', // "bad", disabled, dim text
  dark: '#0D0D0D', // dark punch-moment background
  // derived neutrals (warm greys that sit between bg and dim)
  paper: '#FBFAF7', // card header strips
  mute: '#F1EEE8', // greyed-out ("bad") card fill
  fill: '#ECE9E3', // bar tracks, removed diff lines
  tint: '#E6E2DA', // dim pill background
  track: '#D9D4CA', // placeholder text lines, window dots
  orangeSoft: '#F2B5A1', // pale orange (hatch stripes)
  darkPanel: '#1A1A1A', // panels on a dark scene
} as const;

/** orange / white at a given alpha, e.g. rgba(228,87,46,.14) */
export const orangeA = (a: number) => `rgba(228,87,46,${a})`;
export const whiteA = (a: number) => `rgba(255,255,255,${a})`;

export const R = 14; // the one radius
export const BORDER = `2px solid ${C.border}`;
export const SHADOW = '0 8px 24px rgba(17,17,17,.08)'; // none on dark scenes

export const FPS = 30;
export const CANVAS = {w: 1080, h: 1920} as const; // 9:16 reel (reels are 9:16 only); long-form 16:9 videos pass their own size via props

/** square notebook-grid background (~40 px cells) */
export const gridBg = (cell = 40) => ({
  backgroundColor: C.bg,
  backgroundImage: `linear-gradient(${C.grid} 1px, transparent 1px), linear-gradient(90deg, ${C.grid} 1px, transparent 1px)`,
  backgroundSize: `${cell}px ${cell}px`,
});
