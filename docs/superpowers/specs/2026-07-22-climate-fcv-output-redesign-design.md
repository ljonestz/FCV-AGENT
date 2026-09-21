# Climate-FCV Output Redesign

**Date:** 2026-07-22
**Status:** Approved design, pending user review of the consolidated specification
**Scope:** Climate-FCV Lens analytical contract, Recommendations Note presentation, export parity, and validation
**Related design:** [Climate-FCV Sector Lens Design](2026-07-21-climate-fcv-lens-design.md)

## 1. Purpose

Redesign the Climate-FCV Lens output so that a first-time user can immediately understand that the module was selected, how strongly climate considerations matter for the project, and how Climate-FCV analysis changes the assessment and recommendations.

The redesign must preserve the depth of the existing core FCV Recommendations Note. Climate content strengthens and extends that note; it does not replace its executive summary or reduce FCV sensitivity and responsiveness to rating icons.

The design is based on the first saved test output for a natural-resource and livelihoods project. The test demonstrated three problems:

1. The downloaded HTML did not clearly disclose that the Climate-FCV module had been applied.
2. The live Climate-FCV diagnostic was omitted from the downloaded HTML because the export path did not render `lensDiagnostic`.
3. Few priority recommendations carried Climate-FCV provenance, even though the project documents contained material adaptation, resilience, ecosystem, livelihood, and institutional entry points.

These are separate problems. The first is a communication problem, the second is an export parity defect, and the third is an analytical and prioritization contract problem.

## 2. Climate co-benefit framing

The Climate-FCV Lens is not limited to projects whose primary objective is climate action. Most relevant operations will be development projects with material climate risks, resilience effects, adaptation opportunities, mitigation effects, or climate co-benefits at project or component level.

The lens must therefore screen every project for material climate pathways after the user selects the module. It must not infer that the Climate-FCV Lens is irrelevant merely because the project is labelled as a natural-resource, livelihoods, infrastructure, social protection, governance, or other development operation.

This framing is consistent with the World Bank's continued reporting of climate co-benefits across projects and the joint MDB approach to identifying adaptation finance at activity level:

- [World Bank development finance with climate co-benefits](https://www.worldbank.org/en/programs/world-bank-development-finance-with-climate-co-benefits)
- [Joint MDB methodology for tracking climate change adaptation finance](https://thedocs.worldbank.org/en/doc/20cd787e947dbf44598741469538a4ab-0020012022/original/20220242-mdbs-joint-methodology-climate-change-adaptation-finance-en.pdf)

The module is an FCV design lens informed by this principle. It is not a formal climate co-benefits calculation or an MDB finance-tagging tool.

## 3. Approved design decisions

1. Module selection is authoritative and always disclosed in the output.
2. Climate analytical depth follows a validated High, Medium, or Low materiality level.
3. High and Medium use the same broad readout architecture, with different depth and emphasis.
4. Low stays close to the default FCV note, but explicitly acknowledges limited climate materiality and retains a light climate emphasis because the user selected the module.
5. The existing executive summary retains approximately its current length, organization, and analytical detail.
6. Detailed FCV sensitivity and responsiveness are written into the executive summary. They are not represented only by rating icons or small tabs.
7. A dedicated two-way Climate-FCV interaction box replaces the default two-way FCV box when the Climate-FCV module is active.
8. A separate dividends readout shows credible pathways through which the project may support climate, peace, and social dividends, together with concise suggestions for strengthening them.
9. The six dimensions from the Peace and Social Dividends framework are a baseline, not a mandatory checklist or a closed taxonomy.
10. Weak or unsupported dimensions are suppressed. The output must not render filler such as "no opportunity identified."
11. Bounded project-specific pathways beyond the six baseline dimensions are permitted when supported by project and contextual evidence.
12. Dividend pathways and priority recommendations are separate but linked. Pathways explain mechanisms and improvement directions; priorities specify concrete actions.
13. The final priority list remains capped at five substantive priorities. Climate has no numerical quota, but material and actionable Climate-FCV findings must be considered in the common ranking.
14. One normalized diagnostic is the source of truth for the live application, downloaded HTML, and downloaded DOCX.
15. Option A is the provisional presentation. Option B remains a renderer-level fallback after user testing.

## 4. End-to-end analytical contract

The redesign uses four distinct analytical layers.

### 4.1 Materiality

Stage 2 produces a validated `materiality_level` with one of three values:

- `high`: Climate-FCV dynamics are central to project outcomes, implementation, affected groups, or significant project effects on vulnerability, resilience, mitigation, or transition.
- `medium`: Climate-FCV dynamics are relevant to identifiable components, locations, groups, or delivery choices, but are not dominant across the operation.
- `low`: Climate entry points are limited, indirect, weakly evidenced, or peripheral to the project's principal results and implementation risks.

The level is accompanied by:

- a concise `materiality_summary`;
- the project evidence that supports the rating;
- relevant contextual evidence;
- material evidence gaps or uncertainty;
- validated source identifiers.

The materiality level controls depth, not disclosure. Manual selection of the module is never hidden or silently reversed by the model.

The existing general-lens `applicability` field is retained for compatibility, but the Climate-FCV renderer uses `materiality_level` to control presentation. `high` and `medium` normally map to `material`; `low` maps to `possible`. A legacy `not_applicable` result for a selected Climate-FCV module is rendered with the Low disclosure pattern rather than hiding the module. A malformed diagnostic follows the separate safe-failure behavior in Section 10.

### 4.2 Two-way Climate-FCV interactions

The diagnostic contains two fixed directions:

1. **How Climate-FCV interactions could affect the project**
2. **How the project could influence Climate-FCV dynamics**

Each direction identifies:

- the causal mechanism;
- affected project components, results, locations, or groups;
- credible positive and adverse consequences where relevant;
- the supporting project and contextual evidence;
- important uncertainty or evidence gaps;
- source identifiers.

The first direction may include compound effects involving hazards, resource stress, displacement, insecurity, institutional weakness, exclusion, or delivery constraints. The second may include resilience gains, reduced vulnerability, institutional legitimacy, livelihood effects, resource competition, exclusion, maladaptation, transition effects, or unintended harm.

The interaction readout is analytical. It must not become a list of generic climate risks or repeat the priority recommendations.

### 4.3 Climate, peace, and social dividend pathways

Two readout groups organize positive pathways:

1. **Where the project could build climate, peace, and social dividends**
2. **How project design and delivery could strengthen those dividends**

Each displayed pathway has a fixed user-facing anatomy:

- **How the project may contribute:** the current or plausible project mechanism.
- **How this could be strengthened:** a concise, project-specific improvement direction.

The normalized data also retains:

- pathway status;
- evidence;
- evidence gap;
- trade-off or possible adverse effect;
- source identifiers.

The six baseline dimensions remain:

**Investment entry points**

- social cohesion and inclusion;
- institutional capacity and legitimacy;
- livelihoods and economic opportunity.

**Design and delivery choices**

- context analysis and monitoring;
- trust and collaboration;
- flexible and adaptive delivery.

The six dimensions seed analysis but do not determine the rendered output. A baseline item appears only when its status is `supported` or a well-evidenced `potential`. Items marked `not_material`, generic, duplicative, or unsupported are not rendered.

The model may add a maximum of two additional project-specific pathways per readout group. Each additional pathway must use the same structured fields, cite project evidence, and pass the same source and length validation as a baseline pathway.

### 4.4 Priority recommendations

Priority recommendations remain a common FCV list rather than a separate climate list. Each priority must be specific enough for a task team to act on and should identify, where available:

- the proposed project change;
- the project instrument, component, process, or document affected;
- the responsible actor or owner;
- timing or decision point;
- evidence and rationale;
- implementation trade-offs;
- Climate-FCV provenance.

When a Climate-FCV finding materially shapes a priority, `lens_ids` includes `climate` and `lens_relevance` briefly explains the link. Climate badges are evidence of provenance, not a visual quota.

The ranking remains based on severity, materiality, evidence, actionability, leverage, and feasibility. High materiality should normally yield prominently integrated climate content, but a hard minimum number of climate priorities is not imposed. If no climate-tagged priority survives a High materiality ranking, the pipeline records an internal validation warning so that prompt or extraction failure is not mistaken for a valid analytical result.

## 5. Proposed normalized data shape

The existing lens diagnostic is extended rather than replaced. The conceptual shape is:

```json
{
  "lens_id": "climate",
  "applicability": "material",
  "materiality_level": "high",
  "materiality_summary": "...",
  "analysis_emphasis": ["..."],
  "evidence": ["..."],
  "source_ids": ["..."],
  "interaction_readout": [
    {
      "direction_id": "climate-fcv-on-project",
      "summary": "...",
      "mechanisms": ["..."],
      "project_implications": ["..."],
      "positive_effects": ["..."],
      "adverse_effects": ["..."],
      "evidence": ["..."],
      "evidence_gap": "...",
      "source_ids": ["..."]
    },
    {
      "direction_id": "project-on-climate-fcv",
      "summary": "...",
      "mechanisms": ["..."],
      "project_implications": ["..."],
      "positive_effects": ["..."],
      "adverse_effects": ["..."],
      "evidence": ["..."],
      "evidence_gap": "...",
      "source_ids": ["..."]
    }
  ],
  "readout_sections": [
    {
      "section_id": "invest-in",
      "items": [
        {
          "item_id": "livelihoods-opportunity",
          "status": "supported",
          "mechanism": "...",
          "project_contribution": "...",
          "strengthening_action": "...",
          "evidence": ["..."],
          "evidence_gap": "...",
          "trade_off": "...",
          "source_ids": ["..."]
        }
      ]
    }
  ],
  "additional_pathways": [
    {
      "section_id": "invest-in",
      "title": "Project-specific pathway",
      "status": "supported",
      "mechanism": "...",
      "project_contribution": "...",
      "strengthening_action": "...",
      "evidence": ["..."],
      "evidence_gap": "...",
      "trade_off": "...",
      "source_ids": ["..."]
    }
  ]
}
```

Normalization rules:

- Reject unknown materiality and direction identifiers.
- Retain only active lens identifiers.
- Validate all source identifiers against the lens source catalogue and permitted dynamic sources.
- Enforce bounded list lengths and string lengths before storage or rendering.
- Retain only declared baseline item identifiers.
- Permit bounded free-text titles only within `additional_pathways`.
- Suppress additional pathways without project evidence.
- Preserve evidence gaps and trade-offs in the data even when the primary card shows a shorter summary.
- Escape all user and model text at render time.

## 6. Stage behavior

### 6.1 Stage 1

Stage 1 remains an evidence-collection step. It gathers only the information needed to establish:

- climate exposure and sensitivity;
- project influence on vulnerability, resilience, mitigation, or transition;
- component-level climate co-benefit pathways;
- affected groups and distributional effects;
- delivery constraints and compound FCV risks;
- plausible dividend entry points;
- material evidence gaps.

Stage 1 does not determine the final materiality level or generate recommendations.

### 6.2 Stage 2

Stage 2:

1. determines High, Medium, or Low materiality;
2. produces the two-way interaction readout;
3. assesses the six baseline dividend dimensions;
4. adds only strongly justified project-specific pathways;
5. distinguishes project evidence, contextual evidence, inference, and evidence gaps;
6. emits the normalized diagnostic used by all later surfaces.

The Stage 2 prompt must explicitly state that a development project can have material Climate-FCV pathways even when climate is not its primary objective.

### 6.3 Stage 3

Stage 3 receives a compact but complete representation of:

- materiality level and rationale;
- the two interaction summaries;
- supported and well-evidenced potential dividend pathways;
- strengthening directions;
- actionable Climate-FCV findings;
- evidence and source provenance.

It then integrates these findings into the existing executive summary and common priority ranking. It must not compress the executive summary merely to make room for climate material.

The prompt assigns a distinct role to each layer:

- executive summary: overall FCV assessment, strengths, gaps, sensitivity, and responsiveness;
- interaction readout: causal Climate-FCV dynamics;
- dividends readout: current contribution pathways and ways to strengthen them;
- priorities: concrete project actions.

This role separation is the principal safeguard against repetitive output.

## 7. Recommendations Note presentation

### 7.1 Section order

When the Climate-FCV module is active, the primary note uses this order:

1. Climate-FCV module notice
2. Full executive summary
3. Two-way Climate-FCV interactions
4. Climate, peace, and social dividend pathways
5. Priority recommendations
6. Supporting analysis and annexes

The Climate-FCV interaction and dividend boxes appear after the executive summary, not before it.

### 7.2 Module notice

The blue notice uses plain language suitable for a user who knows nothing about the tool. It has three functions:

1. explain that the user selected the Climate-FCV module;
2. explain how strongly climate has influenced the assessment;
3. identify the evidence library in accessible terms.

The disclosure varies by materiality.

**High materiality pattern**

> You selected the Climate-FCV module. The tool has therefore applied a strong climate emphasis across this FCV assessment, examining how Climate-FCV risks may affect the project and how project design could strengthen climate resilience and wider FCV outcomes.

**Medium materiality pattern**

> You selected the Climate-FCV module. The tool has applied a focused climate emphasis to the parts of this FCV assessment where Climate-FCV risks, opportunities, and delivery choices are material to the project.

**Low materiality pattern**

> You selected the Climate-FCV module. The assessment found limited climate materiality for this project. Climate considerations are therefore included with a light emphasis alongside the wider FCV sensitivity and responsiveness assessment.

All three may use this evidence-base sentence:

> The recommendations draw on a core library of relevant World Bank and external material, including the Peace and Social Dividends of Climate Action report, the framework for FCV-sensitive climate action, the *Defueling Conflict* series, and other internal and external sources.

The notice does not separately name the CCDR approach note or the climate-action compendium.

### 7.3 Executive summary

The executive summary preserves the default note's depth and broad structure:

- Opening Assessment;
- Operational Context;
- Strengths;
- Gaps.

It includes substantive prose on both FCV sensitivity and FCV responsiveness. Rating labels may remain as orientation aids, but never substitute for the written assessment.

The prose should explain:

- how well the project recognizes and manages FCV risks and Do No Harm concerns;
- how the project actively responds to fragility drivers, resilience needs, institutions, inclusion, and wider peace outcomes;
- the strongest design features and most consequential gaps;
- relevant climate interactions in proportion to materiality.

### 7.4 Two-way interaction box

The default two-way FCV box is adapted when the Climate-FCV module is active. Its headings are:

- **How Climate-FCV interactions could affect the project**
- **How the project could influence Climate-FCV dynamics**

The box presents concise synthesis, not icons, isolated ratings, or priority actions.

### 7.5 Dividends introduction and cards

The section uses a project-led rather than report-led introduction. Suggested pattern:

> The project has potential to support wider climate, peace, and social dividends. The pathways below show how the project may already contribute to these outcomes and how those contributions could be strengthened. They draw partly on the Peace and Social Dividends of Climate Action report and other Climate-FCV evidence. They are selective design insights rather than a checklist, and not every pathway needs to be incorporated into the project.

Each visible card shows a pathway title followed by:

- **How the project may contribute**
- **How this could be strengthened**

Cards are concise and selective. They do not display dimensions with weak entry points, and they do not repeat priority wording.

## 8. Materiality-based rendering

### 8.1 High

- Strong module notice.
- Full two-way interaction box.
- Several credible dividend pathways, subject to evidence and space limits.
- Climate prominently integrated across the executive summary and relevant priorities.
- No separate climate priority quota.

### 8.2 Medium

- Focused module notice.
- Same broad architecture as High, with tighter summaries.
- Fewer dividend pathways.
- Climate integrated into the most relevant parts of the summary and priority list.

### 8.3 Low

- Explicit statement that climate materiality is limited.
- Default-like FCV executive summary with light climate emphasis.
- Compact interaction note rather than an expansive diagnostic.
- Dividend content only when at least one credible pathway exists.
- No forced standalone climate priority.

## 9. Live and export parity

The normalized lens diagnostic is the single source of truth for:

- the live application;
- downloaded HTML;
- downloaded DOCX.

All three surfaces must contain the same substantive sections, materiality level, labels, ordering, and text. Formatting may be surface-specific, but content may not silently disappear.

The HTML exporter must explicitly render the Climate-FCV diagnostic. It cannot rely on the live DOM state or a renderer call that is absent from `downloadHTML()`.

The DOCX path must use the same normalized fields and conditional display rules. Existing DOCX Climate-FCV output must be updated to the new headings and pathway anatomy rather than maintaining a separate interpretation of the diagnostic.

## 10. Safe failure behavior

If the selected module's diagnostic is missing or malformed:

1. disclose that the Climate-FCV module was selected;
2. state that a validated Climate-FCV diagnostic could not be produced;
3. retain the core FCV executive summary and recommendations;
4. suppress unvalidated interaction and dividend sections;
5. do not invent climate findings or climate-tagged priorities;
6. retain diagnostic details for troubleshooting without exposing raw model output to the user.

The renderer, not the model, owns this behavior.

## 11. Option B fallback

Option A is the initial implementation:

- FCV sensitivity and responsiveness are detailed in executive-summary prose;
- the two-way Climate-FCV interaction box is visual;
- dividend pathways are visual cards.

Option B remains available if user testing shows that the dividend cards are generic, repetitive, or visually heavy:

- retain the two-way Climate-FCV interaction box;
- restore detailed FCV sensitivity and responsiveness as two visual cards;
- render dividend pathways as prose.

The normalized analytical contract is identical for both options. Switching from A to B must require renderer and style changes only, not new prompts or a new Stage 2 schema.

## 12. Acceptance criteria

### 12.1 High-materiality natural-resource and livelihoods project

- The opening immediately identifies the selected Climate-FCV module and strong climate emphasis.
- The executive summary retains the depth of the current default note.
- The interaction box addresses compound hazard, resource, livelihood, institutional, and exclusion pathways that are supported by evidence.
- Dividend cards explain current project contribution and strengthening directions.
- Relevant priorities carry `climate` provenance.
- Live, HTML, and DOCX content are substantively equivalent.

### 12.2 Medium-materiality development project

- The same broad architecture is used with fewer and shorter climate elements.
- The output does not overstate climate centrality.
- At least one material interaction is clearly connected to project design or delivery when evidence supports it.

### 12.3 Low-materiality project

- The opening clearly states that climate materiality is limited.
- A light climate emphasis remains because the user selected the module.
- No empty dividends cards or forced climate priority appear.
- The default FCV note remains coherent and complete.

### 12.4 Core FCV only

- No Climate-FCV disclosure, headings, or badges appear when the module was not selected.
- Existing default FCV summary and export behavior do not regress.

### 12.5 Malformed or missing diagnostic

- The user sees a safe, plain-language fallback.
- Core FCV content remains available.
- No unvalidated climate analysis is rendered.

### 12.6 Content quality and parity

- No unsupported or `not_material` pathway is shown.
- No empty cards are rendered.
- Executive summary, interactions, dividends, and priorities do not repeat the same wording.
- All Climate-FCV source IDs validate.
- All climate-influenced priorities have valid `lens_ids` and non-empty `lens_relevance`.
- Live, HTML, and DOCX outputs use the same normalized diagnostic.

## 13. Test strategy

Automated coverage should include:

- pipeline normalization for valid and invalid `materiality_level` values;
- validation of both interaction direction identifiers;
- fixed baseline items and bounded additional pathways;
- suppression of unsupported and `not_material` pathways;
- preservation of project contribution and strengthening fields;
- Stage 3 compact-context retention of the fields needed by the note;
- climate priority provenance and the High-materiality omission warning;
- High, Medium, Low, core-only, and malformed-diagnostic rendering;
- live and downloaded HTML section parity;
- DOCX headings and content parity;
- HTML escaping for every new free-text field;
- absence of duplicate climate recommendations;
- preservation of the five-priority ceiling;
- no regression to existing lens registry and core FCV behavior.

The supplied natural-resource and livelihoods project should be retained as a manual end-to-end acceptance case because it reflects the expected mainstream use of the module: a development operation with significant climate co-benefits rather than a dedicated climate project.

## 14. Implementation implications

Expected implementation areas include:

- `sector_lenses/modules/climate/manifest.yaml`: user-facing section titles and declared schema metadata;
- `sector_lenses/modules/climate/guidance.md`: materiality gradient, co-benefit framing, and layer separation;
- `sector_lenses/modules/climate/questions.yaml`: evidence prompts for materiality, interactions, and dividends;
- `sector_lenses/pipeline.py`: normalization and validation of the extended diagnostic;
- `sector_lenses/models.py` and `sector_lenses/registry.py`: schema support if manifest metadata expands;
- `sector_lenses/composer.py`: Stage 1 and Stage 2 prompt contract;
- `app.py`: Stage 2 extraction, Stage 3 compact context, priority provenance validation, DOCX output, and safe fallback;
- `index.html`: active-module notice, Option A renderers, materiality behavior, HTML export parity, and styles;
- climate and sector-lens test files under `tests/`.

Any change to delimiters, Stage 3 priority JSON fields or enums, `background_docs.py` shared constants, or rating semantics is a shared-contract change and must be logged in the local cross-build parity record for the Azure build. The parity record remains local and must never be committed to the public repository.

## 15. Non-goals

This redesign does not:

- calculate formal World Bank or MDB climate co-benefit finance;
- create a separate climate recommendation note;
- make all six dividend dimensions mandatory;
- impose a fixed number of climate priorities;
- treat Climate-FCV analysis as a substitute for the core FCV assessment;
- redesign unrelated sector lenses;
- change the default core-only note beyond the minimum reusable renderer improvements required for parity and regression safety.
