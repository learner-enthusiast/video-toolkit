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
import {GraphBuild} from '../GraphBuild/GraphBuild';
import {TicketCard} from '../TicketCard/TicketCard';
import {CalendarFlip} from '../CalendarFlip/CalendarFlip';
import {SyntaxTree} from '../SyntaxTree/SyntaxTree';
import {CounterPair} from '../CounterPair/CounterPair';
import {PhoneStrip} from '../PhoneStrip/PhoneStrip';
import {CallTimeline} from '../CallTimeline/CallTimeline';
import {IncidentCard} from '../IncidentCard/IncidentCard';
import {TerminalCard} from '../TerminalCard/TerminalCard';
import {DefinitionChip} from '../DefinitionChip/DefinitionChip';
import {ProviderNode} from '../ProviderNode/ProviderNode';
import {RetryStorm} from '../RetryStorm/RetryStorm';
import {CircuitBreakerMCB} from '../CircuitBreakerMCB/CircuitBreakerMCB';
import {FallbackLadder} from '../FallbackLadder/FallbackLadder';
import {ErrorTriage} from '../ErrorTriage/ErrorTriage';
import {JsonValidator} from '../JsonValidator/JsonValidator';
import {CustomerBurn} from '../CustomerBurn/CustomerBurn';
import {AppTile, SrvTile, Wire, Booths} from '../PhoneLine/PhoneLine';
import {TicketSlip} from '../TicketSlip/TicketSlip';
import {XMark, TickMark} from '../glyphs';
import {QueueShield} from '../QueueShield/QueueShield';
import {QuotaTank} from '../QuotaTank/QuotaTank';
import {JsonlFile} from '../JsonlFile/JsonlFile';
import {Machine, GpuRow} from '../LaundryToGpu/LaundryToGpu';
import {OutputShuffle} from '../OutputShuffle/OutputShuffle';
import {DeadlineLane} from '../DeadlineLane/DeadlineLane';

import {PhoneMockup} from '../PhoneMockup/PhoneMockup';
import {TokenStream} from '../TokenStream/TokenStream';
import {ExamSheet, RoughSheet} from '../ExamSheet/ExamSheet';
import {BarCompare} from '../BarCompare/BarCompare';
import {FlowLanes} from '../FlowDiagram/FlowDiagram';
import {LineChart} from '../LineChart/LineChart';
import {ChatBubble} from '../ChatBubble/ChatBubble';

/** the 972x970 grid card every scene is drawn in */
const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{width: 1080, height: 1080, background: C.bg, position: 'relative'}}>
    <div style={{position: 'absolute', left: 54, top: 55, width: 972, height: 970, boxSizing: 'border-box', ...gridBg(), border: BORDER, borderRadius: R, boxShadow: SHADOW, overflow: 'hidden'}}>{children}</div>
  </div>
);
const At: React.FC<{x: number; y: number; children: React.ReactNode}> = ({x, y, children}) => <div style={{position: 'absolute', left: x, top: y}}>{children}</div>;

const previews: Record<string, React.FC> = {
  PhoneStrip: () => <Stage><At x={0} y={300}><PhoneStrip at={-100} calls={[{label: 'call 1', at: -100, hangAt: -60}, {label: 'call 2', at: -100}]} slot={{at: -100, label: 'kill switch', fillAt: -50, fillLabel: 'ac.abort()'}} /></At></Stage>,
  CallTimeline: () => <Stage><At x={36} y={240}><CallTimeline at={-200} seconds={40} leaveAt={2} tokRate={50} stopAt={40} run={{start: -190, leave: -170, end: -60}} money={{perTok: 0.0047, prefix: '₹'}} tag="example" foot="example · prices vary by model" verdict={{at: -50, text: 'read: 100 · paid: 2,000', tone: 'dim'}} /></At></Stage>,
  IncidentCard: () => <Stage><At x={40} y={120}><IncidentCard at={-100} tag="real incident · one report" rows={[{text: '5 requests', at: -90}, {text: 'kept generating', at: -80}]} stat={{value: '12,000+', unit: 'tokens each', at: -70}} source={{text: 'sample source line', at: -60}}><div style={{marginTop: 18}}><DefinitionChip term="token" def="a piece of text you pay for" at={-50} /></div></IncidentCard></At></Stage>,
  TerminalCard: () => <Stage><At x={40} y={120}><TerminalCard at={-100} cmd={{text: 'curl -N localhost:3000/chat …', at: -90}} keys={{text: '^C', at: -40, note: 'after 2 s'}} log={[{text: 'done: 2,000 tokens', at: -30, tone: 'dim', mark: 'warn', label: 'before'}, {text: 'stopped at 104 tokens', at: -20, tone: 'orange', label: 'after'}]} /></At></Stage>,
  DefinitionChip: () => <Stage><At x={120} y={460}><DefinitionChip term="token" def="a piece of text you pay for" at={-50} size={36} /></At></Stage>,
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
  GraphBuild: () => {
    const nodes = [{id: 'a', label: 'ApiController', x: 190, y: 200}, {id: 'b', label: 'UserService', x: 486, y: 400}, {id: 'c', label: 'Billing', x: 782, y: 400}, {id: 'd', label: 'AuthService', x: 190, y: 600}, {id: 'e', label: 'Mailer', x: 486, y: 760}, {id: 'f', label: 'invoices', x: 782, y: 760}];
    return (
      <Stage>
        <GraphBuild nodes={nodes} nodeW={240} show={{a: 2, b: 5, c: 8, d: 11, e: 14, f: 17}} edges={[{a: 'a', b: 'b', at: 20}, {a: 'b', b: 'c', at: 23}, {a: 'c', b: 'f', at: 26}, {a: 'a', b: 'd', at: 29}, {a: 'b', b: 'e', at: 32, dashed: true}]}
          clusters={[{label: 'Billing', ids: ['c', 'f'], at: 36}]} tags={[{edge: ['a', 'b'], text: 'found in code', at: 40, dx: -50}, {edge: ['b', 'e'], text: 'guessed', at: 44, tone: 'orange'}]} pulse={{id: 'b', at: 48}} />
      </Stage>
    );
  },
  TicketCard: () => <Stage><At x={106} y={200}><TicketCard id="TASK-101" title="Add CSV export" meta="Sprint 3 · assigned to you" at={2} /></At><At x={106} y={560}><TicketCard id="TASK-101" title="Add CSV export" at={6} size={44} done={20} /></At></Stage>,
  CalendarFlip: () => <Stage><CalendarFlip days={[{label: 'Mon', at: 2}, {label: 'Tue', at: 10}, {label: 'Wed', at: 18}]} files={['router.ts', 'db.ts', 'auth.ts', 'billing.ts']} forgetAt={40} forgetText="context: forgotten" /></Stage>,
  SyntaxTree: () => (
    <Stage>
      <div style={{position: 'absolute', left: 106, top: 60, width: 760, height: 800}}>
        <SyntaxTree file="cart.py" code={['class Cart:', '  def total(self):', '    return sum(self.items)']} codeAt={0}
          nodes={[{id: 'm', label: 'module', kind: 'root', x: 380, y: 290, at: 6}, {id: 'c', label: 'Cart', kind: 'class', x: 380, y: 400, parent: 'm', at: 12}, {id: 'f', label: 'total()', kind: 'function', x: 380, y: 510, parent: 'c', at: 18}, {id: 'k', label: 'sum', kind: 'call', x: 380, y: 620, parent: 'f', at: 24}]} />
      </div>
    </Stage>
  ),
  CounterPair: () => <div style={{width: 1080, height: 1080, background: C.dark, position: 'relative'}}><div style={{position: 'absolute', left: 54, top: 250, width: 972, height: 600}}><CounterPair left={{label: 'Attempts', to: 1200, at: 2, dur: 30}} right={{label: 'Successes', value: 0, at: 36}} y={0} /></div></div>,
  ProviderNode: () => <Stage><At x={60} y={200}><ProviderNode label="Primary API" sub="down" dim={0.6} badge={<XMark size={48} />} /></At><At x={560} y={200}><ProviderNode label="Backup" sub="healthy" ring={1} badge={<TickMark size={52} />} /></At></Stage>,
  RetryStorm: () => <Stage><RetryStorm at={-60} out={1e9} nodeLogo={{file: 'openai.svg', w: 76, h: 76}} nodeLabel="Provider" waveEvery={20} /></Stage>,
  CircuitBreakerMCB: () => <Stage><At x={400} y={260}><CircuitBreakerMCB at={-60} tripAt={20} failAts={[-40, -30, -20]} w={170} /></At></Stage>,
  FallbackLadder: () => <Stage><FallbackLadder x={170} y={20} dropAt={0} landAt={50} rungs={[{label: 'Primary', sub: 'down', at: -60, failAt: 4}, {label: 'Same model, other region', sub: 'second', at: -55, failAt: 22}, {label: 'Other provider', sub: 'third', at: -50, failAt: 38}, {label: 'Human', sub: 'last stop', at: -45}]} /></Stage>,
  ErrorTriage: () => <Stage><ErrorTriage at={-60} items={[{code: '429', lane: 0, at: -50}, {code: '503', lane: 0, at: -40}, {code: '400', lane: 1, at: -30}]} lanes={[{label: 'Retry', tone: 'orange', at: -55}, {label: 'Never retry', tone: 'dim', at: -55}]} /></Stage>,
  JsonValidator: () => <Stage><JsonValidator at={-60} bad={'{ "status": "o'} good={'{ "status": "ok" }'} rejectAt={-40} rerunAt={-20} passAt={-4} /></Stage>,
  CustomerBurn: () => <div style={{width: 1080, height: 1080, background: C.dark, position: 'relative'}}><div style={{position: 'absolute', left: 54, top: 55, width: 972, height: 970}}><CustomerBurn tagAt={-90} gridAt={-70} leaveAt={-50} countAt={-40} countTo={1000000} unit="₹1,000" unitNote="per customer" gridLabel="× 2,000 customers" leaveTo="Rival" leaveNote="half leave" counterNote="lost" /></div></div>,
  PhoneLine: () => (
    <Stage>
      <AppTile at={-60} />
      <SrvTile at={-60} glow={1} />
      <Wire calls={[{drawAt: -50, silentAt: -30, snipAt: 40, snipX: 560}]} travels={[{t0: -48, t1: -36, dir: 'up'}]} />
      <Booths booths={[
        {x: 362, logo: 'cloudflare.svg', lw: 102, lh: 34, label: 'Proxy A', at: -60, limit: '100 s', limitAt: -60},
        {x: 486, logo: 'nginx.svg', lw: 104, lh: 22, label: 'Proxy B', at: -60, limit: '60 s', limitAt: -60},
        {x: 610, logo: 'heroku.svg', lw: 104, lh: 29, label: 'Router', at: -60, timer: {t0: 0, t1: 36, to: 30, hotAt: 36}, scissorsAt: 30},
      ]} />
    </Stage>
  ),
  QueueShield: () => <Stage><QueueShield x={300} y={300} w={170} h={300} at={0} floodAt={10} floodFrom={{x: 40, y: 330}} bypassAt={30} bypassFrom={{x: 600, y: 360}} bypassTo={{x: 760, y: 420}} /></Stage>,
  QuotaTank: () => <Stage><QuotaTank x={140} y={190} w={260} h={560} at={0} labelAt={0} drainAt={10} dryAt={40} taps={['Thick tap', 'Thin tap']} /><QuotaTank x={580} y={190} w={320} h={560} at={0} labelAt={0} splitAt={20} flowAgainAt={40} dryAt={0} /></Stage>,
  JsonlFile: () => <Stage><JsonlFile at={0} out={1e9} stackAt={0} counterAt={30} dropAt={1e9} chipAt={40} /></Stage>,
  LaundryToGpu: () => <Stage><div style={{position: 'absolute', left: 60, top: 80}}><Machine size={300} load="one" tone="dim" /></div><div style={{position: 'absolute', left: 560, top: 80}}><Machine size={300} load="full" tone="orange" /></div><GpuRow x={60} y={560} at={0} busy={[0, 1]} spareAt={0} fillAt={60} size={120} /></Stage>,
  OutputShuffle: () => <Stage><OutputShuffle at={0} out={1e9} shuffleAt={4} mapAt={1e9} rewindAt={1e9} fixAt={10} snapAt={20} matchAt={30} /></Stage>,
  DeadlineLane: () => <Stage><DeadlineLane at={0} out={1e9} runFrom={0} runTo={30} deadlineAt={34} peelAt={40} laneAt={50} start="day 1, 6 PM" deadline="day 2, 9 AM" leftover="40 pending" lane="Real-time fallback" /></Stage>,
  TicketSlip: () => <Stage><TicketSlip x={486} y={300} w={380} id="#0001" at={2} sub="we'll call you" /><TicketSlip x={486} y={680} w={340} id="#0002" at={0} sub="job_0002" morphFrom={{text: '{ "jobId": "job_0002" }', at: 30}} /></Stage>,
  PhoneMockup: () => <Stage><At x={60} y={40}><PhoneMockup w={420} h={880} app="TripMate" subtitle="Goa · 5 days" days={[{title: 'Day 1', text: 'Land in Panaji. Check in, then a sunset walk on the beach.'}, {title: 'Day 2', text: 'North Goa: a fort at 9, lunch, the beach by evening.'}, {title: 'Day 3', text: 'Morning: take the ferry to'}]} typeFrom={0} typeTo={40} blinkFrom={42} emptyDays={2} at={0} /></At><At x={520} y={40}><PhoneMockup w={400} h={800} variant="home" app="TripMate" at={0} /></At></Stage>,
  TokenStream: () => <Stage><At x={36} y={100}><TokenStream chips={[' take', ' the', ' ferry', ' to']} cutTail=" Chorão…" from={0} to={24} capAt={46} cap={1000} payAt={4} perTok={0.00085} at={0} /></At></Stage>,
  ExamSheet: () => <Stage><At x={30} y={60}><ExamSheet w={440} h={820} lines={10} fillFrom={0} bellAt={44} penStopAt={48} at={0} /></At><At x={500} y={60}><RoughSheet w={440} h={820} drawFrom={0} drawTo={40} at={0} /></At></Stage>,
  BarCompare: () => <Stage><At x={36} y={380}><BarCompare w={900} max={14000} rows={[{label: 'all calls', value: 14000, tone: 'ink', at: 0}, {label: 'wasted', value: 6000, tone: 'orange', at: 8}]} /></At></Stage>,
  FlowDiagram: () => <Stage><At x={36} y={80}><FlowLanes aAt={0} failAt={10} bAt={14} retryAt={40} at={0} /></At></Stage>,
  LineChart: () => <Stage><At x={36} y={120}><LineChart w={900} h={740} drawAt={0} spikeAt={20} dotAt={44} at={0} /></At></Stage>,
  ChatBubble: () => <Stage><div style={{position: 'absolute', left: 300, right: 40, top: 200}}><ChatBubble role="user" text="Five days in Goa." at={0} size={46} /></div><div style={{position: 'absolute', left: 40, right: 200, top: 420}}><ChatBubble role="bot" text="Here's a day-by-day plan." at={6} size={46} /></div></Stage>,
};

export const Root: React.FC = () => (
  <>
    {Object.entries(previews).map(([name, C_]) => <Composition key={name} id={`Preview-${name}`} component={C_} width={1080} height={1080} fps={30} durationInFrames={90} />)}
  </>
);
