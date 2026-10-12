# Sector-Lens Platform Reference

The sector-lens platform overlays optional specialist analysis on the common FCV assessment. It does not add a score, change the rating denominator, or create a second recommendation list. The production catalogue includes the approved manual-only Climate-FCV Lens.

## Module package

Each direct child of `sector_lenses/modules/` is a versioned module with:

- `manifest.yaml`: identity, status, `activation`, aliases, detection signals, declared `readout_sections`, stage budgets, and stage instructions.
- `questions.yaml`: conditional Stage 2 questions, source IDs, priority, and explicit core mappings.
- `guidance.md`: distilled synthesis guidance.
- `sources.yaml`: stable source IDs, titles, citations, and optional URLs.
- optional `source_notes/`: SME distillation notes; these are never read into runtime prompts.

The loader uses `yaml.safe_load`. Invalid packages are quarantined in registry diagnostics and cannot break core screening. Valid mappings are `ost:1` through `ost:12`, `dnh:1` through `dnh:9`, and `shift:A` through `shift:D`. Module budgets cannot exceed 600 / 2,000 / 900 estimated tokens for Stages 1 / 2 / 3.

## Selection and detection

`GET /api/sector-lenses` returns enabled selector metadata, including activation and readout declarations. `/api/detect-document-type` also returns ranked `lens_suggestions` for `suggested` modules. Modules with `activation: manual`, including Climate, are never auto-suggested or preselected. Detection or extraction failure returns an empty list and never blocks manual selection.

Clients send ordered `active_lenses` (maximum two) and optional `lens_versions`. Array order is primary then secondary. The server drops unknown or disabled IDs with `lens_warnings`, enforces the limit, and always resolves the authoritative installed version. Saved sessions use version 3; older sessions load as core-only. An incomplete version-3 run whose module version changed must restart at Stage 1.

## Stage contract

`build_lens_stage_context()` is used by both Express and Step-by-Step paths.

Dedicated Climate-FCV Stages 2 and 3 use its metadata-only mode (`compose_prompt=False`) because their canonical native prompt builders replace the legacy sector-lens prompt. Metadata-only mode retains resolved lenses, warnings, context sources, version checks, and Stage 3 diagnostic normalization.

- Stage 1 injects evidence requests and research intents. The model emits hidden JSON between `%%%LENS_EVIDENCE_START%%%` and `%%%LENS_EVIDENCE_END%%%`. Climate-active runs also execute a dedicated bounded trusted-source research pass. A second pass is allowed only when structured evidence with sources and claims narrowly fails `climate_research_insufficient`; missing output, truncation, timeout, and terminal provider errors are not duplicated. Normalized `ClimateResearchBundle` claims join Stage 1 and Stage 2 context without changing core-only research.
- Stage 2 injects distilled guidance, applicable questions, and bounded normalized Climate claims. The model emits JSON between `%%%LENS_DIAGNOSTIC_START%%%` and `%%%LENS_DIAGNOSTIC_END%%%`, with `lenses[]` and `findings[]`. Climate interaction entries contain stable project-specific `pathways` for both fixed directions. Each pathway includes pressure, mechanism, project implication, design response, project/location/group/system anchors, time horizons, research claim IDs or an evidence gap, and confidence. Lens entries also include `materiality_summary`, `analysis_emphasis`, `readout_sections`, and `other_pathways`; undeclared or generic entries are dropped. Findings include deterministic `finding_id` values plus `lens_ids`, evidence, status, source IDs, core mappings, mechanism, geography, and action target.
- Before Stage 3, findings are merged when mappings, mechanism, geography, and action target match. Contributing lens and source IDs are retained.
- Stage 3 integrates findings into the opening assessment, operational context, two-way risk narrative, strengths, gaps, and existing priority set. Climate compaction prioritizes both directional pathways and recognized dividend IDs within the 900-token platform ceiling. Every priority in a valid Climate-active run carries validated `climate_links`; affected priorities derive `lens_ids` and `lens_relevance` from recognized diagnostic IDs. No separate score or recommendation set is permitted.

One lens may use its module allowance up to the platform ceiling. With two lenses, the platform budget is split two-thirds to the primary lens and one-third to the secondary lens. Questions are included in priority order, as whole blocks, and reported as truncated when they cannot fit.

Hidden blocks are removed from displayed prose. An invalid Climate diagnostic triggers one bounded structured recovery attempt; terminal failure retains the core assessment and suppresses unvalidated Climate claims. Stage 2 retains the internal materiality field and declared readouts, while reader-facing output uses climate relevance language. Climate-active Stage 3 renders a plain scene-setting opening, two stacked directional narratives of up to two short component-anchored paragraphs, a six-tier integration gauge with a concise improvement message, core questions without status chips, framework references, and priority contribution panels. Live HTML, shared HTML, and DOCX use the same validated structures.

**Diagnostic completeness (v9.20).** A Climate diagnostic is *usable* when it has materiality plus one interaction pathway, and *complete* when it additionally carries at least one grounded reflection and a non-empty `integration_summary` (`climate_readout_is_complete()`). Recovery fires on either a hard failure or a usable-but-incomplete readout, and the bounded recovery request asks for the full dedicated-module contract (`reflections`, `integration_level`, `integration_summary`, `less_central`, `sensitivity_evidence`, `responsiveness_evidence`). A usable primary is never downgraded: a recovered diagnostic is adopted only when the primary was unusable or the recovery is complete. When a usable readout is still incomplete after recovery, the module notice (frontend, shared HTML, and DOCX) shows an honest partial notice rather than silently omitting the reflections/integration sections. `_stream_stage` records the provider `stop_reason` so a climate-active Stage 2 `max_tokens` truncation is logged.

## Climate-FCV Lens

Selection is explicit, but screening after selection is automatic across climate-intent and wider development operations. Adaptation, resilience, and climate-risk management are primary; deep mitigation or transition analysis requires a clear material pathway. Dividend items require a mechanism, material relevance, and practical action. The eight fixed source IDs are `peace-social-dividends`, `ccdr-fcv-approach`, `fcv-climate-compendium`, `defueling-conflict`, `defueling-field-notes`, `adelphi-conflict-sensitivity`, `cgiar-climate-security`, and `adaptation-review`.

Optional CCDR material may enter as `context-ccdr` only with a validated World Bank HTTPS URL. Dedicated research sources use allowlisted trusted types and HTTPS hosts. CCDR evidence remains contextual rather than project evidence, retrieval failure is non-blocking, and it must not become a routine recommendation. Core-only runs retain the existing lightweight Climate-FCV check and 4-5 substantive priorities. Active Climate supersedes that check without duplication and uses one list of no more than five substantive priorities with a flexible, non-quota core/Climate/blended mix.

Valid interaction directions are `climate-fcv-on-project` and `project-on-climate-fcv`. Valid horizons are `current-near-term`, `project-lifetime`, and `asset-system-lifetime`. Standard dividend pathway IDs equal their declared item IDs; additional pathway IDs use `additional-{section_id}-1|2`. Climate priority links use `linked` or `no-material-pathway`. Linked records require a recognized interaction, dividend, or finding ID plus `contribution` and `strengthening_effect`; no-material records require empty ID arrays and a concrete core-FCV reason.

## Climate research provider boundary

The Render build uses a bounded evidence-packet adapter between Sonnet web search and Haiku JSON structuring. The adapter accepts SDK objects or dictionaries, keeps only bounded text notes and deduplicated trusted HTTPS source metadata, and bounds the project profile before serialization. Haiku receives one fresh user message; raw tool-result blocks and encrypted content are never replayed. Packet telemetry contains counts and sizes only. This is provider-specific plumbing: it does not change the shared ClimateResearchBundle schema or the Flask/FastAPI parity contract.


## Climate-FCV country evidence bank

`sector_lenses.climate_bank` loads the approved schema `1.0.0` release from the
pinned public submodule or `CLIMATE_COUNTRY_BANK_PATH`. An explicit
`CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate` override may instead load the
schema `1.1.0` candidate release. Materialization is checksum-valid,
review-window bounded, and non-throwing. Selection targets 8 and caps 12 items,
admits at most two physical-baseline records, favors source diversity, and
emphasizes qualitative vulnerability/capacity, affected groups, institutions,
geography, sectors, project elements, systems/resources, and mediators.

Grounding caps bank context at 6,000 characters, accepted live claims at 6, and
combined context at 12,000. Its state enum is `bank+research | bank-only |
research-only | thematic-only`. Conflicts remain visible provenance. Only
server-rematerialized IDs matching `AAA-SRC-999` enter diagnostic source
normalization. South Sudan is approved in production content version
`2026.07.south-sudan-pilot`; the runtime projection selects at most 12 records
from its 19 approved evidence records and seven approved pathways. The candidate
preview release `2026.08.multi-country-preview` contains 24 reviewed country
packages, 291 sources, 565 evidence records, and 178 pathways. It must not be
treated as approved content until country-level substantive review and promotion.
Source URL uniqueness is validated within the selected country package. The same
public source may legitimately appear under country-scoped source IDs in multiple
packages; duplicate normalized URLs within one country remain invalid.
When candidate evidence is used, live HTML, shared HTML, and DOCX readers show
the concise safeguard `Candidate country evidence: preview; not approved.`
without restoring removed technical diagnostics or raw evidence-status panels.

## Compatibility contract

The Flask and private FastAPI builds must keep these fields and delimiters aligned:

- request/session/report: `active_lenses`, `lens_versions`, `lens_context_sources`, saved-session version 3;
- metadata: `lens_suggestions`;
- catalogue: `activation`, `readout_sections`;
- SSE: `active_lenses`, `lens_warnings`, `lens_diagnostic`, `lens_context_sources`;
- Stage 3 priority: `lens_ids: string[]`, `lens_relevance: string`, and additive `climate_links` with status, interaction/dividend/finding IDs, contribution, strengthening effect, and reason;
- Climate research: normalized `sources`, project-specific `claims`, confidence, evidence status, and the three horizon enums;
- Climate diagnostic: stable pathway and finding IDs plus the causal pathway fields described above;
- Climate grounding: `state`, `warning_code`, `content_version`, `country_iso3`, `research_status`, sanitized `bank_manifest`, and display-safe `sources`;
- canonical manifest: `bank_status`, `warning_code`, `schema_version`, `content_version`, `country_iso3`, `evidence_ids`, `pathway_ids`;
- SSE: additive `climate_grounding` on Stage 1 and Stage 2 completion events;
- hidden delimiter names and diagnostic status/core-mapping enums.

Raw literature and source notes are never injected at runtime.

*Last updated: 2026-08-13 - multi-country materialization and visible candidate safeguards.*

## Climate verified-v2.1 compatibility surface (v9.25)

The active Climate-only Express design path now uses `climate-verified-v2.1`; the
`climate-native-v1` normalizer remains readable for legacy sessions and other
routes. Shared v2 fields are `schema_version`, `run_id`, `bank_release_id`,
`evidence_status`, atomic `facts`, `analysis`, four `judgments`,
`executive_readout`, ranked `priorities`, `review_readiness_flags`, `validation`,
additive `operation_context`,
and a privacy-safe `manifest`. Recommendations are capped at three and may be
zero. Candidate evidence remains labelled `preview; not approved`. ITS/FastAPI
must not translate the old single rating into the four judgments; it should mirror
the v2 contract or retain explicit legacy status.

Recommendation suppression is observable through additive privacy-safe
`recommendation_diagnostics`: raw, parsed, structurally valid, gate-admitted,
and final counts; semantic-review invocation/verdict; at most 12 reason codes;
and at most 12 unsupported numeric tokens. Numeric component or subcomponent
labels are accepted only when they occur in a project fact explicitly linked by
the candidate. The pipeline derives support from the linked fact and ignores
model self-attestation; suffixes of structured references such as PF-055 and RG-029
and numbered-list markers such as (1) are not treated as numeric claims.
Unsourced dates, thresholds, and quantities
remain blocking.
Current-document drafting destinations remain bounded by the selected
operational-guidance registry. Before validation, a section-label variant may be
canonicalized only when its cited guidance entry supplies a unique permitted
target for the current document and the labels share a meaningful token. The
repair is recorded as `DRAFTING_CURRENT_SECTION_CANONICALIZED`; unknown guidance,
unrelated section names, and ambiguous matches continue to fail closed.
Deterministic admission failures distinguish total score, materiality, missing or
failed named gates, and the three-priority cap. No candidate or project prose is
included. The canonical reader copies the safe summary into its technical annex.
When no priority survives, both canonical HTML and DOCX render the same explicit
no-recommendation admission message instead of leaving an empty section.

Each admitted priority requires a structured current-document drafting block;
a second operational-instrument block is nullable and is retained only when it
is distinct and linked to an evidenced named instrument. Drafting carries a
bounded guidance ID and uses `standard_document_advisory` when the normal PCN or
PAD destination is advisory rather than a confirmed project commitment. The
compiler alone receives the versioned operational-guidance packet; the packet is
not project evidence and does not claim to reproduce OPCS or ESF policy text.

Operational-guidance registry v2 is fail-closed. A known document with an unknown
instrument selects no packet. New-model IPF uses Project Paper targets; PforR uses
Program Paper/PAD, ESSA, Program Action Plan, DLI and verification targets; DPF
uses Program Document, prior-action/policy-matrix, poverty/social-impact, and
environment/forest/natural-resource targets. An MPA adds a program-layer entry
only after the base instrument resolves to IPF or PforR. PforR and DPF never
inherit IPF ESCP/SEP/ESS drafting destinations.
Candidate validation also blocks instrument-incompatible terminology in the
recommendation and drafting prose: PforR cannot emit IPF ESF/ESS/ESCP/SEP routes,
and DPF cannot emit either IPF or PforR instrument routes. For MPA packets, the
program-layer entry is ranked ahead of the packet cap so it cannot be sliced off
by the base-instrument guidance entries.

Readiness flags carry `residual_gap_ids` and are suppressed when they duplicate
the residual gaps behind final priorities. Judgment values, including unclear or
not-evidenced states, require resolvable evidence IDs. The canonical reader derives
`priority_summary` after admission and semantic review, counts accepted live
research from distinct `CE-LIVE-*` evidence IDs, and keeps drafting labels,
destinations, status, guidance basis, provenance count, and the
`preview; not approved` label in parity across browser, HTML, and DOCX outputs.

## Climate Summary and extraction compatibility (v9.38)

The compatible reader adds `summary_overview.paragraphs` to the existing
four-dimensional judgment response and uses prompt version
`climate-judgments-v2.4`; it does not add a model call or alter delimiter names,
priority JSON, rating semantics, or the three-priority cap. Verified source
manifests use `source-blocks-v3` so structured DOCX metadata can travel beside,
but never replace or reorder, evidence blocks. Structured financing fields outrank
prose markers and conflicts fail closed. Operational guidance remains
`climate-guidance-v3`.

Summary may expose one closed watch-items disclosure and one closed curated WBG
guidance disclosure. Suggested drafting appears in both Summary and Detailed only
after the shared document-plus-instrument gate passes. These are reader-contract
changes; normal FCV retains its narrative/schema/prompt/rating contracts and only
adds conditional render-time watch items from already-returned arrays.


## Climate OPCS parity candidate (2026-10-12)

Branch `fix/climate-opcs-parity` updates verified Climate routing and the bounded
registry to `climate-guidance-v4`. DPF PAD hints normalize to Program Document;
IPF-DDO uses IPF; unsupported TA stays unresolved. PID, Project Paper and Program
Document alone do not establish a preparation regime. Explicit OIS dates use the
shared instrument boundaries. AF/restructuring purpose precedes generic paper
labels. Labelled risk inputs use the shared processing classifier with MPA,
FMRF and hybrid-component safeguards; conflicting processing markers fail closed.
New-model IPF can resolve ESF through the shared OIS rule, while AF/restructuring
needs explicit E&S evidence and mixed framework mentions stay unresolved.

DPF-MPA drafting is withheld. PforR mid-cycle guidance is registered. Hybrid PforR
recommendations can use IPF E&S terminology only in explicitly component-scoped
sentences supported by linked component facts; standalone PforR/DPF guards remain.
`DraftingValidationContext.has_ipf_component` is an internal optional boolean;
no output schema, delimiter, rating or extra model call changes.

Appraisal guidance adds evidence checks and specialist referrals for Paris
Alignment, climate/disaster risk screening, climate co-benefits and indicators.
It never certifies compliance or treats a missing upload as an absent assessment.
Reader timing uses conditional new-model review destinations, and PID is not
assumed concept-stage. Source currency remains subject to live PPF verification.
Live acceptance and release status: see `docs/20261012_climate-opcs-parity-validation.md`.
# October 12 candidate sidebar and responsiveness scale

Verified Climate responsiveness now uses very_limited, limited, moderate, strong,
very_strong, plus unscored not_expected and unclear. Judgment schema/prompt version
is climate-judgments-v2.5. This measures additional contribution in the operation's
scope, not compliance or overall quality. Sensitivity remains separate. Historical
Emerging results are preserved by the reader and displayed as legacy, without a
numeric bar. Reassessment is required for a five-point value. Both live Summary
and Detailed use the shared two-card sidebar and mobile disclosure. Normal FCV's
existing scale is unchanged. Existing standalone exports retain their report layout.

Production-readiness corrections: PID beneficiary fields are preserved before
normalization and establish regional scope; adjacent geographic identifiers do
not become beneficiary countries. E&S framework evidence is searched across
retained primary blocks. Missing OIS metadata is explicitly disclosed in all
reader surfaces. HTML and Word exports include the responsiveness contribution
label, five-point scale and scope message. Reader-only legacy Emerging support
does not change the stricter generation schema.

### 2026-10-12 quality acceptance hold

PR #83 remains a candidate: the one live quality run suppressed all five recommendations. Conditional review now receives current_document, guidance_registry_version and the same operational_guidance as compilation (prompt v2.6), distinguishing permitted advisory destinations from established project commitments. Suppression behavior is unchanged. The fix is offline verified only; another authorized quality run is required before promotion. Incomplete reader exports place the warning first.


### 2026-10-12 offline hardening before another paid run

Shared Markdown spacing/marker-drift cleanup and actor normalization now cover all
visible fields. Saved assessments retain bounded diagnostic_trace snapshots,
excluded from readers/logs/exports; reviewer schema adds per-REC issues. Summary
validation records specific failures without relaxing grounding. Prompt versions:
judgments v2.6, compiler v2.5, review v2.7. No added provider calls. See
`docs/20261012_climate-opcs-parity-validation.md` for checks and acceptance limits.
Production remains held pending a separately authorized live quality check.


### 2026-10-12 second quality trial and post-run fixes

The authorized trial on 152656b retained one of three priorities; two correctly
failed scope/authority review. Production remains held. Post-run fixes accept
ordinary grounded summary prose, reject project-document titles on country-homepage
URLs and avoid treating page_age as publication date. Climate scope/CERC and
conditional proposal guards are strengthened (analysis v2.3, compiler v2.6,
drafting v1.1, review v2.8; judgments v2.6). Reader status partial adds a short
needs-review notice across app, copied Summary and exports. See the current
validation document for trace, evidence and live-acceptance limits.


### Native research-context continuation correction

The existing research structuring call now preserves native search/encrypted
context, with further searches disabled and no added call. All 55 research,
grounding and context checks pass. The current validation record documents the
protocol and remaining live-acceptance hold; ITS remains unchanged.


### 2026-10-12 approved dividends readout candidate

Climate questions and rubrics are aligned with the Peace and Social Dividends
report's investment/delivery framing (judgments v2.7, compiler v2.7, reader v2.4).
Responsiveness needs a specific climate-linked dividend mechanism within project
scope; it remains separate from sensitivity and overall project quality. Summary
now highlights short limitations from admitted priorities between strengths and
actions, preserving evidence qualifications and all withholding notices. Five-point
values, normal-FCV categories, saved grades and model-call counts are unchanged.
Candidate only; production/ITS and live analytical acceptance remain on hold.

### 2026-10-12 third quality trial and source-proof follow-up

Trial fb3f2859-32b1-40a6-8a51-d56ffdcd04ab completed on fc34b77 in about
217 seconds, but remains analytically unaccepted. Native research continuation
worked; research nevertheless misread section/footnote numbers and a sediment-loss
projection. Fresh research now requires source_excerpt, requested <=140 characters
and admitted only <=150, matching a provider cited_text/snippet at its declared
trusted URL. Downstream claim prose is the matched passage itself; changed numeric
tokens, fabricated passages and wrong URLs are rejected. Missing proof makes the
bundle partial or failed. Existing normalization keeps old saved bundles readable;
this gate applies to fresh research, not a retroactive certification of archives.

app.py accumulates provider content from the existing search/continuation/structuring
calls, joins citation-split text without injected newlines and checks proof before
the existing evidence gate. No new fetch, search, dependency or model call. Matching
passages verify provenance, not the project's inferred link or every interpretation.
Research still requires analytical validation, including coverage of regional scope.

Current versions: facts v2.3, analysis v2.4, judgments v2.8, recommendations v2.8,
review v2.9, drafting v1.2; reader v2.5. Shared calibration treats routine hazard
screening as sensitivity, requires a wider dividend mechanism for responsiveness,
preserves planned versus completed commitments and leaves current status unverified
when only historical estimated dates exist. AF timing is the applicable review.
Production/ITS remain held; see the validation record for paid/offline boundaries.


### 2026-10-12 expanded gaps and candidate coverage

Reader v2.6 adds optional summary_gaps: up to five complete qualified residual-gap
statements, independent of action count. Kept-priority links come first, then
design findings before contextual evidence gaps. The projection checks typed
project/pathway/response/evidence references and explicit-negative support for
confirmed omissions, deduplicates IDs/text, and keeps whole qualifications.
Evidence-trail assembly includes those gap IDs, preserving their supporting prose
in detailed HTML/Word. Legacy readers use existing limitation fields; only fresh
or rebuilt readers gain summary_gaps. Archives are not regraded or regenerated.

Analysis v2.5 explains each gap in two/three sentences, 35-65 words: what remains,
its project-specific consequence and evidence/scope qualifier. Compiler v2.9
considers every admitted gap and may return up to five material distinct actions,
grouping only gaps resolved by the same action. No quota or lowered review gate.
The Climate Summary now displays all five supported priorities, matching normal
FCV's cap. Unknown gap evidence IDs are rejected before compilation. Exact source
words within hyphenated expressions no longer falsely fail entity grounding;
unsupported entities still fail. No dependency, extra provider call, repair loop
or native generation-schema field. Other prompt versions are unchanged.


Final pre-paid refinements: Stage 1 now passes its existing explicit PID beneficiary
countries and country scope into both search and bounded structuring. Neighboring
countries in geographic identifiers are excluded. Regional searches prioritize an
uncovered beneficiary within the existing two-search limit; incomplete coverage
must remain partial. Profile/page text is evidence, never instructions, and document
excerpts must not become public search queries. No new provider or metadata call.
The Summary no longer credits high risk relevance as a project strength; genuine
very_strong responsiveness retains its positive interpretation. Literal source
words/acronyms in compounds, including Flood-resilient and C-ESMP, pass the shared
whole-word grounding check; unsupported entities remain rejected. Methodology
wording describes source-linked checks and expert corroboration without promising
that generation cannot invent a claim. Other gates and five-point values remain.


### 2026-10-13 post-quality4 handoff repair

Analysis v2.6 clarifies exact fact/context IDs and project-only mechanisms when
context evidence is empty. Reader v2.7 adds a plain analysis_status/message for
withheld evidence, shown in both views and HTML/Word. Source packets enrich
metadata with later native citations and prioritize quoted passages within the
same four-source cap, using cumulative pause-turn content. Sonnet search uses
between_tools/3000 tokens and bounded cited quotes; the existing Haiku structurer,
two-search/150s limit and independent evidence/review gates remain. No extra call
or fetch. See docs/20261012_climate-opcs-parity-validation.md for the unaccepted
quality4 result, original private artifacts, tests and remaining paid allowance.
