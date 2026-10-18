# Targeted verification notes and fuller core answers

The user approved retaining useful prose with specific verification notes after
bounded correction, across the opening, core answers and recommendations. This
change is offline-tested application work, not a new paid acceptance run. The
856f583 bank-pilot acceptance artifacts and deployed services remain unchanged.

## Behaviour

Reviews now distinguish verify, omit_sentence and withhold. A precise unresolved
claim can stay with a nearby "Verify before sharing" instruction. A clearly defective
sentence can be removed only when the reviewer identifies the exact whole sentence
and judges the remaining argument independently useful. Ambiguous/repeated anchors,
empty remainders and invalid dispositions cannot unlock text. Whole-argument defects
retain the existing withholding path. Block, malformed reviews, missing evidence
and unknown IDs still fail closed. Older reviews without the new fields keep their
previous behaviour; they are not silently reclassified.

The existing single correction and independent re-review remain. Recommendation
retention requires a structurally valid second review, valid source-block/core
records and an exact quote. Unresolved core recommendations are excluded from the
final reader's accepted-action inputs and support registry. Suggested drafting has
the same handling, without weakening the independently accepted parent decision.
Raw text, issue records and revise status stay in the audit assessment. Display
notes/removals are deterministic projections, shared by browser, HTML and Word.
Notes are visible in recommendation action prose, not hidden in a disclosure.
Packet binding detects removal of a note; publication_approved remains false.

Core answers now target 180-240 words in two or three connected paragraphs where
supported. The 400-word hard ceiling stays. Generation, correction, schema,
normalization and renderer agree on paragraph count. No padding is required when
source material is sparse. Correction guidance checks asset scope and planned versus
ongoing status as well as the original objection.

Versions: conditional review v2.24; final reader v1.13; reader correction v1.8;
reader review v1.15; admission v2.6; renderer v2.27. Recommendation generation v2.24
and normal-FCV analytical behaviour are unchanged. No extra model-call loop added.

## Verification and preview

Focused connected suite: 247 passed before final boundary hardening; 24 targeted
schema/invalid-input checks passed after it. The first full suite had 1,862 passes
and one stale schema assertion, now updated. Final full suite: 1,866 passed in 284.30 seconds; see the untracked
20261018_verification-notes-final-tests.txt log. Four
previously hanging Chromium-driver tests remain explicitly excluded.

The saved-case display illustration is
output/20261016-ipf-pilot-live-preflight/20261018_verification-notes-preview.html
(and .docx/.pdf). It explicitly annotates the historical review with proposed display
dispositions. It is not fresh model output, an independent model pass or a replacement
approval packet. It retains the saved answer lengths; the longer target affects
future generation. The first answer and its note were inspected in Edge and the rendered Word PDF
(page 2 of 12 nonempty pages). All preview
artifacts stay outside Git. A single-file loopback server was used; unrelated routes
return404. Initial directory-wide serving was rejected by automatic approval review
and was never started.

Human source review remains required. The model may choose an incorrect disposition
or miss an error; offline tests verify application behaviour, not future semantic
accuracy. No further paid call, merge or deployment is authorized by this change.
