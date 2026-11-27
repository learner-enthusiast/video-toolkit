// Spec: components/specs/DualMeter.md · two vertical meters (requests vs tokens) with the same geometry in every scene,
// plus BudgetBar (the horizontal "budget" mode: free / held / spent / refunded segments).
import React from 'react';
import {C, R, BORDER, whiteA, inter, mono} from '../theme';
import {IconLock} from '../glyphs';

export const fmt = (n: number) => Math.round(n).toLocaleString('en-US');
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const HATCH = `repeating-linear-gradient(45deg, ${C.accent} 0 9px, ${C.accentSoft} 9px 18px)`;

/** geometry inside the grid card; pass `geometry` to move or resize the pair */
export const METER = {x1: 430, x2: 690, w: 200, y: 120, h: 560};
type Geometry = typeof METER;

const Bar: React.FC<{g: Geometry; x: number; frac: number; color: string; title: string; value: string; valueColor: string; notches?: number; o?: number; dark?: boolean; min?: number}> = ({g, x, frac, color, title, value, valueColor, notches = 0, o = 1, dark, min = 0}) => {
  const {y, w, h} = g;
  const fh = frac <= 0 ? 0 : Math.max(min, frac * (h - 4));
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o}}>
      <div style={{position: 'relative', width: w, height: h, boxSizing: 'border-box', border: dark ? `2px solid ${whiteA(0.6)}` : BORDER, borderRadius: R, background: dark ? C.darkPanel : C.white}}>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: fh, background: color, borderRadius: `0 0 ${R - 2}px ${R - 2}px`}} />
        {Array.from({length: Math.max(0, notches - 1)}).map((_, i) => (
          <div key={i} style={{position: 'absolute', left: 0, width: 26, bottom: ((i + 1) * (h - 4)) / notches, height: 2, background: dark ? whiteA(0.5) : C.border, opacity: 0.55}} />
        ))}
      </div>
      <div style={{marginTop: 14, textAlign: 'center', fontFamily: inter, fontWeight: 800, fontSize: 28, letterSpacing: '0.1em', textTransform: 'uppercase', color: dark ? whiteA(0.65) : C.textDim, whiteSpace: 'nowrap'}}>{title}</div>
      <div style={{textAlign: 'center', fontFamily: inter, fontWeight: 900, fontSize: 62, lineHeight: 1.05, color: valueColor, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap', marginLeft: -60, marginRight: -60}}>{value}</div>
    </div>
  );
};

/** req / tok are 0-1 fractions of the bar (req is counted against `reqMax` notches); the *Text props are the printed values */
export const DualMeter: React.FC<{req: number; reqMax?: number; tok: number; reqText: string; tokText: string; reqTitle?: string; tokTitle?: string; counterO?: number; counterDx?: number; dark?: boolean; geometry?: Geometry}> = ({req, reqMax = 6, tok, reqText, tokText, reqTitle = 'Requests', tokTitle = 'Tokens', counterO = 1, counterDx = 0, dark, geometry = METER}) => (
  <>
    {counterO > 0.01 && <div style={{position: 'absolute', inset: 0, transform: `translateX(${counterDx}px)`}}><Bar g={geometry} x={geometry.x1} frac={req / reqMax} color={C.textDim} title={reqTitle} value={reqText} valueColor={dark ? C.white : C.textDim} notches={reqMax} o={counterO} dark={dark} /></div>}
    <Bar g={geometry} x={geometry.x2} frac={tok} color={C.accent} title={tokTitle} value={tokText} valueColor={C.accent} dark={dark} min={7} />
  </>
);

export type Seg = {frac: number; kind: 'free' | 'held' | 'spent' | 'back'; label?: string; lock?: number};
/** budget mode: segments left to right; `lock` (0-1) scales the padlock badge in */
export const BudgetBar: React.FC<{x: number; y: number; w: number; h: number; segs: Seg[]; dark?: boolean; radius?: number}> = ({x, y, w, h, segs, dark, radius = R}) => {
  let acc = 0;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, boxSizing: 'border-box', border: dark ? `2px solid ${whiteA(0.6)}` : BORDER, borderRadius: radius, background: dark ? C.darkPanel : C.white, overflow: 'hidden'}}>
      {segs.map((s, i) => {
        const left = acc * (w - 4);
        acc += s.frac;
        const sw = s.frac * (w - 4);
        if (sw < 0.5) return null;
        const bg = s.kind === 'free' || s.kind === 'back' ? C.accent : s.kind === 'held' ? HATCH : dark ? C.darkPanel : C.fill;
        return (
          <div key={i} style={{position: 'absolute', left, top: 0, width: sw, height: '100%', background: bg, borderRight: i < segs.length - 1 ? `2px solid ${C.border}` : undefined, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, overflow: 'hidden'}}>
            {s.lock !== undefined && sw > 46 && <div style={{background: C.surface, border: BORDER, borderRadius: 99, width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${s.lock})`, flexShrink: 0}}><IconLock size={28} /></div>}
            {s.label && sw > 150 && <span style={{fontFamily: mono, fontWeight: 700, fontSize: 28, color: s.kind === 'spent' ? C.textDim : C.ink, background: s.kind === 'held' ? whiteA(0.88) : 'transparent', borderRadius: 6, padding: '0 8px', whiteSpace: 'nowrap'}}>{s.label}</span>}
          </div>
        );
      })}
    </div>
  );
};
