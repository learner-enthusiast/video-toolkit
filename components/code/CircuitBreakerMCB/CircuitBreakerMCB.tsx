// Spec: components/specs/CircuitBreakerMCB.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';

/* ---------- CircuitBreakerMCB ---------- */
export const CircuitBreakerMCB: React.FC<{at: number; tripAt: number; failAts: number[]; w?: number}> = ({at, tripAt, failAts, w = 170}) => {
  const f = useCurrentFrame();
  const h = w * 1.55;
  const trip = f >= tripAt ? sp(f, tripAt, {damping: 9, stiffness: 160}) : 0;
  const leverY = interpolate(trip, [0, 1], [h * 0.22, h * 0.56]);
  return (
    <div style={{position: 'relative', width: w, height: h + 70, ...popIn(f, at)}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: w, height: h, boxSizing: 'border-box', background: C.white, border: `3px solid ${C.border}`, borderRadius: 18, boxShadow: SHADOW}}>
        <div style={{position: 'absolute', left: w * 0.32, top: h * 0.14, width: w * 0.36, height: h * 0.66, borderRadius: 12, background: '#EEEAE3', border: BORDER}} />
        <div style={{position: 'absolute', left: w * 0.24, top: leverY, width: w * 0.52, height: h * 0.2, borderRadius: 10, background: trip > 0.5 ? C.dim : C.border, boxShadow: '0 4px 0 rgba(0,0,0,.25)'}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: h * 0.02, textAlign: 'center', fontFamily: mono, fontWeight: 700, fontSize: w * 0.11, color: C.ink}}>ON</div>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: h * 0.02, textAlign: 'center', fontFamily: mono, fontWeight: 700, fontSize: w * 0.11, color: trip > 0.5 ? C.orange : C.dim}}>OFF</div>
        <div style={{position: 'absolute', right: 12, top: 12, width: 18, height: 18, borderRadius: 4, background: trip > 0.5 ? C.dim : C.orange}} />
      </div>
      <div style={{position: 'absolute', left: 0, top: h + 14, width: w, display: 'flex', justifyContent: 'center', gap: 8}}>
        {failAts.map((t, i) => f >= t ? <div key={i} style={popIn(f, t)}><XMark size={44} /></div> : null)}
      </div>
    </div>
  );
};

