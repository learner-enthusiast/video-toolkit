// Spec: components/specs/JsonlFile.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
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
export const JsonlFile: React.FC<{at: number; out: number; stackAt: number; counterAt: number; dropAt: number; chipAt: number; fileName?: string; idPrefix?: string; counter?: [string, string]; logo?: string; lane?: string; chip?: [string, string]}> = ({at, out, stackAt, counterAt, dropAt, chipAt, fileName = 'requests.jsonl', idPrefix = 'user_', counter = ['50,000 lines per file', '20 files'], logo, lane = 'Batch lane', chip = ['completion_window: ', '"24h"']}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const lines = Array.from({length: 6}, (_, i) => `${idPrefix}${String(i + 1).padStart(6, '0')}`);
  const drop = ease(f, dropAt, dropAt + 18);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ease(f, out - 8, out, 1, 0)}}>
      {/* the file */}
      <div style={{position: 'absolute', left: 40, top: 60, ...enter(f, at)}}><div style={{width: 600, boxSizing: 'border-box', background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, padding: '18px 22px', transform: `translateY(${drop * 40}px) scale(${1 - drop * 0.25})`, transformOrigin: 'left top', opacity: 1 - drop * 0.6}}>
        <div style={{fontFamily: mono, fontWeight: 700, fontSize: 28, color: C.ink, marginBottom: 10}}>{fileName}</div>
        {lines.map((id, i) => {
          const a = stackAt + i * 5;
          if (f < a - 1) return null;
          const v = sp(f, a);
          return (
            <div key={id} style={{fontFamily: mono, fontWeight: 500, fontSize: 23, color: C.ink, whiteSpace: 'nowrap', lineHeight: 1.65, opacity: Math.min(1, v * 1.5), transform: `translateY(${(1 - v) * -16}px)`}}>
              {'{'}<span style={{color: C.dim}}>"custom_id"</span>: <span style={{color: C.orange, fontWeight: 700}}>"{id}"</span>, <span style={{color: C.dim}}>"body"</span>: {'{…}}'}
            </div>
          );
        })}
        {f > stackAt + 34 && <div style={{fontFamily: mono, fontSize: 26, color: C.dim, ...popIn(f, stackAt + 34)}}>…</div>}
      </div></div>
      {/* counter */}
      {f >= counterAt && (
        <div style={{position: 'absolute', left: 40, top: 560, display: 'flex', alignItems: 'center', gap: 16, ...popIn(f, counterAt)}}>
          <span style={{fontFamily: inter, fontWeight: 900, fontSize: 44, color: C.ink, whiteSpace: 'nowrap'}}>{counter[0]}</span>
          <span style={{fontFamily: inter, fontWeight: 900, fontSize: 44, color: C.orange}}>→</span>
          <span style={{fontFamily: inter, fontWeight: 900, fontSize: 44, color: C.white, background: C.orange, borderRadius: 10, padding: '0 14px', whiteSpace: 'nowrap'}}>{counter[1]}</span>
        </div>
      )}
      {/* fan of files falling into OpenAI (batch lane) */}
      {Array.from({length: 5}).map((_, i) => {
        const a = counterAt + 6 + i * 3;
        if (f < a) return null;
        const v = sp(f, a);
        const d = ease(f, dropAt + i * 3, dropAt + i * 3 + 16);
        const x0 = 60 + i * 92, y0 = 690, x1 = 760, y1 = 330;
        return (
          <div key={i} style={{position: 'absolute', left: lerp(x0, x1, d), top: lerp(y0, y1, d) - Math.sin(d * Math.PI) * 120, opacity: Math.min(1, v * 1.5) * (1 - ease(f, dropAt + i * 3 + 14, dropAt + i * 3 + 18)), transform: `scale(${(0.8 + 0.2 * v) * (1 - d * 0.5)})`}}>
            <FileIcon />
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 680, top: 220, width: 260, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, ...popIn(f, at + 8)}}>
        <div style={{width: 170, height: 170, background: C.white, border: `${f > dropAt + 18 ? 5 : 2}px solid ${f > dropAt + 18 ? C.orange : C.border}`, borderRadius: R, boxShadow: SHADOW, display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box'}}>{logo ? <Logo file={logo} w={100} h={100} /> : <ServerGlyph size={100} />}</div>
        <Pill label={lane} tone="orange" size={26} />
      </div>
      {f >= chipAt && <div style={{position: 'absolute', left: 400, top: 480, ...popIn(f, chipAt)}}><span style={{fontFamily: mono, fontWeight: 700, fontSize: 32, color: C.ink, background: C.white, border: `3px solid ${C.orange}`, borderRadius: 999, padding: '10px 22px', whiteSpace: 'nowrap'}}>{chip[0]}<span style={{color: C.orange}}>{chip[1]}</span></span></div>}
    </div>
  );
};
export const FileIcon: React.FC<{w?: number; label?: string}> = ({w = 76, label = '.jsonl'}) => (
  <div style={{position: 'relative', width: w, height: w * 1.25}}>
    <svg width={w} height={w * 1.25} viewBox="0 0 48 60" style={{position: 'absolute', inset: 0}}><path d="M3 3h28l14 14v40H3z" fill={C.white} stroke={C.border} strokeWidth={3} strokeLinejoin="round" /><path d="M31 3v14h14" fill="none" stroke={C.border} strokeWidth={3} strokeLinejoin="round" />{[28, 36, 44].map((y) => <line key={y} x1={10} x2={38} y1={y} y2={y} stroke={C.orange} strokeWidth={3} strokeLinecap="round" />)}</svg>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: -26, textAlign: 'center', fontFamily: mono, fontWeight: 700, fontSize: w * 0.24, color: C.ink}}>{label}</div>
  </div>
);
