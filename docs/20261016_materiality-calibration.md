# Materiality calibration and next offline acceptance cases

The user clarified on 2026-10-16 that occasional minor LLM errors are acceptable;
the priority is catching major errors that could have substantial consequences if
followed. This is a prospective acceptance clarification. Historical gold labels,
raw responses and strict scores remain unchanged.

## Practical acceptance rule

Treat an error as consequential when correcting it could plausibly change the
recommended action, its priority, the target population/site, the claimed funding
available, the delivery status or a judgment that adequate protection already
exists. Record the concrete decision consequence rather than relying on a severity
label alone. A minor discrepancy changes wording or internal categorization without
changing those decisions or the substantive evidence meaning.

The latest synthetic result is therefore sufficient to continue investigation:
all six planted defects were detected, all protected cases were retained, and the
single recommendation-verdict mismatch is minor under the user's clarified goal.
Its historical strict `passed=false` remains correct. This is not a production pass.

For future evaluations, report consequential detection and preservation separately
from exact-label agreement. Require all preidentified major defects in the bounded
check to be detected, with source-grounded explanations, and no consequential false
rejections of valid analysis. Minor label differences are recorded, not release
blockers by themselves. This is not a claim of zero future errors or a statistical
reliability estimate. Incomplete/malformed review still means incomplete evaluation.

## Recommendations and qualified inference

Keep role, source support and decision handling distinct. A proposed action need
not already be an approved commitment. Calling a grounded proposal `supported`
instead of `not_established` can be minor if the explanation accurately states what
exists and what is proposed. Do not interpret either label alone as action approval.

A false factual premise must be flagged separately and must hold its dependent
recommendation for review. Merely detecting the premise while leaving the dependent
action approved fails the practical gate. Likewise, `may` cannot rescue a possibility
explicitly excluded by evidence. A plausible qualified concern about an unassessed
population remains admissible; uncertainty alone is not a factual defect.

Do not implement a blanket rule that all recommendations or hedged claims are safe.
Source support for a premise also does not establish effectiveness or suitability of
a proposed intervention. Ambiguous consequential judgments should go to supervised
review rather than be automatically edited or certified.

## New frozen offline cases

Location: `tests/fixtures/climate/20261016_materiality_review/`.
Six synthetic cases, ten manually identified propositions, three major defects and
seven nondefects. `reviewer_inputs.json` contains only inputs; `expected.json`
contains labels, reasons and decision consequences; `manifest.json` freezes hashes.

| Cases | Contrast | Required decision |
| --- | --- | --- |
| M01 / M02 | Unbuilt bridge supports access concern; invented operational bridge underpins withdrawal of temporary access | Preserve concern; flag false status and hold dependent withdrawal advice |
| M03 / M04 | Propose confidential complaints; assume general channel already prevents retaliation | Preserve proposal; flag unsupported protection and hold conclusion that measures may be unnecessary |
| M05 / M06 | Access unassessed; alternative route explicitly excluded | Preserve qualified concern; flag contradicted possibility despite its hedge |

M05/M06 deliberately use different source conditions; this is an evidence-boundary
test, not a controlled same-source experiment. For M02/M04, the recommendation or
inference is not independently counted as another defect: the false premise is
counted once, with the parent case explicitly blocked. M06 directly tests a
contradicted conditional inference. These expectations are manual, not model results.

Offline checks passed for unique IDs, exact parent spans, complete gold coverage,
counts and separation of gold fields from reviewer inputs. These checks validate
fixture construction only. No model call or runtime modification was made.

## Next execution work

Prepare a bounded replay of the original real-case reader with human-checked
proposition inventory and original defect/decoy labels preserved. Add these harder
cases as a separately reported calibration section so synthetic success cannot
mask real-case misses. Freeze the consequential decisions before submission.

The existing synthetic scorer has a fixed 24-proposition inventory and strict
role/verdict equality. Do not silently feed this new set into it or change its
historical pass calculation. The next adapter must report the new practical gate
separately, check parent-case handling, and retain exact-label diagnostics. Test
that detecting a bad premise but accepting its dependent recommendation fails.
Use the existing shallow transport and validators where compatible; no production
prompt, shared schema, automatic editor or deployment changes are part of this work.

A future real-case result must report the original two known defects separately,
new material findings with source review, valid analyses preserved, and minor issues.
Publication remains false. The prior one-call authorization is consumed; this
turn completed the authorized offline calibration and fixture preparation only.
