# Proposition diagnostic result: defect gate passes, strict score fails

One authorized synthetic diagnostic call completed on 2026-10-16. This supersedes
the UNSENT status in the preflight for this experiment only. Authorization is
consumed; no retry, follow-on call, real-case replay, deployment or publication
is authorized by this result. `publication_approved` remains `false`.

## Method and result

The frozen request supplied 24 manually enumerated propositions across 12 synthetic
cases with case-specific sources. Expected labels and contrast pairing were withheld.
The response checksum and request bindings were verified, the shallow envelope was
decoded, and each judgment passed local schema, coverage and evidence-quote checks.
The unchanged defect harness and frozen exact labels were then scored offline.

| Check | Result |
| --- | --- |
| Coverage | 24/24 |
| Planted defects detected | 6/6 |
| False positives | 0 (18 nondefects preserved) |
| Role agreement | 24/24 |
| Verdict agreement | 23/24 |
| Defect score passed | true |
| Strict diagnostic passed | false |

The only label mismatch is C11-P02, "the project should offer transport grants".
Both model and gold classify it as `proposed_action` and not a defect. The model
returns `supported`; the frozen verdict is `not_established`. Its explanation
explicitly recognizes that no grant is approved and treats the source's possible
design change and documented transport barrier as support for the recommendation.
This suggests a verdict-semantics ambiguity for recommendations, not a missed
factual defect. That interpretation does not override the frozen acceptance rule:
the strict score remains false and no labels or scoring rules were changed.

## Evidence reasoning review

All 24 returned explanations were read against the supplied synthetic sources.
The six defect explanations address their own propositions rather than borrowing
support from neighbouring clauses:

- C02-P02: operational border posts contradict planned, not-yet-operational posts.
- C04-P03: general instruments and a recognized risk do not establish a documented
  exclusion-specific safeguard; the explanation avoids claiming none exists elsewhere.
- C06-P02: an existing grievance channel does not establish elimination of exclusion.
- C08-P02: retained-site continuity does not establish universal loss of access for
  traders near cancelled sites.
- C10-P01: 92 percent supports "most", but contradicts "all".
- C12-P02: no approved grant and only a possible design change contradict current
  provision of transport grants in this synthetic case.

The supported neighbouring propositions remain intact. Unknown effectiveness does
not erase the grievance provision. The recommendation and qualified access-risk
inference remain nondefects. However, C07-P02's explanation says that being hedged
makes it a nondefect. That is too broad as a general rule: a hedge cannot protect
an inference with a contradicted premise or no defensible evidential basis. This
fixture does not test those harder cases, so it cannot validate that generalization.

This review is recorded separately from the machine result. The scorer's
`reasoning_review_required: true` flag and raw output remain unchanged.

## Execution and artifacts

Experiment: `proposition-diagnostic-v1-81d367bb6c2a4a58`.
One Render-shell call using `claude-sonnet-5-5`, adaptive/high, 16,384 output-token
cap, 300-second timeout and zero retries. The exclusive lock was absent before
submission. Response ended with `end_turn` in 45.470 seconds. Usage: 5,248 input
and 5,591 output tokens, including 1,183 thinking tokens; no cache tokens.

Response SHA256:
`d4e007e3ed3975e3612dd7081b26183a69c2c1a63e5aa04c252b8219bcbc3f2a`.
Prompt SHA256:
`7964c34cc8d7159a374d347ffb69c5178b10f8ce4d9890c3afabfb8a00d655a4`.
Request SHA256:
`d30733f7cfc5def603f2b2a78bb11d7eb1554b88cfdbb8716e3c235f2da38e01`.

Local, uncommitted artifacts under `output/20261016-proposition-diagnostic-v1/`:
`authorization.txt`, `submission.txt`, `terminal.txt`, `response_blob.txt`,
`response.json`, and `result.json`, alongside the frozen request/preflight files.
Repeated terminal accessibility text was deduplicated to one distinct checksum-valid
response for this experiment. Offline scoring completed with exit 0; this indicates
successful decoding/scoring, not a passing diagnostic.

## Interpretation and next decision

This is encouraging evidence that proposition-level review can distinguish the
six simple synthetic contrasts. It does not establish real-case reliability,
automated proposition enumeration, repeatability, or causal improvement over the
previous sentence-level run: the inputs and task difficulty differ.

Before another experiment, clarify the intended verdict semantics for proposed
actions prospectively and add harder qualified-inference cases offline. Preserve
this frozen result. A separately approved real-case replay would then be needed
to test the two original missed defects. No further provider call was made.
