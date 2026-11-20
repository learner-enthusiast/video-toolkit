// Spec: components/specs/CustomerBurn.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';

/* ---------- CustomerBurn (dark) ---------- */
const Person: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill={color}><circle cx="24" cy="15" r="9" /><path d="M7 45c1-11 8-17 17-17s16 6 17 17z" /></svg>
);
export const inrFmt = (n: number) => {
  const s = Math.round(n).toString();
  if (s.length <= 3) return s;
  const last3 = s.slice(-3), rest = s.slice(0, -3);
  return rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + last3;
};
export const CustomerBurn: React.FC<{tagAt: number; gridAt: number; leaveAt: number; countAt: number; countTo: number; fewAt?: number; unit: string; unitNote: string; gridLabel: string; leaveTo: string; leaveNote: string; counterNote: string; fewLabel?: string; prefix?: string}> = ({tagAt, gridAt, leaveAt, countAt, countTo, fewAt = 1e9, unit, unitNote, gridLabel, leaveTo, leaveNote, counterNote, fewLabel, prefix = '₹'}) => {
  const f = useCurrentFrame();
  const cols = 10, rows = 8, cell = 52, gx = 66, gy = 300;
  const grid = f >= gridAt;
  const leave = (i: number) => (i % cols) >= cols / 2; // right half leaves
  const val = f >= countAt ? interpolate(f, [countAt, countAt + 40], [0, countTo], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)}) : 0;
  const land = f >= countAt + 40 ? 1 + 0.08 * Math.sin(Math.PI * Math.min(1, (f - countAt - 40) / 10)) : 1;
  return (
    <div style={{position: 'absolute', inset: 0}}>
      {/* one customer + tag */}
      {!grid && (
        <div style={{position: 'absolute', left: 330, top: 300, ...popIn(f, tagAt - 6)}}>
          <Person size={220} />
          {f >= tagAt && <div style={{position: 'absolute', left: 170, top: 10, ...popIn(f, tagAt)}}><span style={{fontFamily: inter, fontWeight: 900, fontSize: 64, color: C.white, background: C.orange, borderRadius: 14, padding: '6px 22px', border: '2px solid #fff', whiteSpace: 'nowrap'}}>{unit}</span></div>}
          {f >= tagAt + 8 && <div style={{position: 'absolute', left: -30, top: 250, width: 300, textAlign: 'center', fontFamily: inter, fontWeight: 700, fontSize: 30, color: 'rgba(255,255,255,.75)', ...enter(f, tagAt + 8)}}>{unitNote}</div>}
        </div>
      )}
      {grid && (
        <>
          {Array.from({length: cols * rows}).map((_, i) => {
            const c = i % cols, r = Math.floor(i / cols);
            const d = Math.hypot(c - 4.5, r - 3.5);
            const s = sp(f, gridAt + d * 2.2);
            const out = leave(i) && f >= leaveAt ? ease(f, leaveAt + (r % 4) * 3, leaveAt + 30 + (r % 4) * 3) : 0;
            return (
              <div key={i} style={{position: 'absolute', left: gx + c * cell * 1.06 + out * 340, top: gy + r * cell * 1.14, transform: `scale(${s})`, opacity: 1 - 0.65 * out}}>
                <Person size={cell} color={out > 0.3 ? C.dim : C.white} />
              </div>
            );
          })}
          <div style={{position: 'absolute', left: gx, top: 220, ...enter(f, gridAt + 6)}}><span style={{fontFamily: inter, fontWeight: 900, fontSize: 52, color: C.white}}>{gridLabel}</span></div>
          {f >= leaveAt && (
            <div style={{position: 'absolute', left: 760, top: 400, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, ...popIn(f, leaveAt + 10)}}>
              <div style={{width: 150, height: 210, boxSizing: 'border-box', background: C.white, borderRadius: 26, border: '3px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: inter, fontWeight: 900, fontSize: 30, color: C.ink, textAlign: 'center'}}>{leaveTo}</div>
              <span style={{fontFamily: inter, fontWeight: 800, fontSize: 30, color: 'rgba(255,255,255,.75)'}}>{leaveNote}</span>
            </div>
          )}
        </>
      )}
      {f >= countAt && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 790, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, ...enter(f, countAt, 1e9, 16)}}>
          <div style={{fontFamily: inter, fontWeight: 900, fontSize: 116, lineHeight: 1, color: C.orange, fontVariantNumeric: 'tabular-nums', transform: `scale(${land})`}}>{prefix}{inrFmt(val)}</div>
          <div style={{fontFamily: serif, fontStyle: 'italic', fontSize: 52, color: C.white}}>{counterNote}</div>
        </div>
      )}
      {fewLabel && f >= fewAt && (
        <div style={{position: 'absolute', right: 40, top: 40, ...popIn(f, fewAt)}}>
          <span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.ink, background: C.white, borderRadius: 999, padding: '8px 20px', border: `3px solid ${C.orange}`, whiteSpace: 'nowrap'}}>{fewLabel}</span>
        </div>
      )}
    </div>
  );
};
