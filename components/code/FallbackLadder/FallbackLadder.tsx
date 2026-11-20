// Spec: components/specs/FallbackLadder.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';
const inOut = Easing.inOut(Easing.cubic);
/* ---------- FallbackLadder ---------- */
export type Rung = {label: React.ReactNode; sub: React.ReactNode; logos?: LogoRef[]; icon?: React.ReactNode; at: number; human?: boolean; failAt?: number};
export const FallbackLadder: React.FC<{rungs: Rung[]; dropAt: number; landAt: number; x?: number; y?: number; w?: number; rh?: number; gap?: number}> = ({rungs, dropAt, landAt, x = 160, y = 40, w = 740, rh = 150, gap = 34}) => {
  const f = useCurrentFrame();
  const ys = rungs.map((_, i) => y + i * (rh + gap));
  // packet: drops rung to rung between dropAt and landAt, pausing on each failing rung
  const n = rungs.length;
  const seg = (landAt - dropAt) / (n - 1);
  const k = Math.max(0, Math.min(n - 1, (f - dropAt) / seg));
  const ki = Math.floor(k), kf = k - ki;
  const py = ys[ki] + rh / 2 + (ki < n - 1 ? inOut(Math.min(1, kf * 1.6)) * (ys[ki + 1] - ys[ki]) : 0);
  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div style={{position: 'absolute', left: x - 72, top: ys[0] + rh / 2, width: 6, height: (ys[n - 1] - ys[0]) * ease(f, rungs[0].at, rungs[n - 1].at + 10), background: C.border, borderRadius: 3}} />
      {rungs.map((r, i) => {
        const failed = r.failAt !== undefined && f >= r.failAt;
        const active = i === n - 1 ? f >= landAt : false;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: ys[i], ...enter(f, r.at, 1e9, 20)}}>
            <div style={{position: 'absolute', left: -96, top: rh / 2 - 22, width: 44, height: 44, borderRadius: 99, background: C.white, border: BORDER, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: inter, fontWeight: 900, fontSize: 24, color: C.ink}}>{i + 1}</div>
            <ProviderNode w={w} h={rh} icon={r.icon} logos={r.logos} label={r.label} sub={r.sub} dim={failed ? ease(f, r.failAt!, r.failAt! + 8) : 0} ring={active ? sp(f, landAt) : 0}
              badge={failed ? <div style={popIn(f, r.failAt!)}><XMark size={48} /></div> : active ? <div style={popIn(f, landAt + 4)}><TickMark size={52} /></div> : undefined} />
          </div>
        );
      })}
      {f >= dropAt && f <= landAt + 6 && <div style={{position: 'absolute', left: x - 87, top: py - 18, width: 36, height: 36, borderRadius: 10, background: C.orange, border: BORDER}} />}
    </div>
  );
};

