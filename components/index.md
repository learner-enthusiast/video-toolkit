# Component index

One-page lookup for every component spec in `components/specs/` and its saved code in `components/code/` (tokens in `code/theme.ts`, Remotion version in `code/REMOTION_VERSION`). **Read this file first; open a spec only when you will use it.** Never bulk-read `components/`. Pick from your scene table, open just those specs. `layout-states.md` is the HEAD / FULL / SPLIT system, not a component.

Names below are plain: each spec is `components/specs/<Name>.md`.

**✓** after a name = approved code saved in `components/code/<Name>/` (import `shared/<Name>/<Name>`, set props). No mark = spec-only or needs-cleanup.

**Row lookup:** the full table (purpose, key props, Code?, variants, last used) is in `components/index-full.md`. Never read it whole; get single rows with `grep -i '^| \[<Name>\]' components/index-full.md` (several at once: `grep -iE '^\| \[(A|B|C)\]' components/index-full.md`).

**Maintenance:** a new spec adds its row to `index-full.md` (sorted by name) and its name to the matching intent group here; saving code adds ✓ here and in the row's `Code?`; all in the same commit.

## Find by intent

- **Compare A vs B:** CompareSplit · BarCompare ✓ · StackCompare · PersistenceCompare · CommitVsChangeset · VolumeDemo · ChoicePills · KeyPicker · LayerStack · HostingOptions · StorageDrawers · VersionTable · VerdictBoard · ToolShelf · TradeScale ✓ · LockDrawer · RankedList
- **Process / data flow / architecture:** FlowDiagram ✓ · DiagramBlock · FlowArrow · FlowCard · SequenceFlow · DockerPipeline · PipelineCanvas · ContainerStack · ComposeServices · LayerCache · RuntimeBundle · HubSpoke · BrokerCluster · EventStream · ServerFanout · RerankFunnel · ListMerge · ChunkSlicer · PromptStack ✓ · PrefixMatch ✓ · TocTreeWalk · ProtocolStack · RegistryCalls · DiagnosisArrow · FeedbackLoop · KeyGridScan · VerifyChecklist · SharedIpFunnel · TaskBudget · RoutingLadder ✓ · GraphBuild ✓ · RetryStorm ✓ · CircuitBreakerMCB ✓ · FallbackLadder ✓ · ErrorTriage ✓ · JsonValidator ✓ · ProviderNode ✓ · PhoneLine ✓ · QueueShield ✓ · JsonlFile ✓ · OutputShuffle ✓
- **Numbers & stats:** Counter · StatCard · StatBar · Gauge · LoadMeter · DualMeter ✓ · MathStrip ✓ · LineChart ✓ · PriceTag · HoldSettle · RationBags · SlidingCounter · AdoptionHonest · AccountQuotaBar · CheckpointTicket · CostMeter · PrepaidMeter · CohortCounter · IncidentCard ✓ · CounterPair ✓ · CustomerBurn ✓ · TokenStream ✓ · TokenBlocks ✓ · BillCard ✓
- **Code & terminal:** HttpReply · TokenAnatomy · TerminalCrack · TypingIntro · CodeCard ✓ · ComposeServices · FlowCard · PullRequestCard ✓ · TerminalCard ✓ · SyntaxTree ✓ · TokenBlocks ✓
- **Security & auth:** AlgAttack · CookieToss · DecoderReveal · FooterSeal · ImplicitAssertion · JwksRotation · LocalSeal · PhonePush · PublicVerify · StackBurst · TamperCrack · TokenLifetime · TypedKeyGate · XffSpoof · KeyCard · WristbandGate · HashMachine · PhilosophyDials
- **Rate limits, caching & races:** TokenBucket · LeakyBucket · WindowTimeline · SlidingLog · TwinPhones · TwoServerRace · UpdateRace · RaceTimeline · LeaseToken · RequestFlood · CommandPipe · OtpSpam · CacheTiers · CountdownKey · TaskBudget · QuotaTank ✓ · QueueShield ✓
- **Data & storage:** TableBuild · TableJoin · TableScan · TransactionBox · KafkaLog · SessionMapScale · Server3D · BitRow · DualIndex · ImageManifest · InvertedIndexBuild · RowSplit · VectorSpaceMiss · ContextOverflow · EmbeddingMap · ThresholdRing ✓ · KeyLocker
- **Metaphors & analogies:** Buildings · DataPlanPhone · DeliveryTracker · DeskCabinet · FridgeMilk · KitchenChefs · LibraryAnalogy · ShippingContainer · SedanProp · IconMorph · HiddenThinking · PrepaidMeter · PhoneStrip ✓ · CircuitBreakerMCB ✓ · PhoneLine ✓ · TicketSlip ✓ · LaundryToGpu ✓ · TokenDictionary ✓ · KycCounter ✓
- **Text & emphasis:** Headline · Highlight · Stamp ✓ · Badge · Tag ✓ · TagDrop · StickyNote · SourceChip ✓ · ZoomCard · Checklist ✓ · AnswerGrid · UrlAnatomy · PinnedQuestion · Captions · QuoteCard · CheckCard · TextMorph · DefinitionChip ✓
- **People, avatars & chat:** FaceAvatar · Avatar · ChatBubble ✓ · InterviewBubble · Bubble · LowerThird · PresenterSplit · ReelSplit · FaceTrackedCrop · AvatarRow
- **Timing & progress:** Timeline · Timer · WindowTimeline · RaceTimeline · TableScan · DeliveryTracker · CountdownKey · CallTimeline ✓ · CalendarFlip ✓ · DeadlineLane ✓ · ExamSheet ✓
- **Branding, logos & credits:** IconRail · IconMorph · Thumbnail · PartBadge · UrlPill · CreditCTA
- **Openers / hooks:** TypingIntro · OtpSpam · Headline · PinnedQuestion
- **Endings & CTAs:** EndCard · CreditCTA · CanvasZoomOut · AnswerGrid · VerdictBoard · Checklist ✓
- **Frames, screenshots & transitions:** Card · ScreenshotKenBurns · Highlight · PhoneMockup ✓ · ProductCard · ShatterTransition · Bubble · PolaroidDrop · ReceiptStack · TicketCard ✓ · TicketSlip ✓
- **Carousel:** Carousel
- **Social images (LinkedIn photo, X Article header):** LinkedInPhoto
