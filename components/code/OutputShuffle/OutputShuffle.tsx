// Spec: components/specs/OutputShuffle.md · first built in system-design-of-ai/10-batch-inference. Sample text lives in props, never here.
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
export const ReportGlyph: React.FC<{size?: number}> = ({size = 64}) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none" stroke={C.ink} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M12 5h17l9 9v29H12z" fill={C.white} /><path d="M29 5v9h9" /><path d="M18 34v-6M24 34v-10M30 34v-4" stroke={C.accent} strokeWidth={4} /></svg>
);
export const OutputShuffle: React.FC<{at: number; out: number; shuffleAt: number; mapAt: number; leakAt?: number; rewindAt: number; fixAt: number; snapAt: number; matchAt: number; rows?: {name: string; id: string}[]; order?: number[]; files?: [string, string]; labels?: [string, string]; item?: string}> = ({at, out, shuffleAt, mapAt, rewindAt, fixAt, snapAt, matchAt, rows = [{name: 'Asha', id: 'user_00001'}, {name: 'Ravi', id: 'user_00002'}, {name: 'Meena', id: 'user_00003'}], order = [1, 2, 0], files = ['input.jsonl', 'output.jsonl'], labels = ['matched by line number', 'matched by custom_id'], item = 'report'}) => {
  const NAMES = rows.map((r) => r.name);
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const sh = sp(f, shuffleAt, {damping: 15, stiffness: 110});
  const fixed = f >= snapAt;
  const rowY = (k: number) => 150 + k * 92;
  const outRowOf = (name: number) => order.indexOf(name);
  const phoneY = (k: number) => 80 + k * 260;
  // where each report ends up: by line number (wrong) or by custom_id (right)
  const wrong = f >= mapAt && f < rewindAt && !fixed;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ease(f, out - 8, out, 1, 0)}}>
      {/* input */}
      <div style={{position: 'absolute', left: 20, top: 60, width: 300, height: 450, background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at)}}>
        <div style={{fontFamily: mono, fontWeight: 700, fontSize: 26, padding: '16px 18px'}}>{files[0]}</div>
      </div>
      {NAMES.map((n, i) => (
        <div key={n} style={{position: 'absolute', left: 36, top: rowY(i), width: 268, height: 70, display: 'flex', alignItems: 'center', gap: 12, ...enter(f, at + 4 + i * 4)}}>
          <span style={{fontFamily: mono, fontSize: 26, color: C.textDim, width: 26}}>{i + 1}</span>
          <span style={{fontFamily: inter, fontWeight: 800, fontSize: 32, color: C.text}}>{n}</span>
          {f >= fixAt && <span style={{fontFamily: mono, fontWeight: 700, fontSize: 18, color: C.white, background: C.accent, borderRadius: 6, padding: '2px 6px', ...popIn(f, fixAt + i * 4)}}>{rows[i].id}</span>}
        </div>
      ))}
      {/* output */}
      <div style={{position: 'absolute', left: 350, top: 60, width: 300, height: 450, background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, ...enter(f, at + 6)}}>
        <div style={{fontFamily: mono, fontWeight: 700, fontSize: 26, padding: '16px 18px'}}>{files[1]}</div>
      </div>
      {NAMES.map((n, name) => {
        const k = outRowOf(name);
        const y = lerp(rowY(name), rowY(k), sh);
        return (
          <div key={n} style={{position: 'absolute', left: 366, top: y, width: 270, height: 70, display: 'flex', alignItems: 'center', gap: 10, ...enter(f, at + 10 + name * 4)}}>
            <span style={{fontFamily: mono, fontSize: 26, color: C.textDim, width: 26}}>{Math.round(lerp(name, k, sh)) + 1}</span>
            <ReportGlyph size={42} />
            <span style={{fontFamily: inter, fontWeight: 700, fontSize: 26, color: C.text, whiteSpace: 'nowrap'}}>{n}'s {item}</span>
          </div>
        );
      })}
      {/* phones */}
      {NAMES.map((n, i) => {
        const v = sp(f, at + 14 + i * 4);
        // the report landing on phone i: by line number = output line i; by custom_id = its own report
        const landed = wrong ? NAMES[order[i]] : fixed ? n : null;
        const bad = wrong && order[i] !== i;
        const shakeX = bad && f >= mapAt + 12 && f < mapAt + 26 ? Math.sin((f - mapAt) * 2.2) * 6 : 0;
        return (
          <div key={n} style={{position: 'absolute', left: 720, top: phoneY(i), width: 220, height: 200, opacity: Math.min(1, v * 1.4), transform: `translateX(${shakeX}px) scale(${0.85 + 0.15 * v})`}}>
            <div style={{width: 130, height: 200, boxSizing: 'border-box', border: `4px solid ${C.border}`, borderRadius: 22, background: C.surface, display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 14, gap: 8}}>
              <div style={{width: 46, height: 46, borderRadius: 99, background: C.ink, color: C.white, fontFamily: inter, fontWeight: 800, fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{n[0]}</div>
              {landed && <div key={`${landed}-${wrong}`} style={{fontFamily: inter, fontWeight: 800, fontSize: 18, color: bad ? C.textDim : C.ink, textAlign: 'center', lineHeight: 1.1, ...popIn(f, wrong ? mapAt + 10 : snapAt + 8 + i * 4)}}>{landed}'s<br />{item}</div>}
            </div>
            <div style={{position: 'absolute', left: -20, top: 204, width: 170, textAlign: 'center', fontFamily: inter, fontWeight: 800, fontSize: 24, color: C.text}}>{n}</div>
            {bad && f >= mapAt + 12 && <div style={{position: 'absolute', left: 146, top: 100, ...popIn(f, mapAt + 12)}}><WarnMark size={44} /></div>}
            {fixed && f >= matchAt + i * 4 && <div style={{position: 'absolute', left: 146, top: 100, ...popIn(f, matchAt + i * 4)}}><OK size={44} /></div>}
          </div>
        );
      })}
      {/* arrows: output line k → phone k (wrong) or name → own phone (right) */}
      <svg width={972} height={970} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        {NAMES.map((n, k) => {
          const a = wrong ? mapAt + k * 4 : fixed ? snapAt + k * 4 : 1e9;
          if (f < a) return null;
          const v = ease(f, a, a + 10);
          const y1 = (fixed ? rowY(outRowOf(k)) : rowY(k)) + 35, y2 = phoneY(k) + 100;
          const x1 = 640, x2 = 712;
          return <line key={`${k}-${fixed}`} x1={x1} y1={y1} x2={x1 + (x2 - x1) * v} y2={y1 + (y2 - y1) * v} stroke={fixed ? C.accent : C.textDim} strokeWidth={5} strokeLinecap="round" strokeDasharray={fixed ? undefined : '10 8'} />;
        })}
      </svg>
      {wrong && f >= mapAt + 4 && <div style={{position: 'absolute', left: 340, top: 540, ...popIn(f, mapAt + 4)}}><Pill label={labels[0]} tone="dim" size={28} /></div>}
      {fixed && <div style={{position: 'absolute', left: 340, top: 540, ...popIn(f, snapAt)}}><Pill label={labels[1]} tone="orange" size={28} monoFont /></div>}
    </div>
  );
};
