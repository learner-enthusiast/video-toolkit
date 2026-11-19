// Spec: components/specs/RoutingLadder.md · requests fall through numbered rungs and land in a "small" or "big" lane.
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, orangeA, inter, mono} from '../theme';
import {sp, ease, popIn} from '../anim';
import {PRGlyph, ChipGlyph} from '../glyphs';
import {MiniPR} from '../PullRequestCard/PullRequestCard';

export type Rung = {label: string; sub: string; at: number};
export type Drop = {at: number; land: number; label: string; lane: 'small' | 'big'; rung: number};
/** geometry inside the grid card (px); pass `layout` to change it */
export const LADDER = {x: 30, w: 912, top: 72, rh: 84, gap: 14, laneY: 488, laneH: 92};
type Layout = typeof LADDER;

export const RoutingLadder: React.FC<{
  frameAt: number; // when the empty ladder draws in
  rungs: Rung[]; // one rung per entry, built at rung.at
  active: {at: number; i: number}[]; // which rung is lit from each frame
  drops: Drop[]; // requests that fall, flash their deciding rung, then slide into a lane
  lanes?: {small: string; big: string}; // lane names
  prices?: {small?: string; big?: string}; // resting lane tags; replaced by laneNote once it appears
  laneNote?: {at: number; small: string; big: string};
  intake?: string; // label on the intake slot
  out?: number;
  layout?: Layout;
}> = ({frameAt, rungs, active, drops, lanes = {small: 'Small model', big: 'Big model'}, prices, laneNote, intake = 'request in', out = 1e9, layout = LADDER}) => {
  const f = useCurrentFrame();
  const L = layout;
  const rungY = (i: number) => L.top + i * (L.rh + L.gap);
  const laneW = L.w / 2 - 10;
  const laneX = (lane: 'small' | 'big') => (lane === 'small' ? L.x : L.x + L.w / 2 + 10);
  const fr = ease(f, frameAt, frameAt + 14);
  const act = [...active].reverse().find((a) => f >= a.at)?.i ?? -1;
  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div style={{position: 'absolute', left: L.x + L.w / 2 - 150, top: 6, width: 300, height: 52, borderRadius: 999, border: `3px dashed ${C.dim}`, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, opacity: fr, fontFamily: inter, fontWeight: 800, fontSize: 26, letterSpacing: '0.12em', textTransform: 'uppercase', color: C.dim}}>
        <PRGlyph size={30} color={C.dim} /> {intake}
      </div>
      {rungs.map((r, i) => {
        const built = f >= r.at;
        const v = built ? sp(f, r.at) : 0;
        const on = act === i;
        return (
          <div key={i} style={{position: 'absolute', left: L.x, top: rungY(i), width: L.w, height: L.rh}}>
            <div style={{position: 'absolute', inset: 0, borderRadius: R, border: `3px dashed ${C.grid}`, opacity: fr * (1 - v)}} />
            {built && (
              <div style={{position: 'absolute', inset: 0, boxSizing: 'border-box', borderRadius: R, background: C.white, border: on ? `5px solid ${C.orange}` : BORDER, boxShadow: SHADOW, display: 'flex', alignItems: 'center', gap: 20, padding: '0 22px', opacity: Math.min(1, v * 1.4), transform: `scale(${0.9 + 0.1 * v})`}}>
                <div style={{width: 50, height: 50, borderRadius: 99, flexShrink: 0, background: on ? C.orange : C.ink, color: C.white, fontFamily: inter, fontWeight: 900, fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i + 1}</div>
                <span style={{fontFamily: inter, fontWeight: 900, fontSize: 46, color: on ? C.orange : C.ink, whiteSpace: 'nowrap'}}>{r.label}</span>
                <span style={{flex: 1}} />
                <span style={{fontFamily: mono, fontWeight: 600, fontSize: 30, color: C.dim, whiteSpace: 'nowrap'}}>{r.sub}</span>
              </div>
            )}
          </div>
        );
      })}
      {(['small', 'big'] as const).map((lane) => {
        const big = lane === 'big';
        const hits = drops.filter((d) => d.lane === lane && f >= d.land + 6).length;
        const price = prices?.[lane];
        return (
          <div key={lane} style={{position: 'absolute', left: laneX(lane), top: L.laneY, width: laneW, height: L.laneH, boxSizing: 'border-box', borderRadius: R, border: `${big ? 5 : 3}px solid ${big ? C.orange : C.border}`, background: big ? orangeA(0.07) : C.white, display: 'flex', alignItems: 'center', gap: 12, padding: '0 18px', opacity: fr}}>
            <ChipGlyph size={46} big={big} />
            <span style={{fontFamily: inter, fontWeight: 900, fontSize: 36, color: big ? C.orange : C.ink, whiteSpace: 'nowrap'}}>{lanes[lane]}</span>
            <span style={{flex: 1}} />
            {laneNote && f >= laneNote.at - 1 ? (
              <span style={{...popIn(f, laneNote.at + (big ? 6 : 0)), fontFamily: inter, fontWeight: 900, fontSize: 38, color: big ? C.orange : C.ink, whiteSpace: 'nowrap', flexShrink: 0}}>{laneNote[lane]}</span>
            ) : (
              (price || hits > 0) && <span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.dim, whiteSpace: 'nowrap', flexShrink: 0}}>{price ?? ''}{hits ? `${price ? ' · ' : ''}${hits}` : ''}</span>
            )}
          </div>
        );
      })}
      {drops.map((d, k) => {
        if (f < d.at || f > out) return null;
        const yR = rungY(d.rung) + L.rh / 2;
        const yL = L.laneY + L.laneH / 2;
        const mid = d.at + Math.max(8, Math.round((d.land - d.at) * 0.55));
        const p1 = interpolate(f, [d.at, mid], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});
        const p2 = interpolate(f, [mid + 4, d.land], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
        const cx = L.x + L.w / 2, lx = laneX(d.lane) + laneW / 2 + (d.lane === 'small' ? 70 : -70);
        const x = cx + (lx - cx) * p2;
        const y = 30 + (yR - 30) * p1 + (yL - yR) * p2;
        const settle = f > d.land ? ease(f, d.land + 6, d.land + 16, 1, 0) : 1;
        const lit = f >= mid && f < mid + 10;
        return (
          <React.Fragment key={k}>
            {lit && <div style={{position: 'absolute', left: L.x - 6, top: rungY(d.rung) - 6, width: L.w + 12, height: L.rh + 12, borderRadius: R + 4, border: `4px solid ${C.orange}`, opacity: 1 - (f - mid) / 10}} />}
            <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${0.9 + 0.1 * settle})`, opacity: settle}}>
              <MiniPR label={d.label} tone={p2 > 0.5 && d.lane === 'big' ? 'orange' : 'ink'} />
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};
