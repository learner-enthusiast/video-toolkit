// Spec: components/specs/ExamSheet.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/* ---------------- ExamSheet ---------------- */
const BellIcon: React.FC<{size?: number; color?: string}> = ({size = 90, color = C.ink}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M24 6v4" /><path d="M12 34c2-3 3-6 3-12a9 9 0 0 1 18 0c0 6 1 9 3 12z" fill={C.white} /><path d="M9 34h30" /><path d="M21 39a3 3 0 0 0 6 0" /></svg>
);
const PenIcon: React.FC<{size?: number}> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={C.ink} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M34 6l8 8-24 24-11 3 3-11z" fill={C.white} /><path d="M30 10l8 8" stroke={C.orange} /></svg>
);
/** a handwriting-like squiggle across width w */
const scribble = (w: number, seed: number, amp = 7) => {
  let d = `M 0 0`;
  for (let x = 0; x <= w; x += 14) d += ` Q ${x + 7} ${(((x * 7 + seed * 13) % 11) - 5) * (amp / 5)} ${x + 14} ${(((x * 3 + seed * 5) % 9) - 4) * (amp / 6)}`;
  return d;
};
export const ExamSheet: React.FC<{w?: number; h?: number; lines?: number; fillFrom: number; bellAt: number; penStopAt: number; at: number; out?: number; title?: string; blank?: boolean; stopLabel?: string}> = ({w = 600, h = 700, lines = 9, fillFrom, bellAt, penStopAt, at, out = 1e9, title = 'ANSWER SHEET', blank, stopLabel = 'mid-line'}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const top = 92, gap = (h - top - 40) / lines, x0 = 40, lw = w - 80;
  // writing progress in "lines": up to stop line (mid-line) at penStopAt
  const stopLine = lines - 3.45;
  const prog = blank ? 0 : f < penStopAt ? ease(f, fillFrom, penStopAt, 0, stopLine) : stopLine;
  const ring = f >= bellAt ? Math.sin((f - bellAt) * 1.3) * 16 * Math.exp(-(f - bellAt) / 14) : 0;
  const lift = f >= penStopAt ? sp(f, penStopAt, {damping: 12, stiffness: 200}) : 0;
  const penX = x0 + lw * (prog % 1 || (prog >= stopLine ? stopLine % 1 : 0));
  const penY = top + gap * Math.floor(prog) + gap * 0.55;
  return (
    <div style={{position: 'relative', width: w, height: h, boxSizing: 'border-box', background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at, out)}}>
      <div style={{position: 'absolute', left: 30, top: 26, fontFamily: inter, fontWeight: 800, fontSize: 26, letterSpacing: '0.14em', color: C.dim}}>{title}</div>
      <svg width={w} height={h} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        {Array.from({length: lines}).map((_, i) => <line key={i} x1={x0} x2={x0 + lw} y1={top + gap * (i + 1)} y2={top + gap * (i + 1)} stroke={C.grid} strokeWidth={2} />)}
        {Array.from({length: Math.ceil(prog)}).map((_, i) => {
          const frac = Math.min(1, prog - i);
          const len = lw * (i === lines - 1 ? 0.6 : 1);
          return <path key={`s${i}`} d={scribble(len, i)} transform={`translate(${x0}, ${top + gap * i + gap * 0.62})`} fill="none" stroke={C.ink} strokeWidth={3.4} strokeLinecap="round" strokeDasharray={len * 1.4} strokeDashoffset={len * 1.4 * (1 - frac)} />;
        })}
      </svg>
      {/* bell */}
      <div style={{position: 'absolute', right: 22, top: 10, transform: `rotate(${ring}deg)`, transformOrigin: '50% 10%'}}><BellIcon size={84} color={f >= bellAt ? C.orange : C.ink} /></div>
      {f >= bellAt && f < bellAt + 40 && [0, 1, 2].map((i) => (
        <div key={i} style={{position: 'absolute', right: 6 - i * 16, top: 0 - i * 14, width: 120 + i * 32, height: 120 + i * 32, borderRadius: '50%', border: `4px solid ${C.orange}`, borderLeftColor: 'transparent', borderBottomColor: 'transparent', opacity: ease(f, bellAt + i * 3, bellAt + 30 + i * 3, 1, 0), transform: 'rotate(-10deg)'}} />
      ))}
      {/* pen */}
      {!blank && f >= fillFrom && <div style={{position: 'absolute', left: penX - 10, top: penY - 62 - lift * 46, transform: `rotate(${lift * -24}deg)`, transition: 'none'}}><PenIcon size={72} /></div>}
      {!blank && f >= penStopAt + 4 && <div style={{position: 'absolute', left: penX + 30, top: penY - 4, display: 'flex', alignItems: 'center', gap: 6, ...popIn(f, penStopAt + 4)}}><WarnMark size={30} /><span style={{fontFamily: inter, fontWeight: 800, fontSize: 24, color: C.dim, whiteSpace: 'nowrap'}}>{stopLabel}</span></div>}
    </div>
  );
};
/** rough-work page (thinking tokens): grey scribbles + crossed-out sums */
export const RoughSheet: React.FC<{w?: number; h?: number; drawFrom: number; drawTo: number; at: number; out?: number; title?: string}> = ({w = 420, h = 560, drawFrom, drawTo, at, out = 1e9, title = 'ROUGH WORK'}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const n = 11;
  const p = ease(f, drawFrom, drawTo, 0, n);
  return (
    <div style={{position: 'relative', width: w, height: h, boxSizing: 'border-box', background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at, out)}}>
      <div style={{position: 'absolute', left: 24, top: 20, fontFamily: inter, fontWeight: 800, fontSize: 22, letterSpacing: '0.14em', color: C.dim}}>{title}</div>
      <svg width={w} height={h} style={{position: 'absolute', inset: 0}}>
        {Array.from({length: n}).map((_, i) => {
          const len = (w - 70) * (0.5 + ((i * 37) % 50) / 100);
          const fr = Math.max(0, Math.min(1, p - i));
          return <path key={i} d={scribble(len, i + 3, 9)} transform={`translate(${30 + (i % 3) * 8}, ${78 + i * 42})`} fill="none" stroke={C.dim} strokeWidth={3} strokeLinecap="round" strokeDasharray={len * 1.5} strokeDashoffset={len * 1.5 * (1 - fr)} />;
        })}
        {p > 4 && <line x1={34} y1={190} x2={w - 60} y2={160} stroke={C.dim} strokeWidth={4} strokeLinecap="round" opacity={0.8} />}
        {p > 8 && <line x1={34} y1={360} x2={w - 90} y2={330} stroke={C.dim} strokeWidth={4} strokeLinecap="round" opacity={0.8} />}
      </svg>
    </div>
  );
};

