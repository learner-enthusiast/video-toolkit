// Spec: components/specs/ThresholdRing.md · orange ring that draws itself, then springs between radii as the threshold moves.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, orangeA, inter} from '../theme';
import {sp, ease} from '../anim';

export const ThresholdRing: React.FC<{x: number; y: number; r: number; at: number; out?: number; steps?: {at: number; r: number}[]; dashed?: boolean; label?: string; labelAt?: number; width?: number}> = ({x, y, r, at, out = 1e9, steps = [], dashed, label, labelAt, width = 5}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const draw = ease(f, at, at + 14);
  let rad = r;
  for (const s of steps) if (f >= s.at) rad = rad + (s.r - rad) * Math.min(1.04, sp(f, s.at, {damping: 13, stiffness: 90}));
  const o = ease(f, out - 8, out, 1, 0);
  const circ = 2 * Math.PI * rad;
  const la = labelAt ?? at;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: o, pointerEvents: 'none'}} width={1} height={1}>
      <circle cx={x} cy={y} r={rad} fill={orangeA(0.08 * draw)} stroke={C.orange} strokeWidth={width} strokeDasharray={dashed ? '14 10' : `${circ}`} strokeDashoffset={dashed ? 0 : circ * (1 - draw)} transform={`rotate(-90 ${x} ${y})`} strokeLinecap="round" opacity={dashed ? draw : 1} />
      {label && f >= la && (
        <g opacity={ease(f, la, la + 8)}>
          <line x1={x + rad * 0.7071} y1={y - rad * 0.7071} x2={x + rad * 0.7071 + 34} y2={y - rad * 0.7071 - 34} stroke={C.orange} strokeWidth={3} />
          <text x={x + rad * 0.7071 + 40} y={y - rad * 0.7071 - 38} fontFamily={inter} fontWeight={800} fontSize={24} fill={C.orange}>{label}</text>
        </g>
      )}
    </svg>
  );
};
