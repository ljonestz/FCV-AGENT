# Summary–Detailed Alignment and Production UX Design

**Date:** 2026-08-22  
**Branch:** `codex/climate-summary-quality-fixes`  
**Status:** Approved design; implementation not yet started

## Purpose

Make the Summary a concise, accessible, standalone reading of the Detailed assessment while ensuring both views express the same findings, facts, actions, rankings, and project-cycle timing. Reduce the visual obstruction at the top of Detailed so users reach the Recommendations Note immediately.

## Problems Observed

1. Summary and Detailed are generated as partly independent products. Structural validation checks presence and length, but not whether their meaning aligns. This permits titles, rationales, actions, suggested wording, and project-cycle statements to drift.
2. Summary has a prominent “Where this fits in the project cycle” section. Detailed exposes timing inconsistently through pills, metadata, or action prose, so the richer view can contain less visible lifecycle guidance than the concise view.
3. The current Detailed header gives substantial space to two large meters and a Priority Overview before the Recommendations Note. The overview also duplicates priority navigation already present in the note.
4. Lifecycle metadata is insufficiently validated. A concept-stage PID can inherit the example value `mid-cycle`, although that scope should be limited to contexts such as Additional Financing or restructuring.
5. Cross-view consistency does not guarantee factual correctness. An unsupported or imprecise claim can currently appear consistently in both views.
6. Detailed HTML and DOCX exports contain timing metadata but do not consistently present the same explicit project-cycle explanation shown in Summary.

## Design Principles

- Detailed is the canonical source of truth; Summary is a projection of it.
- Summary may simplify and connect ideas, but may not create new facts, recommendations, milestones, rankings, or interpretations.
- Summary must remain understandable without opening Detailed.
- The interface should lead with substantive recommendations, not navigation or decorative scoring.
- Lifecycle language must reflect the actual document type and project stage.
- Invalid concise content should degrade safely at the affected field or priority, not discard an otherwise valid Detailed assessment.
- The same canonical data must drive the browser views and exports.

## Canonical Content Model

Each priority has one stable identity and one canonical Detailed record containing at least:

- rank and canonical title;
- finding or gap;
- contextual rationale and consequences;
- recommended actions, each with a stable action identity where practical;
- canonical project-cycle timing, including primary milestone and optional secondary milestone;
- suggested wording or target document change;
- evidence and source references;
- applicable scope metadata derived from document and review context.

The concise representation belongs to the same priority record. Its accessible title, rationale, action summary, and lifecycle explanation must reference the canonical fields rather than form an independent priority. Concise actions should map to canonical action identities; where action identities cannot be introduced without disproportionate migration risk, normalized text matching plus explicit validation may be used initially.

Project-cycle data should be represented once in structured form. Both views may render it differently, but neither may maintain an independent milestone value.

## Summary Experience

The Summary is a five-minute, non-expert-friendly assessment with this order:

1. Overall assessment and compact ratings.
2. Three strengths that establish what the project can build on.
3. Ranked priorities.
4. A short advisory and synthesis.

Each priority follows the same mini-narrative:

1. what needs attention;
2. why it matters;
3. what to do;
4. where it fits in the project cycle.

The opening identifies the project stage, explains what the ratings mean in plain language, and establishes the assessment’s central message. The transition from strengths to priorities explains that the recommendations build on the existing foundation. Priority ordering is described as an implementation path rather than a disconnected list. The closing distinguishes immediate decisions from later actions and synthesizes the overall pathway.

Transitions are selective and concise. They are generated only from canonical assessment content and must not introduce new causal claims. Repetition of card text in the opening or closing is avoided.

The first priority may remain expanded by default, with one-at-a-time accordion behavior, so the page stays easy to scan on a phone.

## Detailed Experience

### Wide screens

- Use a slim sticky sidebar containing only the Sensitivity and Responsiveness ratings.
- Replace large semicircular meters with compact textual rating cards or slim bars. Rating labels and explanations remain visible without relying on color.
- Remove the separate Priority Overview above the note.
- Begin the Recommendations Note near the top of the first viewport.
- Retain the priority controls within the Recommendations Note, where they have context. They must use semantic buttons, expose selected state, support keyboard operation, and have visible focus styles.

### Narrow screens

- Remove the sidebar from the layout flow.
- Present ratings as one compact, collapsible “Assessment ratings” row above the Recommendations Note.
- Do not introduce a second mobile priority navigator. Use the note’s existing priority controls or accordion pattern.

### Priority structure

Each Detailed priority presents:

1. finding or gap;
2. why it matters in this project and context;
3. recommended actions;
4. an explicit “Where this fits in the project cycle” block;
5. suggested wording or document changes;
6. evidence and sources.

The lifecycle block uses the same structured milestones as Summary, but may add precise decision points, dependencies, responsible project phase, and rationale. It should not bury timing only in implementation prose.

## Content Generation and Validation

### Generation

The generation contract should produce canonical Detailed priorities first. Concise fields are then created as accessible transformations attached to those priorities. If generation remains single-pass, prompt ordering and schema relationships must still make the canonical-to-concise dependency explicit.

Static schema examples must not contain plausible placeholder values such as `mid-cycle` that can escape into production. Examples should use unmistakable placeholders or be omitted where the value must be inferred from document context.

### Structural and semantic validation

Validation must cover:

- identical priority count, rank, and identity across views;
- concise title and rationale grounded in the canonical finding and rationale;
- concise actions mapped to, or a faithful subset of, canonical actions;
- suggested wording linked to a canonical action or documented target;
- identical structured project-cycle milestones across views;
- lifecycle compatibility with document type, financing type, and review stage;
- allowed use of special scope labels such as mid-cycle, restructuring, or multi-country;
- no new named entities, dates, quantitative claims, or institutional assertions in Summary unless present in the canonical evidence-backed record;
- source identifiers that resolve to evidence used by the corresponding claim.

Semantic checks should favor explicit identifiers and controlled enums over open-ended text comparison. Textual similarity can supplement these checks but should not be the sole production safeguard.

### Safe fallback

If a concise field fails alignment validation, derive a conservative fallback from the relevant canonical field. If an entire concise priority fails, render a deterministic shortened version of that Detailed priority. Preserve all other valid Summary priorities. Fall back to Detailed-only mode only when the canonical assessment itself is invalid.

Validation failures should be logged with non-sensitive reason codes and priority identifiers, without logging source-document contents.

## Evidence Quality

Claims require more than agreement between views. The pipeline should distinguish project-document evidence from background context and preserve source attribution at claim or priority level. High-risk claims involving political status, conflict events, dates, institutions, or legal/constitutional changes require direct supporting evidence and should not be strengthened beyond the source wording.

Where evidence is ambiguous, the output should use qualified language or omit the claim. Production tests should include a regression case for date conflation and for a background claim being repeated accurately but unsupported.

## Exports

Detailed HTML and DOCX exports remain Detailed products; a separate Summary export is not required by this design. Both exports must render the canonical project-cycle block for every priority and preserve the same rank, actions, milestones, evidence, and rating semantics as the browser Detailed view.

Export layouts do not reproduce the sticky sidebar. Ratings appear once in a compact assessment header. Priority navigation controls are omitted from static outputs.

DOCX must be visually rendered and inspected before release, including page breaks, heading hierarchy, tables, hyperlinks, and lifecycle blocks. Structural paragraph inspection alone is insufficient.

## Accessibility and Responsive Requirements

- All interactive controls use native buttons or equivalent semantic elements.
- Accordion and priority controls expose expanded/selected state to assistive technology.
- Rating meaning is available in text and is not encoded by color alone.
- Focus order follows reading order; the sticky rail does not intercept or duplicate navigation.
- Touch targets remain usable at phone widths.
- At 200% zoom, content remains readable without overlapping sticky elements.
- Reduced-motion preferences are respected for accordion and selection transitions.

## Production Verification

Automated contract tests should cover:

- Summary fields mapped to the correct canonical priority;
- no concise-only action, milestone, named entity, or quantitative claim;
- correct handling of optional secondary milestones;
- lifecycle/scope validation for concept, appraisal, Additional Financing, restructuring, and multi-country cases;
- per-priority fallback rather than all-or-nothing failure;
- identical canonical content in browser Detailed, HTML export, and DOCX export;
- keyboard and ARIA state for priority and accordion controls;
- removal of the duplicated Priority Overview.

Representative end-to-end fixtures should include short and long titles, one to five priorities, missing optional timing, long evidence lists, and narrow/mobile layouts. Visual regression checks should cover at least phone, tablet, standard laptop, and wide desktop widths.

Before implementation changes to shared prompt, delimiter, or priority JSON surfaces, read the private dual-build parity contract and record the change in its local divergence log. The public repository must not contain private parity-contract content.

## Acceptance Criteria

The design is complete when:

1. Every Summary priority is demonstrably derived from one Detailed priority.
2. Summary and Detailed show the same project-cycle milestones, at different levels of detail.
3. Summary reads as a coherent standalone narrative for a non-expert audience.
4. Detailed begins with substantive note content in the first viewport on a standard laptop.
5. The desktop rail contains only compact ratings; duplicated priority overview/navigation is removed.
6. Mobile has no persistent sidebar and no duplicated priority navigator.
7. Invalid lifecycle scopes cannot pass through from prompt examples or model output.
8. Unsupported factual claims are qualified, rejected, or omitted.
9. Browser Detailed, HTML export, and DOCX export agree on canonical content.
10. Automated, responsive, accessibility, and rendered-export checks pass.

## Out of Scope

- Redesigning the underlying rating methodology.
- Adding a separate Summary download format.
- Replacing the complete Recommendations Note visual language.
- Introducing new external evidence sources or retrieval infrastructure.
- Changing the number of strengths or the approved one-at-a-time Summary interaction unless testing reveals a blocking accessibility issue.

