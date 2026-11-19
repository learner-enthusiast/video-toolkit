// Motion helpers: spring or ease-in-out only, never linear (brand.md). Every `at` / `out` is a frame number
// taken from the word timestamps of what is spoken, never a fixed time.
import {spring, interpolate, Easing} from 'remotion';
import {FPS} from './theme';

export const sp = (f: number, at: number, cfg: {damping?: number; stiffness?: number; mass?: number} = {}) =>
  spring({frame: f - at, fps: FPS, config: {damping: cfg.damping ?? 14, stiffness: cfg.stiffness ?? 140, mass: cfg.mass ?? 0.8}});
/** stiffer spring with a small overshoot, for pops and stamps */
export const pop = (f: number, at: number) => sp(f, at, {damping: 11, stiffness: 170});
export const ease = (f: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(f, [a, b], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
/** ease-out for things that grow (bars) */
export const easeOut = (f: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(f, [a, b], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
/** 0->1 entrance at `at`, 1->0 exit over 8 frames ending at `out` */
export const life = (f: number, at: number, out = 1e9) => Math.min(sp(f, at), ease(f, out - 8, out, 1, 0));
/** fade + rise + slight scale; the exit mirrors it */
export const enter = (f: number, at: number, out = 1e9, dy = 24) => {
  const v = sp(f, at);
  const o = ease(f, out - 8, out, 1, 0);
  return {opacity: Math.min(v, o), transform: `translateY(${(1 - v) * dy - (1 - o) * 10}px) scale(${0.96 + 0.04 * v})`};
};
export const popIn = (f: number, at: number, out = 1e9) => {
  const v = pop(f, at);
  const o = ease(f, out - 8, out, 1, 0);
  return {opacity: Math.min(Math.min(1, v * 1.5), o), transform: `scale(${0.8 + 0.2 * v})`};
};
/** typewriter: `cps` characters per frame */
export const typed = (f: number, at: number, text: string, cps = 2) => text.slice(0, Math.max(0, Math.floor((f - at) * cps)));
