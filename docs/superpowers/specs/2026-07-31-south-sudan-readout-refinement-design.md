# South Sudan Climate-FCV Readout Refinement Design

**Date:** 2026-07-31
**Branch:** `feat/climate-country-bank`
**Status:** Approved for implementation through the user's instruction to apply the recommended layout and editorial changes

## Objective

Make the South Sudan Climate-FCV output easier to scan, more project-specific, and operationally safer without changing the canonical Climate payload, country-bank approval boundary, rating scale, or Stage 3 priority schema.

## Evidence diagnosis

The attached browser run was not bank-grounded. South Sudan remains `reviewed`, not `approved`, so no runtime release is available. The browser assessment's dedicated live Climate research also failed its acceptance gate, leaving the Climate grounding state `thematic-only`. A separate controlled production run accepted live research and completed as `research-only`. The output wording was therefore technically correct, but it exposed backend provenance too prominently and in language that could look like a rendering failure.

The desktop compression is structural: `.main` is capped at 860px and Stage 3 then removes 210px for a sticky sidebar. The main assessment and sidebar therefore both become narrow on a large screen.

The CERC output also shows a real calibration gap. General guardrails prohibit treating conflict escalation as a CERC trigger, but the Climate-native prompts do not explicitly prohibit mixed formulations such as “climate or security emergency.” The generated South Sudan text consequently blurred an eligible climate emergency pathway with conflict/security adaptation.

## Approved design

### 1. Single-column desktop information architecture

- Increase the main desktop content width to 1180px.
- Remove the Stage 3 right sidebar from the rendered layout.
- Place a compact Climate-FCV integration card and a full-width priority overview above the recommendations note.
- Render the priority overview as full-width numbered rows so long project-specific titles remain readable.
- Keep the existing mobile collapse behavior and avoid horizontal scrolling.

### 2. Compact rating presentation

- Retain the six-tier integration rating and dial.
- Remove the “Indicative Climate-FCV Integration Readout” eyebrow.
- Do not display the model's narrative `integration_summary` beside the dial.
- Map the rating to a fixed two- or three-word explanation such as “Partly integrated.”
- Remove the long policy caveat from the rating card; the report-level advisory notice remains the boundary statement.

### 3. Clearer opening and evidence provenance

- Replace “materiality” in visible user-facing labels with “climate relevance.”
- Present “Climate-FCV module” as a small kicker, followed by “Climate relevance to this project.”
- Start the substantive text with the project-specific `materiality_summary`, labelled “Why it matters.”
- Remove generic selected-module prose, bank-release language, and the advisory boundary from the blue opening card.
- Preserve grounding provenance in a quiet “Evidence basis” note after the Climate analysis. Use user-facing descriptions rather than implementation language:
  - reviewed country evidence plus current research;
  - reviewed country evidence, with recent developments to verify;
  - current country research;
  - project documents and thematic sources, with country-specific evidence not verified for the run.

### 4. Executive readout and analytical depth

- Rename the strengths/weaknesses section “Executive readout.”
- Rename the columns “Where the design is stronger” and “Where the design could be strengthened.”
- Stack the green and amber panels vertically at all viewport sizes.
- Normalize title and body typography explicitly across both panels.
- Strengthen Stage 2 instructions so each strength, improvement area, interaction, and reflection names supported project anchors such as component, activity, location, group, institution, delivery mechanism, indicator, or document section and explains the operational mechanism.
- Require improvement language to distinguish a confirmed omission from an item that is simply not evidenced at concept stage.

### 5. Core-question introduction

Use a short plain-language introduction explaining that the section reviews how Climate-FCV dynamics may affect project delivery and how project choices may influence resilience, inclusion, peace, and conflict risks. Then name the analytical frameworks without saying every principle is applied mechanically.

### 6. CERC separation

- In both Climate-native Stage 2 and Stage 3 prompts, prohibit combining a CERC or contingency-financing recommendation with conflict escalation, insecurity, civil unrest, armed-group activity, or access deterioration.
- If a CERC is discussed, require a named eligible natural-hazard, climate, health, or economic emergency, plausible borrower declaration/activation pathway, and PDO link.
- Route conflict/security deterioration to adaptive management, restructuring, SORT updating, security planning, stop/go provisions, and monitoring instead.
- Add prompt-contract regression tests for both Climate stages.

## Compatibility and boundaries

- No change to `climate-native-v1`, delimiter schemas, Stage 3 JSON fields/enums, rating semantics, country-bank release schema, or approval rules.
- The South Sudan bank remains unapproved.
- No production deployment, bank approval, PR merge, or wider-country generation is part of this change.
- Shared HTML export must mirror the live layout wording and evidence treatment. DOCX data contracts remain unchanged.
- The private FCV build-parity log must record the Climate prompt calibration change without exposing private parity content in the repository.

## Verification

- Frontend contract tests prove the new wording, full-width layout, compact rating label, stacked executive panels, and user-facing evidence states.
- Prompt tests prove the mixed CERC/conflict formulation is explicitly forbidden in both Climate stages.
- Existing focused Climate suites must remain green.
- Local rendered QA will inspect desktop and mobile widths, console health, wrapping, and the Stage 3 overview interaction using the available browser path.
