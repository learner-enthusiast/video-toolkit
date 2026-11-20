// Spec: components/specs/DeadlineLane.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, popIn, enter} from '../anim';
import {Logo, WarnMark, ServerGlyph, ChipGlyph} from '../glyphs';
import {Tag} from '../Tag/Tag';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const Pill: React.FC<{label: React.ReactNode; tone?: 'orange' | 'ink' | 'dim' | 'outline'; size?: number; monoFont?: boolean}> = (p) => <Tag {...p} />;
export const OK: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.orange}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}><path d="M9 25l10 10 20-22" /></svg>
);
const NodeLabel: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 26, color = C.ink}) => (
  <div style={{fontFamily: inter, fontWeight: 800, fontSize: size, color, textAlign: 'center', lineHeight: 1.1, whiteSpace: 'nowrap'}}>{children}</div>
);
export const DeadlineLane: React.FC<{at: number; out: number; runFrom: number; runTo: number; deadlineAt: number; peelAt: number; laneAt: number; start?: string; deadline?: string; deadlineNote?: string; leftover?: string; lane?: string}> = ({at, out, runFrom, runTo, deadlineAt, peelAt, laneAt, start = 'submit', deadline = 'deadline', deadlineNote = 'deadline', leftover = 'N pending', lane = 'Fallback lane'}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const X0 = 60, X1 = 760, Y = 380;
  const p = ease(f, runFrom, runTo) * 0.86;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ease(f, out - 8, out, 1, 0)}}>
      <div style={{position: 'absolute', left: X0, top: Y, width: X1 - X0, height: 54, borderRadius: 999, border: BORDER, background: C.white, overflow: 'hidden', ...enter(f, at)}}>
        <div style={{width: `${p * 100}%`, height: '100%', background: C.orange}} />
      </div>
      <div style={{position: 'absolute', left: X0 - 10, top: Y + 74, ...enter(f, at + 4)}}><Pill label={start} size={26} monoFont /></div>
      {/* deadline */}
      <svg width={972} height={970} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        {f >= at + 6 && <line x1={X1 + 30} y1={Y - 120} x2={X1 + 30} y2={Y + 170} stroke={C.ink} strokeWidth={4} strokeDasharray="12 10" opacity={ease(f, at + 6, at + 14)} />}
      </svg>
      <div style={{position: 'absolute', left: X1 - 40, top: Y - 190, ...popIn(f, at + 8)}}>
        <div style={{transform: `scale(${f >= deadlineAt ? 1 + 0.12 * Math.sin(Math.PI * clamp01((f - deadlineAt) / 10)) : 1})`}}><Pill label={deadline} tone={f >= deadlineAt ? 'orange' : 'ink'} size={34} monoFont /></div>
      </div>
      <div style={{position: 'absolute', left: X1 - 36, top: Y + 186, fontFamily: inter, fontWeight: 800, fontSize: 24, color: C.dim, ...enter(f, at + 10)}}>{deadlineNote}</div>
      {/* leftovers */}
      {Array.from({length: 4}).map((_, i) => {
        const a = peelAt + i * 4;
        const k = f >= a ? ease(f, a, a + 18) : 0;
        const x = lerp(X0 + (X1 - X0) * 0.88 + i * 8, 200 + i * 70, k), y = lerp(Y + 8 + i * 4, 760, k) - Math.sin(k * Math.PI) * 80;
        if (f < runTo - 4) return null;
        const done = f >= laneAt + 14 + i * 4;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 56, height: 36, borderRadius: 7, border: BORDER, background: done ? C.orange : '#E6E2DA'}} />;
      })}
      {f >= runTo - 4 && f < peelAt + 4 && (
        <div style={{position: 'absolute', left: X1 - 330, top: Y + 80, display: 'flex', alignItems: 'center', gap: 10, ...popIn(f, runTo - 4)}}><WarnMark size={44} /><Pill label={leftover} size={30} monoFont /></div>
      )}
      {f >= peelAt && (
        <div style={{position: 'absolute', left: 60, top: 720, width: 852, height: 120, borderRadius: R, border: `3px solid ${C.orange}`, background: 'rgba(228,87,46,.08)', ...enter(f, peelAt)}}>
          <div style={{position: 'absolute', right: 26, top: 36, fontFamily: inter, fontWeight: 900, fontSize: 38, color: C.orange, whiteSpace: 'nowrap'}}>{lane}</div>
        </div>
      )}
    </div>
  );
};
