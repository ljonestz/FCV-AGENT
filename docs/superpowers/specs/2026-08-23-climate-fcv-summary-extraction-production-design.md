# Climate and FCV Summary, Follow-up, and Extraction Production Design

**Date:** 2026-08-23  
**Branch:** `codex/climate-summary-quality-fixes`  
**Status:** Design agreed in brainstorming; implementation not yet started

## Purpose

Complete the production alignment of the Climate-FCV and main FCV readouts. The Climate Summary must become a coherent standalone synthesis rather than an excerpt from Detailed; follow-up content must be easier to scan; suggested drafting must appear whenever the document route is genuinely known; and project metadata in modern Word templates must be extracted reliably for both modules.

This design extends the approved Summary-Detailed alignment design dated 2026-08-22. It does not reopen the earlier decisions on compact ratings, removal of duplicate priority navigation, or canonical priority data.

## Goals

1. Give Climate Summary its own evidence-grounded, accessible two-to-three-paragraph overall assessment.
2. Preserve the main FCV Summary's existing dedicated concise narrative, which already meets the intended standalone pattern.
3. Show suggested drafting in Summary and Detailed from the same canonical action data when the current document target is verified.
4. Separate immediate decision checks from optional guidance visually and semantically.
5. Add useful, closed follow-up disclosures without cluttering the initial Summary view.
6. Fix content-control and nested-table extraction once for the shared ingestion path so both FCV modules receive the improvement.
7. Prevent unchecked template options and incidental mentions from producing false instrument classifications.

## Non-goals

- Changing the sensitivity or responsiveness rating methodology.
- Making Climate Summary a shortened copy of Detailed.
- Rewriting the main FCV Summary narrative when it already has a dedicated concise contract.
- Inventing a global FCV guidance collection from per-priority generated references.
- Showing drafting when the lifecycle or document route remains unresolved.
- Treating the Environmental and Social risk classification as the safeguards-framework route.
- Adding another model call solely to produce the Summary.

## Design Principles

- Summary and Detailed express the same assessment but serve different reading needs.
- A Summary synthesis may connect canonical findings; it may not introduce unsupported facts, actions, rankings, or conclusions.
- Ordinary PCN-stage incompleteness is not itself a design failure. The reader must be told which gaps are expected at concept stage and which residual questions require a decision.
- Structured, labelled metadata outranks incidental body-text mentions.
- Uncertainty is explicit and safe: unresolved routing withholds document-targeted drafting and explains why in plain language.
- Closed disclosures preserve a clean mobile-first reading path.
- The browser and shareable exports render the same validated reader model.

## 1. Climate Summary Narrative Contract

### Canonical field

Add a dedicated Climate reader field:

```json
"summary_overview": {
  "paragraphs": [
    "Paragraph 1",
    "Paragraph 2",
    "Paragraph 3"
  ]
}
```

An explicit paragraph array is preferred to a newline-delimited string because it makes the two-to-three-paragraph contract testable and safe to render. `overview_summary` remains the concise sensitivity-panel explanation; the Detailed executive readout remains a separate, longer product. Neither substitutes for `summary_overview` in a newly generated result.

The field is produced within the existing verified Climate analysis call. It is normalized and evidence-checked on the server before entering the reader model.

### Narrative shape

The complete synthesis should normally be about 160–230 words across two or three paragraphs:

1. **Verdict and foundation.** State plainly how well the project recognizes the interaction between climate and FCV risks, what is already credible in the design, and the overall takeaway for a non-expert reader.
2. **Four-dimensional assessment.** Cover relevance, sensitivity, responsiveness, and operationalization. Distinguish elements reasonably not yet specified at PCN stage from substantive residual questions, including inclusion, representation, governance continuity, accountability, or sustainability where supported by the assessment.
3. **Practical implication.** Identify the small set of matters that should be confirmed next and bridge naturally to the ranked priorities. Selected implications from the core Climate-FCV questions may be used only when they materially sharpen the synthesis.

The prose should follow the direct, high-level style of the existing “How sensitive is this project to climate and FCV considerations?” narrative. It should not enumerate every recommendation or begin with low-level implementation detail.

### Emphasis and rendering

The first complete sentence of every paragraph is bold. Emphasis is applied by the renderer after sentence-boundary detection; model-generated Markdown or HTML is not trusted. If a sentence boundary cannot be identified safely, the whole short opening clause may be emphasized, but raw markup must never be injected.

### Validation and fallback

Validation checks:

- exactly two or three non-empty paragraphs;
- sensible aggregate length, with conservative tolerance for short project names and long institutional names;
- coverage of the four assessment dimensions;
- no new named entity, number, date, institution, action, or finding absent from canonical verified fields or evidence;
- no paragraph copied as a prefix or contiguous slice of the Detailed executive readout;
- no contradiction with ratings, priority ordering, project stage, or verified route.

For older saved results without `summary_overview`, construct a conservative display fallback from the full `overview_summary` and other validated rating explanations. Split only at sentence boundaries. Never fall back to the first paragraphs of the Detailed executive readout. A fallback may be shorter than the new production contract and should be labelled only in diagnostics, not in the reader-facing text.

## 2. Main FCV Summary Alignment

The main FCV Summary already has a dedicated `concise_readout` contract: a headline, a 150–200 word overview, strengths, transitions, priorities, and a closing. It is distinct from Detailed and already includes suggested wording in both Summary and Detailed. Its narrative contract therefore remains unchanged.

Add one conditional, closed disclosure titled **What to keep an eye on** after the priority sequence and before the final closing. It draws only from existing normalized watch fields:

- `mid_cycle_watch` for Additional Financing or restructuring;
- `dpf_watch` for DPF operations;
- `p4r_watch` for PforR operations;
- `regional_watch` for multi-country operations;
- existing horizon considerations where they are already present in the reader state.

Only non-empty, context-applicable fields are shown. Duplicate items are normalized and removed while preserving order. Instrument-specific groups receive plain-language labels. If every applicable collection is empty, the disclosure is omitted.

Do not add a global **Relevant WBG guidance** disclosure to the main FCV Summary in this change. The normal FCV route currently validates operational references per priority through “Go Deeper”; it does not expose one canonical, curated guidance collection suitable for safe aggregation. Those references remain where their evidentiary relationship is clear.

## 3. Suggested Drafting

Climate Summary and Detailed render suggested drafting from the same canonical priority action and the same verified document destination. The Summary may use a compact label, while Detailed may retain the fuller explanation, but the text and destination cannot diverge.

Drafting is shown only when:

- the document type and financing instrument have been resolved without material conflict;
- the proposed destination exists or is appropriate at the detected lifecycle stage;
- the wording is supported by the verified finding and does not introduce a new commitment, target, institution, or safeguard conclusion;
- the target is appropriate for the instrument and preparation regime.

If the route is genuinely unresolved, drafting remains withheld. Replace opaque internal language with a plain explanation such as: “Suggested document wording is not shown because the project document type or financing route could not be confirmed reliably.” Diagnostics may retain machine-readable reason codes.

The main FCV route keeps its existing canonical suggested-wording behavior. The shared extraction correction should reduce false withholding there as well, without changing its content contract.

## 4. Follow-up Information Architecture

### Climate Detailed

Render two purpose-led sections after the priority actions:

- **Decision preparation**: an amber-tinted band containing “Points to check before the decision meeting.” This is visually distinct because it represents near-term verification and decisions rather than another recommendation card.
- **Further guidance**: a teal-tinted band containing “Relevant WBG guidance for this project.” This is optional supporting material, not a requirement or project finding.

Both bands use text labels, borders, and icons as secondary cues; meaning must not depend on color alone. They remain readable in print, at 200% zoom, and on a phone.

### Climate Summary

Add two closed native `<details>` disclosures after the ranked priorities and before the closing synthesis:

1. **What to keep an eye on**
2. **Relevant WBG guidance for this project**

The first uses the canonical decision/watch items already shown in Detailed. The second uses the canonical curated guidance items. They load in the document and are available offline in shareable HTML, but do not occupy initial screen space.

### Guidance wording

Each Climate guidance entry shows only the reliable, standard purpose sentence, for example: “Use this source to assess how environmental and natural-resource governance can reduce conflict risk.” Remove the generated project-specific second sentence when it is not explicitly supported by the source. Titles, publication metadata, and links remain unchanged.

The same canonical guidance collection drives Summary, Detailed, and HTML export. No view may independently construct a more specific “for this project” interpretation.

## 5. Shared DOCX Extraction Architecture

### Problem

Modern World Bank templates can place core metadata inside `w:sdt` content controls and nested tables. The current direct-body traversal skips those structures. In the South Sudan PCN this omitted the labelled row containing Operation ID `P511185`, Financing Instrument `Investment Project Financing (IPF)`, and Environmental and Social Risk Classification `Substantial`. A naive all-text recovery would expose unchecked template choices such as Multiphase Programmatic Approach and could falsely classify the operation as an MPA.

### Canonical ordered walker

Introduce one repository-consistent ordered OOXML walker used by both general document ingestion and Climate source-block construction. It recursively traverses:

- document body children in source order;
- `w:sdtContent` inside content controls;
- paragraphs and visible runs;
- table rows and cells;
- tables nested inside cells or content controls.

The walker emits both readable text and structured context. It must avoid duplicate emission when an outer table contains nested tables.

Visible-text extraction excludes hidden runs, field instructions, deleted text, and other non-reader content where Word markup makes that distinction available. Existing supported hyperlink and list behavior must not regress.

### Structured metadata

For table-like structures, preserve label/value relationships rather than flattening everything into one undifferentiated string. At minimum, emit normalized field records for recognizable rows or paired label/value cells. The resolver applies this precedence:

1. an explicit labelled financing-instrument field in the primary project document;
2. another explicit project datasheet or basic-information field;
3. strong instrument-specific structural evidence;
4. incidental narrative mentions only as corroboration, never as the sole override of contradictory labelled metadata.

Operation ID and E&S risk classification should also be preserved as metadata for display or diagnostics, but `Substantial` E&S risk must not be interpreted as the E&S framework or preparation route.

### Checkbox and option-state handling

Template options must retain their state. Checked choices can support classification. Unchecked choices are recorded, if useful for diagnostics, but their labels are excluded from positive instrument evidence. Plain bracket forms such as `[ ]`, `[x]`, and Word checkbox/content-control states should be normalized consistently.

If two checked or labelled fields materially conflict, the resolver fails safely to `Unknown` and records a non-sensitive conflict reason. It must not choose the first substring match.

## 6. Diagnostics and Error Handling

Use stable, non-sensitive diagnostic reason codes for:

- no structured financing field found;
- structured field found but empty;
- conflicting checked or labelled values;
- fallback structural inference used;
- summary synthesis rejected and fallback rendered;
- drafting withheld because route or destination was unresolved.

Logs must not reproduce source-document contents or generated suggested wording. Reader-facing messages translate the reason into accessible language and avoid terms such as “legacy transitional” or “route unresolved” unless a specialist diagnostics view is explicitly open.

## 7. Tests and Verification

### Extraction and routing tests

Add a minimal realistic DOCX/OOXML fixture containing:

- a `w:sdt` content control;
- a nested Basic Information table;
- labelled Operation ID, Financing Instrument, and E&S risk classification fields;
- `Investment Project Financing (IPF)` as the selected instrument;
- an unchecked MPA option elsewhere.

Assert that both shared extraction consumers preserve `P511185`, IPF, and `Substantial`; instrument resolution returns IPF; MPA is false; and the risk rating does not alter the E&S route. Add conflict, empty-field, checked-option, simple-table, paragraph, and nested-table ordering regressions.

### Climate contract tests

- new results contain two or three standalone Summary paragraphs;
- all four dimensions are represented;
- first sentences render with semantic emphasis and escaped content;
- Summary is not a prefix or slice of Detailed executive text;
- old results fall back from the full sensitivity overview, not Detailed;
- Summary and Detailed suggested drafting share the same text and target;
- unresolved routes withhold drafting with a plain explanation;
- amber decision and teal guidance bands render in Detailed;
- both Summary disclosures are closed initially and keyboard accessible;
- guidance entries omit the unsupported project-specific second sentence;
- browser and shareable HTML use the same reader fields.

### Main FCV regression tests

- the existing headline, overview, strengths, transitions, priorities, and closing remain unchanged;
- suggested wording remains available in both views;
- the watch disclosure appears only for non-empty applicable watch data;
- mixed watch collections are labelled and deduplicated in stable order;
- no global guidance disclosure is synthesized from per-priority references;
- the shared DOCX fixture resolves the same project metadata on the normal route.

### Production checks

Run the focused unit and contract tests first, then the full suite. Generate a fresh South Sudan PCN Climate run and a normal FCV regression run. Inspect Summary and Detailed at phone, laptop, and wide-browser sizes. Capture full-browser Climate Summary screenshots, including the closed state and each opened disclosure. Export shareable standalone HTML and verify it offline. Render and inspect any affected DOCX export.

Before release, verify that:

- the South Sudan PCN shows IPF and does not show MPA;
- suggested drafting appears where expected;
- the Climate Summary reads coherently without opening Detailed;
- standard guidance sentences accurately match their cited sources;
- no duplicate watch or guidance content appears;
- all services identify the intended commit after deployment.

## 8. Cross-build Parity and Release

The DOCX metadata walker, instrument-routing semantics, Climate reader schema, and any shared delimiter or priority-field changes are parity-sensitive. Read and update the private local parity contract before implementation and after the final contract is known. Never commit that private content to the public repository.

Implementation should use narrow repository-consistent changes and avoid a second extraction stack. Commit at logical checkpoints, run final acceptance from the coordinating agent, push the feature branch, deploy the approved preview targets, and repeat the verified PCN smoke against the deployed build.

## Acceptance Criteria

1. Climate Summary provides a validated, accessible, standalone two-to-three-paragraph assessment and never slices Detailed executive text.
2. The synthesis covers relevance, sensitivity, responsiveness, and operationalization and separates normal PCN-stage incompleteness from residual design questions.
3. Suggested drafting appears consistently in Climate Summary and Detailed when the document target is verified, and is safely withheld with a plain explanation otherwise.
4. Climate Summary provides closed watch and guidance disclosures; Detailed separates decision preparation and further guidance into distinct purpose-led bands.
5. Guidance shows only source-supported standard purpose text.
6. Main FCV retains its existing concise narrative and gains only the conditional watch disclosure plus shared extraction reliability.
7. The South Sudan PCN's structured metadata resolves to P511185, IPF, and Substantial without falsely activating MPA.
8. The shared extractor handles content controls and nested tables without duplicate or out-of-order text.
9. Browser, shareable HTML, and applicable DOCX output agree on canonical content.
10. Focused tests, the full suite, responsive checks, export checks, and deployed South Sudan smoke all pass.
