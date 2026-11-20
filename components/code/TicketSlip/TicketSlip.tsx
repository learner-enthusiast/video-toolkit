// TicketSlip (components/specs/TicketSlip.md): an orange paper ticket for an async job ID. TicketArt is the static slip;
// TicketSlip positions it and pops it in, optionally morphing from a mono JSON box (`morphFrom`) and docking small (`dock`).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, whiteA} from '../theme';
import {sp, pop, ease} from '../anim';

/* ---------------- TicketSlip ---------------- */
export const TicketArt: React.FC<{w?: number; id: string; label?: string; sub?: string; dim?: boolean; shadow?: boolean}> = ({w = 300, id, label = 'TICKET', sub, dim, shadow = true}) => {
  const h = w * 0.5;
  const bg = dim ? C.dim : C.orange;
  return (
    <div style={{position: 'relative', width: w, height: h, borderRadius: R, background: bg, border: BORDER, boxSizing: 'border-box', boxShadow: shadow ? SHADOW : 'none', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: -h * 0.12, top: h / 2 - h * 0.12, width: h * 0.24, height: h * 0.24, borderRadius: 99, background: C.bg, border: BORDER}} />
      <div style={{position: 'absolute', right: -h * 0.12, top: h / 2 - h * 0.12, width: h * 0.24, height: h * 0.24, borderRadius: 99, background: C.bg, border: BORDER}} />
      <div style={{position: 'absolute', left: w * 0.27, top: h * 0.1, bottom: h * 0.1, borderLeft: `${Math.max(2, w / 150)}px dashed ${whiteA(0.8)}`}} />
      <div style={{position: 'absolute', left: w * 0.05, top: 0, bottom: 0, width: w * 0.2, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: 'rotate(-90deg)', fontFamily: inter, fontWeight: 800, fontSize: w * 0.06, letterSpacing: '0.16em', color: whiteA(0.9)}}>{label}</div>
      </div>
      <div style={{position: 'absolute', left: w * 0.3, right: w * 0.06, top: 0, bottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: h * 0.03}}>
        <div style={{fontFamily: inter, fontWeight: 900, fontSize: w * 0.2, color: C.white, lineHeight: 1}}>{id}</div>
        {sub && <div style={{fontFamily: mono, fontWeight: 700, fontSize: w * 0.065, color: whiteA(0.92)}}>{sub}</div>}
      </div>
    </div>
  );
};
/** positioned TicketSlip: pops in at `at` (or morphs from a JSON box), optional dock (spring to a smaller resting place) */
export const TicketSlip: React.FC<{x: number; y: number; w?: number; id: string; at: number; out?: number; sub?: string; morphFrom?: {text: string; at: number}; dock?: {x: number; y: number; scale: number; at: number}; dim?: number}> = ({x, y, w = 300, id, at, out = 1e9, sub, morphFrom, dock, dim = -1}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 2) return null;
  const o = ease(f, out - 8, out, 1, 0);
  const m = morphFrom ? sp(f, morphFrom.at, {damping: 15, stiffness: 150}) : 1;
  const v = morphFrom ? 1 : pop(f, at);
  const d = dock ? sp(f, dock.at, {damping: 16, stiffness: 120}) : 0;
  const cx = x + (dock ? (dock.x - x) * d : 0), cy = y + (dock ? (dock.y - y) * d : 0);
  const sc = (0.7 + 0.3 * Math.min(1, v)) * (dock ? 1 + (dock.scale - 1) * d : 1);
  const rot = morphFrom ? -3 * m : -3 + 9 * (1 - Math.min(1, v));
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%,-50%) scale(${sc}) rotate(${rot}deg)`, opacity: o * Math.min(1, (morphFrom ? 1 : v) * 1.5)}}>
      {morphFrom && m < 0.98 && (
        <div style={{position: 'absolute', left: '50%', top: '50%', transform: `translate(-50%,-50%) scale(${1 - 0.3 * m})`, opacity: 1 - m, background: C.white, border: BORDER, borderRadius: R, padding: '14px 22px', fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.ink, whiteSpace: 'nowrap'}}>{morphFrom.text}</div>
      )}
      <div style={{opacity: m, transform: `scale(${0.6 + 0.4 * m})`}}><TicketArt w={w} id={id} sub={sub} dim={dim >= 0 && f >= dim} /></div>
    </div>
  );
};

