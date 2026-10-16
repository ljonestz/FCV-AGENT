# Proposition-level review: bounded offline design and frozen contrast set

Status: design and synthetic fixtures only. No live calls, runtime integration,
new execution command, automatic editor or release approval.

## Change the review unit

The last complete 30-sentence review missed both frozen defects. In each case,
evidence for some clauses was accepted as evidence for the whole sentence.
Keep the parent sentence for context, but judge each independently checkable
proposition separately. A sentence containing three propositions needs three
judgments; one supported neighbour cannot clear another proposition.

For this diagnostic, decomposition is manually curated before model review.
It is not regex clause splitting and does not depend on the reviewing model
certifying its own coverage. Automated decomposition is out of scope: first test
whether the model can judge correctly when given an adequate inventory.

Each proposition carries a stable ID, parent sentence ID and an exact character
span. Preserve subject, population, tense, modality, negation and qualifiers.
Split a conjunction only when its parts can independently be supported or false.
If a span needs inherited context, retain the full parent sentence; do not silently
rewrite the assertion or strip words such as may, planned, should or unknown.

## Review contract

Return exactly one judgment per supplied proposition: role, verdict, defect flag,
source quotes and a concise explanation of what those quotes establish for that
specific proposition. For factual assertions, identify the subject/population,
claimed action or relationship, and timing/certainty. Compare those elements
with the source; evidence matching only a neighbouring proposition is insufficient.

Supported factual assertions need evidence for all material parts. Missing support
means not_established; explicit incompatible evidence means contradicted. Neither
word overlap nor the presence of an instrument proves the claimed relationship or
effectiveness. Preserve conditional inference and proposed action unless they
embed a defective factual premise. Such a premise must be separately inventoried.

The existing harness can validate exact spans, sources, roles, coverage and
defect consistency against a manually prepared proposition inventory. It cannot
verify entailment. The frozen per-proposition labels and human source review are
the semantic gate. Any future live transport can reuse the working shallow
envelope, but no new request is prepared or authorized here.

## Frozen synthetic contrast set

Location: `tests/fixtures/climate/20261016_proposition_review/`.

- reviewer_inputs.json: 12 cases, six pairs, 24 exact-span propositions, synthetic
  sources only. No verdicts, expected defect IDs or pair metadata.
- expected.json: separate gold judgments, reasons, evidence and pair mapping.
  Six defective propositions and 18 non-defects. Never send this file to a reviewer.
- manifest.json: byte hashes, counts and pre-model freeze status.

| Pair | Distinction | Required behaviour |
|---|---|---|
| C01/C02 | Planned construction vs already operational | Reject the delivered-status overstatement only |
| C03/C04 | Exclusion risk vs exclusion-specific safeguard | Preserve the centre/indicator clauses; reject unsupported specificity |
| C05/C06 | Existing grievance channel vs proven outcomes | Credit the measure despite unknown effectiveness; reject claimed elimination |
| C07/C08 | Qualified access concern vs universal realised loss | Preserve the concern; reject an unsupported factual loss claim |
| C09/C10 | Most vs all when the source says 92 percent | Accept the weaker paraphrase; reject the universal claim |
| C11/C12 | Proposed grants vs existing commitment | Preserve the recommendation; reject the asserted provision |

All fixtures are explicitly synthetic. They deliberately make distinctions clear;
passing them would not establish performance on ambiguous real documents. Display
order is fixed and separates pair members. Historical real-case inputs and expected
labels are untouched; these fixtures do not replace or relabel that failed test.

## Offline checks and acceptance gates

Verify unique IDs, exact parent spans, no overlapping proposition spans, complete
coverage of the synthetic clauses, exact gold source quotes, complete gold coverage,
pair membership and frozen file hashes. Check gold/input separation recursively.

Exercise the unchanged harness with a clearly labelled synthetic oracle: all 24
judgments must validate and score correctly; missing/duplicate judgments must fail;
an all-supported response must miss all six known defects. This demonstrates
mechanics only. No simulated result may be reported as model detection success.

Executed offline on 2026-10-16: all checks above passed. The curated oracle scored
passed=True; missing and duplicate judgments raised contract errors; the all-
supported response scored passed=False with six missed defects. No model was
called, and no production code or previous real-case fixture was changed.

A later diagnostic model test must cover all 24 propositions and detect exactly
the six gold defects while preserving all 18 non-defects. Report role/verdict
agreement separately from defect precision/recall. Require expected roles and
verdicts as well as exact defect decisions for this diagnostic acceptance; do not
let a factual premise escape by being relabelled as an inference. Review the
actual evidence reasoning; valid substrings alone are insufficient. Missing,
malformed or duplicate judgments cannot pass. Stop after any authorized call;
do not change labels or retry until it passes.

If the simple contrast diagnostic passes, a separately approved next gate is
proposition-level review of the original real case with human-checked decomposition
and its existing defect/decoy labels preserved. If it fails, stop autonomous
acceptance work and discuss a supervised factual-review workflow. No such product
change is approved by this design. publication_approved remains false throughout.
