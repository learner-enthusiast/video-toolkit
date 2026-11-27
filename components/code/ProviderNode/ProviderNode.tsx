// Spec: components/specs/ProviderNode.md · a provider/server card (logo + label), plus the packet and self-drawing line the flow components share.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, accent2A, bgA} from '../theme';
import {ease, tween} from '../anim';
import {Logo} from '../glyphs';

export type LogoRef = {file: string; w: number; h: number};

/** white card with logo(s) or an icon, a bold label and a sub-line. dim 0..1 greys it; ring 0..1 adds the orange focus ring; badge sits on the top-right corner */
export const ProviderNode: React.FC<{w?: number; h?: number; icon?: React.ReactNode; logo?: LogoRef; logos?: LogoRef[]; label: React.ReactNode; sub?: React.ReactNode; dim?: number; ring?: number; dark?: boolean; badge?: React.ReactNode; style?: React.CSSProperties}> = ({w = 300, h = 150, icon, logo, logos, label, sub, dim = 0, ring = 0, dark, badge, style}) => (
  <div style={{position: 'relative', width: w, height: h, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: dark ? 'none' : `${SHADOW}${ring > 0 ? `, 0 0 0 ${8 * ring}px ${accent2A(0.85 * ring)}` : ''}`, display: 'flex', alignItems: 'center', gap: 18, padding: '0 22px', ...style}}>
    <div style={{display: 'flex', gap: 10, alignItems: 'center', opacity: 1 - 0.65 * dim, flexShrink: 0}}>
      {icon}{(logos ?? (logo ? [logo] : [])).map((l, i) => <Logo key={i} file={l.file} w={l.w} h={l.h} />)}
    </div>
    <div style={{display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0}}>
      <div style={{fontFamily: inter, fontWeight: 800, fontSize: 38, lineHeight: 1.05, color: dim > 0.5 ? C.textDim : C.text, whiteSpace: 'nowrap'}}>{label}</div>
      {sub && <div style={{fontFamily: inter, fontWeight: 600, fontSize: 24, color: C.textDim, whiteSpace: 'nowrap'}}>{sub}</div>}
    </div>
    {dim > 0 && <div style={{position: 'absolute', inset: 0, borderRadius: R, background: bgA(0.45 * dim)}} />}
    {badge && <div style={{position: 'absolute', right: -18, top: -18}}>{badge}</div>}
  </div>
);

/** orange packet travelling (x1,y1) → (x2,y2) between frames t0..t1, ease-in-out */
export const Packet: React.FC<{x1: number; y1: number; x2: number; y2: number; t0: number; t1: number; size?: number; color?: string; label?: string; hideAfter?: boolean}> = ({x1, y1, x2, y2, t0, t1, size = 26, color = C.accent, label, hideAfter = true}) => {
  const f = useCurrentFrame();
  if (f < t0 || (hideAfter && f > t1 + 2)) return null;
  return (
    <div style={{position: 'absolute', left: tween(f, t0, t1, x1, x2) - size / 2, top: tween(f, t0, t1, y1, y2) - size / 2, width: size, height: size, borderRadius: 8, background: color, border: `2px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: mono, fontWeight: 700, fontSize: size * 0.45, color: C.onAccent}}>{label}</div>
  );
};

/** line that draws itself from `at` over `dur` frames (scene coords, w x h canvas); optional dash and arrowhead */
export const DrawLine: React.FC<{x1: number; y1: number; x2: number; y2: number; at: number; dur?: number; color?: string; width?: number; dash?: boolean; arrow?: boolean; canvas?: {w: number; h: number}}> = ({x1, y1, x2, y2, at, dur = 12, color = C.border, width = 5, dash, arrow, canvas = {w: 972, h: 970}}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = ease(f, at, at + dur);
  const ang = Math.atan2(y2 - y1, x2 - x1);
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={canvas.w} height={canvas.h}>
      <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke={color} strokeWidth={width} strokeLinecap="round" strokeDasharray={dash ? '14 12' : undefined} />
      {arrow && p > 0.95 && <path d={`M${x2} ${y2} l${-20 * Math.cos(ang - 0.45)} ${-20 * Math.sin(ang - 0.45)} M${x2} ${y2} l${-20 * Math.cos(ang + 0.45)} ${-20 * Math.sin(ang + 0.45)}`} stroke={color} strokeWidth={width} strokeLinecap="round" fill="none" />}
    </svg>
  );
};
