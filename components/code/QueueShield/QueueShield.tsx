// Spec: components/specs/QueueShield.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, ease, popIn, enter} from '../anim';
import {Logo, WarnMark, ServerGlyph, ChipGlyph} from '../glyphs';
import {Tag} from '../Tag/Tag';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const Pill: React.FC<{label: React.ReactNode; tone?: 'orange' | 'ink' | 'dim' | 'outline'; size?: number; monoFont?: boolean}> = (p) => <Tag {...p} />;
export const OK: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.accent}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}><path d="M9 25l10 10 20-22" /></svg>
);
const NodeLabel: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 26, color = C.text}) => (
  <div style={{fontFamily: inter, fontWeight: 800, fontSize: size, color, textAlign: 'center', lineHeight: 1.1, whiteSpace: 'nowrap'}}>{children}</div>
);
const Tickets: React.FC<{n: number; w: number; f: number; at: number; nudge?: number}> = ({n, w, f, at, nudge = -1}) => (
  <div style={{position: 'relative', width: w, height: 18 * n + 30}}>
    {Array.from({length: n}).map((_, i) => {
      const v = sp(f, at + i * 4);
      const nd = nudge > 0 && f >= nudge ? Math.sin(Math.min(1, (f - nudge - i * 3) / 8) * Math.PI) * 6 * (f - nudge - i * 3 > 0 ? 1 : 0) : 0;
      return <div key={i} style={{position: 'absolute', left: (i % 2) * 8 + nd, top: i * 18, width: w - 8, height: 30, boxSizing: 'border-box', borderRadius: 7, background: C.accent, border: BORDER, opacity: Math.min(1, v * 1.5), transform: `translateY(${(1 - v) * -20}px)`}} />;
    })}
  </div>
);
const shieldPath = (w: number, h: number, s: number) => {
  // rectangle (s=0) → shield with a pointed bottom (s=1)
  const r = 14, tip = h * 0.18 * s;
  return `M${r} 0 H${w - r} Q${w} 0 ${w} ${r} V${h - tip - r * (1 - s)} Q${w} ${h - tip * 0.6} ${w / 2} ${h} Q0 ${h - tip * 0.6} 0 ${h - tip - r * (1 - s)} V${r} Q0 0 ${r} 0 Z`;
};

/** Queue as a shield: a ticket stack that morphs from a flat queue box (shieldAt) into an orange-edged shield,
 *  flood dots from `floodFrom` stop at its face (floodAt), and optional arcs fly over it (bypassAt → bypassTo). */
export const QueueShield: React.FC<{x: number; y: number; w: number; h: number; at: number; out?: number; shieldAt?: number; label?: string; tickets?: number;
  floodAt?: number; floodFrom?: {x: number; y: number}; bypassAt?: number; bypassFrom?: {x: number; y: number}; bypassTo?: {x: number; y: number}}> =
  ({x, y, w, h, at, out = 1e9, shieldAt, label = 'Queue', tickets = 5, floodAt, floodFrom, bypassAt, bypassFrom, bypassTo}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const s = shieldAt === undefined ? 1 : clamp01(sp(f, shieldAt, {damping: 18, stiffness: 90}));
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ease(f, out - 8, out, 1, 0)}}>
      <div style={{position: 'absolute', left: x, top: y, width: w, height: h, ...popIn(f, at)}}>
        <svg width={w} height={h} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
          <path d={shieldPath(w, h, s)} fill={C.surface} stroke={s > 0.5 ? C.accent : C.border} strokeWidth={s > 0.5 ? 5 : 2} strokeLinejoin="round" />
        </svg>
        <div style={{position: 'absolute', left: 18, top: 24 + s * 26}}><Tickets n={tickets} w={w - 36} f={f} at={at + 2} nudge={floodAt} /></div>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: s > 0.5 ? -46 : 12}}><NodeLabel size={s > 0.5 ? 28 : 26} color={s > 0.5 ? C.accent : C.text}>{label}</NodeLabel></div>
      </div>
      {floodAt !== undefined && floodFrom && Array.from({length: 9}).map((_, i) => {
        const t0 = floodAt + i * 3, t1 = t0 + 14;
        if (f < t0) return null;
        const k = ease(f, t0, t1);
        return <div key={i} style={{position: 'absolute', left: lerp(floodFrom.x, x + 10, k), top: floodFrom.y + (i % 5) * 40, width: 18, height: 18, borderRadius: 99, background: k > 0.95 ? C.accent : C.text, opacity: ease(f, t1 + 2, t1 + 10, 1, 0)}} />;
      })}
      {bypassAt !== undefined && bypassFrom && bypassTo && [0, 1, 2].map((i) => {
        const a = bypassAt + i * 5;
        if (f < a) return null;
        const v = ease(f, a, a + 14);
        const x1 = bypassFrom.x + i * 30, y1 = bypassFrom.y, x2 = bypassTo.x + i * 50, y2 = bypassTo.y;
        return (
          <svg key={i} width={972} height={970} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
            <path d={`M${x1} ${y1} Q${(x1 + x2) / 2} ${Math.min(y1, y2) - 260 + i * 30} ${x2} ${y2}`} fill="none" stroke={C.accent} strokeWidth={10 - i * 2} strokeLinecap="round" strokeDasharray={900} strokeDashoffset={900 * (1 - v)} />
          </svg>
        );
      })}
    </div>
  );
};
