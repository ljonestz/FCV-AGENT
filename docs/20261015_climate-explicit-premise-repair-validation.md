# Explicit premise review and bounded recovery

## Purpose

The full-context reviewer saw a financing-scope conflict in optional drafting but
still accepted the recommendation containing it. Prompt-only calibration and added
context did not resolve this. The user approved an explicit factual-premise repair,
with a requirement to preserve analytical freedom, and suggested correcting detected
problems within the app rather than broadly rejecting assessments.

## Contract

The existing core reviewer now supplies one source-linked core_reviews record per
recommendation. It separates supported facts, explicitly qualified analysis, and
unsupported premises. The application reconciles those findings with passed_core_ids;
a complete unsupported premise cannot remain accepted merely because its optional
draft was the only target in the old issue list. Valid unrelated recommendations
remain eligible. Missing or malformed evidence decisions do not license invented
corrections or automatic acceptance.

Qualified causal mechanisms, uncertainty and useful proposed actions remain allowed.
The source need not contain the inference verbatim or show the proposed action already
exists. Proportionality and scope still matter: a proposal cannot depend on an invented
relationship between sites, activities, beneficiaries or financing envelopes. A sound
premise does not automatically certify every other aspect of the recommendation.

Reader objections must quote a unique exact span from the current final_reader record.
On correction re-review, correction_originals supplies comparison context only: removed
wording cannot be treated as a remaining defect. The reviewer must explain the meaning
actually asserted and the source difference, without strengthening conditional language
or distributing a modifier across separate list items. Badly anchored objections do not
spend the correction call and do not become automatic passes.

The existing single bounded correction and fresh review remain the recovery path.
Correction cannot expand evidence, inflate ranking or rewrite untouched reader text.
The reader still requires a clean whole-bundle meaning review before publication;
failure retains the verified Detailed fallback. This change does not implement partial
reader publication or a retry-until-pass loop.

## Limits and cost

No additional provider calls, retries, model changes, deployment or spending allowance
are introduced. Review output has additional evidence fields under the same output cap.
A newly eligible correction may use the existing bounded allowance where the previous
implementation stopped early; unchanged maximum budgets do not mean identical actual
usage. Input-token constants remain unenforced and are not monetary caps.

Known source IDs and exact quotations establish provenance and targeting, not semantic
truth. The application cannot detect a model that incorrectly labels a false premise
supported, or quotes accurately but misinterprets meaning. Offline tests verify contract
and recovery behavior. Fresh model performance and production acceptance remain unproven;
no saved failed assessment is relabelled successful.

Versions: core review2.18, reader review1.8, normalization2.10; renderer2.19 unchanged.
Stored successful assessments are not automatically re-reviewed. New model responses
must supply the new fields; legacy responses are not silently upgraded to acceptance.

## Verification record

Schema and prompt regressions were observed failing before the native contract change.
The offline calibration evaluator was observed failing against valid new-contract fake
responses before it was updated. All provider responses used by software tests are
synthetic, and expected labels remain outside model inputs.

- Full offline suite: **1,661 passed in 1,453.27 seconds**, exit 0. All 170
  checked Python/fixture hashes stayed unchanged throughout the run. Existing browser
  layout checks were slow but passed. Submodules were initialized before testing.
- Focused pipeline verification: 129 passed. Connected schema/calibration/context/
  completeness/admission checks: 49 passed. These overlap and are not summed.
- Regression tests reproduced malformed draft re-review restoring rejected text and
  targetless negative reviews admitting cores; both now withhold the affected output.
  Malformed draft review preserves the independently accepted parent.
- Independent review checked issue targeting, suppression accounting and overlapping
  quote matches. Root inspected the final implementation and staged changes.
- After the frozen run, only a trailing blank line in the admission test file was
  removed; its Python AST was verified identical. No runtime source changed.

Local evidence: output/20261015-explicit-premise-suite.txt, corresponding -hashes.json
and -result.json. Raw artifacts are excluded from Git. The run used no provider calls.

The next acceptance gate is a separately authorized, targeted model check against
saved full-context failure cases, including valid qualified analysis. A further full
paid assessment should follow only if that check demonstrates the intended behavior.
All previous paid allowances are consumed; this repair makes no fresh semantic or
production-ready claim and does not authorize an ITS rollout or successful handover.
