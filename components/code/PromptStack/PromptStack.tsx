// Spec: components/specs/PromptStack.md (request-stack variant) · first built for system-design-of-ai/09-prompt-caching. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, ease, popIn, enter} from '../anim';
import {WarnMark, IconLock} from '../glyphs';
import {Tag} from '../Tag/Tag';

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const vis = (f: number, a?: number) => (a === undefined ? 0 : sp(f, a));

/** One LLM request as a stack: clause strip (the plant), system prompt, tools, user details, question.
 *  reorderAt moves the strip from the top (bad: breaks the prefix) to below the static blocks (good); lockAt brackets + locks the static blocks;
 *  breakAt puts ⚠ on the top strip and dims everything below; cursor (0..1) is the model reading top to bottom. */
export type StackLine = {text: React.ReactNode; at: number};
export type StackProps = {
  w: number; at: number; detail?: boolean;
  clauseAt?: number; sysAt?: number; toolsAt?: number; qAt?: number; detailsAt?: number;
  q?: string; clause?: string;
  sysLabel?: string; toolsLabel?: string; detailsLabel?: string; sysCount?: React.ReactNode; toolsCount?: React.ReactNode; tools?: string[]; changesLabel?: string;
  sysLines?: StackLine[]; toolLines?: StackLine[]; k3At?: number; k2At?: number;
  reorderAt?: number; // 'bad' (clauses on top) → 'good' (static first, changing last)
  pulseAt?: number; outlineAt?: number; lockAt?: number; lockLabel?: React.ReactNode;
  breakAt?: number; // prefix breaks at token one: ⚠ on the top strip, all below dims
  stripGlowAt?: number; changesAt?: number;
  cursor?: number; // -1 none, else 0..1 progress top → bottom
  dim?: number;
};
type Key = 'clause' | 'sys' | 'tools' | 'details' | 'q';
export const PromptStack: React.FC<StackProps> = (p) => {
  const f = useCurrentFrame();
  const d = !!p.detail;
  const H: Record<Key, number> = {clause: 58, sys: d ? 262 : 124, tools: d ? 150 : 100, details: 58, q: 68};
  const GAP = 12, PAD = 16;
  const shown: Record<Key, number> = {clause: vis(f, p.clauseAt), sys: vis(f, p.sysAt ?? p.at), tools: vis(f, p.toolsAt ?? p.at), details: vis(f, p.detailsAt), q: vis(f, p.qAt)};
  const t = p.reorderAt === undefined ? 0 : ease(f, p.reorderAt, p.reorderAt + 22);
  const orderA: Key[] = ['clause', 'sys', 'tools', 'details', 'q'];
  const orderB: Key[] = ['sys', 'tools', 'clause', 'details', 'q'];
  const ys = (ord: Key[]) => {
    const y: Record<string, number> = {}; let c = PAD;
    for (const k of ord) { y[k] = c; if (shown[k] > 0.01 || (k === 'details' && p.detailsAt !== undefined)) c += (H[k] + GAP) * Math.min(1, shown[k] * 1.2); }
    return {y, h: c + PAD - GAP};
  };
  const A = ys(orderA), B = ys(orderB);
  const total = lerp(A.h, B.h, t);
  const brk = p.breakAt === undefined ? 0 : ease(f, p.breakAt, p.breakAt + 10);
  const lock = p.lockAt === undefined ? 0 : sp(f, p.lockAt);
  const pulse = p.pulseAt === undefined ? 0 : Math.max(0, Math.sin(Math.PI * Math.min(1, Math.max(0, (f - p.pulseAt) / 14))));
  const outline = p.outlineAt === undefined ? 0 : ease(f, p.outlineAt, p.outlineAt + 8);
  const glow = p.stripGlowAt === undefined ? 0 : ease(f, p.stripGlowAt, p.stripGlowAt + 8);
  const statOn = Math.max(outline, pulse, lock);
  const blk = (k: Key): React.CSSProperties => {
    const y = lerp(A.y[k], B.y[k], t);
    const s = shown[k];
    const below = k !== 'clause' && t < 0.5 ? brk : 0;
    return {position: 'absolute', left: PAD, width: p.w - PAD * 2, top: y, height: H[k], opacity: Math.min(1, s * 1.3) * (1 - 0.6 * below), transform: `translateY(${(1 - s) * -18}px)`, borderRadius: 10, boxSizing: 'border-box', overflow: 'hidden'};
  };
  const statBorder = (on: number) => (on > 0.02 ? `3px solid ${C.orange}` : BORDER);
  const head = (label: string, count?: React.ReactNode, countAt?: number) => (
    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 14px', background: C.paper, borderBottom: `2px solid ${C.grid}`}}>
      <span style={{fontFamily: inter, fontWeight: 800, fontSize: d ? 26 : 22, letterSpacing: '0.06em', textTransform: 'uppercase', color: C.ink}}>{label}</span>
      {count && (countAt === undefined || f >= countAt) && <span style={{fontFamily: mono, fontWeight: 700, fontSize: d ? 26 : 22, color: C.white, background: statOn > 0.5 || pulse > 0.2 ? C.orange : C.ink, borderRadius: 8, padding: '2px 10px', ...(countAt !== undefined ? popIn(f, countAt) : {})}}>{count}</span>}
    </div>
  );
  const lines = (ls: StackLine[] | undefined, n: number) => (
    <div style={{padding: '10px 16px', display: 'flex', flexDirection: 'column', gap: 8}}>
      {ls ? ls.map((l, i) => f >= l.at - 1 && <div key={i} style={{fontFamily: inter, fontWeight: 600, fontSize: 27, color: C.ink, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 10, ...enter(f, l.at, 1e9, 10)}}>{l.text}</div>)
        : Array.from({length: n}).map((_, i) => <div key={i} style={{height: 10, width: `${[86, 70, 78][i % 3]}%`, background: C.track, borderRadius: 5}} />)}
    </div>
  );
  const cur = p.cursor ?? -1;
  return (
    <div style={{position: 'relative', width: p.w, height: total, background: C.white, border: BORDER, borderRadius: R, boxShadow: SHADOW, opacity: 1 - (p.dim ?? 0) * 0.6}}>
      {/* clause strip: the plant */}
      <div style={{...blk('clause'), background: glow > 0.02 ? C.orange : C.mute, border: brk > 0.02 && t < 0.5 ? `3px solid ${C.dim}` : `2px solid ${C.grid}`, display: 'flex', alignItems: 'center', gap: 10, padding: '0 14px'}}>
        {brk > 0.02 && t < 0.5 && <WarnMark size={34} />}
        <span style={{fontFamily: mono, fontWeight: 700, fontSize: 22, color: glow > 0.5 ? C.white : C.dim, whiteSpace: 'nowrap'}}>{p.clause ?? 'retrieved chunks'}</span>
        {p.changesAt !== undefined && f >= p.changesAt && <span style={{marginLeft: 'auto', ...popIn(f, p.changesAt)}}><Tag label={p.changesLabel ?? 'changes'} tone="dim" size={20} /></span>}
      </div>
      <div style={{...blk('sys'), border: statBorder(statOn), background: C.white}}>
        {head(p.sysLabel ?? 'system prompt', p.sysCount, p.k3At)}
        {d ? lines(p.sysLines, 4) : lines(undefined, 3)}
      </div>
      <div style={{...blk('tools'), border: statBorder(statOn), background: C.white}}>
        {head(p.toolsLabel ?? 'tools', p.toolsCount, p.k2At)}
        {d && p.toolLines ? lines(p.toolLines, 0) : <div style={{display: 'flex', gap: 8, padding: '8px 14px'}}>{(p.tools ?? []).map((x) => <span key={x} style={{fontFamily: mono, fontSize: 18, fontWeight: 700, color: C.ink, background: C.fill, borderRadius: 6, padding: '2px 8px'}}>{x}</span>)}</div>}
      </div>
      <div style={{...blk('details'), background: C.mute, border: `2px solid ${C.grid}`, display: 'flex', alignItems: 'center', padding: '0 14px', gap: 10}}>
        <span style={{fontFamily: mono, fontWeight: 700, fontSize: 22, color: C.dim}}>{p.detailsLabel ?? 'user details'}</span>
        {p.changesAt !== undefined && f >= p.changesAt && <span style={{marginLeft: 'auto', ...popIn(f, p.changesAt + 3)}}><Tag label={p.changesLabel ?? 'changes'} tone="dim" size={20} /></span>}
      </div>
      <div style={{...blk('q'), background: C.ink, display: 'flex', alignItems: 'center', padding: '0 16px', gap: 10}}>
        <span style={{fontFamily: inter, fontWeight: 800, fontSize: 26, color: C.white, whiteSpace: 'nowrap'}}>Q: {p.q ?? 'the question'}</span>
        {p.changesAt !== undefined && f >= p.changesAt && <span style={{marginLeft: 'auto', ...popIn(f, p.changesAt + 6)}}><Tag label={p.changesLabel ?? 'changes'} tone="dim" size={20} /></span>}
      </div>
      {/* the 5,000-token bracket + lock on the static blocks */}
      {(lock > 0.01 || pulse > 0.01) && (() => {
        const y0 = lerp(A.y.sys, B.y.sys, t), y1 = lerp(A.y.tools, B.y.tools, t) + H.tools;
        return (
          <div style={{position: 'absolute', left: p.w - 6, top: y0, height: y1 - y0, width: 70, display: 'flex', alignItems: 'center', opacity: Math.max(lock, pulse)}}>
            <div style={{position: 'absolute', left: 4, top: 4, bottom: 4, width: 16, borderTop: `4px solid ${C.orange}`, borderBottom: `4px solid ${C.orange}`, borderRight: `4px solid ${C.orange}`, borderRadius: '0 8px 8px 0'}} />
            {lock > 0.01 && <div style={{position: 'absolute', left: 30, transform: `scale(${0.6 + 0.4 * lock})`, background: C.orange, borderRadius: 12, padding: 6, border: BORDER}}><IconLock size={44} color={C.white} /></div>}
          </div>
        );
      })()}
      {p.lockLabel && lock > 0.01 && <div style={{position: 'absolute', left: PAD, right: PAD, top: -58, display: 'flex', justifyContent: 'flex-end', ...popIn(f, (p.lockAt ?? 0) + 6)}}>{p.lockLabel}</div>}
      {/* reading cursor */}
      {cur >= 0 && (
        <div style={{position: 'absolute', left: 44, right: 8, top: PAD + cur * (total - PAD * 2) - 3, height: 6, background: C.orange, borderRadius: 3, boxShadow: `0 0 0 4px rgba(228,87,46,.2)`}}>
          <div style={{position: 'absolute', left: -34, top: -18, fontFamily: inter, fontWeight: 900, fontSize: 30, color: C.orange}}>▶</div>
        </div>
      )}
    </div>
  );
};
