# Supervised production capability audit

Date: 2026-10-16. Audited candidate: 347c1b2, fix/climate-opcs-parity.
Scope: recovered document classification and existing Climate-FCV review,
persistence and export boundaries. Static inspection only; no paid calls,
deployment, runtime changes or production acceptance.

## Corpus findings

The recovered corpus contains 27 files: six primary project documents, two
project supporting documents, fourteen country-context documents, four previous
outputs and one explicitly synthetic test. These are five project families in
three countries, not 27 independent evaluation cases.

| Family | Source classification | Evidence location |
|---|---|---|
| Afghanistan Human Capital and Jobs, P514193 | IPF concept PID; supporting concept ESRS and CRM agenda | PID OOXML basic-data fields; ESRS PDF pages 1–2 |
| Afghanistan Private Sector Resilience Program, P512394 | IPF PCN | PCN OOXML title and basic-data fields |
| Guinea Support to Local Governance Project 2, P177095 | IPF PAD | BOSIB PDF cover and PDF page 6 datasheet |
| Guinea Water and Sanitation Project, P179017 | IPF PAD | BOSIB PDF cover and PDF page 7 datasheet |
| Honduras Sustainable Connectivity Project, P181166 | IPF PCN and PAD, same family | PCN OOXML basic-data fields; PAD cover and PDF page 6 datasheet |

Honduras BOSIB is a Country Partnership Framework, not another project or a DPF
case. DPF/IPF mentions in acronym lists are not classification evidence. DOCX
basic-data fields required direct OOXML inspection because ordinary paragraph and
table extraction omitted some content. No layout or substantive source review is
claimed by this classification. The two Honduras stages must stay in the same
partition. No DPF or PforR primary document is established in this corpus.

Prior exposure remains unresolved except the already identified Guinea testing.
All holdout eligibility remains false. The corpus can support development and
supervised calibration, but does not fill the twelve proposed holdout slots or
establish cross-instrument production readiness. Sources remain local; no source
text or binaries are committed. Full relative-path roles and SHA-256 values are in
`output/20261016-production-acceptance-inventory/source_classification.json`.

## Existing controls and gaps

| Boundary | Observed implementation | Production implication |
|---|---|---|
| Saved session | `index.html:3361` saves assessment, reader, outputs and lens versions; `3461` imports browser JSON | Reuse this representation, but a user-editable session is not an authenticated approval record. No named sign-off is serialized here. |
| HTML download | `index.html:6094` renders the current `climateVerifiedReader` locally | Export has no human-approval check; current reader is the displayed/exported content. |
| Word download | `app.py:12633` normalizes posted assessment and rebuilds a reader; incoming reader supplies only runtime mode | A change made only in the current reader is not carried through this path. A reviewed version cannot safely be identified only by the browser reader. |
| Structural integrity | `app.py:12659` validates rebuilt reader before Word export | Useful existing gate, but schema integrity does not establish factual accuracy or human approval. |
| Source of export data | `index.html:6036` posts browser assessment/reader payload | Do not treat an added client-side approval boolean as trusted authorization. |
| User guidance | `index.html:5257` contains explicit LLM advisory language | Preserve calibration that minor errors are possible; this does not replace consequential-claim review. |

The inspected download paths contain no named reviewer, approval timestamp,
reviewed-content hash or server validation of an approval record. This is a
bounded path audit, not a claim that every unrelated repository feature was
searched. The HTML/Word difference is established from code; a concrete edited
reader fixture should become the regression test before changing the route.

## Smallest implementation sequence

1. Establish a single validated report snapshot at the review/export boundary.
   Bind assessment, displayed reader, source fingerprints and model/prompt versions
   together. Reuse current reader validation and renderers. Both HTML and Word
   must export that same snapshot; do not blindly trust arbitrary client reader
   text or silently rebuild away approved corrections.
2. Add explicit draft status across browser, Word and HTML. Draft downloads remain
   available for review. A model-reviewed result must not imply human approval.
3. Add a named review record for the snapshot, covering consequential claims and
   dependent advice, including claims the model did not flag. Content/input/version
   changes invalidate that record. Reloaded client files cannot establish trusted
   approval on their own.
4. Connect approved sharing to an authenticated reviewer and durable approval
   record. Audit the deployment's existing identity/storage facilities before
   choosing a new service. Until that boundary exists, operate only a controlled
   supervised pilot with external sign-off of the exact exported files.
5. Evaluate on source-reviewed cases beyond the original Great Lakes example.
   Start with the recovered IPF families as calibration; acquire independent DPF
   and PforR cases before claiming those routes accepted. Keep natural assessment
   performance separate from seeded-error challenges.

Required regression checks: a correction survives both export formats; changed
report/input/version loses approval; imported forged approval cannot approve a
report; drafts stay visibly unapproved; review metadata survives legitimate reload;
existing source evidence and useful qualified recommendations remain unchanged.
A browser/export round trip and focused route/renderer tests are required before
claiming these controls work. This audit does not implement them.

## Current decision

Production acceptance remains held and `publication_approved=false`. The next
runtime change should address report snapshot/export consistency first, followed
by the human review boundary. More prompt retries on the original case are not
the next production-readiness gate. No further provider spending is authorized by
this audit.
