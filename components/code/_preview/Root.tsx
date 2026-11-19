// Preview harness for the component library: one Still per component with default props, used to make each <Name>/preview.png.
// Content here (text, numbers) is sample data only. Render: see components/code/README.md.
import React from 'react';
import {Composition} from 'remotion';
import {C, R, BORDER, SHADOW, gridBg, inter} from '../theme';
import {Tag, TagPop} from '../Tag/Tag';
import {Stamp} from '../Stamp/Stamp';
import {Checklist} from '../Checklist/Checklist';
import {MathStrip} from '../MathStrip/MathStrip';
import {SourceChip} from '../SourceChip/SourceChip';
import {CodeCard} from '../CodeCard/CodeCard';
import {ThresholdRing} from '../ThresholdRing/ThresholdRing';
import {DualMeter, BudgetBar} from '../DualMeter/DualMeter';
import {TradeScale} from '../TradeScale/TradeScale';
import {PullRequestCard} from '../PullRequestCard/PullRequestCard';
import {RoutingLadder} from '../RoutingLadder/RoutingLadder';

/** the 972x970 grid card every scene is drawn in */
const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{width: 1080, height: 1080, background: C.bg, position: 'relative'}}>
    <div style={{position: 'absolute', left: 54, top: 55, width: 972, height: 970, boxSizing: 'border-box', ...gridBg(), border: BORDER, borderRadius: R, boxShadow: SHADOW, overflow: 'hidden'}}>{children}</div>
  </div>
);
const At: React.FC<{x: number; y: number; children: React.ReactNode}> = ({x, y, children}) => <div style={{position: 'absolute', left: x, top: y}}>{children}</div>;

const previews: Record<string, React.FC> = {
  Tag: () => (
    <Stage>
      <At x={60} y={80}><div style={{display: 'flex', gap: 16, flexWrap: 'wrap', width: 840}}><Tag label="Summarize" tone="orange" /><Tag label="Draft reply" /><Tag label="redis.get()" monoFont tone="ink" /><Tag label="legacy" tone="dim" /></div></At>
      <TagPop x={60} y={260} at={4} label="pops in on its word" tone="outline" />
    </Stage>
  ),
  Stamp: () => <Stage><Stamp x={486} y={485} at={4} text="Rejected" /><Stamp x={486} y={700} at={10} text="Draft" tone="dim" rotate={4} /></Stage>,
  Checklist: () => <Stage><At x={120} y={260}><Checklist size={52} gap={26} items={[{text: 'Validate input', at: 4}, {text: 'Check the cache', at: 12}, {text: 'Write the log', at: 20}]} /></At></Stage>,
  MathStrip: () => <Stage><At x={70} y={420}><MathStrip size={50} terms={[{text: '1,200', at: 4}, {text: '30', at: 12, op: '×'}, {text: '36,000', at: 20, op: '='}]} /></At></Stage>,
  SourceChip: () => <Stage><At x={200} y={440}><SourceChip at={4} size={40}>pricing page, 2026</SourceChip></At></Stage>,
  CodeCard: () => <Stage><At x={60} y={150}><CodeCard at={0} width={850} size={34} cps={50} tags={['server', 'pseudo-code']} lines={['const key = hash(req)', 'if (cache.has(key)) {', '  return cache.get(key) // hit', '}', 'return model(req)']} hl={[{line: 2, at: 6}]} /></At></Stage>,
  ThresholdRing: () => <Stage><div style={{position: 'absolute', left: 486, top: 485, width: 26, height: 26, borderRadius: 99, background: C.ink, transform: 'translate(-50%,-50%)'}} /><ThresholdRing x={486} y={485} r={150} at={0} steps={[{at: 10, r: 260}]} label="threshold" labelAt={12} /></Stage>,
  DualMeter: () => <Stage><DualMeter req={0.5} tok={0.72} reqText="3" tokText="7,200" /><BudgetBar x={40} y={885} w={880} h={64} segs={[{frac: 0.45, kind: 'spent', label: 'spent'}, {frac: 0.25, kind: 'held', label: 'held', lock: 1}, {frac: 0.3, kind: 'free'}]} /></Stage>,
  TradeScale: () => <Stage><TradeScale x={486} y={330} at={0} angle={-7} label="trade-off" leftAt={6} rightAt={12} left={<Tag label="Fast" tone="orange" size={40} />} right={<Tag label="Cheap" tone="ink" size={40} />} /></Stage>,
  PullRequestCard: () => (
    <Stage>
      <At x={46} y={70}><PullRequestCard title="Fix typo in README" files="README.md" add={1} del={1} /></At>
      <At x={46} y={290}><PullRequestCard tone="risky" title="Refactor charge flow" files="payments/charge.ts" add={84} del={31} diffAt={4} diff={[{op: '-', text: 'charge(order)'}, {op: '+', text: 'charge(order, key)'}]} warn={{at: 16, text: 'no idempotency key'}} /></At>
      <At x={46} y={700}><PullRequestCard tone="dim" title="Bump version" files="package.json" add={2} del={2} tag={<Tag label="₹5" tone="dim" size={28} />} /></At>
    </Stage>
  ),
  RoutingLadder: () => <Stage><RoutingLadder frameAt={0} prices={{small: '₹5', big: '₹100'}} rungs={[{label: 'Rules', sub: 'path → lane', at: 4}, {label: 'Classifier', sub: 'easy / hard', at: 10}, {label: 'Unsure → Big', sub: 'fail safe', at: 16}, {label: 'Measure', sub: 'cost per review', at: 22}]} active={[{at: 24, i: 1}]} drops={[{at: 14, land: 36, label: 'README', lane: 'small', rung: 0}, {at: 28, land: 50, label: 'charge.ts', lane: 'big', rung: 1}]} /></Stage>,
};

export const Root: React.FC = () => (
  <>
    {Object.entries(previews).map(([name, C_]) => <Composition key={name} id={`Preview-${name}`} component={C_} width={1080} height={1080} fps={30} durationInFrames={90} />)}
  </>
);
