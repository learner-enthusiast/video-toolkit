// Spec: components/specs/LaundryToGpu.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
import React from 'react';
import {useCurrentFrame, interpolate, Easing} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono, serif} from '../theme';
import {sp, ease, popIn, enter} from '../anim';
import {Logo, WarnMark, ServerGlyph, ChipGlyph} from '../glyphs';
import {Tag} from '../Tag/Tag';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const Pill: React.FC<{label: React.ReactNode; tone?: 'orange' | 'ink' | 'dim' | 'outline'; size?: number; monoFont?: boolean}> = (p) => <Tag {...p} />;
export const OK: React.FC<{size?: number; color?: string}> = ({size = 40, color = C.accent}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" style={{flexShrink: 0}}><path d="M9 25l10 10 20-22" /></svg>
);
const NodeLabel: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 26, color = C.ink}) => (
  <div style={{fontFamily: inter, fontWeight: 800, fontSize: size, color, textAlign: 'center', lineHeight: 1.1, whiteSpace: 'nowrap'}}>{children}</div>
);
type Load = 'one' | 'full' | 'none';
export const Machine: React.FC<{size?: number; load: Load; spinAt?: number; tone?: 'dim' | 'orange' | 'ink'; doorFill?: number}> = ({size = 220, load, spinAt = 1e9, tone = 'ink'}) => {
  const f = useCurrentFrame();
  const spin = f >= spinAt ? interpolate(f - spinAt, [0, 20, 200], [0, 60, 1200], {extrapolateRight: 'extend', easing: Easing.inOut(Easing.quad)}) : 0;
  const stroke = tone === 'dim' ? C.textDim : C.border;
  const acc = tone === 'orange' ? C.accent : C.textDim;
  return (
    <svg width={size} height={size * 1.15} viewBox="0 0 100 115" fill="none" strokeLinejoin="round">
      <rect x="4" y="4" width="92" height="107" rx="9" fill={C.white} stroke={stroke} strokeWidth={2.6} />
      <line x1="4" y1="24" x2="96" y2="24" stroke={stroke} strokeWidth={2} />
      <circle cx="16" cy="14" r="4" stroke={stroke} strokeWidth={2} /><rect x="58" y="10" width="28" height="7" rx="3" stroke={stroke} strokeWidth={2} />
      <circle cx="50" cy="67" r="32" stroke={stroke} strokeWidth={3} fill="#F1EEE7" />
      <clipPath id={`drum-${load}-${tone}`}><circle cx="50" cy="67" r="28" /></clipPath>
      <g clipPath={`url(#drum-${load}-${tone})`} transform={`rotate(${spin} 50 67)`}>
        {load === 'one' && <path d="M42 64l8-6 8 6-3 4v12H45V68z" fill={acc} stroke={stroke} strokeWidth={1.6} />}
        {load === 'full' && [[-12, -10], [6, -12], [-16, 8], [2, 6], [16, 4], [-4, 18], [12, 20], [-6, -2]].map(([dx, dy], i) => (
          <rect key={i} x={50 + dx - 8} y={67 + dy - 6} width={17} height={13} rx={3} fill={i % 2 ? C.accent : '#F2A588'} stroke={stroke} strokeWidth={1.3} transform={`rotate(${i * 37} ${50 + dx} ${67 + dy})`} />
        ))}
      </g>
    </svg>
  );
};
export const Shirt: React.FC<{size?: number; color?: string}> = ({size = 120, color = C.white}) => (
  <svg width={size} height={size * 0.8} viewBox="0 0 60 48" fill="none" stroke={C.border} strokeWidth={2.4} strokeLinejoin="round"><path d="M18 4l-14 8 5 10 7-3v25h28V19l7 3 5-10-14-8c-2 4-6 6-12 6S20 8 18 4z" fill={color} /><path d="M24 4l6 7 6-7" /></svg>
);
export const Basket: React.FC<{size?: number}> = ({size = 120}) => (
  <svg width={size} height={size * 0.7} viewBox="0 0 60 42" fill="none" stroke={C.border} strokeWidth={2.4} strokeLinejoin="round"><path d="M4 12h52l-5 26H9z" fill={C.white} />{[16, 26, 36].map((x) => <line key={x} x1={x} y1={16} x2={x - 1} y2={34} />)}<path d="M14 12c0-7 32-7 32 0" /></svg>
);
/** GPU row: chips, `busy` = indices filled by day (real-time), `fillAt` = night batch fills all */
export const GpuRow: React.FC<{x: number; y: number; at: number; out?: number; n?: number; busy: number[]; spareAt: number; fillAt: number; size?: number}> = ({x, y, at, out = 1e9, n = 6, busy, spareAt, fillAt, size = 128}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, display: 'flex', gap: 20, opacity: ease(f, out - 8, out, 1, 0)}}>
      {Array.from({length: n}).map((_, i) => {
        const v = sp(f, at + i * 4);
        const isBusy = busy.includes(i);
        const fill = f >= fillAt + i * 4 ? sp(f, fillAt + i * 4) : 0;
        const spare = !isBusy && f >= spareAt && fill < 0.5;
        return (
          <div key={i} style={{position: 'relative', opacity: Math.min(1, v * 1.4), transform: `scale(${0.7 + 0.3 * v})`}}>
            <div style={{opacity: spare ? 0.55 : 1}}><ChipGlyph size={size} color={spare ? C.textDim : C.ink} big={isBusy || fill > 0.5} /></div>
            {fill > 0.02 && <div style={{position: 'absolute', left: size * 0.27, top: size * 0.27, width: size * 0.46, height: size * 0.46 * fill, borderRadius: 6, background: C.accent, opacity: 0.9}} />}
          </div>
        );
      })}
    </div>
  );
};
