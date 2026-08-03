# Climate-FCV TTL Drafting and Integrity Design

Date: 2026-08-03  
Branch: `feat/climate-country-bank`  
Status: Approved design; implementation planning pending

## 1. Purpose

Improve the verified Climate-FCV recommendation note so every admitted
priority gives Task Team Leaders (TTLs) detailed, targeted text they can adapt
for project documents, while preserving strict evidence, authority, timing,
and instrument safeguards.

The change also resolves the quality defects exposed by the South Sudan PCN
run: recommendation/executive-summary mismatch, empty judgment evidence links,
duplicated readiness flags, unsupported operational precision, and inconsistent
live-research provenance.

This is an output and validation redesign. It does not change the country-bank
generation process unless later evidence isolates a defect there.

## 2. Design Decision

Use structured drafting with a bounded operational-guidance registry and
deterministic validation. Do not add a separate paid "TTL editor" model stage.

This approach provides stable document and section targeting, separates
existing commitments from advisory language, prevents invented operational
details, and makes browser/HTML/DOCX parity directly testable without another
model call.

## 3. User-Facing Drafting Contract

Every admitted recommendation must include at least one complete drafting
block. A second operational-instrument block is included only when it has a
distinct purpose, a safe evidenced destination, and adds practical value for
the TTL. The system must not split one useful draft into repetitive blocks to
satisfy a fixed format.

### 3.1 Required current-document draft

This block targets the document under preparation or review, such as a PCN or
PAD. It specifies:

- target document type and section;
- 90-160 words of ready-to-adapt drafting;
- project evidence and residual-gap references;
- applicable bounded guidance references; and
- whether the text reflects an existing commitment or an advisory proposal.

Typical PCN targets include Project Description, Preliminary Results
Framework, Implementation Arrangements, and Concept Note risk/SORT discussion.
Targets must be stage-appropriate.

### 3.2 Optional operational-instrument draft

When useful, this block targets a verified existing instrument, or a standard
downstream project-document section when a separate instrument is not
evidenced. It carries the same metadata and 90-160 words of ready-to-adapt
drafting.

Omit it when the current-document draft captures the full actionable change,
when no distinct operational destination is supported, or when it would only
restate the first block.

Acceptable targets include an ESMF or Security Risk Management Plan explicitly
evidenced in uploaded project material, or a standard future PAD Results
Framework or Implementation Arrangements section. A separate POM, protocol,
plan, committee, focal point, monitoring system, or other vehicle must never be
invented.

### 3.3 Presentation

The reader and exports label the first block **Draft for the current project
document**. They label a justified second block **Draft for the operational
instrument**. Each block shows its document, section, status, and guidance basis
before the draft. The note and both exports retain "preview; not approved."

Drafting is advisory output and does not depend on a user-facing or workflow
`team_to_confirm` step.

## 4. Data Contract

Replace the single nullable `drafting_language` string with one required object
and one optional object:

```json
{
  "current_document_drafting": {
    "target_document": "PCN",
    "target_section": "Project Description",
    "drafting_status": "existing_commitment|advisory_proposal",
    "text": "...",
    "project_basis_ids": ["PF-..."],
    "gap_basis_ids": ["RG-..."],
    "guidance_ids": ["GUIDE-..."]
  },
  "operational_instrument_drafting": {
    "target_document": "Security Risk Management Plan",
    "target_section": "Business continuity arrangements",
    "drafting_status": "existing_commitment|advisory_proposal",
    "text": "...",
    "project_basis_ids": ["PF-..."],
    "gap_basis_ids": ["RG-..."],
    "guidance_ids": ["GUIDE-..."]
  }
}
```

`current_document_drafting` is required before admission.
`operational_instrument_drafting` is optional and may be null or absent. A
named standalone instrument is permitted only when its existence is evidenced.
Deterministic value-add checks suppress a second block that repeats the same
target, action, or substantive text.

`team_to_confirm` is not a successful route to final output. An admitted
candidate must have a verified existing destination or a safe stage-appropriate
standard document destination presented as an advisory proposal. If neither
exists, actionability or timing fails.

## 5. Bounded Operational-Guidance Registry

Create a small, versioned registry derived only from guidance already reviewed
and represented in the repository. Do not ingest the external raw OPCS/ESF
corpus.

Each entry contains a stable ID, title, applicable documents and stages,
permitted targets, concise application rule, authority class, and prohibited
overstatements. Initial coverage is limited to demonstrated workflow needs:

- PCN/PAD design and implementation arrangements;
- Results Framework indicators, targets, and measurement;
- concept-stage risk/SORT treatment without prescribing a rating;
- adaptive management and decision triggers;
- ESMF/ESCP treatment when instrument and scope are evidenced;
- FCV operational continuity and access arrangements; and
- reviewer-judgment language for advisory improvements.

The registry must not invent policy paragraph numbers or convert good practice
into a mandatory requirement.

## 6. Later OPCS/ESF Conformance Review

After this implementation is complete, the maintainer may run a separate,
paid Cowork exercise in the WBG LLM environment for a specific material
OPCS/ESF ambiguity. This is deliberately deferred because Cowork is expensive.
It is not an automatic product stage and is not needed for ordinary rendering.

Suitable questions include whether a destination fits the instrument and
stage, whether wording overstates a requirement, whether text belongs in an
ESCP/ESMF/PAD section, or whether a timing or authority claim is accurate.

The implementation handoff should provide a concise Cowork review plan listing
only selected guidance propositions, relevant code locations, and targeted
conformance questions. The repository receives a bounded reviewed summary or
correction, not raw restricted sources. Accepted corrections are versioned in
the registry and covered by tests.

## 7. Deterministic Safety and Validation

### Authority and register

- Mandatory language such as `must`, `shall`, and `required` is prohibited
  unless a verified authority basis supports it.
- Existing commitments and advisory proposals are labelled distinctly.
- Proposed text may describe what the project would do but cannot be labelled
  as already agreed.

### Instruments, actors, timing, and precision

- Named standalone instruments must resolve to uploaded-project facts.
- Named actors/functions must resolve to evidence; compound inventions such as
  a new focal point inside an evidenced plan still fail.
- "Before effectiveness," "before appraisal," and fixed deadlines require an
  explicit project or authoritative timing basis.
- Stage-aware drafting may identify a preparation destination but cannot turn
  it into a legal or procedural condition.
- Numeric tokens, place names, institutions, technical systems, and thresholds
  must resolve to facts, admitted evidence, or a declared derivation.
- Validation reports the exact field, token, and unresolved reference rather
  than silently rewriting unsupported precision.

## 8. Judgment Evidence Integrity

All four judgments require non-empty evidence references appropriate to their
claims: project IDs for operation facts; pathway, response, or residual-gap IDs
for analysis; and country-bank or accepted live-research IDs for context.

Deterministic validation emits `JUDGMENT_EVIDENCE_MISSING` for missing or
unresolved references. A judgment with that issue is not fully verified.

## 9. Executive and Recommendation Coherence

The judgment executive must not pre-announce how many issues pass a later
admission threshold. It summarizes the four judgments without asserting the
final recommendation count. The reader then adds a deterministic priority
summary derived from admitted recommendations. This removes count
contradictions without another model call.

## 10. Readiness-Flag Boundaries

Each readiness flag references its residual-gap or topic ID. Suppress a flag
when it overlaps an admitted recommendation's residual-gap/topic basis. Retain
it only when it represents a distinct preparation uncertainty or missing input
that cannot support a fully actionable recommendation.

## 11. Live-Research Provenance

- `live_research_count` equals distinct accepted live claims.
- Every accepted live claim resolves to a declared source.
- Every `CE-LIVE-*` reference resolves to an accepted claim.
- Reject or split a composite claim when any material component is unsupported.
- Preserve partial-status limitations in the provenance annex.

This corrects accounting only; it does not broaden search budgets or replace
the reviewed South Sudan country bank.

## 12. Rendering and Export Parity

The shared rendering model supplies the browser, HTML, and DOCX with the same
recommendation, required current-document draft, justified optional second
draft, targets, status, guidance basis, readiness flags, and preview label.
Drafts must not be truncated. Visual redesign is out of scope.

## 13. South Sudan Acceptance Scenarios

### BFMU operational continuity

- Current document: PCN Project Description and/or concept-stage risk treatment.
- Optional second block: evidenced Security Risk Management Plan, if distinct.
- Reject an invented plan focal point and unsupported "before effectiveness."

### Adaptive operating triggers

- Current document: PCN Project Description and Concept Note Risk section.
- Optional second block: evidenced ESMF, only when scope supports the text.
- Preserve existing mitigation and draft only the residual improvement.

### Habitat-restoration measurement

- Current document: Preliminary Results Framework target and methodology.
- Use a Results Framework monitoring provision or evidenced instrument.
- Reject an invented POM or hydrometeorological system.

### Coherence and provenance

- Final priority count matches the deterministic final summary.
- All four judgments have valid evidence IDs.
- No readiness flag duplicates an admitted priority.
- Accepted live claims and manifest counts agree.
- HTML and DOCX contain the full required draft, any justified second draft,
  and the preview label.

## 14. Test and Deployment Sequence

Implementation follows test-driven development:

1. Add failing schema/validator tests for the required current-document block
   and conditional operational-instrument block.
2. Add failing regressions for unsupported instrument, actor, timing, and
   precision claims.
3. Add failing judgment-evidence, executive-coherence, readiness-deduplication,
   and research-manifest tests.
4. Implement the smallest changes that make those tests pass.
5. Add reader and HTML/DOCX parity tests, then run the relevant full suite.
6. Deploy only to `fcv-agent-1.onrender.com` in smoke mode.
7. Rerun the South Sudan Express workflow and inspect saved textual output.
8. Update the user immediately before a single paid quality run.
9. Save the full quality note as local Markdown/text, assess it against the
   Example B/C standard, and return the testing service to smoke.

## 15. Out of Scope

- lowering the recommendation threshold;
- changing country-bank generation without causal evidence;
- reading or embedding restricted raw OPCS/ESF sources;
- an automatic Cowork/WBG-LLM call;
- changing `fcv-agent.onrender.com`;
- a visual redesign; and
- a separate paid drafting-model stage.

