// Spec: components/specs/TicketCard.md · a Jira/Linear-style ticket with an orange stub; optional DONE stamp for the payoff.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter, whiteA} from '../theme';
import {sp, popIn} from '../anim';
import {Tag} from '../Tag/Tag';

export const TicketCard: React.FC<{id: string; title: string; meta?: string; kicker?: string; at: number; w?: number; size?: number; done?: number; doneText?: string}> = ({id, title, meta, kicker = 'Your first ticket', at, w = 760, size = 50, done, doneText = 'DONE'}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const v = sp(f, at);
  return (
    <div style={{position: 'relative', width: w, opacity: Math.min(1, v * 1.4), transform: `translateY(${(1 - v) * 30}px) rotate(${(1 - v) * -2}deg)`}}>
      <div style={{display: 'flex', borderRadius: R, border: BORDER, background: C.surface, boxShadow: SHADOW, overflow: 'hidden'}}>
        <div style={{width: 22, background: C.accent, borderRight: BORDER}} />
        <div style={{flex: 1, padding: '24px 30px', display: 'flex', flexDirection: 'column', gap: 12}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
            <Tag label={id} tone="ink" size={28} monoFont />
            {kicker && <span style={{fontFamily: inter, fontWeight: 700, fontSize: 26, color: C.textDim, letterSpacing: '0.08em', textTransform: 'uppercase'}}>{kicker}</span>}
          </div>
          <div style={{fontFamily: inter, fontWeight: 900, fontSize: size, color: C.text, lineHeight: 1.05}}>{title}</div>
          {meta && <div style={{fontFamily: inter, fontWeight: 600, fontSize: 26, color: C.textDim}}>{meta}</div>}
        </div>
      </div>
      {done !== undefined && f >= done - 1 && (
        <div style={{position: 'absolute', right: 26, top: '50%', marginTop: -44}}>
          <div style={{...popIn(f, done), transformOrigin: 'center'}}>
            <div style={{transform: 'rotate(-8deg)', padding: '8px 26px', border: `5px solid ${C.accent}`, borderRadius: R, color: C.accent, fontFamily: inter, fontWeight: 900, fontSize: 52, letterSpacing: '0.06em', background: whiteA(0.9)}}>{doneText}</div>
          </div>
        </div>
      )}
    </div>
  );
};
