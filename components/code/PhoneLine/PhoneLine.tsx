// PhoneLine (components/specs/PhoneLine.md): a request as a phone call. App (phone) on the left, server on the right, one wire
// between them that draws, pulses (line open), goes silent, gets snipped and dangles; middleman "booths" (official logos) sit on
// the wire with limit pills, silence timers, scissors and locks. Geometry is fixed in the 972x970 scene space so every beat reuses
// the same drawing; only state props change. Compose: <AppTile/> <SrvTile/> <Wire/> <Booths/> (+ <Tap/> for screen taps).
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, accentA} from '../theme';
import {sp, pop, ease} from '../anim';
import {Logo} from '../glyphs';

const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const Ico: React.FC<{size?: number; color?: string; sw?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({size = 48, color = C.text, sw = 3, children, style}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0, overflow: 'visible', ...style}}>{children}</svg>
);
export const Scissors: React.FC<{size?: number; color?: string; close?: number}> = ({size = 44, color = C.text, close = 0}) => (
  <Ico size={size} color={color}>
    <g transform={`rotate(${-18 * (1 - close)} 24 24)`}><circle cx="11" cy="36" r="6" /><path d="M15.5 32 L40 10" /></g>
    <g transform={`rotate(${18 * (1 - close)} 24 24)`}><circle cx="11" cy="12" r="6" /><path d="M15.5 16 L40 38" /></g>
  </Ico>
);
export const ServerIco: React.FC<{size?: number; color?: string}> = ({size = 72, color = C.text}) => (
  <Ico size={size} color={color} sw={2.6}><rect x="8" y="6" width="32" height="14" rx="3" /><rect x="8" y="26" width="32" height="14" rx="3" /><circle cx="15" cy="13" r="1.8" fill={C.accent} stroke="none" /><circle cx="15" cy="33" r="1.8" fill={C.accent} stroke="none" /><path d="M22 13h12M22 33h12" /></Ico>
);
export const LockIco: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.text}) => (
  <Ico size={size} color={color} sw={3.4}><rect x="10" y="21" width="28" height="21" rx="4" fill={C.surface} /><path d="M16 21v-6a8 8 0 0 1 16 0v6" /><path d="M24 29v6" /></Ico>
);
/* ---------------- PhoneLine (specs/PhoneLine.md) ---------------- */
export const GEO = {app: {x: 46, y: 300, w: 184, h: 310}, srv: {x: 742, y: 335, w: 184, h: 230}, wy: 455, ax: 230, bx: 742, sag: 26, booths: [362, 486, 610]};
const cxw = (GEO.ax + GEO.bx) / 2;
export const wirePt = (t: number) => {
  const cy = GEO.wy + 2 * GEO.sag;
  return {x: GEO.ax + (GEO.bx - GEO.ax) * t, y: (1 - t) * (1 - t) * GEO.wy + 2 * (1 - t) * t * cy + t * t * GEO.wy};
};
export const tOfX = (x: number) => (x - GEO.ax) / (GEO.bx - GEO.ax);
const rot = (p: {x: number; y: number}, o: {x: number; y: number}, deg: number) => {
  const a = (deg * Math.PI) / 180, dx = p.x - o.x, dy = p.y - o.y;
  return {x: o.x + dx * Math.cos(a) - dy * Math.sin(a), y: o.y + dx * Math.sin(a) + dy * Math.cos(a)};
};
const seg = (t0: number, t1: number, pivot?: {x: number; y: number}, deg = 0) => {
  const pts = [];
  for (let i = 0; i <= 24; i++) {
    let p = wirePt(t0 + ((t1 - t0) * i) / 24);
    if (pivot && deg) p = rot(p, pivot, deg);
    pts.push(p);
  }
  return 'M' + pts.map((p) => `${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L');
};
const dangle = (t: number) => (t <= 0 ? 0 : 38 * (1 - Math.exp(-t / 10) * Math.cos(t * 0.42)));

/** booth on the wire: x (scene px), official logo file in icons/logos + its box, label, optional limit pill, silence timer, scissors, lock, badge */
export type Booth = {x: number; logo: string; lw: number; lh: number; label: string; at: number; limit?: string; limitAt?: number;
  timer?: {t0: number; t1: number; to: number; from?: number; hotAt?: number}; scissorsAt?: number; scissorsDimAt?: number; lockAt?: number; badge?: {at: number; text: string}; dimAt?: number};
export type Call = {drawAt: number; pulseTo?: number; silentAt?: number; closeAt?: number; snipAt?: number; snipX?: number; marks?: {x: number; at: number}[]; greyAt?: number};
export type Travel = {t0: number; t1: number; dir: 'up' | 'down'; node?: React.ReactNode; drop?: boolean};

const BoothTile: React.FC<{b: Booth}> = ({b}) => {
  const f = useCurrentFrame();
  if (f < b.at - 1) return null;
  const v = sp(f, b.at, {damping: 12, stiffness: 160});
  const y0 = GEO.wy - 48;
  const dim = b.dimAt !== undefined && f >= b.dimAt ? ease(f, b.dimAt, b.dimAt + 8) : 0;
  const tv = b.timer ? Math.round(interpolate(f, [b.timer.t0, b.timer.t1], [b.timer.from ?? 0, b.timer.to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)})) : 0;
  const hot = b.timer?.hotAt !== undefined && f >= b.timer.hotAt;
  const sc = b.scissorsAt !== undefined && f >= b.scissorsAt;
  const scDim = b.scissorsDimAt !== undefined && f >= b.scissorsDimAt;
  const lock = b.lockAt !== undefined && f >= b.lockAt;
  return (
    <div style={{position: 'absolute', left: b.x - 58, top: y0 + 6, width: 116, transform: `translateY(${(1 - v) * -70}px)`, opacity: Math.min(1, v * 1.6) * (1 - 0.45 * dim)}}>
      {/* limit / timer pill above */}
      {(b.timer && f >= b.timer.t0 - 1) || (b.limit && f >= (b.limitAt ?? 1e9)) ? (
        <div style={{position: 'absolute', left: 58, top: -62, transform: `translateX(-50%) scale(${b.timer ? 1 + (hot ? 0.12 * Math.sin(Math.PI * clamp01((f - b.timer.hotAt!) / 10)) : 0) : 0.8 + 0.2 * Math.min(1, pop(f, b.limitAt!))})`, opacity: b.timer ? Math.min(1, pop(f, b.timer.t0) * 1.5) : Math.min(1, pop(f, b.limitAt!) * 1.5)}}>
          <div style={{padding: '6px 14px', borderRadius: 99, border: BORDER, background: hot || (!b.timer && lock) ? C.accent : C.surface, color: hot || (!b.timer && lock) ? C.onAccent : C.text, fontFamily: mono, fontWeight: 700, fontSize: 26, whiteSpace: 'nowrap'}}>{b.timer ? `${tv} s` : b.limit}</div>
        </div>
      ) : null}
      <div style={{width: 116, height: 84, boxSizing: 'border-box', background: C.surface, border: lock ? `4px solid ${C.accent}` : BORDER, borderRadius: R, boxShadow: SHADOW, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <Logo file={b.logo} w={b.lw} h={b.lh} />
      </div>
      <div style={{position: 'absolute', left: 58, top: 92, transform: 'translateX(-50%)', fontFamily: inter, fontWeight: 700, fontSize: 22, color: C.text, whiteSpace: 'nowrap', background: C.bg, padding: '0 6px', borderRadius: 6}}>{b.label}</div>
      {sc && (
        <div style={{position: 'absolute', left: 88, top: -22, transform: `scale(${Math.min(1, pop(f, b.scissorsAt!) * 1.2)})`, background: C.surface, border: `2px solid ${scDim ? C.textDim : C.border}`, borderRadius: 99, padding: 4, opacity: scDim ? 0.55 : 1}}>
          <Scissors size={34} color={scDim ? C.textDim : C.text} />
        </div>
      )}
      {lock && (
        <div style={{position: 'absolute', left: -14, top: -22, transform: `scale(${Math.min(1, pop(f, b.lockAt!) * 1.2)})`}}><LockIco size={44} color={C.accent} /></div>
      )}
      {b.badge && f >= b.badge.at - 1 && (
        <div style={{position: 'absolute', left: 58, top: 128, transform: 'translateX(-50%)'}}><div style={{opacity: Math.min(1, pop(f, b.badge.at) * 1.5), transform: `scale(${0.8 + 0.2 * pop(f, b.badge.at)})`}}>
          <div style={{padding: '8px 16px', borderRadius: 99, border: BORDER, background: C.inkFill, color: C.onInk, fontFamily: inter, fontWeight: 800, fontSize: 24, whiteSpace: 'nowrap'}}>{b.badge.text}</div></div>
        </div>
      )}
    </div>
  );
};

/** the phone (app side); `screen` renders inside its screen area (172 x 250) */
export const AppTile: React.FC<{at: number; label?: string; screen?: React.ReactNode; dark?: number; ring?: boolean}> = ({at, label = 'App', screen, dark = 0, ring}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const v = sp(f, at);
  const {x, y, w, h} = GEO.app;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: Math.min(1, v * 1.5), transform: `scale(${0.85 + 0.15 * v})`}}>
      <div style={{position: 'absolute', inset: 0, borderRadius: 30, border: `${ring ? 5 : 4}px solid ${ring ? C.accent : C.border}`, background: C.inkFill, boxSizing: 'border-box', padding: 6, boxShadow: SHADOW}}>
        <div style={{position: 'relative', width: '100%', height: '100%', borderRadius: 22, overflow: 'hidden', background: C.bg}}>
          {screen}
          <div style={{position: 'absolute', inset: 0, background: C.inkFill, opacity: dark}} />
          <div style={{position: 'absolute', left: '50%', top: 6, width: 46, height: 10, borderRadius: 99, background: C.inkFill, transform: 'translateX(-50%)'}} />
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: h + 10, textAlign: 'center', fontFamily: inter, fontWeight: 800, fontSize: 28, color: C.text}}>{label}</div>
    </div>
  );
};

export const SrvTile: React.FC<{at: number; label?: string; glow?: number; dim?: number; children?: React.ReactNode; logos?: React.ReactNode}> = ({at, label = 'Server', glow = 0, dim = 0, children, logos}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const v = sp(f, at);
  const {x, y, w, h} = GEO.srv;
  const pulse = glow > 0 ? 0.5 + 0.5 * Math.sin(f / 5) : 0;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: Math.min(1, v * 1.5) * (1 - 0.5 * dim), transform: `scale(${0.85 + 0.15 * v})`}}>
      <div style={{position: 'absolute', inset: 0, borderRadius: R, border: glow > 0 ? `5px solid ${C.accent}` : BORDER, background: C.surface, boxSizing: 'border-box', boxShadow: glow > 0 ? `0 0 ${18 + 22 * pulse * glow}px ${accentA(0.35 * glow)}` : SHADOW, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 6}}>
        {logos ?? <ServerIco size={92} />}
        <div style={{fontFamily: inter, fontWeight: 800, fontSize: 30, color: C.text}}>{label}</div>
      </div>
      {children}
    </div>
  );
};

/** the wire: one Call at a time (the latest whose drawAt has passed), booths on it, travelling packets */
export const Wire: React.FC<{calls: Call[]; travels?: Travel[]}> = ({calls, travels = []}) => {
  const f = useCurrentFrame();
  let c: Call | undefined;
  for (const k of calls) if (f >= k.drawAt) c = k;
  const A = {x: GEO.ax, y: GEO.wy}, B = {x: GEO.bx, y: GEO.wy};
  const els: React.ReactNode[] = [];
  let tc = -1;
  if (c) {
    const p = ease(f, c.drawAt, c.drawAt + 12);
    const snipped = c.snipAt !== undefined && f >= c.snipAt;
    const grey = snipped || (c.greyAt !== undefined && f >= c.greyAt);
    const silent = c.silentAt !== undefined && f >= c.silentAt;
    const col = grey ? C.textDim : C.accent;
    const op = grey ? 0.9 : silent ? 0.45 : 1;
    if (c.closeAt !== undefined && f >= c.closeAt) {
      const q = ease(f, c.closeAt, c.closeAt + 12);
      if (q < 0.99) els.push(<path key="w" d={seg(q * 0.5, 1 - q * 0.5)} stroke={col} strokeWidth={7} fill="none" strokeLinecap="round" opacity={op * (1 - q)} />);
    } else if (snipped) {
      tc = tOfX(c.snipX!);
      const th = dangle(f - c.snipAt!);
      els.push(<path key="l" d={seg(0, tc - 0.012, A, th)} stroke={col} strokeWidth={7} fill="none" strokeLinecap="round" />);
      els.push(<path key="r" d={seg(tc + 0.012, 1, B, -th * 0.9)} stroke={col} strokeWidth={7} fill="none" strokeLinecap="round" />);
      const e1 = rot(wirePt(tc - 0.012), A, th), e2 = rot(wirePt(tc + 0.012), B, -th * 0.9);
      els.push(<circle key="e1" cx={e1.x} cy={e1.y} r={6} fill={C.textDim} />, <circle key="e2" cx={e2.x} cy={e2.y} r={6} fill={C.textDim} />);
      // snap flash
      const fl = 1 - ease(f, c.snipAt!, c.snipAt! + 10);
      if (fl > 0) els.push(<circle key="fl" cx={wirePt(tc).x} cy={wirePt(tc).y} r={18 + 30 * (1 - fl)} fill="none" stroke={C.accent} strokeWidth={5} opacity={fl} />);
    } else {
      els.push(<path key="w" d={seg(0, p)} stroke={col} strokeWidth={7} fill="none" strokeLinecap="round" opacity={op} />);
      const pulseEnd = Math.min(c.pulseTo ?? 1e9, c.silentAt ?? 1e9, c.closeAt ?? 1e9, c.snipAt ?? 1e9, c.greyAt ?? 1e9);
      if (f >= c.drawAt + 8 && f < pulseEnd) for (let k = 0; k < 4; k++) {
        const t = (((f - c.drawAt) * 0.03 + k / 4) % 1) * p;
        const pt = wirePt(t);
        els.push(<circle key={`d${k}`} cx={pt.x} cy={pt.y} r={8} fill={C.accent} stroke={C.border} strokeWidth={2} />);
      }
    }
    for (const m of c.marks ?? []) if (f >= m.at) {
      const pt = wirePt(tOfX(m.x));
      els.push(<g key={`m${m.at}`} opacity={Math.min(1, pop(f, m.at) * 1.4)}><circle cx={pt.x} cy={pt.y} r={16} fill={C.bg} /><path d={`M${pt.x - 12} ${pt.y - 12} L${pt.x + 12} ${pt.y + 12} M${pt.x + 12} ${pt.y - 12} L${pt.x - 12} ${pt.y + 12}`} stroke={C.accent} strokeWidth={6} strokeLinecap="round" /></g>);
    }
  }
  return (
    <>
      <svg width={972} height={970} viewBox="0 0 972 970" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>{els}</svg>
      {travels.map((tr, i) => <TravelEl key={i} tr={tr} tc={tc} />)}
    </>
  );
};

const TravelEl: React.FC<{tr: Travel; tc: number}> = ({tr, tc}) => {
  const f = useCurrentFrame();
  if (f < tr.t0 || f > tr.t1 + 40) return null;
  const node = tr.node ?? <div style={{width: 30, height: 30, borderRadius: 99, background: C.accent, border: BORDER}} />;
  let pt: {x: number; y: number}, o = 1, grey = 0, r = 0;
  if (tr.dir === 'down' && tr.drop && tc > 0) {
    const tEnd = tr.t0 + (tr.t1 - tr.t0) * (1 - tc);
    const p = ease(f, tr.t0, tEnd);
    const t = 1 - (1 - tc) * p;
    pt = wirePt(Math.max(tc, t));
    if (f > tEnd) {
      const dt = f - tEnd;
      pt = {x: pt.x - dt * 1.2, y: pt.y + 0.55 * dt * dt};
      grey = ease(f, tEnd, tEnd + 14);
      o = ease(f, tEnd + 18, tEnd + 34, 1, 0);
      r = dt * 1.6;
    }
  } else {
    const p = ease(f, tr.t0, tr.t1);
    pt = wirePt(tr.dir === 'up' ? p : 1 - p);
    o = ease(f, tr.t1, tr.t1 + 6, 1, 0);
  }
  return (
    <div style={{position: 'absolute', left: pt.x, top: pt.y, transform: `translate(-50%,-50%) rotate(${r}deg)`, opacity: o, filter: grey > 0 ? `grayscale(${grey})` : undefined}}>{node}</div>
  );
};

export const Booths: React.FC<{booths: Booth[]}> = ({booths}) => <>{booths.map((b, i) => <BoothTile key={i} b={b} />)}</>;

/** tap ripple on a point */
export const Tap: React.FC<{x: number; y: number; at: number}> = ({x, y, at}) => {
  const f = useCurrentFrame();
  if (f < at - 2 || f > at + 18) return null;
  const p = ease(f, at, at + 16);
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)'}}>
      <div style={{width: 30 + 70 * p, height: 30 + 70 * p, borderRadius: 99, border: `5px solid ${C.accent}`, opacity: 1 - p, transform: 'translate(-50%,-50%)', position: 'absolute', left: 0, top: 0}} />
      <div style={{width: 26, height: 26, borderRadius: 99, background: C.accent, opacity: 1 - p, transform: 'translate(-50%,-50%)', position: 'absolute', left: 0, top: 0}} />
    </div>
  );
};

