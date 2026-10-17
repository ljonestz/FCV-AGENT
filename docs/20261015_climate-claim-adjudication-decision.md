# Climate claim detection: diagnosis and the smallest credible change

## Diagnosis: a recall collapse, not an evidence or transport failure

The paid experiment's detection call returned an empty findings list for all five
records and missed both known factual defects. The saved artifacts locate the
mechanism precisely, and it is not what a prompt patch would fix.

- The evidence was present. The 34 source passages contain the contradicting facts
  (for example "designed to create climate-resilient standards" and "redesign and
  construction" against "the immediate benefit is... flood-ready border posts").
- The same evidence supported correct judgement. The second call, on the same
  source registry, reasoned correctly that the benefit is "planned... which describe
  redesign and construction." So the model can judge the exact defective claim when
  it is presented to it.
- The earlier full-context reviewer (039a112) found both of these exact defects
  before the conservative claim-level reframing. Its recall was adequate; it failed
  on precision (a false access objection) and the admission contract.

Put together: the model is reliable when a candidate claim is presented for
judgement and unreliable when asked to volunteer defects from the whole reader. The
claim-level redesign fused detection and precision control into one conservative,
per-finding-structured "which claims are defective?" prompt. For that prompt the
empty set satisfies every guardrail perfectly, so it is the cheapest compliant
answer. Earlier prompts swung the other way into over-flagging. One prompt cannot be
both high-recall and high-precision, and every attempt so far has lost one or the
other.

## The smallest credible change: enumerate, then adjudicate per claim

Stop asking the model to volunteer defects. Route all model work through the mode it
demonstrably performs, per-claim adjudication.

1. Enumerate the reader's atomic claims (sentence level) deterministically. This is
   a decomposition, not a judgement, so there is no empty-set escape hatch.
2. Adjudicate each enumerated claim individually: role, verdict
   (supported / contradicted / not_established) and, when defective, a narrow edit
   span with an exact source quote. The existing "preserve qualified inference,
   credit general provisions, faithful paraphrase is acceptable" guardrails live
   only in this judgement step.
3. The adjudication emits the existing `review` structure and feeds the already
   validated clause-level repair and independent re-review pipeline unchanged.

### Why this changes the failure mechanism

Prior explicit-premise prompting still asked one conservative pass to self-select
issues, so it inherited the same recall-hostile framing. This instead presents every
claim for the judgement the model already does reliably, and the contract enforces
that a contradicted or not-established factual assertion cannot be silently left
unflagged (`adjudicate_claims` raises if a factual assertion judged contradicted is
marked non-defective). Detection recall becomes a coverage property the harness can
check, not a behaviour we hope a prompt elicits.

## Offline work done and falsifiable acceptance criteria

No paid call, deployment, app-code change or merge. Added on the branch:

- `scripts/climate_claim_adjudication_harness.py`: `enumerate_claims`,
  `adjudicate_claims`, `score_against_expected`. Reuses the prototype's validated
  primitives (exact unique quotes, real source ids, full coverage).
- `tests/test_climate_claim_adjudication_harness.py`: 11 tests, written first and
  watched fail, covering enumeration determinism, full-coverage enforcement, the
  factual-assertion recall rule, defect evidence requirements, preservation of valid
  qualified inference, downstream pipeline compatibility, and the scoring of true
  defects versus false positives.

Falsifiable acceptance (frozen before any model test): a per-claim adjudication is
accepted only if it (a) flags both true defects with a non-supported verdict and a
source quote, and (b) raises zero false positives against the protected claims
(faithful paraphrase, the valid access question, a valid qualified inference). The
real Great Lakes target is frozen, uncommitted, under
`output/20261015-claim-adjudication-realcase/` (30 enumerated claims, 5 records, 34
sources, 2 true defects, 3 protected claims). A simulated "all supported" review,
reproducing the paid failure, scores `passed=False` with both defects missed.

## Open decision before any paid run: close the soft escape hatch

The harness forces every factual assertion to be judged, but a model can still mark
every claim "supported" with empty support evidence and pass the structural
contract (it fails the frozen score, which is the point of the offline gate, but in
production there is no frozen score). The symmetric tightening is to require an exact
entailing source quote for every factual assertion marked supported, converting
"stay silent" into "quote the source that entails this claim." That is the same
traceability the model did well in call 2.

This is a real design choice, not a silent default: requiring support quotes raises
output-token cost and, if over-applied, could reintroduce suppression. It should be
decided (and, if adopted, tested offline on the frozen target) before a single
bounded paid run is prepared for approval.

## Human review and what remains

A near-term supervised pilot should keep a human factual-review gate. The model's
reliable capability (adjudicating presented claims) is usable; complete autonomous
discovery is not demonstrated from one sample, and enumeration recall (did we list
every claim?) is itself unproven and cannot be model-self-certified. Exact quotes
prove traceability, not entailment or inventory completeness. This is a
recommendation only; the human-review product change is not approved.

Still unaccepted before any production release: the per-claim detection behaviour on
a real bounded run, automatic editor behaviour, core recommendation review,
end-to-end cost and latency, UI, and HTML/DOCX exports. `publication_approved`
remains false everywhere. This document is a design decision, not an acceptance
certificate.

See [results](20261015_climate-claim-model-results.md),
[repair design](20261015_climate-claim-repair-design.md) and
[source-scope failure](20261015_climate-source-scope-review-results.md).
