// Spec: components/specs/TradeScale.md · a balance scale: two pans that pop when each side is named, beam tilted by `angle`.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, headline} from '../theme';
import {ease, popIn} from '../anim';
import {DarkCtx} from '../glyphs';

export const TradeScale: React.FC<{x: number; y: number; at: number; angle: number; left: React.ReactNode; right: React.ReactNode; leftAt: number; rightAt: number; half?: number; label?: string}> = ({x, y, at, angle, left, right, leftAt, rightAt, half = 260, label}) => {
  const f = useCurrentFrame();
  const draw = ease(f, at, at + 14);
  const ang = (angle * Math.PI) / 180;
  const lx = x - half * Math.cos(ang), ly = y - half * Math.sin(ang);
  const rx = x + half * Math.cos(ang), ry = y + half * Math.sin(ang);
  const dark = React.useContext(DarkCtx);
  const ink = dark ? C.onPunch : C.text;
  const pan = (px: number, py: number) => `M ${px - 120} ${py + 90} Q ${px} ${py + 150} ${px + 120} ${py + 90} Z`;
  return (
    <>
      <svg width={1} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <g opacity={draw}>
          <path d={`M ${x - 90} ${y + 300} H ${x + 90}`} stroke={ink} strokeWidth={6} strokeLinecap="round" />
          <path d={`M ${x} ${y + 300} V ${y}`} stroke={ink} strokeWidth={6} />
          <line x1={lx} y1={ly} x2={rx} y2={ry} stroke={ink} strokeWidth={7} strokeLinecap="round" />
          <circle cx={x} cy={y} r={11} fill={C.accent} stroke={ink} strokeWidth={3} />
          {[[lx, ly], [rx, ry]].map(([px, py], i) => (
            <g key={i}>
              <path d={`M ${px} ${py} L ${px - 110} ${py + 90} M ${px} ${py} L ${px + 110} ${py + 90}`} stroke={ink} strokeWidth={3} />
              <path d={pan(px, py)} fill={dark ? C.darkPanel : C.surface} stroke={ink} strokeWidth={4} />
            </g>
          ))}
        </g>
      </svg>
      {label && <div style={{position: 'absolute', left: x, top: y - 70, transform: 'translateX(-50%)', opacity: draw, ...headline, fontSize: 50, color: C.accent, whiteSpace: 'nowrap'}}>{label}</div>}
      <div style={{position: 'absolute', left: lx, top: ly + 92, transform: 'translate(-50%,-100%)'}}><div style={popIn(f, leftAt)}>{f >= leftAt - 1 && left}</div></div>
      <div style={{position: 'absolute', left: rx, top: ry + 92, transform: 'translate(-50%,-100%)'}}><div style={popIn(f, rightAt)}>{f >= rightAt - 1 && right}</div></div>
    </>
  );
};
