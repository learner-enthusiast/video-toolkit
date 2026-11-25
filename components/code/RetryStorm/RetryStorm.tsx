// Spec: components/specs/RetryStorm.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';

/* ---------- RetryStorm ---------- */
const CL = {cols: 3, rows: 6, x0: 70, y0: 150, dx: 92, dy: 112};
export const STORM_NODE = {x: 700, y: 380, w: 230, h: 220};
export const RetryStorm: React.FC<{at: number; out: number; scatterAt?: number; waveEvery?: number; waves?: number; nodeLogo: LogoRef; nodeLabel: string; dimEnd?: number}> = ({at, out, scatterAt = 1e9, waveEvery = 22, waves = 99, nodeLogo, nodeLabel, dimEnd}) => {
  const f = useCurrentFrame();
  const clients = Array.from({length: CL.cols * CL.rows}, (_, i) => ({x: CL.x0 + (i % CL.cols) * CL.dx, y: CL.y0 + Math.floor(i / CL.cols) * CL.dy, i}));
  const tx = STORM_NODE.x + 20, ty = STORM_NODE.y + STORM_NODE.h / 2;
  const travel = 26;
  const pk: React.ReactNode[] = [];
  let hits = 0;
  // lockstep waves
  for (let w = 0; w < waves; w++) {
    const t0 = at + 10 + w * waveEvery;
    if (t0 >= Math.min(scatterAt, out)) break;
    if (f >= t0 + travel) hits++;
    clients.forEach((c) => pk.push(<Packet key={`w${w}-${c.i}`} x1={c.x + 40} y1={c.y + 30} x2={tx} y2={ty + (c.i - 9) * 6} t0={t0} t1={t0 + travel} size={22} />));
  }
  // jitter: same clients, seeded random start, spread out
  if (scatterAt < out) {
    clients.forEach((c) => {
      for (let k = 0; k < 2; k++) {
        const t0 = scatterAt + 6 + Math.round(random(`jit-${c.i}-${k}`) * 70) + k * 40;
        pk.push(<Packet key={`j${k}-${c.i}`} x1={c.x + 40} y1={c.y + 30} x2={tx} y2={ty + (c.i - 9) * 6} t0={t0} t1={t0 + travel + 6} size={22} />);
      }
    });
  }
  const lastHit = at + 10 + Math.max(0, hits - 1) * waveEvery + travel;
  const dim = scatterAt < 1e9 && f >= scatterAt ? Math.max(0, Math.min(0.6, hits * 0.12) - ease(f, scatterAt, scatterAt + 30) * 0.6) : Math.min(0.75, hits * 0.13 + (dimEnd !== undefined && f >= dimEnd ? ease(f, dimEnd, dimEnd + 12) * 0.25 : 0));
  return (
    <div style={{position: 'absolute', inset: 0}}>
      {clients.map((c) => (
        <div key={c.i} style={{position: 'absolute', left: c.x, top: c.y, ...enter(f, at + (c.i % 6) * 2, 1e9, 16)}}>
          <svg width={64} height={64} viewBox="0 0 48 48" fill="none" stroke={C.ink} strokeWidth={3}><rect x="14" y="4" width="20" height="40" rx="5" fill={C.white} /><path d="M21 38h6" strokeLinecap="round" /></svg>
        </div>
      ))}
      {pk}
      <div style={{position: 'absolute', left: STORM_NODE.x, top: STORM_NODE.y, ...popIn(f, at)}}>
        <div style={{transform: `translateX(${shake(f, lastHit - 1, 9)}px)`}}>
          <ProviderNode w={STORM_NODE.w} h={STORM_NODE.h} logo={nodeLogo} label={nodeLabel} dim={dim} style={{flexDirection: 'column', justifyContent: 'center', padding: 14, gap: 10}} />
        </div>
      </div>
    </div>
  );
};

