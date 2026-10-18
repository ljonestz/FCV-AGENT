# Recommendation details: prose presentation

The user approved replacing the Climate priority disclosure's labelled field dump
with readable paragraphs. Browser, standalone HTML and DOCX now show the existing
limitation and caution prose, retain conditional further work when it is not
already visible, and use compact lead/confidence and distinct timing notes.
Suggested wording keeps its document/section destination. Repeated action and
completion rows, drafting-status enums and guidance identifiers are omitted from
this disclosure. The canonical evidence and structured fields remain intact.

The visible why/action paragraphs are unchanged. Normal FCV, schemas, admission
checks, review decisions and provider-call budgets are unchanged. Recommendation
compiler v2.22 requests complementary prose in the existing limitation/caution
fields; conditional review stays v2.21 and final-reader review stays v1.11.
Renderer version is climate-reader-v2.20. Fresh generation with v2.22 has not run.

## Verification

- The four new regression checks failed against the previous presentation, then
  passed with the change. They cover qualifications, conditional work, escaping,
  browser/export content and preservation of the input record.
- Focused contracts: 356 passed, four known hanging browser checks deselected.
- Broader suite on the final code: 1,794 passed, four deselected in 266.72 seconds.
  This is not a complete browser-suite pass.
- The actual browser renderer was exercised locally in the existing Edge session.
  Priority 4's disclosure shows two paragraphs and a compact lead/confidence note.
  All nine Word pages were visually inspected; no clipping or overlap was found.
  Word was rendered through a separate hidden, read-only Word instance because
  LibreOffice is unavailable. The source DOCX hash stayed unchanged.
- The in-process review-packet route returned 200 and rejected reader-only drift
  with 409. Packet file hashes were checked. No provider request was made.

## Local review preview

Artifacts remain untracked under
`output/20261016-ipf-pilot-live-preflight/`, prefix
`20261017_recommendation-details-`: browser.html, report.html, report.docx,
packet.zip, snapshot.json, manifest.json, canonical.json, reader.json,
review-record.json, review-queue.json, start.html and audit.json. Word QA is in
`20261017_recommendation-details-qa/`; final verification is recorded separately
as `20261017_recommendation-details-verification.json`.

The preview uses the saved five-recommendation editorial review copy, originating
from v2.20 generation. Only REC-004's limitation and caution were reworded for
this layout preview, preserving uncertainty about financing coverage. It is not
a fresh model result or a human-approved assessment. Native Summary remains a
fallback; no historical reader-review pass was imported into this changed packet.

Snapshot SHA-256:
`83145b764ec551db26f4cc21003e8d7591d33bab0993f60246f818353c2ad454`.
Report HTML SHA-256:
`575eba41647e2b99a2469789c6b643e91242176f94e68456ccde26ca81b7b7d6`.
Report DOCX SHA-256:
`688b44ffb8f6a60646eab7b5ed0a21a38b5e7cace13193d12037bf70b5b29a15`.
External approval must bind both the snapshot and the actual report file hashes.

## Supervised-pilot boundary

Previously demonstrated improvements remain useful: the corrected saved reader
passed v1.11 review, synthetic calibration caught three planted errors without
flagging four acceptable inferences, and all five regenerated actions named a
document section and concrete edit. Those results do not establish reliable
real-case detection. Conditional reviewer v2.21 still missed REC-004's unsupported
claim that local airstrips are outside the airport revenue stream. Its model pass
remains a failed detection result; this presentation change does not repair it.

Before sharing, a named human must review consequential claims against source
passages, resolve the known financing premise and review the rest of the packet
in the existing authenticated organisational workflow. Keep the useful maintenance
question and other recommendations; unspecified coverage is not an exclusion.
Publication approval remains false.

The next acceptance step is the complete pipeline and export check on a verified
branch/deployed SHA, including fresh v2.22 generation and human analytical review.
That paid action requires a concrete bounded plan and fresh approval first. No
new paid call, deployment, merge or full live acceptance took place. Preview last
recorded at 98048797116a; production remains unchanged.
