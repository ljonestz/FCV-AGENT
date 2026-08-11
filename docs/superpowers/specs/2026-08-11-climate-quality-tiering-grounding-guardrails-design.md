# Climate Quality Tiering and Grounding Guardrails Design

**Date:** 2026-08-11

**Branch:** `feat/climate-country-bank`
**Status:** Approved design boundary; implementation pending

## 1. Problem

A post-deployment smoke run and quality run confirmed that deterministic
project-profile bank selection is working, but exposed three downstream quality
failures in the verified Climate-FCV recommendation path:

1. Document-completion defects can appear both as ranked operational priorities
   and as document checks.
2. Country-context evidence can be promoted into a site-specific project
   obligation without a project fact confirming that the condition applies at
   the named site.
3. Unsupported numeric cleanup can delete a sub-component number while leaving
   malformed surrounding prose such as `under Sub-component`.

The first failure contradicts the reader's one-finding-one-tier design. The
second exceeds the evidence entitlement of country context, which may support a
contextual pathway or materiality question but not establish a site-specific
project fact. The third preserves numeric safety at the cost of reader integrity.

## 2. Goals

- Keep source-linked document defects in the document-check tier unless a
  recommendation has an independent material design-gap basis.
- Permit country context to trigger a project question or conditional
  verification action, but not a new site-specific instrument, agreement,
  protocol, actor, or commitment without confirming project evidence.
- Preserve supported numeric document labels and replace unsupported labels
  with grammatical neutral wording.
- Make every deterministic suppression observable through bounded, content-free
  reason codes.
- Preserve all current rating, recommendation-cap, bank-selection, reader,
  provenance, and context-budget contracts.

## 3. Non-goals

- No country-bank content, literature, release, or approval change.
- No new model call, search, semantic reviewer, or human-review step.
- No redesign of the four judgments, reader hierarchy, or priority scoring.
- No change to the five-priority cap, 6,000-character bank ceiling,
  12,000-character combined ceiling, or six-live-claim limit.
- No generic FCV workflow change.
- No attempt to infer whether a contextual condition is true from lexical
  similarity alone.

## 4. Root causes

### 4.1 Cross-tier duplication

Fact extraction produces source-block-linked `document_integrity_findings`.
Recommendation compilation currently receives facts, analysis, judgments, and
operational guidance, but not those integrity findings. Priorities are admitted
and ranked before integrity findings are converted to readiness flags and merged
into the reader. Model readiness flags are deduplicated against admitted gap IDs;
fact-stage integrity flags have their residual-gap IDs cleared and therefore
cannot use that guard.

### 4.2 Context promotion

The evidence-entitlement table limits country evidence to contextual pathways
and materiality questions. The analysis validator checks ID validity but does
not deterministically require a project-evidence basis before a contextual
pathway becomes a site-specific project obligation. Prompt guidance alone did
not prevent the quality run from requiring a new herder-fisher project
instrument at named Sudd sites.

### 4.3 Label loss

Drafting generation is instructed not to add digits. The precision normalizer
then removes unsupported numeric tokens individually. When a model nevertheless
returns `Sub-component 1.4`, deleting only `1.4` leaves malformed prose. The
normalizer needs a phrase-aware repair before generic token deletion.

## 5. Design

### 5.1 Reserve document checks before recommendation generation

Validate fact-stage integrity findings immediately after fact normalization and
project them into a bounded `reserved_document_checks` input for recommendation
compilation. Each record contains only its stable finding ID, controlled
category, short flag, source-block IDs, and verification text.

The recommendation prompt must state that these records already own the
document-check tier. A recommendation candidate must not merely restate or
operationalize one of them. A candidate may survive only when it cites an
independent residual design gap and its action addresses more than completing,
cleaning, populating, or reconciling the document defect.

The drafting compiler receives the same bounded reservation so it does not turn
a reserved check into recommendation drafting.

### 5.2 Deterministic cross-tier guard

Prompt prevention is backed by a conservative admission guard. Build a mapping
from each validated integrity finding's source-block IDs to normalized project
facts from those blocks. A candidate is classified as `document-check-only`
when all of the following hold:

- its residual gaps are `not_yet_specified` or `contradictory`;
- its linked project facts originate only from source blocks covered by a
  validated integrity finding;
- its action is limited to document completion, placeholder population,
  reconciliation, deletion, or cross-reference repair; and
- it has no independently supported `confirmed_omission` or `partial_response`
  gap tied to a climate-FCV pathway.

Such a candidate is excluded before ranking. The integrity finding remains in
the document-check tier. Suppression emits
`ADMISSION_DUPLICATES_DOCUMENT_CHECK` without candidate prose.

The guard deliberately requires structural evidence as well as controlled
action classification. Text similarity alone cannot suppress a priority.

### 5.3 Context-to-project promotion guard

Recommendation compilation must distinguish three cases:

1. **Confirmed project condition:** a linked project fact explicitly establishes
   the site, group, actor, exposure, or existing arrangement. A proportionate
   project action may be recommended.
2. **Project fact plus contextual pathway:** project facts establish the relevant
   project feature or exposure and country evidence explains the mechanism. A
   recommendation may address the evidenced project design gap.
3. **Context only:** country evidence raises a plausible condition, but no
   project fact establishes it at the site. The only admissible action is to
   assess, verify, or confirm applicability before deciding a response.

A context-only candidate that mandates a new instrument, agreement, protocol,
actor, system, or commitment is suppressed with
`RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED`. It may be regenerated only as a
conditional verification action in a later run; deterministic code must not
rewrite it into a different substantive recommendation.

The conditional semantic-review prompt will repeat this boundary so a reviewer
cannot approve a site-specific obligation supported only by country context.

### 5.4 Phrase-aware numeric-label handling

Before generic unsupported-number removal, drafting normalization detects
document-label phrases whose number is unsupported, including `Component`,
`Sub-component`, `Section`, `Annex`, and `Year` labels.

- If the exact numeric token occurs in a linked project fact, preserve the full
  label.
- Otherwise replace the whole label with grammatical neutral wording, for
  example `the relevant sub-component`, `the relevant section`, or `during the
  relevant preparation year`.
- Never leave a bare label followed by punctuation or a missing object.

The drafting prompt also instructs the model to use neutral labels unless an
exact label is supplied in linked facts. This prevents most repair from being
needed while retaining deterministic safety.

### 5.5 Diagnostics and compatibility

Add the two bounded reason codes to existing recommendation diagnostics and
candidate-suppression records. Do not log candidate text, source excerpts, or
model reasoning. No public assessment schema field is added; the reason-code
arrays are already additive and bounded.

Advance only the prompt versions whose text changes. Preserve saved-reader and
verified-v2.1 compatibility.

## 6. Data flow

1. Extract and normalize project facts and integrity findings.
2. Validate integrity findings against real source-block IDs.
3. Pass bounded reserved document checks into recommendation compilation.
4. Validate and normalize recommendation candidates as today.
5. Apply the document-check-only and context-promotion guards.
6. Rank the remaining candidates.
7. Merge integrity findings into readiness flags, retaining the existing cap.
8. Generate the canonical reader without changing its section structure.

## 7. Testing strategy

Strict TDD will cover the observed failures before production changes:

- a placeholder-target recommendation linked only to the same integrity source
  blocks is rejected while its document check remains;
- an unfinished risk-section recommendation is rejected for the same reason;
- an independent climate-FCV design gap sharing a source block is retained;
- country context without a confirming project fact cannot mandate a new
  site-specific agreement or protocol;
- a conditional applicability assessment remains admissible;
- a context-supported pathway plus an explicit project fact can still support a
  proportionate recommendation;
- supported `Sub-component 1.4` is preserved;
- unsupported `Sub-component 1.4` becomes `the relevant sub-component`, not
  `Sub-component` with a missing number;
- diagnostics contain only the new reason codes and bounded IDs;
- existing priority caps, reader ordering, rating semantics, and bank/context
  limits remain unchanged.

Focused recommendation, pipeline, prompt, runtime, and render suites will run
before the full tracked suite. A fresh external pytest basetemp will be used for
the known Windows ACL issue.

## 8. Acceptance and deployment

The patch is acceptable when:

- all focused and full local tests pass;
- no production file outside the verified Climate recommendation path changes;
- the smoke deployment completes without reader-integrity failure;
- a quality run no longer duplicates document checks as priorities;
- contextual conditions remain conditional until project evidence confirms
  site applicability; and
- document labels are either fully preserved or grammatically generalized.

No merge to `main` occurs in this increment. Push and smoke deployment require
the existing explicit user authorization boundary.
