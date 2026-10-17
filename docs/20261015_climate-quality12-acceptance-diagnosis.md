# Quality12 acceptance diagnosis

## Outcome and authority

The final authorized paid trial completed successfully at the transport layer but
failed analytical and native-reader acceptance. Do not merge, release, deploy to ITS,
or label this candidate production ready. Both of the user's two paid allowances
are consumed. No third assessment or provider review is authorized.

Candidate: 23958aea7d0f7cf21efec180ce8f2f4932d5015c.
Assessment: 5289893e-fc9d-497b-ad6c-6234b36c2e05.
Paid FCV-AGENT deploy: dep-db80cctg1s2s738i4r80.
Submitted once 2026-10-14 22:50:13.403 UTC; completed 22:54:33.521 UTC; HTTP 200.
The source is the unchanged public Great Lakes PID, SHA256
70238ba18f619c36e0d678468779427134c5a3c77572c6e6cdfb3fd7457579c3.

Production was restored by dep-db80ii8u01pc738ev6tg, live at 23:00:04.693534 UTC,
to original main 1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205. On Commit auto-deploy
was restored and verified. Direct health returned HTTP 200 and original build.
The free branch service remains on candidate 23958ae with auto-deploy off.
Main and ITS were not changed. Render availability no longer blocks this candidate;
the remaining blocker is assessment quality.

## Method and observed behavior

Review used the immutable saved assessment and diagnostic trace, actual browser
session/HTML/DOCX downloads, assessment-ID-filtered Render logs, and the original
15-page PDF. An independent read-only review checked claims against exact source
paragraphs. Structural tests and reviewer verdicts were not treated as factual proof.

The frozen candidate passed 1,565 offline tests and CodeQL before deployment.
Research retained both Burundi and DRC evidence on its first attempt and passed the
application grounding gate. Its status remains partial; country coverage alone does
not establish complete or current evidence. Three recommendations survived core
review from four candidates. The native Summary was 204 words. Findings were
104, 171 and 184 words; the only initial mechanical defect was the inclusion finding
four words above its 180-word limit. Summary length is not the acceptance blocker.

Exactly one initial meaning review requested revisions to SUM-001 and
NARR-dividends. The combined correction also targeted NARR-inclusion for length.
The dividends patch introduced June 2029, absent from that original record.
The deterministic validator correctly rejected the entire patch with
READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED. The date exists in the document,
but this text-only repair was not authorized to expand the original claim scope.
There was no post-correction meaning review. The reader_review field retains the
initial review, not a fresh review of the rejected patch. Native prose stayed withheld.
The UI visibly reports that the automated Summary could not be independently verified.

## Substantive source checks

Page numbers below are PDF page indices plus one, not the printed footer number.

| Generated assertion | Source check | Required interpretation |
|---|---|---|
| Displaced traders from cancelled sites; traders losing their original sites | Page 5 paragraph 4 establishes displacement and suspended sites separately; page 8 paragraph 18 describes remapping for displacement; page 10 paragraph 22 describes cancelled target areas | No evidence links that particular displaced trader population to cancelled sites. Ask about small-scale traders and displacement-affected populations without inventing the link. |
| The package does not state siting criteria | Page 13 paragraph 27 explicitly gives trade volume/importance, political commitment, donor complementarity, consultations and site-specific reasons | Credit these criteria. Ask narrowly how flood exposure and distributional access inform sequencing. |
| Six suspended versus four cancelled sites is inconsistent | Different statuses and potentially different units/populations | Both can be true. DIF-001 remains an unsupported contradiction in readiness flags even though it no longer drives a core recommendation. |
| ESCP should be updated versus has been updated is contradictory | Page 13 paragraph 28 states updated, with disclosure before negotiations; other passages state requirements | A requirement and subsequent status can coexist. Verify version/disclosure timing; do not assert a logical contradiction. |
| Burundi call launch status is not shown | Page 8 paragraph 18 says launching June 2026; page 9 paragraph 20 says expected summer 2026 | Planned status is shown; actual launch/awards remain unverified by this snapshot. |
| Most climate-exposed traders | Weather-exposed value chains and small-scale/women traders are supported | The comparative superlative is not established. |
| Clarifications would show whether protections work in practice | Clarification can describe intended arrangements | It cannot prove implementation effectiveness. |

The reader reviewer also made false-positive objections. Page 5 paragraph 5 says
floods inundated low-lying infrastructure, so affected is a valid weaker paraphrase.
Page 9 paragraphs 19-20 supports intended safer commercial spaces, reduced harassment,
economic resilience and social capital. Conditional benefits language is legitimate
when it preserves intended rather than achieved status. Page 8 paragraph 18 explicitly
says the current June 2028 schedule has no buffer and proposes extension to June 2029;
a qualified concern about a tight schedule is grounded. Grouping jobs and access
indicators as showing who benefits is looser: sex/youth job disaggregation helps,
but an aggregate access count alone does not establish distribution.

## Root causes and next acceptance boundary

1. Evidence IDs establish provenance, not entailment. Separate true facts were joined
   into an unsupported beneficiary relationship, and a missing dimension became a
   blanket omission despite existing source criteria.
2. Fact-stage integrity findings currently reach readiness flags after structural
   category/source-block checks. Those checks cannot establish a genuine contradiction.
   The docstring overstates their guarantee. A future repair must make these claims
   subject to semantic admission, not only add another instruction to extraction.
   The existing conditional review receives source_blocks but does not receive the
   readiness flags as review targets; source access alone did not prevent REC-003
   from passing despite the paragraph 27 omission error.
3. The reader reviewer sometimes rejects valid weaker paraphrases and documented
   conditional benefits, while failing to identify the unsupported linkage elsewhere.
4. The correction prompt has a strict numeric/date constraint but lacked an explicit
   per-target inventory of permitted tokens. Exposing the validator's exact inventory
   is a bounded offline improvement; it does not validate the remaining analysis.

Do not solve this by increasing length limits, relaxing scope validation, manufacturing
an offline pass, silently editing saved results, or repeating full paid runs. A broader
repair should reuse the existing review call to adjudicate integrity flags against
source passages and explicitly assess relational scope and claimed omissions. Any
implementation needs fail-closed tests for missing/malformed verdicts and evidence
that valid flags remain available. Prompt wording tests alone cannot establish model
compliance. Fresh analytical acceptance remains necessary and is outside the exhausted
paid allowance. No successful ITS handover Word document has been authored.

## Evidence retained locally and excluded from Git

Under output/playwright/:
- 20261014-quality12-225519-state.json: full assessment and diagnostic trace.
- 20261015-quality12-session.json: actual downloaded saved session.
- 20261015-quality12-actual.html and -actual.docx: actual standalone exports.
- 20261015-quality12-summary.png and -detailed.png: browser screenshots.
- 20261015-quality12-render-logs.json: twelve ID-filtered application logs.

DOCX text contains all three priority titles and no private diagnostic delimiters.
These checks establish artifact delivery, not analytical acceptance or full layout QA.
The World Bank Burundi historical warming source was independently checked. The
IFRC listing confirms the DRC flood operation and date; the underlying PDF download
was inaccessible, so its exact road-access quote was not independently reverified.

## Remaining monitoring window

The read-only local monitor checks production and candidate health every five minutes
through 2026-10-15 05:11:10 UTC, the original eight-hour deadline. It makes no provider
calls, assessments, deployments or configuration changes. Local evidence is in
output/20261015_render-health-watch.jsonl; helper and PID are beside it. Its first
completed check found both expected builds healthy. It requires this workstation
to remain running. Health monitoring cannot establish analytical readiness.

## Subsequent offline repair (not deployed)

The bounded plan is docs/superpowers/plans/2026-10-15-climate-readiness-flag-admission.md.
The initial conditional review now receives the merged flags and must explicitly accept
each retained flag via passed_readiness_ids. Structural source linkage alone no longer
admits a flag. Missing, malformed, duplicate, unknown or disputed acceptances withhold
flags. No-priority runs withhold flags without adding a model call. Core/drafting
corrections receive an empty flag list, and the reader-review schema is unchanged.

Independent review found that disputed flag IDs could target all accepted cores; a
red/green regression now proves known flag disputes preserve explicit core acceptance.
Unknown targets and missing core acceptance still fail closed. The review also identified
that pre-review deduplication can suppress a minor point sharing rejected flag wording.
This conservative suppression is retained deliberately: otherwise an unaccepted statement
could reappear through an unreviewed fallback. A distinct gap ID does not establish that
the repeated text is true. This can omit a useful minor point; it does not manufacture
one or turn a rejected claim into accepted output.

Correction payloads expose each target's existing numeric tokens and date phrases,
using the validator's extraction rules. The deterministic guard remains the safety
boundary; this inventory does not guarantee model compliance. Saved quality12 replay
still rejects the original June 2029 patch, makes zero provider calls and leaves its
archive SHA256 unchanged. Evidence: output/playwright/20261015-quality12-offline-contract-replay.json.

Versions: conditional-review2.15, reader-correction1.3, normalization2.7; other prompt
versions and renderer2.19 unchanged. Neither production nor the preview has these
subsequent changes. The model's unsupported relational linkage and reviewer false
positives are not claimed fixed by these application-level changes.

## Final offline verification

Full final offline regression: **1,573 passed in 548.06 seconds**, exit 0; all 163 tracked source/test hashes unchanged. The child pytest process explicitly used UTF-8. The earlier non-UTF-8 attempt was stopped after a reproduced Windows encoding failure; its targeted test passed with the corrected invocation. Local Playwright startup was slow but all browser checks completed. Focused and independent review findings were resolved before this final frozen run.

Logs: output/20261015-quality12-followup-utf8-full-regression.log and
output/20261015-quality12-followup-utf8-source-hashes.json.
No additional model, assessment or deployment call was made.
