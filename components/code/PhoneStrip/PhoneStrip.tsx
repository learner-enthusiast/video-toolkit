// Spec: components/specs/PhoneStrip.md · first built for system-design-of-ai/06-cancellation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, pop, ease, popIn} from '../anim';
import {Tag} from '../Tag/Tag';
import {ChipGlyph, DarkCtx, ServerGlyph, UserGlyph, HandsetGlyph} from '../glyphs';

const mix = (a: string, b: string, t: number) => {
  const p = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const A = p(a), B = p(b);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * t)).join(',')})`;
};

export type PSCall = {label: string; at: number; deadAt?: number; hangAt?: number};
export type PSFlow = {call: 0 | 1; dir: 1 | -1; from: number; to: number};
export type PSNode = {label: string; icon: 'user' | 'server' | 'model'; at?: number};
export const PhoneStrip: React.FC<{w?: number; compact?: boolean; nodes?: PSNode[]; calls: [PSCall, PSCall]; flow?: PSFlow[]; at: number; out?: number; slot?: {at: number; label: string; fillAt?: number; fillLabel?: string; out?: number}}> = ({
  w = 972, compact, nodes = [{label: 'User', icon: 'user'}, {label: 'Server', icon: 'server'}, {label: 'Model', icon: 'model'}], calls, flow = [], at, out = 1e9, slot,
}) => {
  const f = useCurrentFrame();
  const dark = React.useContext(DarkCtx);
  if (f < at - 1) return null;
  const s = compact ? 124 : 176;
  const cx = [w * 0.13, w * 0.5, w * 0.87];
  const cy = s / 2;
  const o = ease(f, out - 8, out, 1, 0);
  const ink = dark ? C.onPunch : C.text;
  const callState = (c: PSCall) => {
    const cp = ease(f, c.at, c.at + 12);
    const dp = c.deadAt !== undefined ? ease(f, c.deadAt, c.deadAt + 8) : 0;
    const hp = c.hangAt !== undefined && f >= c.hangAt ? sp(f, c.hangAt, {damping: 9, stiffness: 160}) : 0;
    return {cp, dp: Math.max(dp, c.hangAt !== undefined ? ease(f, c.hangAt, c.hangAt + 8) : 0), hp};
  };
  const cord = (i: 0 | 1) => {
    const x1 = cx[i] + s / 2 + 12, x2 = cx[i + 1] - s / 2 - 12;
    return {x1, x2};
  };
  const wave = (x1: number, x2: number, amp: number) => {
    const pts: string[] = [];
    for (let k = 0; k <= 40; k++) { const x = x1 + ((x2 - x1) * k) / 40; pts.push(`${k === 0 ? 'M' : 'L'}${x.toFixed(1)} ${(cy + amp * Math.sin((k / 40) * Math.PI * 6)).toFixed(1)}`); }
    return pts.join(' ');
  };
  const len = (x1: number, x2: number) => (x2 - x1) * 1.25;
  return (
    <div style={{position: 'relative', width: w, height: s + (compact ? 52 : 64), opacity: o}}>
      <svg width={w} height={s + 60} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {calls.map((c, i) => {
          const {x1, x2} = cord(i as 0 | 1);
          const st = callState(c);
          if (f < c.at - 1) return null;
          const col = mix(C.accent, C.textDim, st.dp);
          const L = len(x1, x2);
          return (
            <path key={i} d={wave(x1, x2, compact ? 5 : 7)} fill="none" stroke={col} strokeWidth={compact ? 5 : 6} strokeLinecap="round"
              strokeDasharray={st.dp > 0.5 ? '10 12' : `${L} ${L}`} strokeDashoffset={st.dp > 0.5 ? 0 : L * (1 - st.cp)} />
          );
        })}
        {/* packets along live calls */}
        {flow.map((fl, k) => {
          const c = calls[fl.call];
          const {x1, x2} = cord(fl.call);
          const dots: React.ReactNode[] = [];
          for (let t0 = fl.from; t0 <= fl.to; t0 += 6) {
            const u = (f - t0) / 18;
            if (u < 0 || u > 1) continue;
            const dead = c.deadAt !== undefined ? c.deadAt : c.hangAt;
            if (dead !== undefined && t0 >= dead) continue;
            const e = Easing.inOut(Easing.cubic)(u);
            const x = fl.dir === 1 ? x1 + (x2 - x1) * e : x2 - (x2 - x1) * e;
            const y = cy + (compact ? 5 : 7) * Math.sin(((x - x1) / (x2 - x1)) * Math.PI * 6);
            dots.push(<circle key={`${k}-${t0}`} cx={x} cy={y} r={compact ? 8 : 10} fill={C.accent} stroke={C.border} strokeWidth={2} />);
          }
          return dots;
        })}
      </svg>
      {/* handsets + call labels */}
      {calls.map((c, i) => {
        if (f < c.at - 1) return null;
        const {x1, x2} = cord(i as 0 | 1);
        const st = callState(c);
        const mx = (x1 + x2) / 2;
        const hs = compact ? 40 : 54;
        const col = mix(C.accent, C.fade, st.dp);
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: mx - hs / 2, top: cy - hs / 2 - 2, transform: `translate(${st.hp * 8}px, ${-st.hp * 26 + Math.max(0, st.hp - 0.6) * 40}px) rotate(${-38 * st.hp}deg) scale(${pop(f, c.at + 6)})`}}>
              <HandsetGlyph size={hs} color={col} />
            </div>
            <div style={{position: 'absolute', left: mx, top: cy + (compact ? 28 : 40), transform: 'translateX(-50%)'}}>
              <div style={popIn(f, c.at + 4)}><Tag label={c.label} tone={st.dp > 0.5 ? 'dim' : 'orange'} size={compact ? 20 : 24} /></div>
            </div>
          </React.Fragment>
        );
      })}
      {/* nodes */}
      {nodes.map((n, i) => {
        const a = n.at ?? at + i * 5;
        if (f < a - 1) return null;
        const v = pop(f, a);
        const ic = Math.round(s * 0.5);
        return (
          <div key={i} style={{position: 'absolute', left: cx[i] - s / 2, top: 0, width: s, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, opacity: Math.min(1, v * 1.5), transform: `scale(${0.8 + 0.2 * v})`}}>
            <div style={{width: s, height: s, boxSizing: 'border-box', borderRadius: R, border: BORDER, background: C.surface, boxShadow: dark ? 'none' : SHADOW, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              {n.icon === 'user' ? <UserGlyph size={ic} /> : n.icon === 'server' ? <ServerGlyph size={ic} /> : <ChipGlyph size={ic} big />}
            </div>
            <div style={{fontFamily: inter, fontWeight: 800, fontSize: compact ? 24 : 30, color: ink, whiteSpace: 'nowrap'}}>{n.label}</div>
          </div>
        );
      })}
      {/* "your code" slot under the server */}
      {slot && f >= slot.at - 1 && (() => {
        const filled = slot.fillAt !== undefined && f >= slot.fillAt;
        const fv = filled ? pop(f, slot.fillAt!) : 0;
        const so = ease(f, (slot.out ?? 1e9) - 8, slot.out ?? 1e9, 1, 0);
        return (
          <div style={{position: 'absolute', left: cx[1], top: s + (compact ? 44 : 54), transform: 'translateX(-50%)', opacity: so}}>
            <div style={popIn(f, slot.at)}><div style={{transform: `scale(${filled ? 0.9 + 0.1 * fv : 1})`, padding: compact ? '6px 16px' : '8px 20px', borderRadius: 999, border: `3px ${filled ? 'solid' : 'dashed'} ${C.accent}`, background: filled ? C.accent : 'transparent', color: filled ? C.onAccent : C.accent, fontFamily: mono, fontWeight: 700, fontSize: compact ? 22 : 28, whiteSpace: 'nowrap'}}>
              {filled ? slot.fillLabel ?? slot.label : slot.label}
            </div></div>
          </div>
        );
      })()}
    </div>
  );
};
