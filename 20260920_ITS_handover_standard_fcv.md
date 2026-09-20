# Standard FCV management brief and prioritization handover

Date: 20 September 2026

**Status: review candidate. Live testing of the updated Render build with a real PAD is required before final acceptance.**

## Baseline and scope

ITS reported that QA includes application commit `f8e8142` on `codex/climate-summary-quality-fixes`. This change branch, `codex/nairobi-project-screener`, starts from that exact commit. It is intended as a bounded port onto the QA baseline, not a replacement of the ITS infrastructure or retrieval implementation. The GitHub `main` branch remains an older baseline and is not the target for this patch.

Scope is the standard FCV project screener. Diagnostic-bank expansion, new sector resources, and analytical changes to the Climate module are deferred. The user explicitly included the Climate route in the routing-disclosure removal. This presentation change applies to Summary, Detailed and matching HTML/Word exports; analytical and internal routing behavior remains unchanged.

## Product changes

1. A compact management brief uses the existing Stage 3 result. It shows plain-language findings, genuinely evidenced strengths, and the leading suggested action for each of one to five priorities. The complete assessment retains formal ratings, all actions, drafting, and evidence.
2. Core prompts consider PDO relevance, activity and beneficiary scale, severity of potential harm, and delivery dependencies. Spending is an input to judgement, not a mechanical score. Critical low-budget implementation arrangements and serious harms remain eligible for highest priority.
3. Core generation no longer fills a four-to-five-priority quota. Advice should use applicable project, operational, and commitment instruments without prescribing unnecessary revisions to supporting assessments.
4. Responsiveness is interpreted in relation to the operation's purpose. A limited direct contribution to FCV drivers is not automatically evidence of poor design.
5. Unsupported policy authority, portfolio-wide comparisons, and invented numerical decision thresholds must not be presented as established requirements.
6. Separate Word and print-ready HTML brief downloads supplement the existing comprehensive exports. Browser Print / Save as PDF works with the HTML; no server-side PDF dependency is added.
7. Technical routing disclosures are removed from reader views. Internal routing, document/instrument detection, and actionable unresolved-route warnings remain.
8. Watch narratives retain their paragraphs and Markdown structure instead of appearing as one escaped bullet.

## ITS issue reproduced before changes

On the completed standard-route QA result, the Summary's `What to keep an eye on` section contained one `<li>` holding the entire multiline horizon narrative. Literal `###` and `**` markers appeared in the user-facing text. There were four numbered watch headings inside that single bullet. This was verified from the rendered DOM, not inferred from a model error.

The Render baseline has the equivalent defect: `normalFcvWatchGroups()` collapses whitespace in `horizonConsiderations`, and `renderNormalFcvWatchDisclosure()` treats the result as a plain escaped list item. ITS should render horizon Markdown through its safe Markdown renderer in a prose block and retain true array entries as ordinary bullets. Preserve line breaks before Markdown parsing; do not pass unsanitized model HTML to the DOM.

The QA Summary also displayed a `How this operation was routed` box containing an internal preparation-status label. Remove the routing disclosure in both Summary and Detailed for standard and Climate views and matching exports, without disabling routing logic or suppressing a substantive warning about incomplete analysis.

Private run observations and screenshots are kept outside Git. Their analytical claims have not been independently fact-checked against the uploaded project package. Portfolio comparisons and precise monitoring thresholds were identified as content-review flags, not proven factual errors.

## Shared contract and porting instructions

- Preserve delimiter names, formal rating semantics and timing enum values.
- Retain `concise_readout` and per-priority `concise`; new output is shorter, while valid older concise bundles remain readable.
- Core brief generation targets a 40-80-word overview and zero to three evidenced strengths. Do not generate positive findings solely to fill three cards.
- Keep canonical Detailed priorities as the source for concise alignment, lifecycle admission and deterministic fallback. The brief must not introduce a new fact, action or milestone.
- Browser and exports use each admitted concise priority's title, rationale and first action; they explicitly refer readers to Detailed for the complete actions and evidence.
- `POST /api/download-management-brief` accepts `concise_readout`, canonical `priorities`, `fcv_rating`, `fcv_responsiveness_rating`, resolved `doc_type`, `active_lenses` and `format` (`html` or `docx`). Revalidate on the server, reject specialist routes and unavailable concise bundles, and return the generated attachment. The existing comprehensive download route retains its behavior.
- Reuse the standalone Python exporter in `fcv_management_brief.py` from FastAPI after validation. It has no Flask dependency and no model calls.
- Keep internal OPCS retrieval and ITS infrastructure unchanged. No raw policy corpus, credentials or assessment output belongs in the patch.

## Files and integration points

| Area | Files / symbols to mirror |
|---|---|
| Core prompts and admission | `app.py`: standard Stage 1/2 context, `append_core_concise_stage3_contract()`, `_prepare_standard_stage3_prompt()`, concise normalizers and `extract_priorities()` |
| Brief endpoint | `app.py`: `download_management_brief()`; adapt the Flask response handling to FastAPI while preserving canonical validation |
| Portable exporters | `fcv_management_brief.py`: `render_management_brief_html()` and `render_management_brief_docx()` |
| Browser | `index.html`: concise capability gate, compact priority list, exact-priority links, watch Markdown, brief controls, advisory timing/context, routing disclosure removal |
| Climate export consistency | `sector_lenses/climate_verified_render.py`: HTML/Word presentation only; retain internal route state and drafting gates |
| Regression coverage | `tests/test_nairobi_backend.py`, `tests/test_nairobi_frontend.py`, `tests/test_management_brief.py`, and updated concise/Climate renderer tests |

The public patch is based on the reported QA commit. Adapt shared behavior to the ITS layout rather than replacing its infrastructure wholesale. Restart from a fresh assessment when validating prompt changes; a saved result can validate presentation and downloads but cannot demonstrate the revised model output quality.

## Acceptance cases

- One, two and five substantive priorities retain their order and correspondence across the brief, Detailed and brief exports.
- A project dominated by one component receives proportionate attention, while a critical cross-cutting implementation or harm issue can outrank budget share.
- A valid older saved summary remains readable. An incomplete concise bundle falls back to Detailed with an explicit notice.
- Summary contains no formal rating widgets or technical routing box; Detailed retains formal ratings.
- Every brief priority links to the matching Detailed priority, including non-first priorities and after tab switches.
- A four-section horizon narrative displays headings and paragraphs without literal Markdown markers; ordinary watch arrays remain bullets, and embedded HTML is escaped.
- Brief Word and HTML contain the same leading actions. Comprehensive exports still contain all actions and suggested wording.
- Unsupported comparison claims and numerical trigger values are not invented or presented as policy obligations.
- Existing Climate analytical contracts remain unchanged; only the specifically requested routing disclosure removal may affect its shared display.

## Validation status

- **1,260 tests passed across partitioned runs:** 1,167 broad-suite cases, 11 bank-selector cases, and 82 Climate frontend contracts. This includes standard prompt/parser, concise compatibility, brief endpoint/export, and Climate rendering coverage.
- Python compilation, complete inline JavaScript syntax, and diff whitespace checks passed.
- Four Chromium browser cases remain unverified: print and phone-layout runs stalled in the Windows Playwright runner, and the two following browser cases were not completed. These are not counted as passes.

The bank-selector suite exposed a calendar-dependent archived-snapshot test. It now evaluates the August release at its publication date; all 32 bank/selector tests passed, including expiry rejection. Runtime bank code, expiry safeguards and the pinned country-bank commit are unchanged. Six entries in that candidate bank currently return `bank_content_expired` and require content review before a future Climate bank update.

Visual checks used synthetic data only. All one/two/five priorities remained visible, the fourth priority opened the correct Detailed card, formal ratings stayed in Detailed, and the watch disclosure rendered escaped headings/paragraphs. Mobile width was checked at 390 pixels. A five-priority management brief printed on one A4 page in both Word and Chromium HTML; longer legacy content is allowed to overflow to additional pages. The local browser completed its assertions but stalled during shutdown and was terminated after the diagnostic timeout; the captured output and screenshots establish the UI checks, not a successful browser-process exit.

Live acceptance is required before finalization, explicitly requested by the user: run the existing Honduras Sustainable Connectivity PAD (P181166) through the updated Render standard route, check all priorities against the source package, compare summary/full downloads, and confirm the ITS watch formatting and routing removal. Prompt guards reduce risk but do not prove factual accuracy without this source-based review. Neither Render nor ITS QA is claimed to have this candidate deployed.

## Live PAD trial source checks

The test PAD provides a useful materiality case: the main corridor is US$158m of US$187m (84.5%); feeder roads are US$14m, landscape/livelihood activities US$5m, and institutional strengthening/project management US$10m. The output should give the main investment proportionate attention while retaining serious harm and delivery dependencies. The source already includes an estimated 185 hectares of land acquisition, resettlement instruments, labor-influx/SEA-SH measures, participatory selection, and grievance arrangements. Recommendations must recognize those commitments and identify specific verification or operational gaps. Planned measures must not be described as completed. Current implementation status cannot be established from this historical PAD alone.
