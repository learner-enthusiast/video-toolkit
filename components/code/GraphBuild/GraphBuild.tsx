// Spec: components/specs/GraphBuild.md · nodes pop, edges draw, clusters wrap, tags label edges.
// One node map serves a hop trail (ordered hops with travelling packet), a full graph, a god-node pulse and a blast radius.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, SHADOW, mono, inter, orangeA, whiteA} from '../theme';
import {sp, pop, ease} from '../anim';

export type GNode = {id: string; label: string; x: number; y: number; w?: number};
export type GEdge = {a: string; b: string; at: number; dashed?: boolean; tone?: 'ink' | 'orange' | 'dim'; arrow?: boolean; dur?: number; hot?: boolean}; // hot: never dimmed
export type GCluster = {label: string; ids: string[]; at: number; pad?: number};
export type GTag = {edge: [string, string]; text: string; at: number; tone?: 'ink' | 'orange'; dx?: number; dy?: number};

const NH = 70;
const box = (n: GNode, nw: number) => ({x: n.x - (n.w ?? nw) / 2, y: n.y - NH / 2, w: n.w ?? nw, h: NH});
/** point where the segment from a's centre to b's centre leaves a's box (edge-to-edge connectors) */
const exitPt = (a: GNode, b: GNode, nw: number, gap = 8) => {
  const bx = box(a, nw);
  const dx = b.x - a.x, dy = b.y - a.y;
  const hw = bx.w / 2 + gap, hh = bx.h / 2 + gap;
  const t = Math.min(dx ? hw / Math.abs(dx) : 1e9, dy ? hh / Math.abs(dy) : 1e9);
  return {x: a.x + dx * t, y: a.y + dy * t};
};

export const GraphBuild: React.FC<{
  nodes: GNode[];
  show: Record<string, number>; // node id -> frame it pops (missing = hidden)
  edges?: GEdge[];
  clusters?: GCluster[];
  tags?: GTag[];
  lit?: {ids: string[]; at: number; out?: number}; // ring these nodes orange
  dimOthers?: {at: number; out?: number}; // dim nodes/edges not in lit
  pulse?: {id: string; at: number}; // god node: pulsing ring
  packet?: {path: string[]; at: number; per: number}; // orange dot travelling hop by hop
  nodeW?: number;
  size?: number;
  w?: number;
  h?: number;
  dark?: boolean;
}> = ({nodes, show, edges = [], clusters = [], tags = [], lit, dimOthers, pulse, packet, nodeW = 280, size = 22, w = 972, h = 970, dark}) => {
  const f = useCurrentFrame();
  const N = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const litOn = lit ? Math.min(ease(f, lit.at, lit.at + 8), lit.out ? ease(f, lit.out - 8, lit.out, 1, 0) : 1) : 0;
  const dimOn = dimOthers ? Math.min(ease(f, dimOthers.at, dimOthers.at + 10), dimOthers.out ? ease(f, dimOthers.out - 8, dimOthers.out, 1, 0) : 1) : 0;
  const isLit = (id: string) => !!lit && lit.ids.includes(id);
  const ink = dark ? whiteA(0.75) : C.border;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: w, height: h}}>
      {/* clusters (behind) */}
      {clusters.map((c, i) => {
        if (f < c.at - 1) return null;
        const v = sp(f, c.at);
        const pad = c.pad ?? 22;
        const bs = c.ids.map((id) => box(N[id], nodeW));
        const x0 = Math.min(...bs.map((b) => b.x)) - pad, y0 = Math.min(...bs.map((b) => b.y)) - pad - 34;
        const x1 = Math.max(...bs.map((b) => b.x + b.w)) + pad, y1 = Math.max(...bs.map((b) => b.y + b.h)) + pad;
        return (
          <div key={i} style={{position: 'absolute', left: x0, top: y0, width: x1 - x0, height: y1 - y0, borderRadius: R + 8, border: `3px dashed ${C.orange}`, background: orangeA(dark ? 0.08 : 0.06), opacity: Math.min(1, v * 1.3) * (1 - 0.6 * dimOn), transform: `scale(${0.94 + 0.06 * v})`}}>
            <div style={{position: 'absolute', left: 18, top: 4, fontFamily: inter, fontWeight: 900, fontSize: 26, letterSpacing: '0.08em', textTransform: 'uppercase', color: C.orange}}>{c.label}</div>
          </div>
        );
      })}
      {/* edges */}
      <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          {['ink', 'orange', 'dim'].map((t) => (
            <marker key={t} id={`gb-ar-${t}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0 0 L10 5 L0 10 z" fill={t === 'orange' ? C.orange : t === 'dim' ? C.dim : ink} />
            </marker>
          ))}
        </defs>
        {edges.map((e, i) => {
          const A = N[e.a], B = N[e.b];
          if (!A || !B || f < e.at) return null;
          const p0 = exitPt(A, B, nodeW), p1 = exitPt(B, A, nodeW);
          const p = ease(f, e.at, e.at + (e.dur ?? 12));
          const lighted = e.hot ? 1 : lit && isLit(e.a) && isLit(e.b) ? litOn : 0;
          const tone = lighted > 0.5 ? 'orange' : e.tone ?? 'ink';
          const col = tone === 'orange' ? C.orange : tone === 'dim' ? C.dim : ink;
          const op = 1 - 0.75 * dimOn * (lighted > 0.5 ? 0 : 1);
          const len = Math.hypot(p1.x - p0.x, p1.y - p0.y);
          return (
            <line key={i} x1={p0.x} y1={p0.y} x2={p0.x + (p1.x - p0.x) * p} y2={p0.y + (p1.y - p0.y) * p} stroke={col} strokeWidth={tone === 'orange' ? 6 : 4} strokeLinecap="round"
              strokeDasharray={e.dashed ? '14 12' : undefined} opacity={op} markerEnd={e.arrow !== false && p > 0.95 ? `url(#gb-ar-${tone})` : undefined} data-len={len} />
          );
        })}
      </svg>
      {/* packet */}
      {packet && (() => {
        const k = (f - packet.at) / packet.per;
        if (k < 0 || k >= packet.path.length - 1) return null;
        const i = Math.floor(k), t = ease(k - i, 0.1, 0.9);
        const A = N[packet.path[i]], B = N[packet.path[i + 1]];
        return <div style={{position: 'absolute', left: A.x + (B.x - A.x) * t - 13, top: A.y + (B.y - A.y) * t - 13, width: 26, height: 26, borderRadius: 13, background: C.orange, border: `3px solid ${C.white}`, boxShadow: `0 0 0 3px ${orangeA(0.35)}`}} />;
      })()}
      {/* nodes */}
      {nodes.map((n) => {
        const t0 = show[n.id];
        if (t0 === undefined || f < t0 - 1) return null;
        const v = pop(f, t0);
        const b = box(n, nodeW);
        const on = isLit(n.id) ? litOn : 0;
        const dm = isLit(n.id) ? 0 : dimOn;
        const pu = pulse && pulse.id === n.id && f >= pulse.at ? 0.5 + 0.5 * Math.sin((f - pulse.at) / 4.5) : 0;
        const puOn = pulse && pulse.id === n.id ? ease(f, pulse.at, pulse.at + 8) : 0;
        return (
          <div key={n.id} style={{position: 'absolute', left: b.x, top: b.y, width: b.w, height: b.h, boxSizing: 'border-box', borderRadius: R, background: on > 0.5 || puOn > 0.5 ? C.orange : dark ? C.darkPanel : C.white,
            border: `${on > 0.5 || puOn > 0.5 ? 3 : 2}px solid ${on > 0.5 || puOn > 0.5 ? C.border : ink}`, boxShadow: puOn > 0 ? `0 0 0 ${8 + pu * 16}px ${orangeA(0.35 - pu * 0.2)}` : dark ? 'none' : SHADOW,
            opacity: Math.min(1, v * 1.4) * (1 - 0.65 * dm), transform: `scale(${(0.82 + 0.18 * v) * (1 + 0.04 * on)})`, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: mono, fontWeight: 700, fontSize: size, color: on > 0.5 || puOn > 0.5 ? C.white : dark ? C.white : C.ink, whiteSpace: 'nowrap'}}>
            {n.label}
          </div>
        );
      })}
      {/* edge tags */}
      {tags.map((t, i) => {
        if (f < t.at - 1) return null;
        const A = N[t.edge[0]], B = N[t.edge[1]];
        const v = pop(f, t.at);
        const mx = (A.x + B.x) / 2 + (t.dx ?? 0), my = (A.y + B.y) / 2 + (t.dy ?? 0);
        return (
          <div key={i} style={{position: 'absolute', left: mx, top: my, transform: `translate(-50%,-50%) scale(${0.8 + 0.2 * v})`, opacity: Math.min(1, v * 1.4) * (1 - 0.6 * dimOn)}}>
            <div style={{padding: '6px 16px', borderRadius: 999, border: `2px solid ${C.border}`, background: t.tone === 'orange' ? C.orange : C.white, color: t.tone === 'orange' ? C.white : C.ink, fontFamily: inter, fontWeight: 800, fontSize: 24, whiteSpace: 'nowrap', boxShadow: SHADOW}}>{t.text}</div>
          </div>
        );
      })}
    </div>
  );
};
