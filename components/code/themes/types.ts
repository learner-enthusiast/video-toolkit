// The shape every brand theme has. Values: brand1.ts, brand2.ts, brand3.ts (docs: /brand.md, /brands/).
export type Theme = {
  /** page + grid card background */
  bg: string;
  /** card fill */
  surface: string;
  /** main text */
  text: string;
  /** dim text, "bad", disabled */
  textDim: string;
  /** 2 px card/pill border */
  border: string;
  /** grid lines / dots */
  grid: string;
  /** the main accent */
  accent: string;
  /** focus / key-word accent */
  accent2: string;
  /** failure punch stamp only */
  alert: string;
  /** text on an accent fill */
  onAccent: string;
  /** dark fills: phone bodies, dark badges */
  inkFill: string;
  /** text on inkFill */
  onInk: string;
  /** punch-moment background */
  punchBg: string;
  /** text on punchBg */
  onPunch: string;
  /** card header strips */
  paper: string;
  /** greyed-out card fill */
  mute: string;
  /** bar tracks, removed diff lines */
  fill: string;
  /** dim pill background */
  tint: string;
  /** placeholder lines, window dots */
  track: string;
  /** pale accent (hatch stripes) */
  accentSoft: string;
  /** panels on a punch scene */
  darkPanel: string;
  /** idle bar / breaker body */
  barBg: string;
  /** dead-time hatch, dark stripe */
  hatch: string;
  /** dead-time hatch, light stripe */
  hatchLight: string;
  /** washer drum glass */
  drum: string;
  /** every second item beside accent */
  accentMid: string;
  /** cut-off chip stripes */
  stripe: string;
  /** colour a live shape fades to */
  fade: string;
  /** dim mono text on punchBg */
  dimOnPunch: string;
  /** phone edge on a dark scene */
  phoneEdge: string;
  /** chat bubble on a dark scene */
  bubblePunch: string;
  /** tile behind a logo that would vanish on a dark card */
  logoTile: string;
  /** second stop of the big-number gradient (the first is accent) */
  gradientEnd: string;
  /** diagram edges, axes, rails and outlines that must stay visible */
  line: string;
  /** text that was left at the browser default */
  plain: string;
  /** the one shadow */
  shadow: string;
  /** page pattern drawn by gridBg() */
  gridStyle: 'lines' | 'lines-scanlines' | 'dots';
  /** headline family: serif = Instrument Serif Italic, inter = Inter 800 */
  headlineFont: 'serif' | 'inter';
};
