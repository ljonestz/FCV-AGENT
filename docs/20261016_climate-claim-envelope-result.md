# Shallow-envelope adjudication: complete response, failed detection

## Result

One authorized call completed normally with end_turn. All 30 claim judgments were
returned, inner JSON parsed, strong local schemas and exact-source-quote checks
passed, and the unchanged frozen scorer ran. **passed=False**: zero defects found,
both frozen true defects missed, zero false positives. publication_approved=False.

| Measure | Result |
|---|---|
| Experiment | claim-envelope-v1-1fafeb556d8bb0c6 |
| Model/configuration | claude-sonnet-5-5, adaptive/high, 16,384 cap, 300 seconds, zero retries |
| Input tokens | 17,563 |
| Output tokens | 10,208, including 4,587 thinking tokens |
| Provider elapsed time | 61.076 seconds |
| Coverage | 30/30 |
| Defects found | 0 |
| Frozen true defects missed | 2 |
| False positives | 0 |

Response SHA256: `323737a838fdf7ee3944341c8ec2422415b29630ebec8976ee42983099361ce2`.

The shell reported the experiment lock absent before submission. The command was
verified against frozen local inputs and submitted once. The response checksum,
prompt/schema/input bindings, end_turn and all downstream checks were verified.
No retry, additional batch/call, automatic editor, deployment or merge occurred.
The one-call authorization is consumed.

## What failed analytically

Both target sentences were classified as factual_assertion, supported, non-defect.
They did not escape validation by being relabelled as qualified inference.

- NARR-dividends#p0#s0: the cited quote establishes climate-smart agricultural and
  post-harvest support for trader resilience. It does not establish the sentence's
  disputed immediate/flood-ready infrastructure benefit. The surrounding source
  describes redesign and revised specifications.
- NARR-inclusion#p0#s2: separate quotes support the care centre and disaggregated
  jobs indicators. The quote used for the disputed safeguard clause names
  vulnerable-group exclusion among social risks. Naming a risk does not establish
  an exclusion-specific safeguard; the source also lists general ESF instruments.

This is a semantic support failure: true quotes about part of a compound sentence
were accepted as support for the whole sentence. Exact substring checks established
traceability, not entailment of every material proposition. The inventory calls its
entries atomic claims, but these two entries each contain multiple propositions.
Sentence coverage is therefore not equivalent to factual-premise coverage.

Overall labels were 20 supported factual assertions, 7 supported conditional
inferences, 2 not-established conditional inferences and 1 not-established proposed
action. All 30 were marked non-defective. The frozen expected labels were untouched.

## Implications and stopping point

The shallow provider schema resolves the observed compilation/coverage obstacle
for this request. It does not establish reliable detection: the now-complete
enumerate/adjudicate output reproduces the two semantic misses. Do not report this
as a success, soften expected labels, or continue a blind schema/prompt retry loop.

Any next design must address support for each material factual proposition inside
compound sentences while preserving valid qualified analysis. That work and any
further call are not authorized by this result. Human factual review remains
necessary for any proposed near-term supervised pilot; no product release or
human-review feature is approved here.

## Local evidence (uncommitted)

Under output/20261016-claim-envelope-v1/:

- request.json, manifest.json, run_command_compact.sh: frozen inputs/command.
- authorization.txt and submission.txt: one-call record.
- terminal.txt and response_blob.txt: captured, checksum-verified transport.
- response.json: original provider response envelope.
- result.json: unchanged scorer's failed result and usage.

The manifest's original UNSENT status is historical; this document records the
completed attempt. Earlier failed batch/preflight artifacts remain untouched.
Production/ITS acceptance and publication remain held.
