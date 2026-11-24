// Fonts from brand.md, loaded through @remotion/google-fonts. Import from here, never load a font elsewhere.
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadSerif} from '@remotion/google-fonts/InstrumentSerif';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';

/** Body, labels (400-700), bold UI (800), captions (900) */
export const inter = loadInter('normal', {weights: ['400', '500', '600', '700', '800', '900'], subsets: ['latin']}).fontFamily;
/** Headlines: Instrument Serif Italic, orange, large */
export const serif = loadSerif('italic', {weights: ['400'], subsets: ['latin']}).fontFamily;
/** Code only: JetBrains Mono 400-700 */
export const mono = loadMono('normal', {weights: ['400', '500', '700'], subsets: ['latin']}).fontFamily;
/** Indic text (token blocks, Hindi/Bengali UI strings): Noto Sans Devanagari / Bengali, keeps conjuncts intact at ≥ 34 px */
import {loadFont as loadDeva} from '@remotion/google-fonts/NotoSansDevanagari';
import {loadFont as loadBeng} from '@remotion/google-fonts/NotoSansBengali';
export const deva = loadDeva('normal', {weights: ['500', '700'], subsets: ['devanagari', 'latin']}).fontFamily;
export const bengali = loadBeng('normal', {weights: ['500', '700'], subsets: ['bengali', 'latin']}).fontFamily;
