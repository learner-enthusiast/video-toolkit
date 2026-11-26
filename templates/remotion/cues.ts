// Named cues (pipeline/composition.md). Scenes call cue() and beatAt(): no spoken words in TSX, so
// another language only swaps public/data/. cue_frames.json comes from tools/captions/resolve_cues.py.
import timeline from '../../public/data/timeline.json';
import cueFrames from '../../public/data/cue_frames.json';
import trailerData from '../../public/data/trailer_ranges.json';

/** The trailer's [from, to] ranges on the main timeline (data, so a Hindi twin brings its own). */
export const trailerRanges = (trailerData as unknown as {ranges: [number, number][]}).ranges;

const CUES = cueFrames as unknown as Record<string, number>;
const WORDS = (timeline as unknown as {words: {s: number; e: number; b?: string}[]}).words;

/** Output frame of a named cue. */
export const cue = (name: string): number => {
  const frame = CUES[name];
  if (frame === undefined) throw new Error(`cue(): "${name}" is not in cue_frames.json (run resolve_cues.py)`);
  return frame;
};

/**
 * The frame `fraction` (0..1) of the way through a beat, for a moment no word marks.
 * A beat runs from its first word to the next beat's first word; the last one ends with its last word.
 */
export const beatAt = (beat: string, fraction = 0): number => {
  const first = WORDS.findIndex((w) => w.b === beat);
  if (first < 0) throw new Error(`beatAt(): beat "${beat}" has no words in timeline.json`);
  if (fraction < 0 || fraction > 1) throw new Error(`beatAt(): fraction ${fraction} is outside 0..1`);
  let last = first;
  while (last + 1 < WORDS.length && WORDS[last + 1].b === beat) last++;
  const from = WORDS[first].s;
  const to = last + 1 < WORDS.length ? WORDS[last + 1].s : WORDS[last].e;
  return Math.round(from + fraction * (to - from));
};
