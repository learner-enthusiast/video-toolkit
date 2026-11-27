// Spec: components/specs/CamFrame.md · Brand 2 signature: CCTV viewfinder overlay that fills its parent.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, FPS, mono} from '../../theme';
import {enter, ease} from '../../anim';

/** "dd-mm-yyyy hh:mm:ss" plus `secs` seconds */
const tick = (start: string, secs: number) => {
  const [d, mo, y, h, mi, s] = start.split(/[-: ]/).map(Number);
  const t = new Date(Date.UTC(y, mo - 1, d, h, mi, s + secs));
  const p = (n: number) => String(n).padStart(2, '0');
  return `${p(t.getUTCDate())}-${p(t.getUTCMonth() + 1)}-${t.getUTCFullYear()} ${p(t.getUTCHours())}:${p(t.getUTCMinutes())}:${p(t.getUTCSeconds())}`;
};

export const CamFrame: React.FC<{cam: number; startTime: string; kicker?: string; at: number; out?: number}> = ({cam, startTime, kicker, at, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1 || f > out + 1) return null;
  const o = ease(f, at, at + 8) * ease(f, out - 8, out, 1, 0);
  const m = 54, len = 70, line = `4px solid ${C.text}`;
  const text: React.CSSProperties = {position: 'absolute', fontFamily: mono, fontWeight: 700, fontSize: 30, color: C.text, letterSpacing: '0.08em', whiteSpace: 'nowrap'};
  const blink = 0.35 + 0.65 * (0.5 + 0.5 * Math.cos((Math.max(0, f - at) / FPS) * Math.PI * 2));
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o, pointerEvents: 'none'}}>
      {([['top', 'left'], ['top', 'right'], ['bottom', 'left'], ['bottom', 'right']] as const).map(([v, h]) => {
        const edge = {[v === 'top' ? 'borderTop' : 'borderBottom']: line, [h === 'left' ? 'borderLeft' : 'borderRight']: line};
        return <div key={v + h} style={{position: 'absolute', [v]: m, [h]: m, width: len, height: len, ...edge}} />;
      })}
      <div style={{...text, left: m + 28, top: m + 24, display: 'flex', alignItems: 'center', gap: 14}}>
        <span style={{width: 20, height: 20, borderRadius: 99, background: C.alert, opacity: blink}} />REC
      </div>
      <div style={{...text, right: m + 28, top: m + 24}}>CAM {String(cam).padStart(2, '0')}</div>
      {kicker && <div style={{...text, left: m + 28, top: m + 78, fontSize: 22, color: C.accent, textTransform: 'uppercase', letterSpacing: '0.2em', ...enter(f, at + 6, out, 10)}}>— {kicker}</div>}
      <div style={{...text, left: m + 28, bottom: m + 24, fontVariantNumeric: 'tabular-nums'}}>{tick(startTime, Math.max(0, Math.floor((f - at) / FPS)))}</div>
    </div>
  );
};
