// Spec: components/specs/IncidentCard.md · first built for system-design-of-ai/06-cancellation. Every text, number and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, headline} from '../theme';
import {ease, popIn, enter, bump} from '../anim';
import {Tag} from '../Tag/Tag';
import {Logo} from '../glyphs';

export const IncidentCard: React.FC<{w?: number; tag: string; rows: {text: string; at: number}[]; stat: {value: string; unit: string; at: number; from?: number; to?: number}; source: {text: string; at: number; logo?: {file: string; w: number; h: number}}; children?: React.ReactNode; at: number; out?: number}> = ({w = 892, tag, rows, stat, source, children, at, out = 1e9}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const sv = f >= stat.at ? ease(f, stat.at, stat.at + 14) : 0;
  const shown = stat.to !== undefined ? `${Math.round((stat.from ?? 0) + (stat.to - (stat.from ?? 0)) * sv).toLocaleString('en-IN')}+` : stat.value;
  return (
    <div style={{width: w, boxSizing: 'border-box', background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, padding: '26px 34px 22px', ...enter(f, at, out)}}>
      <Tag label={<><span style={{width: 12, height: 12, borderRadius: 99, background: C.accent}} />{tag}</>} tone="ink" size={24} />
      <div style={{display: 'flex', flexDirection: 'column', gap: 12, marginTop: 22}}>
        {rows.map((r) => f >= r.at - 1 && (
          <div key={r.text} style={{display: 'flex', alignItems: 'center', gap: 16, ...enter(f, r.at, 1e9, 14)}}>
            <div style={{width: 10, height: 38, borderRadius: 4, background: C.accent}} />
            <span style={{fontFamily: inter, fontWeight: 700, fontSize: 42, color: C.text, whiteSpace: 'nowrap'}}>{r.text}</span>
          </div>
        ))}
      </div>
      {f >= stat.at - 1 && (
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 0, marginTop: 18, ...popIn(f, stat.at)}}>
          <span style={{fontFamily: inter, fontWeight: 900, fontSize: 150, lineHeight: 1, color: C.accent, fontVariantNumeric: 'tabular-nums', transform: `scale(${bump(f, stat.at + 14)})`, transformOrigin: 'left bottom', display: 'inline-block'}}>{shown}</span>
          <span style={{...headline, fontSize: 64, color: C.text, whiteSpace: 'nowrap'}}>{stat.unit}</span>
        </div>
      )}
      {children}
      {f >= source.at - 1 && (
        <div style={{display: 'flex', alignItems: 'center', gap: 12, marginTop: 20, paddingTop: 14, borderTop: `2px dashed ${C.grid}`, opacity: ease(f, source.at, source.at + 8)}}>
          {source.logo && <Logo file={source.logo.file} w={source.logo.w} h={source.logo.h} />}
          <span style={{fontFamily: inter, fontWeight: 600, fontSize: 26, color: C.textDim, whiteSpace: 'nowrap'}}>{source.text}</span>
        </div>
      )}
    </div>
  );
};
