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


2026-10-13 final readout safeguards: reader v2.8 withholds a whole narrative that
introduces responsiveness absent from the reviewed action fields; complete field
presentation retains every action/qualification and grades are unchanged.
Compiler/reviewer v2.10 align titles with minimum actions and distinguish ordinary
measurement from wider dividends. Source proof retains only cited sources and
explicit provider publication dates; unknown dates stay unknown. Climate gaps
carry a concise optional-dividend scope note. No new model/fetch call; original
paid archives remain unchanged. Final trial/check evidence is recorded in
`docs/20261012_climate-opcs-parity-validation.md`.


Detailed export completeness: HTML/Word render the optional reader summary_gaps
as Supporting gap findings before priorities, preserving all five full qualified
statements and the optional-dividend scope note. They still use detailed renderer
boundaries. Legacy readers without summary_gaps do not gain an empty section.


Final export parity: browser Detailed/Share HTML also includes Supporting gap
findings under the core questions, matching the complete data in Python HTML/Word.
Final full verification: 1,444 passed after the hostname-boundary follow-up; paid and replay limits are recorded in the
validation handover. Production/main and ITS remain unchanged.


### 2026-10-13 action-led Climate candidate (rollout held)

The verified reader derives `assessment_themes` from admitted gap statements and
question/evidence links, with `priority_ranks` or explicit evidence follow-up. Detailed
retains full questions in supporting analysis; Word uses an appendix. Summary retains
five complete gaps. Paired five-point ratings replace the old export panel. Climate
Detailed no longer renders the normal route's duplicate priority stepper/cards.
Judgment prompt v2.9 targets 180–260 words of operational context; recommendation
prompt v2.11 targets three to five substantive decisions where evidence warrants them.
An explicit explained revise verdict permits one bounded compiler correction plus
independent re-review through the same validation and original deadline. Original
review and correction diagnostics remain separate; accepted actions survive repair
failure. Reader version v2.9. No new paid generation has validated this candidate.
See `docs/20261013_climate-action-led-validation.md` for acceptance and saved replay.


### 2026-10-13 narrative findings follow-up

The existing judgment call now returns assessment_narratives (design/dividends/inclusion),
one or two connected paragraphs per theme, targeting 70-130 words and citing verified
register IDs. Shared reader admission requires unique themes, known citations including
a project fact, complete plain prose and number/entity/action checks. This narrative
path permits natural paraphrase; the existing strict Summary vocabulary gate is unchanged.
Original canonical gaps and recommendation links remain available as supporting detail.
Browser and HTML use question headings, prose and native disclosures; Word preserves
prose with original detail in its supporting appendix. Sections 04-07 use distinct cards
in HTML. Common prompt calibration assesses conditional potential and enabling conditions,
without penalizing missing peace/dividends terminology. Executive provider schema is
aligned to the existing 180-260 word instruction. No extra generation call or dependency.

Prompt versions: facts2.4, analysis2.7, judgments2.10, recommendations2.12, review2.11,
drafting1.3; reader2.10. Fresh provider output remains unvalidated; PR83 stays draft.


### 2026-10-13 reader simplification (supersedes visible supporting detail above)

User-approved follow-up removes per-theme project-detail disclosures and the
supporting question/watch appendix from Detailed, HTML and Word. Internal evidence
and canonical questions remain available for validation and audit. The three
question-led narrative answers remain. Method shows coverage, limitations and
sources without repeating pathways. Priority cards now use Why this matters and
What the team could do, with implementation/drafting in Recommendation details.
Word mirrors those headings with a detail block. Legacy narrative/field fallback
preserves complete text. Mobile card padding is reduced. Summary watches unchanged.
Judgment and recommendation instructions require natural prose without framework
recaps, label-and-colon verdicts, semicolons or literal Done looks like cues.
Versions: judgments2.11, recommendations2.13, reader2.11. No added model calls.
See docs/20261013_climate-reader-simplification-validation.md for evidence and limits.


### 2026-10-13 standalone brief review

Context/findings/priority prose instructions now develop a connected brief instead
of repeating project history and gap inventories. A reproduced capitalization
false positive rejected sentence-initial Links and silently restored old dividends
wording. Analytical paraphrase now permits bounded generic sentence openings and
inflections of existing permitted prose terms. Multiword names/acronyms, figures,
dates, markup and action checks remain. Strict Summary mode is unchanged.
Versions judgments2.12, recommendations2.14, reader2.12. No added provider calls
or schema fields. New editorial preview asserts admission of all three narratives.
See docs/20261013_climate-cohesive-brief-validation.md. Fresh paid generation remains
unvalidated and PR83 remains draft.

### 2026-10-13 quality6 and reader2.14

The newly authorized quality run failed acceptance: four admitted candidates became
two after semantic review; bounded correction recovered none; research failed quote
provenance checks; native Summary fell back. Rollout remains held. Reader2.14 repairs
full Democratic Republic of Congo wording only against admitted DRC support in
analytical paraphrase mode, and sentence-initial Today. No other country alias is
invented or conflated. The obsolete four-label Summary requirement is removed;
strict vocabulary and other grounding controls remain. Correction diagnostics now
record bounded response and reasons for pre-review rejection. No added model calls,
retries or generation prompt changes. The same saved assessment now displays all
three generated narrative answers and keeps the two-action warning. See quality6
validation handover; this replay is not a second paid run or release acceptance.

Reader2.15 presentation follow-up: all ranked operational priority cards start open
in Detailed/browser HTML and Python HTML. Their Recommendation details remain closed,
as do review checks, guidance and method disclosures. Users can close individual cards;
the print handler restores their chosen state. No generation changes or additional
paid calls. The separate pipeline readiness assessment proposes backend redesign;
it is not evidence that the failed quality6 result is accepted.


### 2026-10-14 approved backend redesign

Native recommendations and optional drafting have separate validation boundaries.
conditional_review receives core-only decisions plus separately identified artifacts
(REC-ID::current_document / ::operational_instrument) and must explicitly return
passed_core_ids. Missing/ambiguous review acceptance withholds cores. A draft-only
defect cannot accept or erase its separately reviewed parent. Core and drafting
repairs use their matching compiler, do not expand supporting evidence or rank,
and receive independent re-review. Correction work shares9,000 output tokens;
unknown usage consumes the full requested allowance, and repair calls do not retry.
Optional drafting reserves the conditional-review deadline. Optional post-review
provider failure records a limited result; cancellation always propagates.

The native judgment schema now returns final-reader-v1 instead of pre-admission
Summary/narratives. reader_compiler (4,000 output tokens/180s) and reader_review
(2,500/120s) run after final accepted decisions, within the existing14-minute cap.
Paragraphs bind to known facts/findings and accepted action IDs; paraphrase receives
entity/number/date guards and a separate meaning check. Reader2.16 derives both
Summary and findings from the reviewed final_reader, rechecks saved support, and
uses a clear limited fallback if that reader is missing/invalid. Legacy saves keep
their former contracts; their rejected recommendations are never reclassified.

Research selects bounded received passage IDs. Complementary quotes per URL are
retained whole; classifier-selected project labels must match uploaded source labels,
and geography/group/asset labels must be meaningful complete source spans. Quote,
URL, title and publication metadata remain application owned. Pure classification
uses no encrypted conversation or tools; actual search continuation preserves the
provider blocks. Incomplete country coverage/failed quorum stays partial inspection
proof and cannot enter either admitted prompt path. Explicit unavailable bank scope
and country reasons are preserved. No policy entitlement is inferred from web prose.

Model/usage diagnostics record each returned/failed attempt and its initial/repair/
reader scope, with unknown usage marked unknown. Added reader calls and net cost
have not been measured live. The source-based acceptance benchmark describes three
material Great Lakes decision areas and preserves existing funded responses.
Synthetic one/three/five-action fixtures test transport, not fresh model quality.
Production/main/ITS remain held pending separately authorized live acceptance.


## 2026-10-14 paid reader-boundary follow-up

Native final-reader-v1 is carried into reader validation. Only an absent optional
current-document block is allowed; malformed supplied blocks still fail. Legacy
readers retain strict current-drafting checks. Native final prose needs the complete
three-theme package. The core-only transport test now crosses the runtime gate and
both export writers. Reader/normalization versions are 2.17/2.2.

ClimateReaderIntegrityError carries a completed normalized assessment and reason
codes separately from its message. The same SSE caller receives diagnostic_only
climate_verified_failure before the ordinary blocking error. Browser manual Save
Session/load uses climateVerifiedFailure only; it never becomes climate assessment
or reader, is excluded from automatic storage/report/follow-on payloads, and clears
on reset/new run/rerun. No server assessment cache/GET endpoint is introduced.

ContextEvidenceRef adds source_details, evidence_gap and time_horizons with empty
backwards-compatible defaults. The live adapter preserves all cited source titles,
URLs and publication dates with received limitations. Missing dates explicitly
leave current conditions unverified. Relevance horizons are not observation dates;
historical/off-site events cannot establish current project-site conditions.
All eight prompt versions advance to record that common calibration. No budget,
provider, retry, entitlement, authority or paid-call-count change is introduced.


## 2026-10-14 benefits prose preflight

Analysis2.10 preserves plausible positive benefit mechanisms and their enabling
conditions in the existing evidence-linked response/pathway registers. The final
compiler and meaning reviewer1.2 assess project-feature-led, conditional potential
and fairness, rather than missing dividends language or an unstated mechanism.
Dividends/inclusion target two connected paragraphs,150-180 words when supported.
Native findings accept70-180 words, aligned with the existing shared renderer180
cap; short saved native outputs remain valid. Reader version2.18. An exact ordinary
sentence-initial Clear access arrangements exemption retains one-word actor,
multiword-name and acronym rejection.
Practical strengthening actions still follow independently accepted decisions.
No new fields, evidence entitlements, dependencies, calls, retries or budgets.
Fresh paid acceptance remains separate from offline transport and export checks.

## 2026-10-14 quality8 reader admission follow-up

Paid quality8 retained four accepted action cores and five Summary gaps, but its
native reader was withheld before meaning review. Original output is preserved;
no retroactive pass is supplied. The single paid allowance is consumed.

Compiler1.3/normalization2.3 add a unique explicit same-passage missing-entity
citation repair, bounded grammatical/conditional-causality checks, and at most one
targeted final-reader correction plus fresh meaning review. The existing shared
correction allowance/deadline bounds this path. Untargeted records, themes and
accepted actions are preserved; new evidence IDs, names, quantities and action
anchors are rejected. Independent clean native reader_review remains mandatory.
An external source-checked editorial preview is separate from native acceptance.
Production/main/ITS remain held; PR83 stays draft.

Renderer2.19 also links directly cited accepted recommendations from findings to
their priority cards, preserving existing gap-based links. Compiler1.3 answers
the renderer's questions directly instead of repeating their headings in prose.
