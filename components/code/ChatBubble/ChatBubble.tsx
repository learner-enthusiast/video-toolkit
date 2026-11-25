// Spec: components/specs/ChatBubble.md · first built for system-design-of-ai/11-max-tokens-and-truncation (from the SDAI chat bubble). Every text and timing is a prop.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, R, BORDER, SHADOW, inter} from '../theme';
import {sp, ease} from '../anim';

/** user (near-black, right) or assistant (white, left) bubble; `typeTo` types the text in; `children` adds a trailing mark (e.g. an orange tick) */
export const ChatBubble: React.FC<{role: 'user' | 'bot'; text: string; at: number; typeTo?: number; out?: number; w?: number; size?: number; dark?: boolean; dim?: boolean; children?: React.ReactNode; style?: React.CSSProperties}> = ({role, text, at, typeTo, out = 1e9, w, size = 38, dark, dim, children, style}) => {
  const f = useCurrentFrame();
  if (f < at - 1) return null;
  const v = sp(f, at);
  const o = Math.min(v, ease(f, out - 8, out, 1, 0));
  const n = typeTo === undefined ? text.length : Math.round(ease(f, at + 2, typeTo) * 0 + Math.max(0, Math.min(1, (f - at - 1) / Math.max(1, typeTo - at - 1))) * text.length);
  const typing = typeTo !== undefined && f < typeTo + 6;
  const caret = typing && Math.floor(f / 8) % 2 === 0;
  const user = role === 'user';
  return (
    <div style={{opacity: o, transform: `translateY(${(1 - v) * 20}px) scale(${0.96 + 0.04 * v})`, transformOrigin: user ? 'right bottom' : 'left bottom', display: 'flex', justifyContent: user ? 'flex-end' : 'flex-start', ...style}}>
      <div style={{position: 'relative', width: w, maxWidth: w ? undefined : 760, boxSizing: 'border-box', padding: `${size * 0.5}px ${size * 0.7}px`, borderRadius: R, borderBottomRightRadius: user ? 4 : R, borderBottomLeftRadius: user ? R : 4, background: user ? C.ink : dark ? '#1B1B1B' : C.white, border: user ? BORDER : dark ? '2px solid rgba(255,255,255,.5)' : BORDER, boxShadow: dark ? 'none' : SHADOW, color: user ? C.white : dim ? C.dim : dark ? C.white : C.ink, fontFamily: inter, fontWeight: 600, fontSize: size, lineHeight: 1.22, display: 'flex', alignItems: 'center', gap: 14}}>
        <span style={{whiteSpace: w && text.length < 24 ? 'nowrap' : undefined}}>
          {text.slice(0, n)}
          <span style={{opacity: caret ? 1 : 0, color: C.orange}}>|</span>
        </span>
        {children}
      </div>
    </div>
  );
};

