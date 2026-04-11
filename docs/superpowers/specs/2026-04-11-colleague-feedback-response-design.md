# Design Spec: Colleague Feedback Response — Instrument Awareness, Temporal Logic, Two-Tab Architecture

**Date:** 2026-04-11
**Status:** Draft
**Triggered by:** Detailed practitioner feedback from FCV colleague testing the app with a real PAD
**Version target:** v8.0

---

## 1. Problem Statement

An experienced FCV practitioner tested the app extensively with a real PAD and identified systemic issues that fall into three categories:

1. **Knowledge gaps:** The LLM lacks understanding of WB instrument types (IPF/PforR/DPO/TA), applies current-day standards to historical projects, recommends beyond PDO scope, and uses narrow keyword matching instead of concept recognition.
2. **Assessment logic flaws:** The rating rubric rewards complexity over fit-for-purpose design, the LLM produces contradictory statements without reconciling them, and marks recommendations as gaps when they're not applicable to the instrument or project stage.
3. **UX friction:** Poor navigation between stages, opaque FCV terminology for non-specialists, insufficient upload guidance, and no glossary for key FCV concepts.

Additionally, the colleague raised the need for a separate workflow for **implementation-stage assessment** (MTR, ISR, AF, Restructuring, ICR) — distinct from the current design-stage review.

---

## 2. Overall Architecture

### Two-Mode App with Shared Knowledge Core

```
+---------------------------------------------------+
|              FCV Project Screener v8.0             |
|  +--------------------+ +------------------------+|
|  |  Design Review     | | Implementation Review  ||
|  |  (Pre-Appraisal)   | | (Post-Appraisal)      ||
|  +--------+-----------+ +----------+-------------+|
|           |                        |               |
|     3-stage pipeline         3-stage pipeline      |
|     (current, improved)     (new prompts,          |
|                              multi-doc,            |
|                              backward+forward)     |
|           |                        |               |
|           +----------+-------------+               |
|                      |                             |
|        +-------------+--------------+              |
|        |   Shared Knowledge Core    |              |
|        | - WB_INSTRUMENT_GUIDE      |              |
|        | - FCV framework constants  |              |
|        | - FCV_GLOSSARY             |              |
|        | - WB_PROCESS_GUIDE (new)   |              |
|        +----------------------------+              |
+---------------------------------------------------+
```

**Mode selection:** Landing page offers two clear entry points. Once selected, the pipeline, prompts, and UI adapt. User cannot switch mid-assessment (would invalidate context).

**Priority:** Design Review improvements (Workstreams 0-3) are primary. Implementation Review tab (Workstream 4) is secondary but shapes the architecture from the start.

---

## 3. Workstream 0: Guardrails & Robustness

Cross-cutting workstream that prevents improvements from degrading performance.

### 3.1 Token Budget Management

**Hard ceiling per stage:** Total prompt (system instructions + background docs + conversation history + document text) must not exceed 150k tokens, leaving 50k headroom for LLM response.

**Priority order when budget is tight (trim from bottom first):**
1. User's primary document (never truncated beyond existing MAX_DOC_CHARS)
2. Conversation history (needed for stage continuity)
3. Instrument-specific knowledge slice
4. Stage-specific prompt instructions
5. Supplementary document summaries (condensed aggressively)
6. General FCV framework constants (can be trimmed to essentials)

**Implementation:** A `calculate_token_budget()` function that estimates total context before each API call and applies condensation/trimming in priority order if needed. Logs what was trimmed for debugging.

### 3.2 Multi-Document Handling

**Design Review tab:** 1 primary + up to 2 supplementary documents.
- Primary doc: full extraction (condensed only if >150k chars, as now)
- Supplementary docs: always condensed to ~20% of original via LLM summary, focused on FCV-relevant content
- Total document budget: ~80k chars across all docs after condensation

**Implementation Review tab:** Up to 5 documents.
- Most recent/primary doc (e.g., MTR report): full extraction
- Supporting docs (PAD, ISRs): condensed to FCV-relevant summaries
- Chronological ordering preserved so the LLM understands the timeline
- Total document budget: same ~80k chars, split across more documents

**User feedback:** If documents are condensed, show a note: "X was condensed for analysis. Key content preserved; some detail may be summarised."

### 3.3 Background Doc Injection Strategy

Only inject what each stage needs. Updated injection map:

| Constant | Design S1 | Design S2 | Design S3 | Impl S1 | Impl S2 | Impl S3 |
|---|---|---|---|---|---|---|
| FCV_GUIDE | Yes | Yes | — | Yes | Yes | — |
| FCV_OPERATIONAL_MANUAL | — | Yes | — | — | Yes | — |
| FCV_REFRESH_FRAMEWORK | Yes | Yes | Yes | Yes | Yes | Yes |
| PLAYBOOK (stage-appropriate) | Yes | — | Yes | Yes | — | Yes |
| WB_INSTRUMENT_GUIDE (slice) | Yes | Yes | Yes | Yes | Yes | Yes |
| WB_PROCESS_GUIDE (slice) | — | — | — | Yes | Yes | Yes |
| FCV_GLOSSARY | — | Yes | — | — | Yes | — |

### 3.4 Graceful Degradation

- **Temporal extraction fails** (no dates found): Proceed without temporal anchoring. Display: "Could not determine project dates from document. Assessment uses current standards."
- **Instrument type extraction fails**: Default to IPF (most common). Display: "Instrument type not identified — defaulting to IPF. Correct if needed."
- **Supplementary document extraction fails**: Warn and proceed with primary document only.
- **Background doc injection exceeds budget**: Trim glossary first, then general framework constants. Never trim instrument guide or user documents.

---

## 4. Workstream 1: Instrument & Context Awareness (Prompt Changes)

Six interconnected changes to the prompt pipeline.

### 4.1 Instrument-Aware Assessment

**Extraction:** Stage 1 extracts instrument type (IPF/PforR/DPO/TA) from the document alongside the existing `DOC_TYPE` extraction. Passed to Stages 2 and 3 as `{instrument_type}`.

**Stage 2 rating rubric changes:**
- Each of the 12 OST recs gets an applicability flag per instrument type. E.g., "Pros/cons of impact evaluation" is relevant to IPF but less applicable to DPO. "Policy prior actions" is DPO-specific.
- The LLM can mark a rec as "N/A for this instrument" — these do not count toward or against the rating.
- Rating denominator becomes: applicable recs addressed / applicable recs (not addressed / 12).
- Same logic for DNH principles — some manifest differently under different instruments.

**Stage 3 recommendations:**
- Must be feasible under the identified instrument. No suggesting DPO-style policy conditionality for an IPF.
- The `WB_INSTRUMENT_GUIDE` slice for the relevant instrument gets injected so the LLM knows what operational levers are actually available.

### 4.2 Temporal Anchoring

**Stage 1 extraction:** New delimiter block `%%%TEMPORAL_CONTEXT_START%%%` / `%%%TEMPORAL_CONTEXT_END%%%` containing:
- Approval/board date (or preparation date for PCN/PID)
- Closing date (if available)
- Safeguards framework in use (ESF or old OP/BPs — determined from document, not assumed)
- Other temporal markers (restructuring dates, AF dates)

**Surfaced to user:** Displayed as a small info panel after Stage 1 output:
```
Working Context
Instrument: IPF       Approved: June 2018
Safeguards: OP/BP (pre-ESF)    Closing: December 2024
Assessment anchored to preparation period
```

**Injected to Stages 2-3:** Hard guardrail instruction: "Assess this project by the standards, policies, and events available as of [extracted date]. Do not penalise for events, policy changes, or knowledge that post-dates this. Post-preparation developments may be noted in the Horizon Considerations section but must not affect ratings."

**Data Sheet reading:** Explicit Stage 1 instruction to extract and use Data Sheet fields. If the Data Sheet specifies OP/BP safeguards, the LLM must never reference ESF. If it specifies a closing date, the LLM must recognise the project's temporal boundaries.

### 4.3 PDO/Scope Bounding

**Stage 1:** Explicit extraction of PDO statement, ToC summary, and RF scope markers.

**Stage 2:** Assessment is bounded: "Evaluate FCV integration within the stated PDO, ToC, and RF. If an OST recommendation falls outside the operation's scope, mark it as 'Beyond scope' rather than 'Weakly addressed'. Do not penalise a national project for lacking regional-level activities, or an IPF for lacking DPO-style policy conditionality."

**Stage 3 — two distinct sections:**
- **Priority Actions** (rated, within scope): As now, but only for things achievable within PDO/instrument/scope.
- **Horizon Considerations** (unrated, clearly labelled, beyond scope): "The team may wish to be aware of..." for legitimate FCV concerns outside the current operation's mandate. Does not affect ratings. Also receives unresolved analytical tensions from Stage 2. Rendered as a collapsible `<details>` panel below the priority cards, visually distinct (lighter background, dashed border) to clearly separate it from rated content.

### 4.4 Simplicity Recognition

**Prompt instruction (Stage 2):** "A deliberately simple, fit-for-purpose design with fewer components, a lean results framework, and narrow scope may be an intentional and appropriate FCV strategy — particularly for IPF in high-fragility settings where implementation capacity is limited, or where the team plans a follow-on AF to scale up. Do not penalise lean design. Assess whether the design elements that are present are FCV-informed, not whether every possible FCV element is included."

**Rubric modifier:** When the LLM identifies a deliberately lean design, it notes this in the rating reasoning and adjusts the denominator accordingly (similar to N/A for instrument, but for intentional scope choices).

### 4.5 Concept Recognition

**Stage 1 prompt addition:** "Read and apply any Abbreviations and Acronyms table in the document. When assessing against FCV recommendations, recognise the concept and intent, not just specific terms. Each recommendation represents a principle that can be fulfilled through multiple approaches — assess whether the intent is met, not whether a specific keyword appears."

**Examples to embed in prompts (illustrative, not exhaustive):**
- Geospatial monitoring: GEMS, GIS, geo-localization, satellite imagery, remote sensing, spatial analysis
- Independent verification: TPM, third-party monitoring, independent spot checks, remote verification
- Impact evaluation: IE, rigorous evaluation, experimental design, quasi-experimental methods
- Capacity building: includes crisis management capacity, institutional strengthening, not just M&E capacity
- Digital tools: encompasses geospatial platforms, mobile data collection, digital GRM, remote monitoring — not limited to any single platform

**Background docs update:** Each OST recommendation and operational flexibility in the existing constants gets broadened from specific terms to concept families. The principle is: teach the concept, give examples, don't create a keyword checklist.

**Abbreviation handling:** Stage 1 prompt explicitly instructs: "If the document contains an Abbreviations/Acronyms section, parse it and use those definitions throughout analysis. When encountering abbreviations in the document text (e.g., IE for Impact Evaluation), resolve them using the document's own definitions."

### 4.6 Logical Consistency

**Stage 2 prompt addition:** "Before finalising, review your findings for internal contradictions. If you identify tension between findings (e.g., a project both addresses resource scarcity and potentially intensifies competition), explicitly reconcile the tension with reasoning rather than stating both flatly. Acknowledge nuance — real FCV analysis often holds tensions — but explain your reasoning."

**Stage 3:** The Horizon Considerations section also receives any analytical tensions that could not be fully reconciled — flagged transparently for the team rather than buried or ignored.

---

## 5. Workstream 2: Knowledge Base (background_docs.py)

### 5.1 New Constant: WB_INSTRUMENT_GUIDE

Structured as a per-instrument reference, sliceable so only the relevant instrument is injected per stage.

**Per-instrument structure:**
```python
WB_INSTRUMENT_GUIDE = {
    "IPF": {
        "name": "Investment Project Financing",
        "description": "...",  # What it is, how it works
        "fcv_levers": "...",   # FCV-relevant tools available (CERC, HEIS, TPM, phased disbursement, etc.)
        "not_applicable": "...",  # What it can't do (policy conditionality, results-based disbursement)
        "typical_structure": "...",  # Standard components/design
        "common_fcv_considerations": "...",  # Where IPFs typically need FCV attention
        "preparation_process": "...",  # Key stages and decision points
        "supervision_process": "...",  # ISR cycle, MTR trigger, restructuring options
    },
    "PforR": { ... },
    "DPO": { ... },
    "TA": { ... }
}
```

**Token budget:** ~2,000 tokens per instrument, ~8,000 total. Only the relevant slice (~2,000 tokens) injected per stage.

**Emphasis:** IPF gets the most detailed treatment (60-70% of use cases). PforR and DPO get solid coverage. TA gets lightweight coverage.

**Sourcing strategy:**
1. Research publicly available WB operational policy documents, IPF/PforR/DPO policy frameworks, public guidance notes
2. Draft the constant with publicly available knowledge
3. User reviews and identifies gaps — particularly "what's realistic to expect under an IPF" vs. "what policy technically allows"
4. User queries internal LLM for gap-filling summaries on procedures and common practice
5. Integrate and finalise

### 5.2 New Constant: WB_PROCESS_GUIDE

For the Implementation Review tab. Same sliceable structure.

**Per-process structure:**
```python
WB_PROCESS_GUIDE = {
    "MTR": {
        "purpose": "...",        # What it's for, when it happens
        "scope": "...",          # What it can and can't change
        "backward_look": "...",  # What to assess (approval -> MTR performance)
        "forward_look": "...",   # What to recommend (MTR -> closure adjustments)
        "key_policies": "...",   # Relevant OPs, procedures
        "typical_documents": "...",  # What docs are available at this stage
        "fcv_considerations": "...",  # FCV-specific guidance for this process
    },
    "ISR": { ... },
    "AF": { ... },
    "Restructuring": { ... },
    "ICR": { ... }
}
```

**Token budget:** ~1,500 tokens per process, ~7,500 total. Only the relevant slice injected.

**Sourcing:** Same 5-step strategy. This constant will likely need more internal knowledge since MTR/ISR procedures have operational nuances not fully public.

### 5.3 New Constant: FCV_GLOSSARY

Serves double duty: frontend glossary tooltips and prompt grounding for consistent definitions.

```python
FCV_GLOSSARY = {
    "elite_capture": {
        "definition": "...",
        "measurement": "...",  # How it's typically assessed
        "relevance": "...",    # Why it matters for FCV screening
        "source": "..."        # WBG source document or trusted external source
    },
    "social_cohesion": { ... },
    "conflict_analysis": { ... },
    "do_no_harm": { ... },
    "third_party_monitoring": { ... },
    "grievance_redress_mechanism": { ... },
    "cerc": { ... },
    "heis": { ... },
    # ... ~15-20 key terms
}
```

**Definition sourcing priority:**
1. WBG OST Manual, FCV Playbook, FCV Strategy/Refresh documents
2. WBG public website and operational policy definitions
3. Trusted external FCV sources: UN (UNDP, UNHCR, UNOCHA), OECD (States of Fragility), ICG, SIPRI
4. Academic FCV literature (only for terms not defined by practitioner sources)

**Token budget:** ~2,000 tokens total. Injected into Stage 2 only (where terms are most actively used). Served to frontend as static JSON endpoint for tooltips.

### 5.4 Broadening Existing Constants

Updates to `FCV_OPERATIONAL_MANUAL` and Playbook constants:
- GEMS references -> "geospatial monitoring (including but not limited to GEMS, GIS, geo-localization, satellite/remote sensing, spatial analysis)"
- M&E capacity references -> "monitoring, evaluation, and crisis management capacity (including institutional capacity building for crisis preparedness and recovery planning)"
- Each OST recommendation gets a brief "recognition note" — 2-3 variant terms/approaches that satisfy the same intent
- Impact evaluation references broadened to include "IE" abbreviation and methodology-level discussion
- TPM references broadened to the concept of independent verification mechanisms

### 5.5 Date-Stamping and Policy Currency

Every knowledge constant gets a header comment:
```python
# Last verified: 2026-04
# Policy-sensitive fields: ESF framework (post-Oct 2018), procurement framework, IDA allocation rules
# Review trigger: Update when WBG operational policies change
```

**Transition-sensitive areas flagged explicitly in WB_INSTRUMENT_GUIDE:**
- "Projects approved before October 2018 use OP/BP safeguards; projects approved after use the ESF. The document's Data Sheet is authoritative."
- Similar notes for procurement framework changes and any other policy transitions

**Research approach:** Web searches for current WBG policies at time of drafting — not relying solely on LLM training data for policy specifics.

---

## 6. Workstream 3: Frontend UX (index.html)

### 6.1 Stage Navigation

**Fix:** Make the stepper bar clickable after stages complete in both Step-by-Step and Express modes. Currently `enableClickableStepper()` only activates after Express — extend to Step-by-Step.

**Addition:** Sticky breadcrumb below stepper when in Stage 3: `Context | Assessment | Recommendations` as inline text links that jump to the relevant output section.

### 6.2 Expanded Badge Labels

All four FCV Refresh shift badges get full labels:
- `"A: Anticipate"` -> `"FCV Refresh Shift A: Anticipate"`
- `"B: Differentiate"` -> `"FCV Refresh Shift B: Differentiate"`
- `"C: Jobs & Private Sector"` -> `"FCV Refresh Shift C: Jobs & Private Sector"`
- `"D: Enhanced Toolkit"` -> `"FCV Refresh Shift D: Enhanced Toolkit"`

Risk badges: `"Risk: High"` -> `"FCV Risk: High"` (similarly for Medium/Low).

**Compact mode** (priority stepper tabs): Keeps short form but adds tooltip with full label and a one-line explanation of what the shift means.

### 6.3 FCV Glossary Tooltips

Key FCV terms in rendered output get dotted-underline styling and a hover tooltip:
- Terms: elite capture, social cohesion, conflict analysis, Do No Harm, third-party monitoring, grievance redress mechanism, CERC, HEIS, geospatial monitoring, etc.
- Tooltip content: definition + how typically measured/applied (pulled from `FCV_GLOSSARY` constant)
- Implementation: JS function scans rendered output for glossary terms and wraps in `<span class="glossary-term" data-term="...">` with CSS tooltip

**Collapsible glossary panel:** Accessible from sidebar or footer — the "virtual annex" for browsing all definitions.

### 6.4 Enhanced Upload Instructions

Context-aware helper text in the upload zone:

**Design Review tab:**
> "Upload your primary project document (PCN, PID, or PAD). For a stronger assessment, also upload supporting documents such as the RRA, technical/feasibility studies, PPSD, or stakeholder analysis. The tool works best with 1-3 documents."

**Implementation Review tab:**
> "Upload the documents relevant to your review. For an MTR, upload the original PAD plus recent ISRs and the MTR report. For an ICR, upload the PAD, key ISRs, and the draft ICR. The tool works best with 2-5 documents."

**Size note:** "Documents over 150k characters will be automatically condensed. Very large uploads may reduce analysis depth."

### 6.5 Temporal Context Display

Small info panel displayed after Stage 1 completes, between Stage 1 output and Stage 2 input:

```
Working Context
Instrument: IPF       Approved: June 2018
Safeguards: OP/BP (pre-ESF)    Closing: December 2024
Assessment anchored to preparation period
```

Visible but unobtrusive. User can immediately verify the LLM's temporal frame.

### 6.6 Two-Tab Mode Selector

Landing page offers two clear entry points before any upload:

**Design Review:**
> Assess FCV integration in project design (PCN / PID / PAD)

**Implementation Review:**
> Assess FCV performance during implementation and recommend course corrections (MTR / ISR / AF / Restructuring / ICR)

Once selected, the pipeline adapts: different upload instructions, different prompts, different output structure. User can return to mode selection to start a new assessment. Both tabs support Express mode and Step-by-Step mode — the mode selector (Design vs. Implementation) is chosen first, then the workflow mode (Express vs. Step-by-Step) applies within it.

---

## 7. Workstream 4: Implementation Review Tab — Prompt Pipeline

Secondary priority. Shares the knowledge core but has its own prompt pipeline.

### 7.1 Stage 1: Context & Performance Extraction

**Input:** Primary process document (MTR/ISR/AF/Restructuring/ICR) + original PAD + supporting docs.

**Key differences from Design Review:**
- Extracts a timeline of events: approval -> key milestones -> restructurings -> current stage
- Identifies what changed since approval: scope changes, component modifications, triggering events
- Extracts performance data: disbursement rates, RF indicator progress, ISR ratings history, flagged issues
- Applies `WB_PROCESS_GUIDE` slice for the specific process

**Output:**
- Part A: Document extraction (timeline-oriented)
- Part B: Contextualised with FCV developments since approval
- Temporal context panel: approval date, current stage, key inflection points

### 7.2 Stage 2: Performance Assessment

**Backward look:** How well did the original FCV-sensitive design hold up? Did assumptions prove correct? Were FCV risks that materialised anticipated? Were adaptive mechanisms used?

**Forward look:** What FCV-relevant adjustments are needed for the remaining implementation period?

**Process-appropriate framing:**
- MTR: "What should be restructured or reinforced for the second half?"
- ISR: "What flags need attention before the next mission?"
- AF: "Does the additional financing address FCV gaps from the original design?"
- Restructuring: "Is the restructuring FCV-informed?"
- ICR: "What FCV lessons should be captured?"

**Rating approach:** Still uses S/R framework, but rates current FCV integration (design + adaptation + implementation) rather than just design intent. A project well-designed but never adapted to changing FCV context would rate differently.

### 7.3 Stage 3: Course-Correction Recommendations

**Key differences:**
- Recommendations are action-oriented for the current process, not design suggestions
- `when` field values reflect implementation timing: "Before next ISR mission" / "At MTR decision meeting" / "In restructuring paper" / "For ICR lessons section"
- `actions[]` reference implementation instruments: restructuring triggers, AF justification language, ISR flag explanations, MTR recommendations
- Horizon Considerations section flags emerging FCV risks for the remainder of the project
- Process-specific output: MTR gets restructuring recommendations; ICR gets lessons learned framing

### 7.4 What's Shared vs. Distinct

| Element | Shared | Distinct per tab |
|---|---|---|
| FCV framework (S/R, shifts, DNH) | Yes | — |
| Instrument guide | Yes | — |
| Scope bounding / simplicity logic | Yes | — |
| Temporal anchoring | Yes | Direction differs (forward vs. bidirectional) |
| Stage 1 extraction prompt | — | Design = single doc focus; Impl = multi-doc timeline |
| Stage 2 assessment prompt | — | Design = intent assessment; Impl = performance assessment |
| Stage 3 recommendation prompt | — | Design = design recs; Impl = course-correction recs |
| Process guide injection | — | Implementation tab only |
| Rating rubric | Partially | Impl adds adaptation/responsiveness criteria |
| Priority JSON schema | Mostly | `when` field values differ; `actions[]` reference different instruments |

---

## 8. Feedback Traceability

Every point from the colleague's feedback mapped to where it's addressed:

| Feedback Point | Addressed In |
|---|---|
| LLM lacks instrument knowledge (IPF vs DPO vs PforR) | WS2 s5.1 (WB_INSTRUMENT_GUIDE) + WS1 s4.1 |
| Judges IPFs for things only possible under other instruments | WS1 s4.1 (N/A flag per instrument) |
| Time dimension: judges past with today's knowledge | WS1 s4.2 (temporal anchoring) |
| ESF vs old safeguards confusion | WS1 s4.2 + WS2 s5.5 (date-stamping) |
| PDO/scope creep: recommends beyond scope, then penalises | WS1 s4.3 (scope bounding + horizon scan) |
| Complexity vs simplicity: "more the merrier" bias | WS1 s4.4 (simplicity recognition + rubric modifier) |
| Narrow term matching (GEMS, IE, capacity building) | WS1 s4.5 (concept recognition) + WS2 s5.4 |
| Doesn't read abbreviation/acronym tables | WS1 s4.5 |
| Contradictory statements in assessment | WS1 s4.6 (logical consistency) |
| Can't navigate back to earlier tabs easily | WS3 s6.1 (clickable stepper) |
| "B: Differentiate" opaque to non-specialists | WS3 s6.2 (expanded labels, all 4 shifts) |
| "Risk" badge unclear | WS3 s6.2 ("FCV Risk") |
| FCV terms need definitions/glossary | WS3 s6.3 (glossary tooltips + annex) |
| Upload should ask for supplementary docs | WS3 s6.4 (enhanced upload instructions) |
| MTR needs backward + forward look | WS4 s7.2 (Implementation Review pipeline) |
| Data Sheet not being read properly | WS1 s4.2 + WS0 s3.4 |
| ICR applicability at PAD stage illogical | WS1 s4.1 (N/A for instrument/stage) |
| Insufficient info from PAD alone given page limits | WS3 s6.4 + WS0 s3.2 |
| Token/robustness risks from expanded knowledge | WS0 (full guardrails layer) |
| Policy currency (ESF, procurement, etc.) | WS2 s5.5 (date-stamping + web research) |

---

## 9. Implementation Order

**Phase 1 — Knowledge Base (Workstream 2)**
Build the knowledge first. Other workstreams consume it.
1. Research and draft `WB_INSTRUMENT_GUIDE` (public sources)
2. Research and draft `FCV_GLOSSARY` (WBG + trusted external sources)
3. Broaden existing constants (concept families)
4. User reviews, identifies gaps, supplements from internal LLM
5. Date-stamp all constants

**Phase 2 — Prompt Changes (Workstream 1)**
Consume the new knowledge in prompt updates.
1. Stage 1: instrument extraction + temporal extraction + PDO extraction + abbreviation handling
2. Stage 2: instrument-aware rubric + scope bounding + simplicity recognition + logical consistency
3. Stage 3: scope-bounded recommendations + Horizon Considerations section + instrument-feasible actions
4. All stages: temporal anchoring guardrail

**Phase 3 — Frontend UX (Workstream 3)**
Independent of prompt changes; can partially overlap with Phase 2.
1. Clickable stepper navigation
2. Expanded badge labels (all 4 shifts + FCV Risk)
3. Glossary tooltips + collapsible glossary panel
4. Enhanced upload instructions
5. Temporal context display panel
6. Two-tab mode selector (landing page)

**Phase 4 — Implementation Review Pipeline (Workstream 4)**
Builds on all previous phases.
1. Draft `WB_PROCESS_GUIDE` (MTR/ISR/AF/Restructuring/ICR)
2. User supplements with internal process knowledge
3. Implementation Review Stage 1 prompt (multi-doc, timeline extraction)
4. Implementation Review Stage 2 prompt (backward + forward assessment, process-specific framing)
5. Implementation Review Stage 3 prompt (course-correction recommendations)
6. Frontend: Implementation Review upload zone, output structure, process-specific rendering

**Robustness (Workstream 0) runs throughout:**
- Token budget function built in Phase 2
- Multi-document handling built in Phase 1-2
- Graceful degradation tested in Phase 2-3
- Injection strategy table enforced from Phase 2 onward

---

## 10. Instrument Usage Expectations

Based on user input, expected distribution:
- **IPF:** 60-70% of assessments — gets most detailed treatment in instrument guide and prompt testing
- **PforR:** ~15% — solid coverage
- **DPO:** ~15% — solid coverage
- **TA:** ~5% — lightweight coverage

Due diligence and testing effort should mirror this distribution.

---

## 11. Risk & Mitigation

| Risk | Mitigation |
|---|---|
| New background docs consume too many tokens | Sliceable design — only relevant instrument/process injected. Token budget function enforces ceiling. |
| Temporal extraction unreliable across doc formats | Graceful degradation — proceed with note if extraction fails. Data Sheet is primary source. |
| Instrument knowledge gaps in public sources | 5-step sourcing strategy with user supplementation from internal LLM. |
| Two-tab architecture becomes "two apps in one UI" | Shared knowledge core + shared rendering components. Only prompts and output structure diverge. |
| Concept recognition too loose (false positives) | Prompt instructs concept-level matching with examples, not unconstrained inference. |
| Glossary maintenance burden | Start with ~15-20 terms. Source from authoritative documents. Review annually or when feedback indicates gaps. |
| Implementation Review tab scope creep | Each process (MTR/ISR/AF/Restructuring/ICR) gets tailored but bounded treatment via WB_PROCESS_GUIDE slices. |
