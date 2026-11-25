// Spec: components/specs/LineChart.md · first built for system-design-of-ai/11-max-tokens-and-truncation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, easeOut, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

/* ---------------- LineChart · ₹ spend vs length rate ---------------- */
/** two series on one axis; series B turns orange from `markIdx` on (a spike after a change), with an alert dot on its last point */
export const LineChart: React.FC<{w?: number; h?: number; drawAt: number; spikeAt: number; dotAt: number; at: number; out?: number; a?: number[]; b?: number[]; markIdx?: number;
  labels?: {a: string; b: string; mark: string; alert: string; x: string}}> = ({w = 900, h = 640, drawAt, spikeAt, dotAt, at, out = 1e9, a, b, markIdx = 7,
  labels = {a: '₹ AI spend', b: 'finish_reason = length', mark: 'prompt v7', alert: 'waste meter', x: 'weeks →'}}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const x0 = 70, x1 = w - 40, y0 = h - 90, y1 = 90;
  const v7 = markIdx;
  const spend = a ?? Array.from({length: 12}, (_, i) => 0.35 + i * 0.018 + (i >= v7 ? (i - v7 + 1) * 0.05 : 0));
  const len = b ?? Array.from({length: 12}, (_, i) => (i < v7 ? 0.08 + ((i * 7) % 3) * 0.015 : 0.08 + Math.min(1, (i - v7 + 1) / 2) * 0.72));
  const N = spend.length;
  const X = (i: number) => x0 + ((x1 - x0) * i) / (N - 1), Y = (v: number) => y0 - (y0 - y1) * v;
  const path = (a: number[]) => a.map((v, i) => `${i ? 'L' : 'M'} ${X(i)} ${Y(v)}`).join(' ');
  const p1 = ease(f, drawAt, drawAt + 24), p2 = ease(f, spikeAt - 6, spikeAt + 18);
  return (
    <div style={{position: 'relative', width: w, height: h, background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at, out)}}>
      <svg width={w} height={h} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <line x1={x0} y1={y0} x2={x1} y2={y0} stroke={C.border} strokeWidth={2} />
        <line x1={x0} y1={y1} x2={x0} y2={y0} stroke={C.border} strokeWidth={2} />
        <line x1={X(v7 - 0.5)} y1={y1 - 20} x2={X(v7 - 0.5)} y2={y0} stroke={C.dim} strokeWidth={3} strokeDasharray="8 8" opacity={p2} />
        <path d={path(spend)} fill="none" stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={2000} strokeDashoffset={2000 * (1 - p1)} />
        <path d={path(len.slice(0, v7))} fill="none" stroke={C.dim} strokeWidth={6} strokeLinecap="round" strokeDasharray={1200} strokeDashoffset={1200 * (1 - p1)} />
        <path d={len.slice(v7 - 1).map((v, k) => `${k ? 'L' : 'M'} ${X(v7 - 1 + k)} ${Y(v)}`).join(' ')} fill="none" stroke={C.orange} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={1200} strokeDashoffset={1200 * (1 - p2)} />
        {f >= dotAt && <circle cx={X(N - 1)} cy={Y(len[N - 1])} r={16 + 6 * Math.sin((f - dotAt) / 4)} fill={C.orange} stroke={C.border} strokeWidth={3} />}
      </svg>
      <div style={{position: 'absolute', left: x0 + 14, top: 26, display: 'flex', gap: 22, fontFamily: inter, fontWeight: 800, fontSize: 26}}>
        <span style={{display: 'flex', alignItems: 'center', gap: 8, color: C.ink}}><span style={{width: 30, height: 6, background: C.ink, borderRadius: 3}} />{labels.a}</span>
        <span style={{display: 'flex', alignItems: 'center', gap: 8, color: C.orange, fontFamily: mono, fontWeight: 700, fontSize: 24}}><span style={{width: 30, height: 6, background: C.orange, borderRadius: 3}} />{labels.b}</span>
      </div>
      {p2 > 0.3 && <div style={{position: 'absolute', left: X(v7 - 0.5) - 70, top: y0 + 18, opacity: p2}}><Tag label={labels.mark} tone="dim" size={24} monoFont /></div>}
      {f >= dotAt && <div style={{position: 'absolute', right: 70, top: Y(len[N - 1]) - 86, ...popIn(f, dotAt)}}><Tag label={labels.alert} tone="orange" size={28} /></div>}
      <div style={{position: 'absolute', left: x0, bottom: 20, fontFamily: inter, fontWeight: 700, fontSize: 22, color: C.dim}}>{labels.x}</div>
    </div>
  );
};
