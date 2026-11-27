// Spec: components/specs/CalendarFlip.md · days flip in on their words; the same item stack slides in again, greyer each day.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {sp, enter, popIn} from '../anim';
import {WarnMark} from '../glyphs';
import {Tag} from '../Tag/Tag';

export const CalendarFlip: React.FC<{days: {label: string; at: number}[]; files: string[]; sub?: string; again?: string; forgetAt?: number; forgetText?: string; w?: number; forgetY?: number; ghostAt?: number}> = ({days, files, sub = 'new session', again = 'read again', forgetAt, forgetText = 'architecture: forgotten', w = 972, forgetY = 720, ghostAt}) => {
  const f = useCurrentFrame();
  const colW = 292, gap = (w - 60 - colW * days.length) / Math.max(1, days.length - 1);
  return (
    <>
      {/* ghostAt: dashed placeholders where the days will land, so the card is never empty before the first day word */}
      {ghostAt !== undefined && days.map((d, i) => f >= ghostAt - 1 && f < d.at + 6 ? (
        <div key={`g${i}`} style={{position: 'absolute', left: 30 + i * (colW + gap), top: 60, width: colW, height: 128, boxSizing: 'border-box', borderRadius: R, border: `3px dashed ${C.textDim}`, opacity: Math.min(enter(f, ghostAt + i * 4).opacity as number, 1 - Math.min(1, Math.max(0, (f - d.at) / 6))), display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: inter, fontWeight: 800, fontSize: 30, color: C.textDim}}>session {i + 1}</div>
      ) : null)}
      {days.map((d, i) => {
        if (f < d.at - 1) return null;
        const flip = sp(f, d.at, {damping: 13, stiffness: 120});
        const grey = i / Math.max(1, days.length - 1);
        return (
          <div key={d.label} style={{position: 'absolute', left: 30 + i * (colW + gap), top: 60, width: colW}}>
            <div style={{transform: `perspective(900px) rotateX(${(1 - flip) * -85}deg)`, transformOrigin: 'top center', opacity: Math.min(1, flip * 2)}}>
              <div style={{borderRadius: R, border: BORDER, background: C.surface, boxShadow: SHADOW, overflow: 'hidden'}}>
                <div style={{background: C.accent, borderBottom: BORDER, padding: '10px 0', textAlign: 'center', fontFamily: inter, fontWeight: 900, fontSize: 50, color: C.onAccent}}>{d.label}</div>
                <div style={{padding: '10px 0 14px', textAlign: 'center', fontFamily: inter, fontWeight: 700, fontSize: 26, color: C.textDim}}>{sub}</div>
              </div>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: 18, marginTop: 30}}>
              {files.map((fl, j) => (
                <div key={fl} style={{...enter(f, d.at + 6 + j * 4, 1e9, 30), padding: '16px 12px', borderRadius: 10, border: `2px solid ${grey > 0.5 ? C.textDim : C.border}`, background: C.surface, fontFamily: mono, fontWeight: 700, fontSize: 22, color: grey > 0.5 ? C.textDim : C.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{fl}</div>
              ))}
            </div>
            {i > 0 && f >= d.at + 6 + files.length * 4 && (
              <div style={{marginTop: 14, display: 'flex', justifyContent: 'center', ...popIn(f, d.at + 8 + files.length * 4)}}><Tag label={again} tone="dim" size={26} /></div>
            )}
          </div>
        );
      })}
      {forgetAt !== undefined && f >= forgetAt - 1 && (
        <div style={{position: 'absolute', left: 0, top: forgetY, width: w, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, ...enter(f, forgetAt)}}>
          <WarnMark size={60} at={forgetAt} />
          <Tag label={forgetText} tone="outline" size={36} />
        </div>
      )}
    </>
  );
};
