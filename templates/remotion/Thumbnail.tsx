// Spec: components/specs/Thumbnail.md · Concept-first cover, a still. Copied to src/lib/ by tools/scaffold_remotion.py.
// The video's own scene goes in the `scene` slot, drawn in canvas coordinates. Every brand value comes from the theme.
// Register it as: <Composition id="Thumb" component={MyCover} width={1080} height={1920} fps={FPS} durationInFrames={1} />
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {BORDER, C, CANVAS, R, SHADOW, accentA, accent2A, blackA, gridBg, inter} from '../shared/theme';

export type Texture = 'none' | 'globe' | 'circuit' | 'document' | 'map' | 'planes';

/** my PNG with alpha. Measure these on the file, from its alpha bounding box, for every new photo. */
export type CutoutSource = {
  /** path under public/ */
  src: string;
  /** file size in px */
  w: number;
  h: number;
  /** top of my hair, source px */
  hairTop: number;
  /** centre of my face, source px */
  faceX: number;
};

export type CutoutPlacement = {
  /** where the top of my hair lands on the canvas */
  headY?: number;
  scale?: number;
  /** pin the file's edge to the canvas edge, for a boom arm that leaves the photo there */
  bleed?: 'left' | 'right';
};

export type ThumbnailProps = {
  cutout: CutoutSource;
  place?: CutoutPlacement;
  badge: {text: string; ep?: string};
  /** ≤ 3 lines */
  headline: string[];
  /** the key phrase; it must sit inside one headline line */
  hl: string;
  scene?: React.ReactNode;
  /** scene elements drawn over me, for what the boom cable would otherwise cross; never over my face */
  front?: React.ReactNode;
  texture?: Texture;
  sparks?: boolean;
  /** headline size in px; fitted to the longest line when left out */
  headlineSize?: number;
  size?: {w: number; h: number};
};

type Size = {w: number; h: number};

const layoutFor = ({w, h}: Size) =>
  w > h
    ? {badgeTop: 44, head: {top: 140, left: 64, width: w * 0.58, align: 'flex-start' as const}, font: [72, 96], faceAt: w * 0.78, headY: 150, scale: 0.42}
    : {badgeTop: 262, head: {top: 366, left: 0, width: w, align: 'center' as const}, font: [104, 124], faceAt: w / 2, headY: 1040, scale: 0.65};

/** spread into the one focal element of the scene: the brand's ring and glow */
export const focal: React.CSSProperties = {border: `4px solid ${C.accent2}`, borderColor: C.accent2, boxShadow: `0 0 0 8px ${accent2A(0.18)}, 0 0 56px 10px ${accent2A(0.45)}`};

const range = (n: number) => Array.from({length: n}, (_, i) => i);

const TextureArt: React.FC<{texture: Texture; size: Size}> = ({texture, size: {w, h}}) => {
  if (texture === 'none') return null;
  const cx = w / 2;
  const cy = h * 0.56;
  const art: Record<Exclude<Texture, 'none'>, React.ReactNode> = {
    globe: (
      <>
        <circle cx={cx} cy={cy} r={w * 0.56} />
        {[0.14, 0.3, 0.44].map((k) => <ellipse key={k} cx={cx} cy={cy} rx={w * k} ry={w * 0.56} />)}
        {[-0.36, -0.18, 0, 0.18, 0.36].map((k) => {
          const half = Math.sqrt(0.56 ** 2 - k ** 2) * w;
          return <ellipse key={k} cx={cx} cy={cy + k * w} rx={half} ry={half * 0.12} />;
        })}
      </>
    ),
    circuit: (
      <>
        {range(14).map((i) => {
          const y = h * 0.1 + i * h * 0.062;
          const left = i % 2 === 0;
          const x0 = left ? 0 : w;
          const x1 = left ? w * (0.14 + (i % 5) * 0.05) : w * (0.86 - (i % 4) * 0.06);
          const bend = left ? 60 : -60;
          return (
            <React.Fragment key={i}>
              <path d={`M${x0} ${y} H${x1} l${bend} 60 h${bend * 1.6}`} />
              <circle cx={x1 + bend * 2.6} cy={y + 60} r={9} />
            </React.Fragment>
          );
        })}
      </>
    ),
    document: (
      <>
        {range(34).map((i) => (
          <path key={i} strokeWidth={i % 9 === 0 ? 16 : 8} d={`M${w * 0.08} ${h * 0.08 + i * h * 0.026} h${w * (i % 9 === 0 ? 0.4 : 0.84 - ((i * 7) % 5) * 0.07)}`} />
        ))}
      </>
    ),
    map: (
      <>
        {range(9).map((i) => <path key={`a${i}`} d={`M0 ${h * 0.12 + i * h * 0.1} L${w} ${h * 0.05 + i * h * 0.1 + ((i * 5) % 4) * 40}`} />)}
        {range(7).map((i) => <path key={`b${i}`} d={`M${i * w * 0.17} 0 L${i * w * 0.17 + ((i * 3) % 5) * 70 - 140} ${h}`} />)}
        <path strokeWidth={18} d={`M0 ${h * 0.7} C${w * 0.3} ${h * 0.52} ${w * 0.6} ${h * 0.82} ${w} ${h * 0.6}`} />
      </>
    ),
    planes: (
      <>
        {range(5).map((i) => {
          const y = h * 0.3 + i * h * 0.13;
          return <path key={i} d={`M${w * 0.2} ${y} H${w * 0.96} L${w * 0.8} ${y + h * 0.075} H${w * 0.04} Z`} />;
        })}
      </>
    ),
  };
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" stroke={C.textDim} strokeWidth={3} style={{position: 'absolute', opacity: 0.16}}>
      {art[texture]}
    </svg>
  );
};

/** never flat: the brand's page pattern, the texture at low contrast and a vignette */
export const Background: React.FC<{texture?: Texture; size?: Size}> = ({texture = 'none', size = CANVAS}) => (
  <AbsoluteFill style={gridBg()}>
    <TextureArt texture={texture} size={size} />
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, transparent 58%, ${blackA(0.16)} 100%)`}} />
  </AbsoluteFill>
);

/** pill with an accent dot; the episode number sits on an accent chip */
export const Badge: React.FC<{text: string; ep?: string; top: number; left?: number}> = ({text, ep, top, left}) => (
  <div style={{position: 'absolute', top, left: left ?? 0, right: left === undefined ? 0 : undefined, display: 'flex', justifyContent: 'center'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 16, height: 66, padding: ep ? '0 10px 0 26px' : '0 28px', background: C.surface, border: BORDER, borderColor: C.line, borderRadius: R, boxShadow: SHADOW, fontFamily: inter, fontWeight: 800, fontSize: 30, letterSpacing: '0.06em', textTransform: 'uppercase', color: C.text, whiteSpace: 'nowrap'}}>
      <span style={{width: 18, height: 18, borderRadius: 999, background: C.accent}} />
      {text}
      {ep && <span style={{background: C.accent, color: C.onAccent, borderRadius: R - 4, padding: '7px 16px'}}>{ep}</span>}
    </div>
  </div>
);

const Sparks: React.FC = () => (
  <svg width={70} height={70} viewBox="0 0 70 70" fill="none" stroke={C.accent2} strokeWidth={6} strokeLinecap="round" style={{position: 'absolute', left: '100%', top: -4, marginLeft: 8}}>
    <path d="M10 28 L18 7" />
    <path d="M26 40 L50 22" />
    <path d="M32 58 L60 54" />
  </svg>
);

/** up to three heavy lines; `hl` sits on a tilted accent2 block; the sparks go beside the shortest line */
export const Headline: React.FC<{lines: string[]; hl: string; sparks?: boolean; fontSize?: number; size?: Size}> = ({lines, hl, sparks = true, fontSize, size = CANVAS}) => {
  if (lines.length > 3) throw new Error('Thumbnail headline: at most 3 lines');
  const hlLine = lines.findIndex((l) => l.includes(hl));
  if (!hl || hlLine < 0) throw new Error(`Thumbnail headline: "${hl}" is not inside one line`);
  const {head, font} = layoutFor(size);
  const longest = Math.max(...lines.map((l) => l.length));
  // 0.6 em is about one Inter 900 character; 120 px keeps the side margins and the block's padding
  const px = fontSize ?? Math.round(Math.max(font[0], Math.min(font[1], (head.width - 120) / (longest * 0.6))));
  const sparkAt = lines.reduce((best, l, i) => (l.length < lines[best].length ? i : best), 0);
  return (
    <div style={{position: 'absolute', top: head.top, left: head.left, width: head.width, display: 'flex', flexDirection: 'column', alignItems: head.align, fontFamily: inter, fontWeight: 900, fontSize: px, lineHeight: 0.98, letterSpacing: '-0.025em', color: C.text}}>
      {lines.map((line, i) => {
        const [before, after] = i === hlLine ? [line.slice(0, line.indexOf(hl)).trim(), line.slice(line.indexOf(hl) + hl.length).trim()] : [line, ''];
        return (
          <div key={i} style={{position: 'relative', display: 'flex', alignItems: 'center', gap: '0.24em', whiteSpace: 'nowrap', margin: i === hlLine ? '14px 0' : 0}}>
            {before && <span>{before}</span>}
            {i === hlLine && (
              <span style={{position: 'relative', padding: '0 24px', lineHeight: 1.18}}>
                <span style={{position: 'absolute', inset: 0, background: C.accent2, borderRadius: R, transform: 'skewX(-5deg)'}} />
                <span style={{position: 'relative', fontStyle: 'italic', color: C.onAccent}}>{hl}</span>
              </span>
            )}
            {after && <span>{after}</span>}
            {sparks && i === sparkAt && <Sparks />}
          </div>
        );
      })}
    </div>
  );
};

const placeCutout = (cutout: CutoutSource, place: CutoutPlacement, size: Size) => {
  const layout = layoutFor(size);
  const scale = place.scale ?? layout.scale;
  const width = cutout.w * scale;
  const left = place.bleed === 'right' ? size.w - width : place.bleed === 'left' ? 0 : layout.faceAt - cutout.faceX * scale;
  const headY = place.headY ?? layout.headY;
  return {left, top: headY - cutout.hairTop * scale, width, height: cutout.h * scale, headY, faceAt: left + cutout.faceX * scale};
};

/** me: a soft accent glow behind my shoulders and a thin rim light. Placed from the hair top, never stretched. */
export const Cutout: React.FC<{cutout: CutoutSource; place?: CutoutPlacement; size?: Size}> = ({cutout, place = {}, size = CANVAS}) => {
  const p = placeCutout(cutout, place, size);
  const glowY = p.headY + (size.w > size.h ? 330 : 500);
  // a side of the photo that ends inside the canvas is feathered; a side that reaches the canvas edge is left alone
  const fadeL = p.left > 1 ? 'transparent 0, black 70px' : 'black 0';
  const fadeR = p.left + p.width < size.w - 1 ? 'black calc(100% - 70px), transparent 100%' : 'black 100%';
  const mask = `linear-gradient(90deg, ${fadeL}, ${fadeR})`;
  const rim = [[2.5, 0], [-2.5, 0], [0, -2.5]].map(([x, y]) => `drop-shadow(${x}px ${y}px 0 ${C.accent})`).join(' ');
  return (
    <>
      <AbsoluteFill style={{background: [
        `radial-gradient(ellipse 380px 360px at ${p.faceAt}px ${glowY}px, ${accent2A(0.34)}, transparent 100%)`,
        `radial-gradient(ellipse 680px 640px at ${p.faceAt}px ${glowY}px, ${accentA(0.46)}, transparent 100%)`,
      ].join(', ')}} />
      <div style={{position: 'absolute', left: p.left, top: p.top, width: p.width, height: p.height, WebkitMaskImage: mask, maskImage: mask}}>
        <Img src={staticFile(cutout.src)} style={{width: '100%', height: '100%', filter: rim}} />
      </div>
    </>
  );
};

/** the whole cover. Order: background, scene, me (the scene may run behind), then the badge and headline on top. */
export const Thumbnail: React.FC<ThumbnailProps> = ({cutout, place, badge, headline, hl, scene, front, texture = 'none', sparks = true, headlineSize, size = CANVAS}) => {
  const layout = layoutFor(size);
  return (
    <AbsoluteFill>
      <Background texture={texture} size={size} />
      <AbsoluteFill>{scene}</AbsoluteFill>
      <Cutout cutout={cutout} place={place} size={size} />
      <AbsoluteFill>{front}</AbsoluteFill>
      <Badge text={badge.text} ep={badge.ep} top={layout.badgeTop} left={size.w > size.h ? layout.head.left : undefined} />
      <Headline lines={headline} hl={hl} sparks={sparks} fontSize={headlineSize} size={size} />
    </AbsoluteFill>
  );
};
