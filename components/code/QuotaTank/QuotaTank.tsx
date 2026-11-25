// Spec: components/specs/QuotaTank.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
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
export const QuotaTank: React.FC<{x: number; y: number; w: number; h: number; at: number; out?: number; labelAt: number; drainAt?: number; dryAt?: number; splitAt?: number; flowAgainAt?: number; label?: string; dark?: boolean; logo?: string; taps?: [React.ReactNode, React.ReactNode]; splitLabels?: [string, string]; errorText?: string}> = ({x, y, w, h, at, out = 1e9, labelAt, drainAt, dryAt, splitAt, flowAgainAt, label = 'Shared limit · per account', logo, taps = ['Thick tap', 'Thin tap'], splitLabels = ['Batch queue', 'Live limit'], errorText = '429'}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const v = sp(f, at);
  const tankH = h - 210, tankW = w;
  const level = drainAt !== undefined ? lerp(0.85, 0.06, ease(f, drainAt, drainAt + 40)) : 0.85;
  const split = splitAt !== undefined ? sp(f, splitAt, {damping: 16, stiffness: 110}) : 0;
  const wave = Math.sin(f / 7) * 4;
  const dry = dryAt !== undefined ? ease(f, dryAt, dryAt + 10) : 0;
  const again = flowAgainAt !== undefined ? ease(f, flowAgainAt, flowAgainAt + 10) : 0;
  const thinOn = (1 - dry) + again;
  const gap = split * 26;
  const half = (tankW - gap) / 2;
  const tankBody = (bx: number, bw: number, lv: number, key: string, lbl?: string) => (
    <g key={key}>
      <rect x={bx} y={0} width={bw} height={tankH} rx={14} fill={C.white} stroke={C.border} strokeWidth={3} />
      <clipPath id={`tk-${key}`}><rect x={bx + 2} y={2} width={bw - 4} height={tankH - 4} rx={12} /></clipPath>
      <g clipPath={`url(#tk-${key})`}>
        <path d={`M${bx} ${tankH * (1 - lv) + wave} Q${bx + bw / 4} ${tankH * (1 - lv) - 8 + wave} ${bx + bw / 2} ${tankH * (1 - lv) + wave} T${bx + bw} ${tankH * (1 - lv) + wave} V${tankH} H${bx} Z`} fill="rgba(228,87,46,.82)" />
      </g>
      {[0.25, 0.5, 0.75].map((t) => <line key={t} x1={bx + bw - 22} x2={bx + bw - 6} y1={tankH * t} y2={tankH * t} stroke={C.border} strokeWidth={2} />)}
    </g>
  );
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: Math.min(1, v * 1.4) * ease(f, out - 8, out, 1, 0), transform: `scale(${0.9 + 0.1 * v})`, transformOrigin: 'center bottom'}}>
      <div style={{position: 'absolute', left: -20, right: -20, top: -96, display: 'flex', justifyContent: 'center', ...popIn(f, labelAt)}}>
        {split < 0.5 ? (
          <div style={{display: 'flex', alignItems: 'center', gap: 10, background: C.white, border: BORDER, borderRadius: R, padding: '8px 14px'}}>
            {logo && <Logo file={logo} w={40} h={40} />}
            <div style={{fontFamily: inter, fontWeight: 800, fontSize: 24, lineHeight: 1.1, color: C.ink, whiteSpace: 'nowrap'}}>{label.split(' · ')[0]}<br /><span style={{color: C.orange}}>{label.split(' · ')[1]}</span></div>
          </div>
        ) : null}
      </div>
      {split >= 0.5 && (
        <>
          <div style={{position: 'absolute', left: -24, top: -70, ...popIn(f, splitAt! + 6)}}><Pill label={splitLabels[0]} tone="orange" size={24} /></div>
          <div style={{position: 'absolute', right: -24, top: -70, ...popIn(f, splitAt! + 10)}}><Pill label={splitLabels[1]} size={24} /></div>
        </>
      )}
      <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {split < 0.02 ? tankBody(0, tankW, level, 'one') : <>{tankBody(0, half, Math.max(level, 0.7 * split), 'a')}{tankBody(half + gap, half, 0.85, 'b')}</>}
        {/* taps */}
        <path d={`M${w * 0.22} ${tankH} v40 h-26`} fill="none" stroke={C.border} strokeWidth={12} strokeLinecap="round" />
        <path d={`M${w * 0.78} ${tankH} v40 h26`} fill="none" stroke={C.border} strokeWidth={6} strokeLinecap="round" />
        {/* thick stream: report job (in the split it pours from the batch side) */}
        {(drainAt === undefined || f < drainAt + 44 || split > 0.5) && <rect x={w * 0.22 - 26 - 14} y={tankH + 46} width={28} height={70} rx={8} fill={C.orange} opacity={drainAt !== undefined && f >= drainAt ? 0.9 : 0.3} />}
        {/* thin stream: live assistant, sputters dry */}
        {Array.from({length: 4}).map((_, i) => {
          const sput = dry > 0 && again < 0.5 ? (Math.sin(f * 1.3 + i) > 0.2 ? 0 : 1) : 1;
          return <rect key={i} x={w * 0.78 + 26 - 4} y={tankH + 46 + i * 18} width={8} height={12} rx={3} fill={thinOn > 0.5 ? C.orange : C.dim} opacity={thinOn > 0.5 ? 0.9 : sput * (1 - dry) * 0.8} />;
        })}
      </svg>
      <div style={{position: 'absolute', left: w * 0.22 - 26 - 60, top: tankH + 124, width: 120, ...popIn(f, at + 6)}}><NodeLabel size={22}>{taps[0]}</NodeLabel></div>
      <div style={{position: 'absolute', left: w * 0.78 + 26 - 60, top: tankH + 124, width: 120, ...popIn(f, at + 10)}}><NodeLabel size={22} color={dry > 0.5 && again < 0.5 ? C.dim : C.ink}>{taps[1]}</NodeLabel></div>
      {dry > 0.4 && again < 0.5 && (
        <div style={{position: 'absolute', left: w * 0.78 + 26 - 80, top: tankH + 190, display: 'flex', alignItems: 'center', gap: 6, ...popIn(f, dryAt! + 6)}}>
          <WarnMark size={40} /><span style={{fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.white, background: C.dim, borderRadius: 8, padding: '2px 10px', border: BORDER}}>{errorText}</span>
        </div>
      )}
      {again > 0.5 && <div style={{position: 'absolute', left: w * 0.78 + 26 - 20, top: tankH + 190, ...popIn(f, flowAgainAt! + 4)}}><OK size={40} /></div>}
    </div>
  );
};
