// Spec: components/specs/Tag.md · pill / chip for keywords, verbs and icon-less tech names.
// Library rules: tokens from ../theme, text and timings come in through props.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, BORDER, inter, mono} from '../theme';
import {popIn} from '../anim';

export type TagTone = 'orange' | 'ink' | 'dim' | 'outline';

/** Static pill. tone: orange (filled), ink (filled dark), dim (grey = "bad"), outline (white) */
export const Tag: React.FC<{label: React.ReactNode; tone?: TagTone; size?: number; monoFont?: boolean; style?: React.CSSProperties}> = ({label, tone = 'outline', size = 34, monoFont, style}) => {
  const bg = tone === 'orange' ? C.accent : tone === 'ink' ? C.inkFill : tone === 'dim' ? C.tint : C.surface;
  const fg = tone === 'orange' ? C.onAccent : tone === 'ink' ? C.onInk : tone === 'dim' ? C.textDim : C.text;
  return (
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 10, padding: `${size * 0.32}px ${size * 0.62}px`, borderRadius: 999, border: tone === 'dim' ? `2px solid ${C.textDim}` : BORDER, background: bg, color: fg, fontFamily: monoFont ? mono : inter, fontWeight: monoFont ? 600 : 800, fontSize: size, lineHeight: 1, whiteSpace: 'nowrap', ...style}}>
      {label}
    </div>
  );
};

/** Tag that pops in at frame `at` and fades out ending at `out`. `anchor` center centres it on x. */
export const TagPop: React.FC<{x: number; y: number; at: number; out?: number; label: React.ReactNode; tone?: TagTone; size?: number; monoFont?: boolean; anchor?: 'left' | 'center'}> = ({x, y, at, out, label, tone, size, monoFont, anchor = 'left'}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: anchor === 'center' ? 'translateX(-50%)' : undefined}}>
      <div style={{...popIn(f, at, out), transformOrigin: 'center'}}>
        <Tag label={label} tone={tone} size={size} monoFont={monoFont} />
      </div>
    </div>
  );
};
