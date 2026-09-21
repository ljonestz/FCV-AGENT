# Climate Verified HTML Visual Refresh

**Date:** 2026-08-09
**Branch:** `feat/climate-reader-lay-comprehensibility`
**Status:** Visual direction approved; ready for user review before implementation planning

## Objective

Refresh the verified Climate-FCV HTML reader so it feels modern, calm, and credible for a World Bank Group audience without materially changing the assessment. The existing analytical depth, prompts, ratings, priority reasoning, suggested drafting, checks, watch items, caveats, and evidence trail remain intact.

The approved direction is deliberately restrained. This is a presentation and navigation improvement, not another content restructure.

## User need

The reader is used by non-specialist WBG staff who need to understand three things in sequence:

1. What the overall Climate-FCV assessment means for the project.
2. Which issues deserve action, with enough detail to revise the project documents.
3. Where to go for relevant follow-up guidance.

The current output contains this substance, but the visual hierarchy is uneven. Small cards, inline styles, similar-looking headings, and a weak distinction between substantive Climate-FCV considerations and mechanical document checks make the report harder to scan. The sources area also behaves like a bibliography rather than practical guidance.

## Scope

### In scope

- Restyle the verified Climate-FCV reader in `index.html`.
- Preserve the same reader model and all current assessment prose.
- Reorder the two groups under “Points to check before the decision meeting” so smaller Climate-FCV points appear before document checks.
- Add a tailored “Relevant WBG guidance for this project” section near the end.
- Keep the live reader and downloaded standalone HTML visually consistent because both use `renderClimateVerifiedAssessment()` and the same CSS.
- Add focused frontend contract tests for order, source selection, semantic structure, and export parity.

### Out of scope

- Prompt, model, schema, rating, priority-admission, or evidence-bank changes.
- Rewriting assessment findings or producing new substantive recommendations.
- Changes to the general FCV Stage 3 reader.
- Redesigning the DOCX report in this round.
- Adding dashboards, filters, tabs, side panels, modal help, or other interaction layers.
- Reading or changing the restricted OPCS/ESF source corpus.

## Content hierarchy

The reader keeps the current broad sequence and uses stronger visual hierarchy rather than more containers:

1. **Overview**: the existing sensitivity rating, plain-language overview summary, caveat, and executive readout form one opening sequence. The rating remains prominent, but the scale and supporting prose read as part of the report rather than as a dashboard widget.
2. **Core climate-FCV questions**: retain the full prose and source cues. Each question is a quiet report subsection with a fine divider, not a compact tile in a grid.
3. **Ranked operational priorities**: retain the ranking, detailed narrative, suggested drafting, minimum and enhanced actions, ownership, completion evidence, limitations, and recommendation-detail disclosure. Priority cards remain the strongest visual units because they are the main action layer.
4. **Points to check before the decision meeting**: show “Smaller climate and fragility points to consider” first, followed by “Document points to confirm.” This makes substantive design considerations precede mechanical cleanup.
5. **What to keep an eye on**: keep monitor-only items as a simple list with restrained emphasis.
6. **Relevant WBG guidance for this project**: place selected follow-up literature after the analytical and action sections, not near the opening.
7. **How this analysis was produced**: retain methodology, evidence key, pathways, sources, diagnostics, and limitations in the existing collapsed disclosure.

This order moves from orientation to diagnosis, action, secondary checks, monitoring, follow-up guidance, and finally audit detail.

## Visual system

### Reading surface

- Use a single white report surface with generous vertical spacing.
- Keep a comfortable prose measure and a consistent 1.6 to 1.7 line height.
- Avoid nested cards unless the content has a distinct task, such as a ranked priority or a drafting block.
- Replace most heavy borders and tinted panels with fine rules, whitespace, and typographic contrast.

### WBG visual language

- Use the existing WBG navy and blue variables as the primary palette.
- Reserve green, amber, and red for meaning, especially the rating state, rather than decoration.
- Use a quiet warm tint only for the guidance section and a pale blue tint only for ready-to-use drafting.
- Retain the application’s existing fonts and controls so the reader remains part of the product rather than looking like an embedded microsite.

### Headings and numbering

- Give each top-level section a visible two-digit number and a sentence-case heading.
- Use larger, less compressed headings instead of uppercase eyebrow headings for the main hierarchy.
- Use smaller uppercase labels only where they provide a functional cue, such as “Suggested drafting for the current document.”
- Keep priority rank circles because they express sequence clearly and efficiently.

### Density and disclosure

- Keep nuanced prose visible by default.
- Retain disclosures only for “Recommendation details,” “How this analysis was produced,” and existing diagnostics.
- Do not add summary tiles, floating panels, popovers, or expandable layers for ordinary findings.
- Ensure the first view gives context before priorities; priorities must not appear at the top without the overview and core questions.

## Relevant WBG guidance

The guidance section must be tailored without asking the model to generate new prose.

`renderClimateVerifiedAssessment()` will derive it from fields already present in the reader model:

- `core_questions[].source` identifies which source informed a finding.
- `sources[]` provides the authoritative title, public URL, and description.

The renderer will normalize titles, match question source references to `sources[]`, and include only matched sources. Each included source will show:

- the linked publication title;
- its existing description; and
- a short deterministic sentence identifying the Climate-FCV question or questions in this report for which it is most useful.

The section will be omitted if no authoritative source can be matched. Unmatched sources will remain available in the methodology disclosure but will not be promoted as tailored guidance. This prevents the same generic report tiles from appearing in every assessment and avoids fabricated source relevance.

## Responsive and accessibility behavior

- The reader remains a single column at all breakpoints.
- On narrow screens, section spacing and type sizes reduce slightly, but prose is not hidden or converted to cards.
- Priority headers wrap naturally, and rank markers remain aligned with the first heading line.
- Links retain visible focus states and meaningful link text.
- Color never carries meaning alone; rating labels and section labels remain explicit.
- Existing semantic elements (`article`, `section`, headings, lists, `details`, and links) are retained or improved.
- Standalone HTML export includes the same responsive rules and remains usable without external assets or scripts.

## Implementation boundary

The implementation should stay within the existing frontend rendering boundary:

- `index.html`: revise verified-reader CSS, refactor `renderClimateVerifiedAssessment()` into small rendering helpers where useful, add deterministic relevant-guidance selection, and keep `downloadHTML()` using the same render output.
- `tests/test_sector_lens_app_contract.py`: assert section order, guidance-source filtering, no all-source tile list, and the revised semantic classes.
- `tests/test_climate_lens_frontend.py`: retain or extend the export contract so the standalone HTML contains the refreshed reader and responsive CSS.
- `claude.md`: record the reader visual refresh after implementation, as required by the repository maintenance rule.

No new endpoint, schema field, dependency, or persistence mechanism is required.

## Error and fallback behavior

- Missing sensitivity rating: preserve the current behavior and begin with the executive readout.
- Missing overview summary: do not invent one; render the rating and available executive prose.
- No priorities: retain the existing withheld/no-admitted recommendation message.
- No minor Climate-FCV points: show document checks directly without an empty group.
- No document checks: show minor Climate-FCV points without an empty group.
- No matched guidance: omit the tailored guidance section and keep the full sources list in methodology.
- Non-public or unconfirmed source URL: do not promote it into tailored guidance.

## Testing and acceptance criteria

The change is accepted when:

- The overview and executive readout appear before core questions and priorities.
- Existing analytical prose and drafting text remain present and untruncated.
- Core questions render as prose-led sections rather than a two-column tile grid.
- Priority cards remain ranked and preserve suggested drafting and recommendation details.
- “Smaller climate and fragility points to consider” appears before “Document points to confirm.”
- The guidance section appears near the end and includes only sources referenced by this assessment’s core questions.
- Each guidance entry explains which current question it supports using deterministic existing data.
- The methodology disclosure still contains the complete source and evidence trail.
- Live and downloaded HTML use the same reader markup and responsive CSS.
- The layout remains clear at desktop and mobile widths.
- Focused frontend contract tests and the existing Climate-FCV test suite pass.

## Risks and mitigations

- **CSS leakage into the general reader:** scope every new selector beneath `.climate-verified-assessment`.
- **Over-design:** prefer typography and spacing over additional components; add no new interaction pattern.
- **Guidance-title mismatch:** normalize case and punctuation and fall back to methodology-only sources rather than guessing.
- **Long question titles in guidance:** use a short deterministic follow-up line and cap the displayed question list without dropping the source from methodology.
- **Export divergence:** continue using `renderClimateVerifiedAssessment()` and collected stylesheet text in `downloadHTML()` rather than maintaining separate templates.

## Non-negotiable content guardrails

- Do not change ratings, findings, recommendations, evidence claims, or institutional caveats.
- Do not convert nuanced prose into short bullets merely to make the page look lighter.
- Do not promote minor issues into ranked priorities.
- Do not surface internal routing metadata in the reader.
- Do not show the same standard literature set when it is not linked to the current assessment.
- Do not add WBG branding elements that imply an official institutional rating or approval.
