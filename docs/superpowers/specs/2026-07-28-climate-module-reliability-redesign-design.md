# Climate-FCV Native Reliability Redesign

**Date:** 2026-07-28
**Branch:** `feat/climate-readout-redesign`
**Status:** Approved in brainstorming; implementation plan pending
**Extends:** `2026-07-25-climate-readout-questions-redesign-design.md`
**Restores:** the climate-native direction in `2026-07-24-climate-native-flow-design.md`

## 1. Executive decision

When the Climate-FCV module is selected, the app will take a dedicated
climate-native route. It will not run the full generic FCV Stage 2 engine and
then append a climate diagnostic.

The climate-native route will:

1. conduct mandatory, targeted external climate and climate-FCV research;
2. stop without producing an assessment if that research fails its evidence
   gate;
3. generate a compact FCV baseline rather than the full generic FCV machinery;
4. produce the climate diagnostic as a first-class Stage 2 output;
5. retain the approved detailed climate-FCV readout and source-derived question
   bank;
6. produce only climate-specific Stage 3 priorities; and
7. fail honestly if a valid climate result cannot be produced.

The standard FCV route remains unchanged. The restored ITS-compatible `main`
branch must not be used for this development until the climate branch has been
implemented, preview-deployed, and accepted.

## 2. Relationship to the earlier approved designs

This is not a new reader-facing concept. It completes the climate-native
architecture already approved in:

- `docs/superpowers/specs/2026-07-24-climate-native-flow-design.md`
- `docs/superpowers/specs/2026-07-25-climate-readout-questions-redesign-design.md`
- `docs/superpowers/plans/2026-07-26-climate-readout-questions-redesign.md`

Those documents already require:

- a standalone climate-led assessment;
- removal of the visible 12-OST, DNH-9, and 25-question engine in climate mode;
- compact FCV ratings and evidence;
- a source-derived climate-FCV question bank;
- a six-tier integration gauge;
- detailed strengths and weaknesses;
- project-specific climate-FCV analysis;
- approximately three, with no more than five, climate-linked priorities; and
- unchanged non-climate behavior.

The current branch implemented much of the question bank, schema, guardrails,
rendering, and export work, but did not complete the plan's Task 3.2: "Drop the
verbose generic engine framing in climate Stage 2."

This redesign makes that missing architectural step explicit and adds one
user-approved policy that was not in the earlier design:

> Targeted external climate research is mandatory and fail-closed. If it cannot
> provide usable evidence, the Climate-FCV assessment does not run.

## 3. Production failure diagnosis

### 3.1 Observed behavior

The run history supplied on 2026-07-28 showed:

- climate research failing after two attempts, with no accepted sources or
  claims;
- Stage 2 completing but omitting the structured Climate-FCV diagnostic;
- the primary diagnostic being rejected as absent;
- the recovery request reaching its 120-second timeout; and
- the app correctly withholding unvalidated climate findings.

A separate Anthropic HTTP 529 overload was also observed. Bounded retry on
stream-open overload is useful, but it is not the root cause of the persistent
climate failure.

### 3.2 Prompt overload

The climate Stage 2 route currently combines:

- roughly 45,000 characters of generic Stage 2 instructions; and
- roughly 13,000 characters of additional climate instructions;
- plus injected project, research, instrument, and guidance context.

The generic instructions still request the full narrative, 12-standard table,
DNH assessment, 25-question map, evidence trail, ratings, and reasoning. The
climate suffix then requests a second large structured diagnostic.

The climate diagnostic is placed after a much larger body of work. The model
commonly completes the generic output but omits the trailing diagnostic. Raising
token caps or stating that the block is mandatory does not remove this
architectural conflict.

### 3.3 Load-bearing recovery

The recovery path was designed as a fallback. In practice it has become the
normal path because the primary call omits the diagnostic.

The current recovery:

- makes a large non-streaming Sonnet request;
- uses an approximately 120-second read timeout;
- asks for most of the full climate diagnostic again;
- blocks the server-sent-event workflow while it runs; and
- returns no validated climate module when it times out.

Increasing the timeout would reduce some failures but would leave the recovery
path load-bearing and leave Render appearing stalled.

### 3.4 Research budget mismatch

Climate research can make two sequential calls, while the parent Stage 1
research coordinator has a shorter aggregate budget. A retry can therefore
finish after the parent has stopped waiting, causing its result to be discarded.

The research problem is a scheduling defect as well as a search-quality
problem. One owner must control the total deadline and decide whether sufficient
time remains for a retry.

### 3.5 Test blind spots

The current branch has 457 passing tests. Those tests do not establish
production reliability because they:

- inspect climate suffix text rather than the complete assembled Stage 2 prompt;
- do not assert the absence of generic Stage 2 machinery in climate mode;
- use immediate fake model responses for recovery;
- do not simulate parent and child deadline conflicts;
- do not exercise a blocked server-sent-event stream; and
- do not require the happy path to complete without recovery.

## 4. Scope and invariants

### 4.1 In scope

- Dedicated climate-native routing.
- Mandatory targeted climate and climate-FCV research.
- Fail-closed behavior when research evidence is unavailable.
- Compact FCV baseline.
- Primary structured climate diagnostic.
- Bounded field-level recovery.
- Source-derived core and supplementary questions.
- Climate-specific priorities and operational adaptations.
- Specificity, provenance, and instrument-vocabulary validation.
- Render-safe streaming, time budgets, and observability.
- Live, shared HTML, downloaded HTML, and DOCX parity.
- Production-like latency and failure tests.

### 4.2 Out of scope

- Reworking the standard full FCV assessment.
- Running the full 12-OST, DNH-9, or 25-question engine in climate mode.
- Implementing climate changes directly on `main`.
- ITS/FastAPI implementation before the Render design is accepted.
- Reading the restricted raw OPCS corpus. Implementation must use the existing
  approved summaries, guardrails, and review outputs.
- A generic assessment generated from project documents alone after mandatory
  climate research fails.

### 4.3 Preserved invariants

- Non-climate output and behavior remain unchanged.
- The module remains advisory and cannot make formal OPCS, ESF, Paris Alignment,
  CDRS, ESS, ESRC, or other compliance determinations.
- Recommendations route by instrument before naming operational instruments.
- Claims remain conditional and evidence-based; climate change is not presented
  as deterministically causing conflict.
- Live and exported readouts use the same validated data.
- The climate branch remains separate from the ITS-compatible `main`.

## 5. Climate-native execution flow

### 5.1 Mode routing

`climate` in the active module selection chooses a dedicated prompt and
execution route. The climate route must not be created by concatenating a suffix
onto `DEFAULT_PROMPTS["2"]`.

The complete assembled climate prompt must exclude instructions to generate:

- the 12 operational-standard table;
- the nine-part DNH checklist;
- the 25-question map;
- the generic visible FCV recommendation table; and
- the long generic FCV Stage 2 narrative.

The compact baseline may be informed by relevant FCV principles, but the model
does not enumerate or silently generate the full generic checklists.

### 5.2 Stage 1A: document extraction

Stage 1 extracts only the project characteristics needed by the climate route,
including:

- document and instrument type;
- project development objective;
- components and subcomponents;
- activities, infrastructure, and locations;
- beneficiary groups;
- implementing and counterpart institutions;
- delivery mechanisms;
- climate-relevant design elements;
- displacement, livelihoods, inclusion, and access signals;
- implementation arrangements;
- results indicators and financing arrangements; and
- preparation, restructuring, AF, or MPA status where relevant.

These structured signals drive research, question selection, specificity
validation, and instrument routing.

### 5.3 Stage 1B: mandatory targeted research

Research focuses on:

- country- and location-specific climate hazards and projections;
- exposure and vulnerability relevant to project components;
- climate impacts on livelihoods, services, infrastructure, ecosystems, and
  institutions;
- displacement, exclusion, access, resource competition, and fragility
  mechanisms that interact with those hazards; and
- current contextual evidence needed to interpret the project.

Broad generic FCV research is reduced because the climate route no longer needs
to populate the full generic engine.

The research coordinator owns one overall deadline. It may authorize a retry
only when sufficient budget remains. Child calls cannot overrun the parent
deadline and later return an unusable result.

Research succeeds only when it returns usable, traceable evidence. The initial
acceptance target is:

- at least two relevant sources;
- at least one authoritative climate source where available;
- at least one accepted claim tied to a project-relevant hazard, exposure, or
  climate-FCV mechanism; and
- a retained URL or stable source identifier for each external claim.

The implementation plan may tune exact thresholds after fixture testing, but it
must preserve the principle that a completed search call is not automatically a
successful evidence result.

### 5.4 Research failure behavior

If the research evidence gate fails:

1. stop before Stage 2;
2. do not generate the compact FCV baseline;
3. do not generate climate findings or priorities;
4. display a clear explanation that required external climate evidence could
   not be retrieved; and
5. offer:
   - Retry Climate-FCV screening.
   - Run the full standard FCV assessment.

There is no project-document-only climate fallback.

### 5.5 Stage 2: primary climate-native assessment

One primary model call receives:

- structured project signals and relevant document excerpts;
- accepted research claims and source metadata;
- triggered climate-FCV question-bank entries;
- relevant source-framework summaries;
- instrument and process routing context; and
- scoped OPCS advisory guardrails.

It produces:

- a compact FCV baseline;
- a short climate-FCV synthesis;
- a compact evidence trail;
- the six-tier integration rating and summary;
- three-part operating context;
- detailed strengths and weaknesses;
- both interaction directions;
- material core and supplementary question answers; and
- the complete structured climate diagnostic.

The structured diagnostic is a first-class required output. Its placement and
schema must not make it a trailing appendix after optional prose.

### 5.6 Compact FCV baseline

The compact baseline contains:

- FCV sensitivity rating and short reasoning;
- FCV responsiveness rating and short reasoning;
- key contextual conditions that affect climate action; and
- a small, traceable evidence trail.

It does not contain the full 12-OST, DNH-9, 25-question map, or generic
recommendation process.

### 5.7 Bounded recovery

Recovery is invoked only when the primary climate call returns an incomplete or
invalid structured diagnostic.

Recovery:

- receives the completed Stage 2 analysis and accepted sources;
- requests only missing or invalid fields;
- does not regenerate the full climate assessment;
- uses the same specificity, provenance, and instrument guardrails;
- streams progress or permits periodic server-sent-event heartbeats;
- operates within a single explicit deadline; and
- records why it was invoked and which fields were repaired.

If recovery cannot produce a valid diagnostic, the Climate-FCV screening fails
honestly. The app must not present the compact baseline alone as a successful
climate assessment.

### 5.8 Stage 3: climate-specific priorities

Stage 3 runs only after a valid Stage 2 climate diagnostic exists. It receives
the validated diagnostic, compact baseline, project evidence, and accepted
research sources.

It generates approximately three priorities, with a hard maximum of five. Each
priority must:

- link to a specific climate-FCV interaction, pathway, or question;
- identify the project component, location, beneficiary group, institution, or
  implementation provision it affects;
- state the gap;
- explain why it matters;
- propose concrete, proportionate actions;
- identify who acts and when;
- identify relevant project-document sections;
- carry an `authority_basis`; and
- follow instrument-specific OPCS terminology and advisory boundaries.

Stage 3 does not run the standard generic FCV recommendation process.

## 6. Reader-facing output

The approved order is:

1. Executive summary.
2. Six-tier integration gauge.
3. Operating context.
4. Strengths and weaknesses.
5. Core and supplementary climate-FCV questions.
6. Climate-specific priority action areas.
7. Advisory boundary.

### 6.1 Executive summary

The executive summary identifies:

- the principal climate-FCV interaction;
- the overall integration rating;
- the most consequential strength;
- the most important operational gap; and
- the highest-priority adaptation.

### 6.2 Integration gauge

The approved scale remains:

`Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded`

The readout shows the rating, a short need phrase, one summary sentence, and the
existing caveat that it is not an official WBG rating.

### 6.3 Operating context

The three blocks remain:

1. The FCV setting.
2. The climate setting.
3. Where they meet.

The third block must connect the intersection to named project components,
locations, beneficiaries, or delivery institutions.

### 6.4 Strengths and weaknesses

The module may show up to four material strengths and four material weaknesses
or gaps. Each point:

- is normally two or three substantive sentences;
- explains why the issue is both climate- and FCV-relevant;
- names the specific design feature it attaches to; and
- is suppressed when evidence is too generic.

### 6.5 Core and supplementary questions

The six established themes remain stable organizing anchors:

1. How could climate and FCV affect the project?
2. How could the project affect climate and FCV dynamics?
3. Could the design lock in maladaptation?
4. Does it engage root causes or create peace and social dividends?
5. Are vulnerable groups reached through appropriate institutions?
6. Is the design adaptive to uncertainty and changing conditions?

They are not a ceiling. Additional questions drawn from approved source
materials may be surfaced when they identify a material, project-specific issue
that is not adequately covered by the six headings.

Selection rules:

- both interaction directions are always required;
- only materially triggered questions are answered;
- triggered bank questions shape the analysis behind each theme;
- supplementary questions require evidence and a decision-relevant "so what";
- relevance and depth take priority over a fixed question count; and
- non-specific questions are dropped rather than padded.

Each surfaced answer includes:

- a clear finding;
- a causal explanation;
- application to named project features;
- an understated status cue;
- traceable source attribution; and
- two substantive paragraphs where the evidence supports that depth.

### 6.6 Climate-specific priorities

Each priority presents:

- title;
- identified gap;
- why it matters;
- concrete actions;
- responsible actor;
- timing;
- relevant project-document sections;
- linked climate-FCV pathway or question; and
- authority basis.

Priorities are instrument-routed before mentioning ESS, ESCP, ESSA, PSIA, CERC,
CDRS, Paris Alignment, or other operational processes.

## 7. Specificity and evidence standard

Specificity is a cross-cutting validation requirement, not merely a prompt
preference.

Where the evidence supports it, every major section and priority should name:

- project components and subcomponents;
- financed activities and infrastructure;
- locations and sites;
- beneficiary groups;
- implementing and counterpart institutions;
- delivery mechanisms;
- indicators and financing arrangements;
- implementation provisions;
- relevant project-document sections; and
- applicable OPCS instruments, processes, or guidance.

Preferred pattern:

`pressure -> mechanism -> effect on a named project feature -> current design
response or gap -> proportionate operational adaptation`

The validator should flag:

- generic terms when named details exist;
- priorities without a component, institution, geography, or document anchor;
- external claims without a retained source;
- OPCS references without an authority classification;
- instrument-incompatible terminology;
- unsupported formal compliance determinations; and
- deterministic climate-conflict claims.

Missing source detail must not be fabricated. The output should identify the
evidence gap or unresolved operational question.

## 8. Completeness and failure rules

A Climate-FCV result is complete only when it has:

- passed the mandatory research evidence gate;
- a valid compact FCV baseline;
- a valid six-tier integration rating and summary;
- both interaction directions;
- at least one additional material core or supplementary question;
- climate and FCV operating-context evidence;
- project-specific strengths and weaknesses;
- traceable external research sources;
- at least one valid climate-specific priority, normally approximately three;
  and
- no prohibited instrument terminology or unsupported determination.

Failure of a recoverable field invokes bounded recovery. Failure after recovery
prevents the app from representing the screening as complete.

## 9. Render safeguards and observability

### 9.1 Time-budget ownership

Research, Stage 2, recovery, and Stage 3 each receive an explicit deadline
within a documented overall assessment budget. Nested work cannot exceed its
parent deadline.

### 9.2 Streaming and heartbeats

Long model operations must stream content or allow regular progress events.
Recovery must not make a silent synchronous call that blocks server-sent events
for the full timeout period.

### 9.3 Typed failure states

Record and surface failure categories such as:

- `climate_research_failed`;
- `climate_research_insufficient`;
- `climate_stage2_timeout`;
- `climate_diagnostic_invalid`;
- `climate_recovery_timeout`;
- `climate_priority_invalid`; and
- `provider_overloaded`.

Logs retain:

- assessment ID;
- stage;
- attempt;
- elapsed time;
- deadline remaining;
- accepted source and claim counts;
- diagnostic validation reason;
- recovery fields requested; and
- final disposition.

Logs must not expose project-document contents or secrets.

## 10. Testing strategy

### 10.1 Prompt routing

- Assert the complete climate Stage 2 prompt excludes the generic 12-OST,
  DNH-9, 25-question, and generic recommendation instructions.
- Assert the standard FCV prompt remains unchanged.
- Assert climate selection chooses a dedicated base prompt rather than a suffix
  on `DEFAULT_PROMPTS["2"]`.

### 10.2 Research

- Simulate a successful targeted search with accepted sources and claims.
- Simulate insufficient evidence despite a technically successful API response.
- Assert child retries cannot exceed the parent deadline.
- Assert failed mandatory research stops before Stage 2.
- Assert no baseline or climate result is generated after research failure.

### 10.3 Primary diagnostic and recovery

- Assert the happy path produces a complete diagnostic without recovery.
- Assert incomplete fields trigger a bounded field-level repair.
- Assert recovery receives only necessary context and requested fields.
- Simulate slow recovery and verify progress or heartbeat behavior.
- Assert failed recovery cannot yield a misleading partial result.

### 10.4 Question selection and specificity

- Assert all required interaction directions are present.
- Assert relevant supplementary source-derived questions can surface beyond the
  six anchors.
- Assert irrelevant questions are omitted.
- Assert project details and source identifiers survive parsing and rendering.
- Assert generic priorities fail or are returned for repair when more specific
  evidence is available.

### 10.5 OPCS and instrument routing

- Test IPF, PforR, DPF, AF, restructuring, and MPA cases.
- Assert formal determinations are prohibited.
- Assert `authority_basis` normalization and display.
- Assert CERC, CDRS, Paris Alignment, ESS, ESSA, and PSIA terminology is
  instrument-appropriate.

### 10.6 Rendering and export

- Assert live HTML, shared HTML, downloaded HTML, and DOCX use the same validated
  data and section order.
- Assert failure states do not leave stale climate sections visible.

### 10.7 Production-like validation

Tests must include delayed fake clients, explicit timeouts, nested deadline
simulation, and server-sent-event behavior. Immediate fake responses alone are
not sufficient.

## 11. Rollout

1. Implement on `feat/climate-readout-redesign`.
2. Keep `main` on the restored ITS-compatible baseline.
3. Run focused climate tests and the complete regression suite.
4. Exercise representative IPF, PforR, DPF, AF, restructuring, and MPA
   fixtures.
5. Deploy the feature branch to an isolated Render preview or service.
6. Re-run the South Sudan SSNRL PCN plus CCDR case that exposed the failure.
7. Confirm the primary diagnostic completes without recovery.
8. Deliberately test research failure, diagnostic failure, recovery timeout, and
   provider overload.
9. Compare the live and exported result with the approved climate mock and this
   specification.
10. Obtain user acceptance before any integration decision.
11. Plan ITS parity only after the Render behavior and shared contract are
    settled.

## 12. Acceptance criteria

The redesign is accepted when:

- climate mode never assembles the full generic FCV Stage 2 prompt;
- mandatory targeted research either provides validated evidence or stops the
  route;
- the normal climate path completes without diagnostic recovery;
- recovery is bounded, field-specific, observable, and genuinely exceptional;
- the compact FCV baseline contains no full checklist machinery;
- the readout supports the six anchors plus material supplementary questions;
- insights and priorities are demonstrably tied to project specifics and
  traceable guidance;
- climate priorities are instrument-aware and advisory;
- production-like timeout tests pass;
- the South Sudan live validation completes on the preview deployment;
- all exports match the live readout; and
- the standard FCV route remains unchanged.

## 13. Implementation planning notes

The implementation plan should begin with tests that expose the current
architecture:

1. complete-prompt routing test;
2. mandatory-research stop test;
3. research deadline-ownership test;
4. happy-path-no-recovery test; and
5. recovery streaming/deadline test.

Only then should it:

1. introduce a dedicated climate Stage 2 base prompt;
2. remove the generic engine from the climate route;
3. refactor research deadline ownership;
4. make research fail-closed;
5. change recovery to bounded field-level repair;
6. strengthen specificity and provenance validation;
7. preserve the approved readout and climate priority rendering; and
8. complete preview deployment and live acceptance testing.
