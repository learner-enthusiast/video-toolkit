// Spec: components/specs/BillCard.md · first built for system-design-of-ai/09-prompt-caching. Every text, number and asset is a prop.
import React from 'react';
import {C, R, BORDER, SHADOW, inter, mono} from '../theme';
import {Logo} from '../glyphs';
import {Tag} from '../Tag/Tag';

/** Provider bill card: logo + title header, a total (optionally blurred, or struck old amount above an orange new one) and a mono line item. */
export const BillCard: React.FC<{amount: React.ReactNode; blur?: number; line?: React.ReactNode; w?: number; strike?: React.ReactNode; logo?: string; title?: React.ReactNode; tag?: string; totalLabel?: string}> = ({amount, blur = 0, line, w = 560, strike, logo, title = 'API usage · this month', tag, totalLabel = 'TOTAL'}) => (
  <div style={{width: w, background: C.surface, border: BORDER, borderRadius: R, boxShadow: SHADOW, overflow: 'hidden'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '14px 20px', background: C.paper, borderBottom: `2px solid ${C.grid}`}}>
      {logo && <Logo file={logo} w={40} h={40} />}
      <span style={{fontFamily: inter, fontWeight: 800, fontSize: 28, color: C.text}}>{title}</span>
      {tag && <span style={{marginLeft: 'auto'}}><Tag label={tag} tone="dim" size={20} /></span>}
    </div>
    <div style={{padding: '18px 22px', display: 'flex', flexDirection: 'column', gap: 6}}>
      <span style={{fontFamily: inter, fontWeight: 700, fontSize: 22, color: C.textDim, letterSpacing: '0.08em'}}>{totalLabel}</span>
      {strike && <span style={{fontFamily: inter, fontWeight: 900, fontSize: 44, color: C.textDim, textDecoration: 'line-through'}}>{strike}</span>}
      <span style={{fontFamily: inter, fontWeight: 900, fontSize: 72, color: strike ? C.accent : C.text, filter: blur > 0 ? `blur(${blur * 16}px)` : undefined, lineHeight: 1.05, whiteSpace: 'nowrap'}}>{amount}</span>
      {line && <span style={{fontFamily: mono, fontWeight: 700, fontSize: 22, color: C.text}}>{line}</span>}
    </div>
  </div>
);
