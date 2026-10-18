# Step-by-Step fixes and supervised pilot release

Ricardy Valcin's 13 October handover (supplied as
20261014_ITS_Handover_fy26_app_updates.docx) identifies three reproducible bugs.
His cited local commit 344949f and branch fix/step-by-step-qa were unavailable in
the shared GitHub repository. The user supplied messages explaining that write
access prevented his push. These are independently implemented fixes from his
diagnosis, not a reviewed or cherry-picked copy of his patch.

## Included changes

- Save real Stage 1 and Stage 2 outputs behind compact stage labels. Stage 3
  receives both. Refining a standard stage replaces that stage's saved result without
  duplicating stages or retaining obsolete downstream results.
- Recover original outputs from legacy embedded context where they still exist.
  Preserve section separators and stage numbers. Already-lost text cannot be
  recovered; restart from the source document when the old session lacks it.
- Initialise instrument and lens context before the Refine branch, including
  its existing lens-version restart check. Refine no longer crashes after the
  model completes because those variables were missing.
- Return the detected doc_type from Stage 1. Later requests with unknown type
  recover the Stage 1 delimiter; an explicit known request type takes precedence.
  The Step-by-Step browser now consumes this field and retains delimiter fallback
  for older responses. Its existing session persistence saves the resulting type.

Only app.py, the Step-by-Step completion handler and regression tests change for
these fixes. Express generation,
model selection, provider-call count, prompt budgets and export formats are
unchanged. Climate native admission remains in place. ITS should mirror these
history, context-initialisation and doc_type semantics in its own route while
preserving its retrieval implementation.

## Evidence and boundaries

New offline route tests first reproduced eight failures, covering all three
reported defects; the explicit document-type precedence control already passed.
Additional checks cover repeated refinement, legacy section separators, missing
Stage 1 and full saved outputs beyond the model-request cap. Connected suite:
304 passed initially. Full suite: 1,879 passed, four documented Chromium hangs
excluded (305.37 seconds), after restoring the native Climate history contract.
The final browser-field correction and three new browser cases were checked in
a 143-test focused run. Those three cases were added after full-suite collection.
No complete browser-suite pass or paid generation is claimed. Deployed replay
results are recorded separately with the release bundle.

The separately reported Guinea substring/classification problem and the
40,000-character model-history cap are not fixed here. Saving history now retains
full outputs, but the existing request cap still applies and can truncate a
structured block sent to the model. Verify country/classification and source
coverage during supervised review. The ITS-specific Climate failure and Express
Summary fallback from the older diagnostic runs are not established as resolved
by these three fixes.

The last full paid acceptance remains the 856f583 bank-only Quality run. The new
verification-note behaviour and these Step-by-Step fixes have offline/replay
evidence, not a new full paid acceptance. Publication remains false. Production
promotion and its operating allowance remain separate release decisions.
