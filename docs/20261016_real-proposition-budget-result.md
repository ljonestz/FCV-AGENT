# Adjusted real replay: complete output, major real-case errors still missed

The user authorized "adjust and proceed" after adaptive/high consumed nearly all
of the previous output budget. One adjusted call was prepared, verified and run.
No retry or follow-on call was made; this authorization is consumed.

## Adjustment and execution

Kept claude-sonnet-5-5 and high effort, changed thinking to between_tools, and raised
max_tokens from 16,384 to 32,768. Timeout remains 300 seconds; retries remain zero.
The provider documents between_tools as avoiding up-front thinking and producing
only text when no tools are supplied, accepted at high effort or below:
https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide

The prompt, 135-byte schema, 102 required IDs, sources, propositions, expected labels
and scoring rules were unchanged. New files and a fresh exclusive lock preserve
all historical artifacts. Offline checks verified frozen hashes and byte equality,
compiled the runner, and used a fake SDK to assert actual generation settings and
block a duplicate attempt before any provider request. The live shell reported
commit 1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205 and no existing experiment lock.

Experiment: real-proposition-envelope-v3-ef8e8d8d66833951.
Request SHA256: 38a93634c816938afc5a1ca4fff1bef2decf3992d52fa56cfb582e1fe4782ea8.
Response SHA256: 8f36b6e0da11d5bd38a19bb0b43a48910392181765c2c24af7a599cf1a02ae42.

| Measure | Result |
| --- | --- |
| Stop reason | end_turn |
| Elapsed runner time | 75.376 seconds |
| Input tokens | 22,947 |
| Output tokens | 14,341 |
| Thinking tokens | 0 |
| Cache tokens | 0 |
| Real propositions returned | 56/56 |
| Synthetic propositions returned | 10/10 |
| Parent decisions returned | 36/36 |

The budget adjustment solved output completion for this attempt. It does not prove
that turning off up-front thinking improves analytical quality; settings changed
and this is a single run.

## Validation and substantive findings

Checksum, request bindings, duplicate/extra/missing-key checks and all 102 inner
schemas passed. Strict evidence validation rejected one citation: SUM-002#p0#s3~3
contains source ID DOC-ce08d41a57d2a4c6-B-27161 and quote "placeholder". That source
is absent. It was not repaired or ignored in the official scorer. No result.json
semantic score was produced; diagnostic_result.json separately records failure and
raw-label diagnostics. All other returned source quotes passed exact membership.

The two original major defects were both labelled factual_assertion, supported,
severity none, with their parent sentences retained:

1. NARR-dividends#p0#s0~1: immediate climate resilience / flood-ready border posts.
   The model cites revised flood-protection specifications, calls the claimed
   immediate benefit interpretive, and accepts it as design-grounded. The evidence
   establishes design intent, not delivered flood-ready infrastructure or an
   immediate realized benefit. The frozen delivery-status defect remains missed.
2. NARR-inclusion#p0#s2~3: safeguards against vulnerable-group exclusion. The model
   cites the exclusion risk and the generic ESF instrument list, then concludes
   that safeguards addressing that specific risk are documented. Those excerpts
   do not establish the specific provision. The frozen specificity defect remains
   missed even though its proposition is now isolated.

These misses are independent of the placeholder citation elsewhere. Removing that
citation would not change the real-case failure. All real propositions were assigned
severity none, and all real parent sentences were retained. The three original
protected claims (most displacement, qualified access risk, unstated climate site
criteria) were correctly preserved. All 56 real-case explanations and the synthetic
findings were inspected; this is focused diagnostic review, not full source audit.

The three synthetic major target propositions were detected and all three harmful
parent cases held. The model also flags their dependent advice (M02-P02 and M04-P02)
as major. Frozen gold counts only the faulty premise and protects those subordinate
propositions from double-counting, so these are raw-label mismatches. Substantively,
the model's decision to hold that advice agrees with the user-calibrated objective;
it is not evidence of rejecting valid advice. Labels remain unchanged. All three
safe synthetic parent cases were retained. Supported/not_established or
contradicted/not_established differences are secondary to the two real misses.

## Conclusion and next direction

Overall accepted: false. Complete output and simple synthetic discrimination do not
establish real-case detection. The original substantive weakness persists: generous
interpretation of delivery status and generic safeguards conceals consequential
unsupported claims. Minor-error tolerance does not make these known targets pass.

Do not integrate this as a reliable automated major-error gate. A useful next design
would focus on source-grounded checks of delivered status and specific protective
provisions, with supervised review of consequential claims. Another broad prompt or
budget retry should not be treated as a demonstrated solution. No new experiment,
production change or human-review feature was implemented here.

## Local artifacts

Under output/20261016-real-proposition-envelope-v3/: request.json, manifest.json,
reviewer_inputs.json, expected.json, run_command.sh, offline_validation.json,
offline_mock/, authorization.txt, paste files, submission records, terminal_poll1.txt,
response_blob.txt, response.json, quote_validation_diagnostics.json and
diagnostic_result.json. The existing envelope module was loaded with DEST set to
this new directory for scoring; its code and underlying evaluator were unchanged.

No deployment, merge, correction generation, publication or additional provider call.
publication_approved remains false. Raw model responses and source inputs remain
uncommitted. Historical scores and gold labels remain intact.
