# Fresh reader evaluation: useful improvement, revisions remain

The user explicitly approved sending the prepared assessment, source passages and
corrected recommendations to Anthropic for at most two calls, with a USD2
reservation ceiling and no retries. This superseded the approval block recorded
in 20261017_dividends-live-preflight.md. Both authorized calls are now consumed.

## Execution and scope

The frozen a1508ef bundle ran once in an isolated temporary directory using the
existing authenticated Render shell. Neither deployed app, configuration nor
preview blocker was changed. Production preflight SHA was
1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205; preview remains 460eaef.

Reader compiler v1.11 and reader review v1.12 used saved Quality evidence from
13290d23-ae01-4bdc-8656-3dcbc3eeefef with approved source qualifications. The editorial
answers were not provided to the compiler. Upstream analysis, judgment and
recommendation generation were not rerun. This is not full-pipeline acceptance.

Both Sonnet 5.5 calls returned normally in 19.475 seconds overall, with zero retries:
68,721 input tokens and 2,469 output tokens. Conservative reservations total
USD0.921508, not invoice charges. The unused ceiling is not new call authorization.
Preserve the consumed local/remote locks and ledger. No follow-up call is queued.

## Results and source review

Mechanical admission checks passed with one existing same-passage reference repair.
Independent semantic review returned **revise**, targeting SUM-001 and
NARR-inclusion. The reader was not admitted; publication remains false.

The fresh three answers contain 124/163/169 words. The dividends answer now develops
livelihood, institutional-capacity, trust and cooperation pathways, qualifies them
as potential, and connects priorities to additional benefits. The reviewer did not
object to this conditional analysis. The design answer considers possible adverse
siting and off-footprint impacts. These are useful improvements, not proof of
reliable semantic detection.

Source review of the original PID passages found:

- **Valid objection:** SUM-001 combines general activity-selection criteria with
  airstrip-specific criteria. Separate them. PF-010 concerns connectivity,
  urban-service bottlenecks and sustainable jobs; PF-011/footnote 10 additionally
  concerns demand, maintenance capacity, population served and humanitarian access.
- **Overstrict objection:** the reviewer questions SURP II hiring reaching women,
  IDPs and youth, then concedes it is a supported paraphrase. Footnote 12 records
  job shares of 24%, 49% and 80%; this historical claim is supported.
- **Ambiguous inclusion objection:** the text explicitly labels airstrip criteria
  and the earlier SURP II precedent, so the review overstates its alleged transfer
  of all criteria to drainage/jobs. Still, calling all these "real protections"
  can blur current commitments and historical precedent. Separate those roles.
- **Additional edits:** narrow "final sites are still under discussion" because
  five Phase 1 airstrips are already selected. Say the PID does not specify Challenge
  Fund eligibility, rather than asserting no design exists. These were not the
  reviewer's targets and show why consequential source review remains necessary.

No prompt, schema, renderer or gate was changed in response. Do not discard the
other recommendations or launch another automatic correction experiment.

## Artifacts and practical next step

All raw files remain untracked under output/20261016-ipf-pilot-live-preflight/:
dividends-live-20261017-result.json, packet.json, zip, submission.lock, shell/log
captures and review.html. The readable review preserves fresh model text unchanged,
sets out source findings, and links the approved editorial v2. Its SHA256 is
e21195bc58552a515af7b6b0e39b2ea7014a8536a07af1b309f5c47dc240fb62.
Remote result checksum was verified before saving; local HTML assertions preserve
every generated paragraph. Existing Edge loaded all five narrative records and the
editorial link. No new Word/export-packet or visual-layout acceptance is claimed.

Use the approved editorial v2 as the human-reviewed narrative candidate. Reconcile
its corrections into canonical records and regenerate a matching version-bound
review packet through the supported workflow, retaining the actual automated
revise and pending publication status. Named approval must be recorded externally
in the existing authenticated organisational workflow against that exact version.
The current fresh-reader failure must not be overwritten with a borrowed pass.
Full live pipeline/export acceptance of the revised candidate remains outstanding;
the completed 460eaef technical campaign is separate historical evidence.
