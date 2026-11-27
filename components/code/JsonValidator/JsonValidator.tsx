// Spec: components/specs/JsonValidator.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';

/* ---------- JsonValidator ---------- */
export const JsonValidator: React.FC<{at: number; bad: string; good: string; rejectAt: number; rerunAt: number; passAt: number; gateLabel?: string; rerunLabel?: string}> = ({at, bad, good, rejectAt, rerunAt, passAt, gateLabel = 'valid JSON?', rerunLabel = 'rerun'}) => {
  const f = useCurrentFrame();
  const GX = 486, GY = 420;
  const badX = interpolate(ease(f, at + 4, at + 20), [0, 1], [-420, 40]) + ease(f, rejectAt - 14, rejectAt) * (GX - 340); // enters fast, waits, steps into the gate
  const fall = f >= rejectAt + 6 ? sp(f, rejectAt + 6, {damping: 14, stiffness: 120}) : 0;
  const goodX = interpolate(ease(f, passAt - 10, passAt + 14), [0, 1], [-420, GX + 26]);
  const card = (txt: string, torn: boolean) => (
    <div style={{position: 'relative', width: 430, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, padding: '18px 20px', fontFamily: mono, fontWeight: 600, fontSize: 25, color: C.text, whiteSpace: 'pre', clipPath: torn ? 'polygon(0 0,100% 0,96% 22%,100% 44%,95% 66%,100% 88%,97% 100%,0 100%)' : undefined}}>
      {txt}
    </div>
  );
  return (
    <div style={{position: 'absolute', inset: 0}}>
      {/* gate */}
      <div style={{position: 'absolute', left: GX - 10, top: GY - 170, ...popIn(f, at)}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: 16, height: 340, background: C.line, borderRadius: 8}} />
        <div style={{position: 'absolute', left: -150, top: -64, width: 316, textAlign: 'center', fontFamily: inter, fontWeight: 800, fontSize: 30, color: C.text}}>{gateLabel}</div>
        {f >= rejectAt && f < rerunAt && <div style={{position: 'absolute', left: -22, top: 140, ...popIn(f, rejectAt)}}><WarnMark size={60} /></div>}
        {f >= passAt + 12 && <div style={{position: 'absolute', left: -18, top: 140, ...popIn(f, passAt + 12)}}><TickMark size={56} /></div>}
      </div>
      {/* bin */}
      <svg style={{position: 'absolute', left: 120, top: 760, ...popIn(f, at + 6)}} width={190} height={180} viewBox="0 0 190 180" fill="none" stroke={C.line} strokeWidth={5} strokeLinejoin="round">
        <path d="M20 40h150l-16 132H36z" fill={C.surface} /><path d="M10 40h170M70 40V18h50v22" strokeLinecap="round" /><path d="M70 70v80M95 70v80M120 70v80" stroke={C.grid} />
      </svg>
      {f < rerunAt + 4 && (
        <div style={{position: 'absolute', left: badX, top: GY - 60 + fall * 330, transform: `rotate(${fall * -14}deg) scale(${1 - fall * 0.45})`, transformOrigin: 'center', opacity: 1 - ease(f, rerunAt - 6, rerunAt + 4)}}>
          {card(bad, true)}
        </div>
      )}
      {f >= rerunAt && (
        <div style={{position: 'absolute', left: goodX, top: GY - 60, ...enter(f, rerunAt, 1e9, 16)}}>
          <div style={{position: 'absolute', left: 0, top: -54}}><span style={{fontFamily: inter, fontWeight: 800, fontSize: 26, color: C.onAccent, background: C.accent, borderRadius: 999, padding: '6px 18px'}}>{rerunLabel}</span></div>
          {card(good, false)}
        </div>
      )}
    </div>
  );
};

