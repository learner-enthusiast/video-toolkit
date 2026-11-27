// Spec: components/specs/Checklist.md · rows with an orange tick that draws itself, one row per spoken item.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, inter} from '../theme';
import {sp, enter} from '../anim';
import {Tick} from '../glyphs';

export type ChecklistItem = {text: string; at: number};
export const Checklist: React.FC<{items: ChecklistItem[]; size?: number; gap?: number}> = ({items, size = 44, gap = 14}) => {
  const f = useCurrentFrame();
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap}}>
      {items.map((it, i) => (
        <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16, ...enter(f, it.at, 1e9, 0), transform: `translateX(${(1 - sp(f, it.at)) * -24}px)`}}>
          <Tick at={it.at + 2} size={size * 1.05} />
          <span style={{fontFamily: inter, fontWeight: 800, fontSize: size, color: C.text, whiteSpace: 'nowrap'}}>{it.text}</span>
        </div>
      ))}
    </div>
  );
};
