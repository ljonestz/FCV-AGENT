# Real replay envelope v2: schema accepted, token budget exhausted

The user approved exactly one prepared compact-envelope call. It was submitted once
on 2026-10-16 through the existing Render shell after checking the deployed SHA
1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205 and absence of this experiment's lock.
Local request, input and scorer hashes were verified. Three paste chunks followed
by one Enter submitted one request. No retry, follow-on or correction call occurred.

Experiment: `real-proposition-envelope-v2-b56105370523ac5c`.
The 135-byte single-string provider schema was accepted, resolving the prior
102-key grammar rejection for this attempt. The model then stopped at max_tokens.

| Measure | Observed value |
| --- | --- |
| Model | claude-sonnet-5-5, adaptive/high |
| Input tokens | 22,948 |
| Output tokens | 16,384 (the cap) |
| Thinking tokens within output | 15,703 |
| Other output tokens | 681 |
| Elapsed runner time | 111.189 seconds |
| Cache tokens | 0 |
| Stop reason | max_tokens |
| Returned text length | 1,422 characters |

Thinking consumed approximately 95.8 percent of the output budget. The remaining
text begins judgments for the first summary sentences and cuts off inside a source
ID. The outer JSON is invalid (unterminated string); neither original known defect
has a completed judgment available in the returned text. This is not a scored
semantic failure or a detection success. It is an incomplete response.

## Validation and interpretation

One distinct response was extracted from repeated terminal accessibility text.
Verified response SHA256:
`1f56f31976339ded166777078fdea3b1bfc8408f18fece461006b34b33cb2f54`.

The offline scorer verified checksum, frozen inputs/scorer and response bindings,
saved response.json, then correctly rejected max_tokens with Incomplete provider
result. It did not repair the JSON, fabricate missing judgments or compute a pass
from partial coverage. transport_result.json records practical_passed null and no
validated coverage. There is no result.json semantic score.

The simplified envelope fixes the observed schema obstacle but does not establish
full output reliability. The immediate bottleneck is reasoning consuming nearly
all of the shared output-token budget. The next design decision should address
reasoning/output allocation or bounded workload before another call, preserving
all major-error criteria and original labels. Merely removing evidence checks or
accepting an incomplete review would not solve the task. No new request or changed
model configuration was prepared in this turn.

## Artifacts and boundary

Local, uncommitted under output/20261016-real-proposition-envelope-v2/:
authorization.txt, paste_0.txt through paste_2.txt, submission_started.txt,
submission.txt, terminal_poll1.txt through terminal_poll3.txt, response_blob.txt,
response.json and transport_result.json. The old UNSENT manifest is historical;
this result supersedes that status. All prior artifacts and labels remain intact.

The one-call authorization is consumed. No further provider calls, runtime changes,
deployment, merge or publication. publication_approved remains false. Real-case
major-error detection remains unproven; the earlier smaller synthetic success must
not be generalized to this incomplete real replay.
