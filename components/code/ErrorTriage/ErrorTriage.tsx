// Spec: components/specs/ErrorTriage.md
import React from 'react';
import {useCurrentFrame, random, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, pop, ease, enter, popIn, tween, shake} from '../anim';
import {XMark, TickMark, WarnMark} from '../glyphs';
import {ProviderNode, Packet, LogoRef} from '../ProviderNode/ProviderNode';

/* ---------- ErrorTriage ---------- */
export type TriageItem = {code: string; lane: 0 | 1; at: number};
export const ErrorTriage: React.FC<{at: number; items: TriageItem[]; lanes: {label: string; note?: React.ReactNode; tone: 'orange' | 'dim'; at: number}[]; kicker?: string; title?: string}> = ({at, items, lanes, kicker = 'ERROR?', title = 'classify'}) => {
  const f = useCurrentFrame();
  const LX = [70, 520], LW = 400, LY = 420, LH = 470;
  const SX = 330, SY = 60;
  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div style={{position: 'absolute', left: SX, top: SY, width: 312, height: 150, boxSizing: 'border-box', background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', ...popIn(f, at)}}>
        <div style={{fontFamily: inter, fontWeight: 800, fontSize: 24, letterSpacing: '0.12em', color: C.dim}}>{kicker}</div>
        <div style={{fontFamily: serif, fontStyle: 'italic', fontSize: 58, color: C.orange, lineHeight: 1}}>{title}</div>
      </div>
      {lanes.map((l, i) => (
        <div key={i} style={{position: 'absolute', left: LX[i], top: LY, width: LW, height: LH, boxSizing: 'border-box', borderRadius: R, border: `3px ${l.tone === 'orange' ? 'solid' : 'dashed'} ${l.tone === 'orange' ? C.orange : C.dim}`, background: l.tone === 'orange' ? 'rgba(228,87,46,.07)' : 'rgba(138,133,124,.08)', ...enter(f, l.at, 1e9, 20)}}>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 22, textAlign: 'center', fontFamily: inter, fontWeight: 900, fontSize: 36, color: l.tone === 'orange' ? C.orange : C.dim}}>{l.label}</div>
          {l.note && <div style={{position: 'absolute', left: 0, right: 0, bottom: 76, display: 'flex', justifyContent: 'center'}}>{l.note}</div>}
        </div>
      ))}
      {items.map((it, i) => {
        if (f < it.at) return null;
        const drop = ease(f, it.at + 10, it.at + 34);
        const slot = items.filter((x, j) => j < i && x.lane === it.lane).length;
        const x = interpolate(drop, [0, 1], [SX + 156, LX[it.lane] + LW / 2]);
        const y = interpolate(drop, [0, 1], [SY + 75, LY + 60 + slot * 82]);
        const orange = it.lane === 0;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, transform: `translateX(-50%) scale(${pop(f, it.at)})`}}>
            <div style={{fontFamily: mono, fontWeight: 700, fontSize: 40, padding: '8px 22px', borderRadius: 999, border: BORDER, background: orange ? C.orange : C.white, color: orange ? C.white : C.dim, whiteSpace: 'nowrap'}}>{it.code}</div>
          </div>
        );
      })}
    </div>
  );
};

