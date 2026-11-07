# Readout presentation simplification - 28 October 2026

## Candidate and scope

Presentation code commit: `17d45c39a245b72c66e77afe6e7554e1e48f424b`, on
`feat/global-country-bank-depth-20261026`. The local-only approved plan is
`docs/superpowers/plans/2026-10-28-readout-presentation-simplification.md`.
This continues the bank and deploy-readiness work recorded in
`docs/20261027_deploy-readiness-follow-through.md`.

Test deployment: `dep-dbgvqkp42hec73e4em90`, **live at 2026-10-28 13:50:24 UTC**.
Service `fcv-agent-climate-smoke` (`srv-d6gsivcr85hc73a2833g`) serves
https://fcv-agent-1.onrender.com in the confirmed FCV LLM Services workspace.
Auto-deploy is off. **Hosted health reports build `17d45c39a245`, live research, Quality and Haiku research. The saved-session hosted check passed; no app error/critical logs were returned for the post-live interval checked.**

Production remains on `6f3d5e65e213`, main, bank-only and Quality, with auto-deploy
off. **The complete service metadata matches the pre-deploy record; updatedAt remains `2026-10-18T14:35:48.223085Z`, and production health still reports the same build and modes.** No merge, production deployment, hosted
configuration change, bank approval or new paid assessment occurred.
The app still pins bank `72ce351e0f19fe52ff786196b516e6dc4a684290`.

## Resulting behavior

- Summary uses compact priority cards: rank, title, Suggested action, the complete
  existing short action and a link to the matching Detailed priority. Climate
  actions in the saved Somalia run are 39-45 words. Action paragraphs use regular
  font weight on both routes; titles and labels retain their emphasis.
- Summary and Detailed start directly with their assessments. Generic opening
  `reader_review_notice` preambles are omitted from browser views, Copy and
  Word/HTML; the offline Word builder also omits `overview_notice` and the old
  `context_note` preparation banner. Canonical review metadata and specific source
  qualifications remain unchanged.
- Summary omits the duplicate Climate sensitivity line, project-cycle blocks,
  specialist reasoning disclosure and What to keep an eye on disclosure. Useful
  timing, qualifications, supporting analysis and follow-up remain in Detailed.
- Detailed uses **Practical considerations and Suggested Text**. Distinct timing
  entries are stacked, and drafting labels use Suggested Text consistently.
- Both routes show the user's full optional-priorities advisory. It precedes
  Summary priorities and accompanies the existing priority-count introduction in
  Detailed and exports. Normal FCV uses FCV context; Climate uses climate and FCV
  context. Normal implementation-mode Word exports receive optional
  `metadata.review_mode`, with the existing design fallback for older clients.
- One **Copy** button copies the active Summary main text or the complete Detailed
  report. It excludes navigation and toolbar controls, preserves the Summary's
  explicitly open guidance, and reports clipboard failure accurately. Detailed
  copy includes all priorities, drafting and applicable document/provenance notes.
- One **Download report** menu offers Word and HTML, both the complete Detailed
  report regardless of the active tab. Review-packet and management-brief buttons
  are removed from the main toolbar; their backend mechanisms and saved sessions
  remain available.
- Generic draft/human-review and preparation-route banners are removed. Partial,
  incomplete, smoke and candidate warnings, specific verification notes and actual
  drafting-route gates remain. Packet approval fields remain blank/unapproved;
  client-supplied approval flags cannot change report content.

No prompt, provider, retrieval, bank, model schema, canonical reader projection or
renderer-version change was needed. Word design/style files, logos and fixtures
are unchanged; ancestry through `3ab33b598492f8f9ee8882d094b00ee2dfa453a3` is retained.
The private parity note was updated; ITS was not edited or validated.

## Final opening-preamble cleanup

The final follow-up removes generic opening verification notices from Detailed,
Copy and Word/HTML, including both equivalent offline Word preambles. It changes
only three rendering files and four regression-test files: ten insertions and
18 deletions. Canonical reader data, review verdicts, source-specific qualifications,
partial/smoke/candidate warnings and actual drafting-route gates are retained.

Focused tests failed before each display removal and passed afterward. The final
full offline suite passed with unchanged source hashes. Headed Edge repeated the
saved Somalia check on the final files: all five priority links, Summary/Detailed
Copy, actual Word/HTML downloads, 390/320-pixel layouts and standalone HTML print
restoration passed. The canonical reader/assessment restored exactly, including
the now-hidden generic notice value. No assessment endpoint was called.

The fresh actual Word download rendered read-only in native Word; all 13 pages
were visually inspected. There is no clipping or layout issue, all five priorities
and the advisory remain, and the source DOCX hash is unchanged. Page 13 is a short,
nonempty ending. The normal-route/18-page evidence below is the unchanged preceding
presentation baseline; it was not regenerated for this climate-only follow-up.

The final hosted saved-session check passed at the exact commit above: Detailed
has no generic review notice, five compact cards use regular-weight actions,
Copy/download controls and the full advisory remain, and there are no browser/API
errors or attempted assessments. GitHub CodeQL passed on this code checkpoint.
Production health and its complete service metadata still match the pre-deploy
record. Both PRs remain drafts; this is a test-only deployment.

Fresh ignored evidence is under `output/20261028-readout-presentation/preamble-removal/`:
`full-suite-final.log`, `full-suite-final-result.json`, `browser-check.json`,
`final-source-export-checks.json`, `climate-final-report.docx/.html`,
`climate-final-word-render.json`, `climate-final-word-visual-review.json`, all
13 page PNGs, `hosted-preview-check.json` and hosted opening screenshots/HTML.
The earlier interrupted full run is retained as diagnostic evidence and is not
the final acceptance result. The native Word helper required normal process
permissions; its successful render and owned process exit are recorded.

## Verification

- Final full offline app suite: **2,079 passed, two skipped, four deselected** in
  **515.79s**, exit 0. The four exclusions are the documented hanging headless
  Chromium print/phone cases. Submodule sync/init completed before testing.
- An earlier presentation pass found ten stale presentation assertions or isolated Node
  harness dependencies. They were updated without dropping packet, route or source
  safeguards; all ten passed in focused runs, followed by the clean full run.
- All three inline scripts pass Node syntax checks. Modified Python files compile,
  `git diff --check` passes, and browser/Python advisory wording matches exactly
  across both routes and design/implementation modes.
- Real headed Edge checks used the saved Somalia Quality session and the supplied
  Syria ITS reference. All five links per route, both Copy payloads, both actual
  downloads, retained identity and 390/320-pixel layouts passed. No browser runtime
  error, failed API request or assessment endpoint call occurred. Every action
  paragraph computed to font-weight 400; Summary had no opening review notice.
- Actual standalone HTML print checks passed: all 14 Climate disclosures open for
  print and restore afterward. Print PDFs have 14 Climate and 17 normal pages,
  all nonempty. Normal standalone HTML has no disclosures to expand.
- Actual downloaded Word files rendered read-only in native Microsoft Word.
  The coordinator inspected **all 13 Climate and 18 normal pages**: no clipped or
  overlapping text or blank pages. Existing normal table continuation/pagination
  is retained. Both source DOCX files remained byte-identical after rendering.
- Both original input sessions remain byte-identical. The Somalia assessment and
  canonical reader also restored exactly in the browser. Bank, model and source
  content was not regenerated for this presentation task.

## Evidence and reproducibility

All raw artifacts are ignored under `output/20261028-readout-presentation/`:

| Artifact | Evidence |
| --- | --- |
| `final-full-suite-green.log`, `final-full-suite-green-result.json` | Exact final command, exclusions and exit code |
| `final-source-checks.json`, `advisory-parity-final.json` | Syntax, compile, source hash and wording parity |
| `climate-final-browser-check.json`, `normal-final-browser-check.json` | Copy, all links, actual download hashes, phone measurements and requests |
| `*-final-summary-copy.txt`, `*-final-detailed-copy.txt` | Actual Copy button payloads captured without overwriting the OS clipboard |
| `*-final-report.docx`, `*-final-report.html` | Actual downloads from the Summary toolbar |
| `*-final-word-render.json`, `*-final-word-visual-check.json` | Native rendering hashes and coordinator page inspection |
| `standalone-html-check.json`, `standalone-html-pdf-check.json` | Print expansion/restoration and nonempty PDF checks |
| `source-fixture-record.json` | Original input paths, hashes and the Syria adapter scope |
| `local-assessment-blocker-check.json` | Local assessment requests rejected with HTTP403 |
| `hosted-preview-check.json` | Final hosted SHA and saved-session acceptance |

The root `output/playwright/` folder contains earlier CLI snapshots. CLI named
sessions closed unexpectedly and the browser connector had no available surface.
The final checks therefore used the installed Playwright library directly in one
headed Edge process, without installing packages or changing browser security.
The packaged DOCX renderer lacked `pdf2image`, so the established native Word
fallback was used. Its helper processes lingered after complete render records;
only their exact helper PIDs were stopped. Word process listings were stale; no
broad Word process action was taken. Windows `Invoke-RestMethod` worked for health
checks without TLS overrides after Python/curl certificate-chain failures.

## Limits and supervised testing

The Syria JSON is an ITS save without the native Render session envelope. An
ignored UI adapter converts key names and preserves its existing priorities/prose;
it supplies no invented strengths or new analysis. This is a presentation/style
check, not a fresh native normal-FCV assessment. Long recommendations in that old
save remain complete rather than being cut arbitrarily.

The Somalia save remains historical evidence from the earlier paid run. Its three
inline source qualifications remain in Detailed/exports; `revise`, `attention`
and the generic notice value remain in canonical review metadata.
Removing a banner does not resolve those findings or record publication approval.
See the preceding readiness handoff for the source-admission fix and remaining
country-bank evidence limitations. No new analytical quality claim is made here.

The combined conservative test debit remains **USD10.729492**; this task added
**USD0**. Test spending remains blocked: web flag0, budget1 microUSD and the
previous finished-blocked SQLite path. The additional USD5 was not used.

For unpaid supervised review, open the test URL and use Load session with
`output/20261027-global-bank-deployment/global146-ready-quality-session.json`.
Check Summary, follow a non-first priority link, switch Detailed/Summary, use Copy
on each tab, and download Word/HTML from either tab. Downloads contain Detailed.
Do not start a new assessment while the test spending blocker is in place.
Both PRs remain draft; bank PR #5 is unchanged by this presentation follow-up.
Keep both worktrees and unrelated root work.
