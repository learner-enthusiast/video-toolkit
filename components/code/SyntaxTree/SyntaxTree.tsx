// Spec: components/specs/SyntaxTree.md · a source file, then its syntax tree unfolding node by node (tree-sitter / AST).
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {pop, ease, enter} from '../anim';

export type TNode = {id: string; label: string; kind: string; x: number; y: number; parent?: string; at: number};
/** kinds drawn filled orange (the ones the story points at) */
const HOT = ['class', 'call'];
export const SyntaxTree: React.FC<{file: string; code: string[]; codeAt: number; nodes: TNode[]; w?: number; codeSize?: number}> = ({file, code, codeAt, nodes, w = 760, codeSize = 28}) => {
  const f = useCurrentFrame();
  const N = Object.fromEntries(nodes.map((n) => [n.id, n]));
  return (
    <>
      <div style={{position: 'absolute', left: 0, top: 0, width: w, ...enter(f, codeAt)}}>
        <div style={{borderRadius: R, border: BORDER, background: C.white, boxShadow: SHADOW, overflow: 'hidden'}}>
          <div style={{padding: '8px 18px', borderBottom: BORDER, background: C.fill, fontFamily: mono, fontWeight: 700, fontSize: 22, color: C.dim}}>{file}</div>
          <div style={{padding: '14px 20px'}}>
            {code.map((l, i) => <div key={i} style={{fontFamily: mono, fontWeight: 600, fontSize: codeSize, color: C.ink, whiteSpace: 'pre', lineHeight: 1.4}}>{l}</div>)}
          </div>
        </div>
      </div>
      <svg width={w} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {nodes.filter((n) => n.parent && f >= n.at - 4).map((n) => {
          const p = N[n.parent!];
          const t = ease(f, n.at - 4, n.at + 6);
          return <line key={n.id} x1={p.x} y1={p.y + 30} x2={p.x + (n.x - p.x) * t} y2={p.y + 30 + (n.y - 60 - p.y) * t} stroke={C.border} strokeWidth={3.5} strokeLinecap="round" />;
        })}
      </svg>
      {nodes.map((n) => {
        if (f < n.at - 1) return null;
        const v = pop(f, n.at);
        const hot = HOT.includes(n.kind);
        return (
          <div key={n.id} style={{position: 'absolute', left: n.x, top: n.y, transform: `translate(-50%,-50%) scale(${0.8 + 0.2 * v})`, opacity: Math.min(1, v * 1.4)}}>
            <div style={{padding: '8px 16px', borderRadius: 12, border: BORDER, background: hot ? C.orange : C.white, color: hot ? C.white : C.ink, boxShadow: SHADOW, textAlign: 'center', whiteSpace: 'nowrap'}}>
              <div style={{fontFamily: inter, fontWeight: 700, fontSize: 18, opacity: 0.75, textTransform: 'uppercase', letterSpacing: '0.06em'}}>{n.kind}</div>
              <div style={{fontFamily: mono, fontWeight: 700, fontSize: 24}}>{n.label}</div>
            </div>
          </div>
        );
      })}
    </>
  );
};
