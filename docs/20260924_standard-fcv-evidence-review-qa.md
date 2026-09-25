# Standard FCV evidence review: live QA and release decision

Date: 24 September 2026
Decision: **Hold the draft candidate. Do not merge, deploy to production, or transfer to ITS.**

## Method and source boundary

I tested the in-app standard-FCV evidence reviewer on the paid [Render Preview](https://fcv-agent-climate-preview.onrender.com/) service. This avoids the free service's idle sleep and keeps a long assessment on one host. Each run checked the deployed `/health` build SHA, completed all three stages through SSE, rejected any unreviewed `chunk` event, and saved reviewed completion events locally in the ignored `app_feedback/20260923_readiness_qa/` directory.

The Honduras cases used the public [P181166 PAD](https://documents1.worldbank.org/curated/en/099112224130011785/pdf/BOSIB-0763d08d-6db6-4e0f-b0a5-33dcc6acc0ac.pdf), with and without its public [ESCP](https://documents1.worldbank.org/curated/en/099102524074028310/pdf/P181166-eb1e7153-522a-4427-8501-e95109b7b048.pdf). The other public case used the Somalia STAIRP P513127 concept PID. I compared Honduras claims to the PAD, ESCP, and the source review recorded on 24 September. Somalia checks workflow breadth and contract integrity; it has not received an independent FCV/ESF analytical sign-off. No restricted OPCS or ESF corpus was uploaded.

## Live results

| Preview SHA | Public case and workflow | Operational result | Analytical result |
|---|---|---|---|
| `9429dad` | Honduras PAD only, step by step (`render-ready-96746e655c17`) | Stages 1-3 completed; 3 priorities; no raw draft SSE chunks or parse error. | **Fail.** HEIS approval became "activation"; PAD silence became absence of a security plan; national or regional crime reporting became corridor facts. |
| `9429dad` | Honduras PAD + ESCP, step by step (`render-ready-9086bc2bb9eb`) | Stages 1-3 completed; 4 priorities; no raw draft SSE chunks or parse error. | **Fail.** The output recognized ESCP action 4.4 but called the plan "not yet prepared" without status evidence, and retained unsupported departmental extortion assertions. |
| `9429dad` | Somalia concept PID, Express (`render-express-0bdb47b222f7`) | Stages 1-3 completed; 3 priorities; no raw draft SSE chunks or parse error. | **Contract fail.** The reviewer rewrote fixed `fcv_rating` and `fcv_responsiveness_rating` fields as long "Needs confirmation" prose. |
| `cedd817` | Somalia concept PID, Express (`render-express-c587147258ca`) | Stages 1-3 completed; 5 priorities; no raw draft SSE chunks or parse error. | **Contract pass.** Stage 3 kept both ratings as `Low`, exactly matching Stage 2. Substantive Somalia conclusions remain exploratory. |

The two Honduras runs took about 14.7 and 17.7 minutes. For PAD + ESCP, the source reviewer itself took 56, 91, and 61 seconds across Stages 1-3.

## Source findings that block release

- **HEIS status:** The PAD records a request and management approval on 22 October 2024. It does not establish that support was operating. The PAD-only Stage 2 reviewer nevertheless marked "HEIS activation" as supported by the checkbox and approval date; Stage 3 retained activation language.
- **Security Management Plan:** PAD silence cannot establish absence. The companion ESCP commits to assessing and implementing a Security Management Plan under action 4.4, with the action 1.1 instrument schedule. The PAD + ESCP run acknowledged the commitment but asserted that the plan was "not yet prepared." Current preparation or implementation status was not established by the supplied sources.
- **Site-level criminal risk:** PAD paragraph 58 supports "illicit activities in the Project area." It does not establish gang extortion, drug-trafficking control, or incidents at the named corridor. Both runs converted broader reporting into stronger corridor or departmental claims. These may motivate a site-specific assessment; they cannot be presented as verified project-site facts.
- **Playbook continuation:** The security-priority `/api/run-deeper` call completed and returned 6,008 characters, but described organized crime penetration of public works as a documented corridor condition and did not anchor the specific commitment and timing to ESCP action 4.4. The Playbook output needs its own provenance check before operational use.
- **Other project-specific duties:** The PAD + ESCP should distinguish ESCP actions E, 4.3, 4.4, and 10.2 from optional design advice. Each proposed deadline, recipient, target, or grievance channel requires its exact authority and trigger. FCV/ESF specialist review remains necessary.

The source reviewer made useful corrections but missed these material claims. In some cases it spent issue slots on routine supported facts or less consequential details. The result is a functioning review mechanism, not a reliable analytical release gate.

## UI, exports, and tests

The paid Preview browser loaded saved Honduras sessions. Summary and detailed views, copy actions, brief and full HTML/Word downloads, session save/load round-trip, and a 390-pixel mobile width check all passed their assertions. The generated files preserve the reviewed output, including the remaining source errors. The browser QA process stalled during Playwright shutdown after printing its pass result and was stopped; the completed assertions and downloaded files were inspected.

The complete local suite passed on `9429dad`: **1,364 tests**. After enum protection, **128 targeted parser and reviewer tests passed** on `cedd817`. A further full-suite attempt on `cedd817` made very slow progress in the Windows environment and was stopped at 52%; it did not report a test failure, but it is **not a full-suite pass**. A diagnostic step-route Somalia Stage 3 replay on `cedd817` also failed to return a completion event after the server logged reviewer completion. That replay used prior Express history, so it is an incomplete diagnostic, not a normal user workflow result. The fresh full Express run above did complete and preserved the rating contract.

## Release gates

1. Correct the Honduras source and status false positives in actual generated outputs, then repeat PAD-only and PAD + ESCP acceptance on the proposed final SHA.
2. Make the Playbook continuation source-aware, or keep it outside analytical acceptance until a specialist verifies its provenance.
3. Complete a full test suite on the final SHA and investigate the incomplete step-route replay if it reproduces with a normal saved session.
4. Obtain FCV/ESF specialist review of residual judgments and source use before production promotion or ITS handover.

The production Render service remained on `e12c725` at the final check. The internal ITS build was not changed.
