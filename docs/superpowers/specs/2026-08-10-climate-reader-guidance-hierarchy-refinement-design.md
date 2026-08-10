# Climate Reader Guidance and Hierarchy Refinement Design

**Date:** 2026-08-10
**Status:** Approved visual direction; implementation pending written-spec review
**Branch:** `feat/climate-reader-lay-comprehensibility`

## Purpose

Refine the verified Climate-FCV reader without changing its substantive analytical depth or report sequence. The approved direction is a balanced hierarchy: one stronger overview treatment, progressive disclosure for lower-ranked priorities, numbered secondary points, richer project-specific WBG guidance, and a simpler methodology section.

The change must preserve the reader as a prose-led technical report for a WBG audience. It must not return to the earlier card-heavy or multi-layered design.

## Goals

1. Make the overview visually distinct enough to orient a reader immediately.
2. Reduce initial page length while keeping every priority narrative, recommendation detail and drafting suggestion available.
3. Replace the redundant priority-title summary with a useful transition from analysis to action.
4. Make decision checks and monitoring points easier to scan without enclosing every item in a tile.
5. Select two to four WBG sources according to the findings of each assessment and explain, in project-specific prose, what the team can learn from each source.
6. Remove technical content that does not help the intended reader: the evidence-status banner, raw evidence-code inventory and run diagnostics.
7. Preserve the plain-language methodology, limitations and sources/further-reading list.
8. Keep live web, standalone HTML export and DOCX output aligned wherever their formats support the same treatment.

## Non-goals

- Do not shorten or rewrite the executive readout or core climate-FCV answers.
- Do not change the rating semantics, priority admission logic, evidence validation, source-of-truth assessment schema, or recommendation content.
- Do not make source selection random. Variation must follow project evidence and the core questions actually answered.
- Do not add a new dashboard, sidebar, sticky navigation or nested card system.
- Do not expose internal diagnostics elsewhere after removing them from the reader.
- Do not treat guidance or reviewer judgment as a mandatory WBG policy requirement.

## Approved Reading Experience

### 1. Overview

The entire sensitivity block becomes one restrained panel with a white background, subtle border, green accent and modest radius. It contains the existing question, rating, scale, rating gloss, overview summary and institutional caveat. The section number and `Overview` heading remain outside or visually attached to the panel according to the existing report-heading pattern.

The executive readout stays in the normal document flow below the panel. It is not placed inside a second box.

The non-approved evidence-status banner is removed. Smoke mode retains its explicit workflow-only warning because that message describes runtime behavior rather than evidence approval.

### 2. Core Climate-FCV Questions

No structural change. The section remains the main analytical body and retains its current prose depth and source attribution. Existing spacing and heading treatments remain.

### 3. Ranked Operational Priorities

Replace the generated title list with this narrative pattern:

> Drawing on the overview and core climate-FCV questions, the analysis identifies **[N] main operational priority/priorities** for strengthening climate resilience, conflict sensitivity and implementation readiness in this project. These are followed by secondary points to check before the decision meeting and issues to keep under review as preparation advances.

The count and singular/plural grammar are dynamic. When no priority is admitted, preserve the existing no-priority explanation rather than showing this transition.

Priority 1 is expanded by default and preserves all current content, including suggested drafting and recommendation details. Priorities 2 onward render as accessible disclosure elements showing rank and title in the closed state. Expanding one reveals the complete existing priority body. No priority content is removed from HTML, export or DOCX; DOCX remains fully expanded because collapsible interaction is not available in Word.

Disclosure summaries must be keyboard operable, expose visible focus, and retain semantic `<details>/<summary>` behavior in HTML.

### 4. Points to Check Before the Decision Meeting

Retain the two groups and their order:

1. Smaller climate and fragility points to consider.
2. Document points to confirm.

Number items locally within each group using two-digit labels (`01`, `02`, and so on). Use a number column, thin dividing rules and whitespace. Do not add individual boxes.

### 5. What to Keep an Eye On

Number monitoring items sequentially with the same restrained number-column pattern, using the existing blue accent. Preserve the distinction between a current action and an issue to monitor.

### 6. Relevant WBG Guidance for This Project

Show the two to four most relevant publicly linked WBG sources for the current assessment. Relevance is deterministic and evidence-led:

1. A source must be referenced by at least one admitted core question.
2. Its title must match a catalogued source after normalization.
3. Its URL must pass the existing public World Bank HTTPS allowlist.
4. Sources are ranked by the number and materiality of matched core questions, then by stable catalog order.
5. Display at most four and at least two when two eligible matches exist. If only one eligible source exists, show one rather than adding an unrelated item. If none exists, omit the section.

Each displayed item contains:

- linked source title;
- a short explanation of the source's practical value;
- a project-specific narrative explaining what the team can learn or test using the source;
- explicit links to concrete project components, institutions, risks, design choices or monitoring questions already present in the admitted core-question summaries.

The project-specific narrative is assembled only from verified reader fields. It may use the catalogued practical-value statement plus concise excerpts or sentence-level summaries from the matched core-question answers. It must not introduce new facts, recommendations or claims. It must not merely repeat question titles under `Most useful for following up on`.

For the South Sudan PCN, the intended form is:

- **Maximizing the Peace and Social Dividends of Climate Action:** explain how the team can strengthen positive peace and social outcomes through BFMUs, Community Wildlife Conservancies, Community Forestry Associations, the Pariang refugee-host value chain, benefit sharing, dispute resolution and social-cohesion monitoring.
- **FCV-Sensitive Climate Action Framework:** explain how the team can stress-test delivery under combined flood-conflict conditions, future-climate infrastructure sizing, sequencing, access, security and contingency arrangements across the ESMF and Security Risk Management Plan.
- **Defueling Conflict:** explain how natural-resource governance can reduce rather than intensify conflict through boundary delineation, customary and displaced people's access rights, elite-capture safeguards, benefit sharing and incentives for cooperation.

The source catalog is not fixed to those three. Other confirmed core WBG material, including the Conflict-Sensitive Climate Action Compendium and CCDR guidance, can appear when admitted questions make them more relevant. Missing or unverified public URLs remain in the further-reading list as unlinked references but are not promoted into the tailored guidance section.

### 7. How This Analysis Was Produced

Retain one disclosure titled `Method, limitations, and sources`. It contains:

- the plain-language methodology note;
- a concise limitations statement;
- `Sources & further reading` with the existing linked/reference-only literature entries.

Remove from all reader-facing surfaces:

- the raw evidence-key explanation and evidence-code list;
- run diagnostics;
- diagnostic counts, reviewer verdict and country-bank release details.

The underlying assessment evidence and diagnostics remain available to internal runtime validation and logs. This is a presentation change, not deletion from the analytical pipeline.

## Data and Rendering Design

The canonical reader model remains the source for all reader surfaces. Prefer deriving the richer guidance presentation from existing verified `core_questions` and catalogued source metadata rather than adding a second unvalidated LLM call.

For each core question, guidance rendering can use:

- `source` to match a catalogued publication;
- `question` to identify the decision being supported;
- `summary` to recover project-specific components, risks and design considerations;
- `watch` as an optional follow-up cue.

Source metadata may gain a concise `practical_value` string if the existing `description` is insufficient. Such metadata is static WBG literature orientation, not project evidence. Any new catalog URL must be verified against a public official World Bank page before inclusion.

The following helpers should remain independently testable:

- public World Bank URL validation;
- title normalization and source matching;
- guidance-item ranking and two-to-four cap;
- project-specific narrative construction from matched verified questions;
- priority summary/transition generation;
- item numbering and disclosure state.

## Accessibility and Responsive Behavior

- Preserve semantic section headings and gap-free section numbering.
- Use native `<details>/<summary>` for lower priorities.
- Keep priority 1 open and later priorities closed on initial HTML load.
- Maintain visible focus states for disclosures and links.
- Do not rely on color alone for rating, priority rank, check type or monitoring type.
- At widths below 760 px, number columns remain visible, text wraps without horizontal overflow, the rating scale remains usable, and disclosure titles remain fully readable.
- Standalone HTML includes the same viewport metadata and scoped styles as the live reader.

## Testing Strategy

Follow red-green-refactor cycles.

1. Add frontend regression tests that execute the real renderer and assert:
   - overview uses the approved panel class;
   - evidence-status HTML is absent outside smoke mode;
   - priority transition does not repeat priority titles;
   - priority 1 is expanded and later priorities use closed native disclosures;
   - complete priority prose, drafting and details remain in the DOM;
   - check and watch items carry local sequential number labels;
   - evidence key and run diagnostics are absent;
   - methodology and source list remain.
2. Add guidance tests covering:
   - one, two, four and more-than-four eligible sources;
   - deterministic ranking and stable order;
   - unmatched, non-public and malformed URLs;
   - project-specific narrative includes matched verified project details;
   - no unrelated source is added to reach the preferred range;
   - South Sudan-like fixtures can surface sources other than the current three when their questions are admitted.
3. Update Python HTML and DOCX renderer tests so canonical surfaces preserve the same content decisions. DOCX priorities remain fully expanded.
4. Retain export-parity, semantic hierarchy, focus styling and viewport contracts.
5. Run the focused climate frontend and app-contract suites, followed by the broader project suite subject to the documented Windows temporary-directory limitation.
6. Generate a new synthetic standalone HTML preview for desktop and mobile visual QA. If a paid live run is needed, obtain explicit approval before incurring another quality-model cost.

## Acceptance Criteria

- The overview is visually prominent without adding nested panels.
- The executive readout and core questions retain their current depth.
- Priority 1 is open; all later priorities are collapsed but complete.
- The priority introduction explains the overall action sequence and never repeats all titles.
- Decision checks and monitoring points are locally numbered and remain prose-led.
- Tailored guidance displays one to four evidence-matched sources, normally two to four, with concrete project-specific learning value.
- Source selection varies with admitted core questions and never varies randomly.
- The South Sudan fixture produces materially project-specific guidance rather than a list of question titles.
- Raw evidence codes, run diagnostics and the evidence-status banner are absent from the reader.
- Methodology, limitations and sources/further reading remain accessible.
- Live HTML, standalone export and DOCX remain content-consistent.
- Focused regression tests and visual QA pass before completion is claimed.
