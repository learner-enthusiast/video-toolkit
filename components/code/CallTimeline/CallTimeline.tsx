// Spec: components/specs/CallTimeline.md · first built for system-design-of-ai/06-cancellation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, ease, popIn, bump} from '../anim';
import {Tag} from '../Tag/Tag';
import {WarnMark} from '../glyphs';

export const CallTimeline: React.FC<{
  w?: number; seconds: number; leaveAt: number; run: {start: number; leave: number; end: number}; stopAt: number; tokRate: number;
  money?: {perTok: number; prefix: string}; tag?: string; foot?: string; verdict?: {at: number; text: React.ReactNode; tone: 'dim' | 'orange'}; rewindFrom?: number;
  labels?: {read: string; paid: string; money: string; left: string}; at: number; out?: number;
}> = ({w = 900, seconds, leaveAt, run, stopAt, tokRate, money, tag, foot, verdict, rewindFrom, labels = {read: 'read', paid: 'generated · paid', money: 'wasted', left: 'user left'}, at, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  let t: number;
  if (f < run.start) t = rewindFrom !== undefined ? rewindFrom * (1 - ease(f, at, Math.min(run.start, at + 14))) : 0;
  else if (f < run.leave) t = leaveAt * ease(f, run.start, run.leave);
  else if (f < run.leave + 8) t = leaveAt;
  else t = interpolate(f, [run.leave + 8, run.end], [leaveAt, stopAt], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: stopAt - leaveAt > 1 ? Easing.in(Easing.quad) : Easing.out(Easing.cubic)});
  const rewinding = f < run.start && rewindFrom !== undefined;
  const x0 = 44, x1 = w - 44, by = 150, bh = 34;
  const X = (s: number) => x0 + ((x1 - x0) * s) / seconds;
  const gen = Math.round(t * tokRate);
  const read = Math.round(Math.min(t, leaveAt) * tokRate);
  const wasted = Math.max(0, gen - read);
  const cash = money ? wasted * money.perTok : 0;
  const frozen = f >= run.end && stopAt - leaveAt < 1;
  const left = f >= run.leave - 2;
  const lv = left ? sp(f, run.leave - 2, {damping: 10, stiffness: 170}) : 0;
  const box = (label: string, value: string, tone: 'ink' | 'orange', bumpAt?: number) => (
    <div style={{flex: 1, boxSizing: 'border-box', borderRadius: R, border: `2px solid ${tone === 'orange' ? C.accent : C.border}`, background: C.surface, padding: '10px 14px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2}}>
      <span style={{fontFamily: inter, fontWeight: 900, fontSize: 60, lineHeight: 1.05, color: tone === 'orange' ? C.accent : C.text, fontVariantNumeric: 'tabular-nums', transform: `scale(${bumpAt !== undefined ? bump(f, bumpAt) : 1})`, whiteSpace: 'nowrap'}}>{value}</span>
      <span style={{fontFamily: inter, fontWeight: 700, fontSize: 22, color: C.textDim, whiteSpace: 'nowrap'}}>{label}</span>
    </div>
  );
  return (
    <div style={{position: 'relative', width: w, height: verdict ? 450 : 380, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, opacity: ease(f, out - 8, out, 1, 0), ...(f < at + 10 ? popIn(f, at) : {})}}>
      {tag && <div style={{position: 'absolute', right: 18, top: 16}}><Tag label={tag} tone="dim" size={22} /></div>}
      {/* track */}
      <div style={{position: 'absolute', left: x0, top: by, width: x1 - x0, height: bh, borderRadius: 10, background: C.barBg, border: `2px solid ${C.grid}`, boxSizing: 'border-box'}} />
      <div style={{position: 'absolute', left: x0, top: by, width: Math.max(0, X(Math.min(t, leaveAt)) - x0), height: bh, borderRadius: '10px 0 0 10px', background: C.accent}} />
      {t > leaveAt && (
        <div style={{position: 'absolute', left: X(leaveAt), top: by, width: X(t) - X(leaveAt), height: bh, background: `repeating-linear-gradient(135deg, ${C.hatch} 0 10px, ${C.hatchLight} 10px 20px)`, borderRadius: '0 10px 10px 0'}} />
      )}
      {/* ticks */}
      {[0, seconds].map((s, i) => (
        <div key={s} style={{position: 'absolute', left: X(s), top: by + bh + 8, transform: i ? 'translateX(-100%)' : undefined, fontFamily: mono, fontWeight: 700, fontSize: 24, color: C.textDim}}>{s} s</div>
      ))}
      {/* user-left pin */}
      {left && (
        <div style={{position: 'absolute', left: X(leaveAt), top: by - 70, transform: `translateY(${(1 - lv) * -16}px)`, opacity: Math.min(1, lv * 1.5)}}>
          <div style={{position: 'absolute', left: -1, top: 30, width: 3, height: 44, background: C.text}} />
          <div style={{position: 'absolute', left: 6, top: 0}}><Tag label={`${labels.left} · ${leaveAt} s`} tone="ink" size={22} /></div>
        </div>
      )}
      {/* playhead */}
      <div style={{position: 'absolute', left: X(t) - 2, top: by - 16, width: 4, height: bh + 32, borderRadius: 2, background: C.text, opacity: rewinding ? 0.6 : 1}} />
      {!left && <div style={{position: 'absolute', left: X(t), top: by - 52, transform: 'translateX(-50%)', fontFamily: mono, fontWeight: 700, fontSize: 26, color: C.text, whiteSpace: 'nowrap'}}>{t < 10 ? t.toFixed(1) : Math.floor(t)} s</div>}
      {left && <div style={{position: 'absolute', right: 30, top: 66, fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.text, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap'}}>t = {t < 10 ? t.toFixed(1) : Math.floor(t)} s{frozen ? ' · stopped' : ''}</div>}
      {/* counters */}
      <div style={{position: 'absolute', left: 30, right: 30, top: 236, display: 'flex', gap: 16}}>
        {box(labels.read, read.toLocaleString('en-IN'), 'ink')}
        {box(labels.paid, gen.toLocaleString('en-IN'), 'orange', frozen ? run.end : undefined)}
        {money && box(labels.money, `${cash < 0.5 && f >= run.end ? '≈ ' : ''}${money.prefix}${Math.round(cash)}`, 'orange', frozen ? run.end : undefined)}
      </div>
      {verdict && f >= verdict.at - 1 && (
        <div style={{position: 'absolute', left: 30, right: 30, top: 370, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, ...popIn(f, verdict.at)}}>
          {verdict.tone === 'dim' && <WarnMark size={44} />}
          <span style={{fontFamily: inter, fontWeight: 900, fontSize: 38, color: verdict.tone === 'dim' ? C.textDim : C.accent, whiteSpace: 'nowrap'}}>{verdict.text}</span>
        </div>
      )}
      {foot && <div style={{position: 'absolute', left: 0, right: 0, bottom: -34, textAlign: 'center', fontFamily: inter, fontWeight: 600, fontSize: 20, color: C.textDim, whiteSpace: 'nowrap'}}>{foot}</div>}
    </div>
  );
};
